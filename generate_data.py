"""Generate a randomized week of fictional content for volume testing."""
import json
import random
from pathlib import Path

import pandas as pd

random.seed(42)

ROOT = Path(__file__).parent
DATA = ROOT / "data_volume"
DATA.mkdir(exist_ok=True)
OUT = ROOT / "test_cases" / "volume"
OUT.mkdir(parents=True, exist_ok=True)

# Fictional companies: (company name, short name for URLs and handles, [two speakers])
COMPANIES = [
    ("Northwind Silicon", "northwind", ["Dana Whitfield", "Marcus Lee"]),
    ("Tech Innovations Inc", "techinnovations", ["Sarah Johnson", "David Brown"]),
    ("Global Solutions Ltd", "globalsolutions", ["Emily Davis", "Michael Wilson"]),
    ("Creative Minds Co", "creativeminds", ["Olivia Martinez", "James Anderson"]),
    ("Halcyon Compute", "halcyon", ["Priya Raman", "Theo Grant"]),
    ("Cobalt Ridge Networks", "cobaltridge", ["Liam O'Brien", "Sofia Castellano"]),
    ("Lumen Grid Systems", "lumengrid", ["Grace Okafor", "Ethan Brooks"]),
    ("Vantage Thermal", "vantagethermal", ["Nora Delgado", "Isaac Moreno"]),
    ("Quarry Labs", "quarrylabs", ["Hana Takeda", "Owen Fletcher"]),
    ("Meridian Fabric", "meridianfabric", ["Zara Malik", "Caleb Turner"]),
    ("Solace Storage", "solacestorage", ["Mei Chen", "Jonah Pierce"]),
    ("Brightwater AI", "brightwater", ["Amara Nwosu", "Felix Hartmann"]),
    ("Keystone Racks", "keystoneracks", ["Lucia Romero", "Victor Song"]),
    ("Summit Dynamics", "summitdynamics", ["Elena Petrova", "Ravi Kapoor"]),
    ("Aurora Tech", "auroratech", ["Sofia Rossi", "Liam O'Connor"]),
    ("Nimbus Networks", "nimbusnetworks", ["Isabella Cruz", "Ethan Patel"]),
    ("Pinnacle Systems", "pinnaclesystems", ["Ava Thompson", "Noah Kim"]),
    ("Vertex Solutions", "vertexsolutions", ["Mia Chen", "Lucas Silva"]),
    ("Horizon Labs", "horizonlabs", ["Chloe Martin", "Ethan Nguyen"]),
    ("Stratosphere Inc", "stratosphereinc", ["Lily Johnson", "Aiden Brown"]),
]

# Industry terms: approved spelling -> a common wrong version to plant
TECH_TERMS = {
    "NVIDIA": "Nvidia", "PCIe": "Pcie", "Wi-Fi": "WiFi", "HPE": "Hpe", "AMD": "Amd",
    "CXL": "Cxl", "HBM": "Hbm", "Ethernet": "Ethernt", "USB": "Usb",
    "Thunderbolt": "ThunderBolt", "DDR": "Ddr", "NVMe": "Nvme", "SATA": "Sata",
    "RAID": "Raid", "SAS": "Sas", "InfiniBand": "Infiniband",
    "DisplayPort": "Displayport", "HDMI": "Hdmi", "VGA": "Vga", "DVI": "Dvi",
}


def handle(name):
    return "@" + name.lower().replace(" ", "_").replace("'", "").replace(".", "")[:15]


def slug(name):
    return name.lower().replace(" ", "-").replace("'", "").replace(".", "")


def misspell(name):
    """Plant a realistic typo: drop the last letter of the longest word."""
    words = name.split()
    i = max(range(len(words)), key=lambda n: len(words[n]))
    words[i] = words[i][:-1]
    return " ".join(words)


# 1. Source-of-truth files
roster, links, assets = [], [], []
for company, short, people in COMPANIES:
    for person in people:
        roster.append({"name": person, "type": "person",
                       "linkedin_url": f"linkedin.com/in/{slug(person)}-{short}",
                       "x_handle": handle(person)})
    roster.append({"name": company, "type": "company",
                   "linkedin_url": f"linkedin.com/company/{short}",
                   "x_handle": f"@{short}"})

