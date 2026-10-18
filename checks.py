import pandas as pd
from pathlib import Path
from rapidfuzz import fuzz
DATA = Path(__file__).parent / "data"


def load_data(folder=DATA):
    """Load the source-of-truth lists. Defaults to data/, or pass another folder."""
    folder = Path(folder)
    return {
        "roster": pd.read_csv(folder / "roster.csv"),
        "links": pd.read_csv(folder / "approved_links.csv"),
        "assets": pd.read_csv(folder / "approved_assets.csv"),
        "terms": pd.read_csv(folder / "terms.csv"),
    }


def result(level, platform, message, fix=""):
    """One finding. Level is Pass, Flag, or Escalate."""
    return {"level": level, "platform": platform, "message": message, "fix": fix}


def check_blog_links(post, data):
    """Failure 1: wrong link on the client's Webflow blog."""
    findings = []
    approved = data["links"][data["links"]["content_id"] == post["content_id"]]
    approved_urls = set(approved["url"])
    for link in post.get("links", []):
        if link["url"] in approved_urls:
            findings.append(result("Pass", "Webflow", f'"{link["text"]}" goes to an approved page.'))
        else:
            findings.append(result(
                "Escalate", "Webflow",
                f'"{link["text"]}" goes to {link["url"]}, which is not on the approved list.',
                "Replace it with the approved URL for this article."))
    return findings


def check_linkedin_tags(post, data):
    """Failure 2: wrong LinkedIn account tagged."""
    findings = []
    roster = data["roster"]
    tagged = set(post.get("tagged_urls", []))
    for _, person in roster.iterrows():
        if person["name"] not in post["text"]:
            continue
        if person["linkedin_url"] in tagged:
            findings.append(result("Pass", "LinkedIn", f'{person["name"]} is tagged with the verified profile.'))
        else:
            findings.append(result(
                "Escalate", "LinkedIn",
                f'{person["name"]} is not tagged with their verified profile.',
                f'Tag {person["linkedin_url"]}.'))
    for url in tagged - set(roster["linkedin_url"]):
        findings.append(result(
            "Escalate", "LinkedIn",
            f"Tagged profile {url} is not on the verified roster.",
            "Remove this tag and use the verified profile."))
    return findings


def check_x_handles(post, data):
    """Failure 3: X handle not used."""
    findings = []
    for _, person in data["roster"].iterrows():
        mentioned = person["name"] in post["text"] or person["x_handle"] in post["text"]
        if not mentioned:
            continue
        if person["x_handle"] in post["text"]:
            findings.append(result("Pass", "X", f'{person["name"]} uses the handle {person["x_handle"]}.'))
        else:
            findings.append(result(
                "Flag", "X",
                f'{person["name"]} is named but their X handle is missing.',
                f'Replace the name with {person["x_handle"]}.'))
    return findings


def check_final_assets(post, data):
    """Failure 4: archive file used instead of the final file."""
    findings = []
    assets = data["assets"][data["assets"]["content_id"] == post["content_id"]]
    finals = assets[assets["status"] == "final"]
    for path in post.get("assets", []):
        row = assets[assets["path"] == path]
        if not row.empty and row.iloc[0]["status"] == "final":
            findings.append(result("Pass", "Assets", f"{path} is the final version."))
        else:
            match = finals[finals["asset_name"].apply(lambda n: n in path)]
            fix = f'Use {match.iloc[0]["path"]}.' if not match.empty else "Use the file from the final folder."
            findings.append(result("Escalate", "Assets", f"{path} is not an approved final file.", fix))
    return findings


def check_spelling(post, data):
    """Failure 5: industry terms not spelled to standard."""
    findings = []
    approved = list(data["terms"]["approved"])
    for word in post["text"].replace(",", " ").replace(".", " ").split():
        clean = word.strip("@#()\"'")
        for term in approved:
            close = clean.lower() == term.lower() or fuzz.ratio(clean.lower(), term.lower()) >= 85
            if close and clean != term:
                findings.append(result("Flag", post["platform"].title(),
                                       f'"{clean}" should be spelled "{term}".',
                                       f'Change "{clean}" to "{term}".'))
    return findings

def check_names(post, data):
    """Catch misspelled speaker and company names, like 'Halcyon Comput'."""
    findings = []
    names = list(data["roster"]["name"])
    valid = set(names)
    words = post["text"].replace(",", " ").replace(".", " ").split()
    for name in names:
        size = len(name.split())
        for i in range(len(words) - size + 1):
            chunk = words[i:i + size]
            if any(w.startswith("@") for w in chunk):
                continue  # handles are checked elsewhere
            window = " ".join(chunk)
            if window in valid:
                continue  # an exact, correct name
            if fuzz.ratio(window.lower(), name.lower()) >= 85:
                findings.append(result("Flag", post["platform"].title(),
                                       f'"{window}" looks like a misspelling of "{name}".',
                                       f'Change "{window}" to "{name}".'))
    return findings