episodes = []
for i in range(60):
    content_id = f"EP{200 + i}"
    company, short, people = random.choice(COMPANIES)
    episodes.append((content_id, company, short, people))
    links.append({"content_id": content_id, "link_text": "Watch the full conversation",
                  "url": f"https://signalpath.example/episodes/{content_id.lower()}"})
    links.append({"content_id": content_id, "link_text": f"Read the {company} announcement",
                  "url": f"https://{short}.example/news/{content_id.lower()}"})
    assets.append({"content_id": content_id, "asset_name": "thumbnail",
                   "path": f"/final/{content_id}/thumbnail_v3.png", "status": "final", "version": 3})
    assets.append({"content_id": content_id, "asset_name": "thumbnail",
                   "path": f"/archive/{content_id}/thumbnail_v1.png", "status": "archive", "version": 1})

pd.DataFrame(roster).to_csv(DATA / "roster.csv", index=False)
pd.DataFrame(links).to_csv(DATA / "approved_links.csv", index=False)
pd.DataFrame(assets).to_csv(DATA / "approved_assets.csv", index=False)
pd.DataFrame({"approved": list(TECH_TERMS)}).to_csv(DATA / "terms.csv", index=False)

# 2. Posts: clean, single-error, multi-error, and missing-information
ERRORS = {
    "webflow": ["wrong_link", "archive_file", "spelling", "company_name"],
    "linkedin": ["wrong_tag", "spelling", "company_name"],
    "x": ["missing_handle", "spelling"],
}
REMOVABLE = {
    "webflow": ["text", "links", "assets", "content_id"],
    "linkedin": ["text", "tagged_urls", "content_id"],
    "x": ["text", "content_id"],
}
roster_df = pd.DataFrame(roster)
url = dict(zip(roster_df["name"], roster_df["linkedin_url"]))
xh = dict(zip(roster_df["name"], roster_df["x_handle"]))
key = []

for content_id, company, short, people in episodes:
    a, b = people
    t1, t2 = random.sample(list(TECH_TERMS), 2)
    for platform in ["webflow", "linkedin", "x"]:
        roll = random.random()
        if roll < 0.12:
            scenario, errors = "multi", random.sample(ERRORS[platform], 2)
        elif roll < 0.30:
            scenario, errors = "single", [random.choice(ERRORS[platform])]
        elif roll < 0.38:
            scenario, errors = "missing", ["missing_info"]
        else:
            scenario, errors = "clean", []

        terms = [TECH_TERMS[t1] if "spelling" in errors else t1, t2]
        shown_company = misspell(company) if "company_name" in errors else company

        if platform == "webflow":
            post = {"text": f"{a} and {b} of {shown_company} discuss {terms[0]} and {terms[1]} in data centers.",
                    "links": [{"text": "Watch the full conversation",
                               "url": f"https://signalpath.example/episodes/{content_id.lower()}"},
                              {"text": f"Read the {company} announcement",
                               "url": f"https://{short}.example/news/{content_id.lower()}"}],
                    "assets": [f"/final/{content_id}/thumbnail_v3.png"]}
            if "wrong_link" in errors:
                post["links"][1]["url"] = f"https://{random.choice(COMPANIES)[1]}.example/news/old-post"
            if "archive_file" in errors:
                post["assets"] = [f"/archive/{content_id}/thumbnail_v1.png"]
        elif platform == "linkedin":
            post = {"text": f"{a} and {b} of {shown_company} on {terms[0]} and {terms[1]}.",
                    "tagged_urls": [url[a], url[b], url[company]]}
            if "wrong_tag" in errors:
                post["tagged_urls"][1] = f"linkedin.com/in/{slug(b)}-impostor"
        else:
            names = [xh[a], xh[b], xh[company]]
            if "missing_handle" in errors:
                names[1] = b
            post = {"text": f"{names[0]} and {names[1]} of {names[2]} on {terms[0]} and {terms[1]}."}

        post.update({"content_id": content_id, "platform": platform})
        if scenario == "missing":
            field = random.choice(REMOVABLE[platform])
            if field == "content_id" and random.random() < 0.5:
                post["content_id"] = "EP999"  # an ID that is not on any approved list
            else:
                post.pop(field)

        post_id = f"{content_id}_{platform}"
        (OUT / f"{post_id}.json").write_text(json.dumps(post, indent=2))
        key.append({"post_id": post_id, "platform": platform, "scenario": scenario,
                    "planted_errors": ";".join(errors)})

pd.DataFrame(key).to_csv(OUT / "answer_key.csv", index=False)
counts = pd.DataFrame(key)["scenario"].value_counts()
print(f"Created {len(roster)} roster rows, {len(episodes)} episodes, {len(key)} posts.")
print(counts.to_string())