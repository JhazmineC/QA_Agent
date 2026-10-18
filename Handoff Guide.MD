# Handoff Guide: Handoff QA Agent

This guide is for the person taking over content QA. It explains what the agent does, how to run it, how to keep its reference data current, how to act on its findings, and what to do when something goes wrong.

All data in this repository is fictional.

---

## 1. Purpose and scope

The agent exists so content QA no longer depends on one person. It checks every post against a set of approved reference lists and reports anything that does not match.

### What the agent checks

| Check | Platform | What it catches |
|---|---|---|
| `check_blog_links` | Webflow | Any link not on the approved list for that article |
| `check_final_assets` | Webflow | Archive or draft files used instead of the approved final version |
| `check_linkedin_tags` | LinkedIn | Speakers or companies tagged with the wrong profile, or profiles not on the verified roster |
| `check_x_handles` | X | Speakers or companies named without their verified X handle |
| `check_spelling` | All | Industry terms that do not match the approved spelling (for example, Nvidia instead of NVIDIA) |
| `check_names` | All | Misspelled speaker or company names (for example, Halcyon Comput) |
| `check_completeness` | All | Missing text, links, tags, or files, and content IDs not on any approved list |

### What remains a human responsibility

The agent only knows what is in the reference lists. A person still owns:

- **Accuracy of the reference data.** If a wrong link is added to the approved list, the agent will approve it.
- **Content judgment.** Tone, voice, and whether the copy fits the client.
- **Quotes and claims.** Confirming that quotes and numbers match the transcript. The agent does not check this yet; see the roadmap in the README.
- **Client approval.** The agent does not replace sign-off from the client or content owner.
- **Publishing.** Posts are published natively, by a person. The agent does not post or edit anything.
- **New speakers and companies.** Anyone not yet in the roster will not be checked until they are added.

---

## 2. Getting started

### One-time setup

1. Install [Anaconda](https://www.anaconda.com/download) if it is not already installed.
2. Open the project folder in VS Code (**File > Open Folder > QA_Agent**).
3. Open the terminal in VS Code (**Ctrl + `**) and create the project environment:
   ```
   conda create -n qa_agent python=3.12 -y
   conda activate qa_agent
   pip install -r requirements.txt
   ```
4. In VS Code, press **Cmd + Shift + P**, choose **Python: Select Interpreter**, and pick **qa_agent**.

### Every Time You Work on the Project

1. Open the `QA_Agent` folder in VS Code.
2. Open **Terminal > New Terminal**.
3. Activate the Conda environment:

   ```bash
   conda activate qa_agent
   ```

Your terminal line should start with `(qa_agent)`. If it shows `(base)`, the environment is not active and the libraries will not be found.

### Run the tests

| Command | What it does | Expected result |
|---|---|---|
| `python test_run.py` | Runs the agent on the five real-failure test cases in `test_cases/` | Each known mistake is caught |
| `python generate_data.py` | Creates a fresh week of 180 fictional posts in `data_volume/` and `test_cases/volume/` | Prints the number of clean, single-error, multi-error, and missing-information posts |
| `python volume_test.py` | Grades the agent on the generated week | 100% detection, 0 false alarms, 0 crashes, and the line `No classification discrepancies identified.` |

Run all three after any change to `checks.py` or the reference data. If the volume test result changes, investigate before using the agent on real posts.

---

## 3. Maintaining reference data

The agent is only as reliable as these four files. Keep them current and they keep the agent accurate. All four live in the `data/` folder and can be edited in VS Code or any spreadsheet tool. Save them as CSV.

### Rules for every file

- Do not rename the files or change the column headers in the first row.
- No extra spaces after commas.
- Save, then run `python test_run.py` to confirm nothing broke.

### `roster.csv`: verified people and companies

| Column | What to enter | Example |
|---|---|---|
| `name` | Exact spelling as it should appear in posts | Dana Whitfield |
| `type` | `person` or `company` | person |
| `linkedin_url` | The verified profile URL, copied from the profile itself | linkedin.com/in/dana-whitfield-nw |
| `x_handle` | The verified X handle, including the @ | @dwhitfield |

**When to update:** before any post that features a new speaker or company. Always copy the LinkedIn URL from the actual profile, never search by name, since two people can share a name.

### `approved_links.csv`: approved links per piece of content

| Column | What to enter | Example |
|---|---|---|
| `content_id` | The episode or article ID | EP101 |
| `link_text` | The link's display text | Watch the full conversation |
| `url` | The exact approved destination | https://signalpath.example/episodes/northwind-inference |

**When to update:** when the content owner approves the links for a new episode or article. Add one row per link.

### `approved_assets.csv`: final and archived files

| Column | What to enter | Example |
|---|---|---|
| `content_id` | The episode or article ID | EP101 |
| `asset_name` | What the file is | thumbnail |
| `path` | Where the file lives | /final/EP101/thumbnail_v3.png |
| `status` | `final` or `archive` | final |
| `version` | The version number | 3 |

**When to update:** whenever a new final version is approved. Mark the new file `final` and change the previous one to `archive`. Only one file per asset should be `final`.

### `terms.csv`: approved industry spellings

| Column | What to enter | Example |
|---|---|---|
| `approved` | The correct spelling and capitalization | NVIDIA |

**When to update:** when a new company, product, or standard starts appearing in content. Check the spelling on the company's own website before adding it.

---

## 4. Reviewing findings

Every finding has a level, a message explaining what was found, and, for anything other than Pass, a suggested fix.

| Level | Meaning | Before publishing | If the post is already live |
|---|---|---|---|
| **Pass** | The item matches the approved reference data | No action needed | No action needed |
| **Flag** | A likely mistake that needs a quick human look, such as a missing X handle or a misspelled term | Fix it, or confirm it is intentional, before publishing | Correct the post as soon as possible |
| **Escalate** | A serious or client-facing problem, such as a wrong link, the wrong person tagged, an archive file, or missing information | **Stop.** Do not publish until the content owner confirms the fix | Correct or remove the post immediately and notify the content owner |

### How to respond

1. **Read the message and the fix.** Each one names exactly what is wrong and what it should be.
2. **Fix the post, not the reference data,** unless the reference data is what is wrong.
3. **If you believe the agent is wrong,** check the reference data first. Most unexpected results come from a missing or outdated row.
4. **Rerun the check after fixing** and confirm everything returns Pass.

### One problem, one alert

When required information is missing, the agent reports the root cause once rather than every downstream symptom. For example, a LinkedIn post with no tags produces one alert ("Missing tagged_urls"), not one alert per untagged person. Fix the root cause, then rerun to see any remaining issues.

---

## 5. Troubleshooting and escalation

### Missing data

| What you see | What it means | What to do |
|---|---|---|
| `Missing "text"` (or links, tagged_urls, assets) | The post is missing required information, so it cannot be fully checked | Add the missing information and rerun |
| `EP___ is not in the approved content list` | The content ID is wrong, or the approved lists have not been updated for this content | Confirm the ID with the content owner, or add the content to the reference files |
| A new speaker is not being checked | They are not in `roster.csv` yet | Add them with their verified LinkedIn URL and X handle |

### Unexpected results

| What you see | Likely cause | What to do |
|---|---|---|
| A correct post is flagged | The reference data is outdated, or a valid name is close to another name | Update the reference file. If it persists, log it as a false alarm and notify the agent owner |
| A known mistake is not caught | The item is not in the reference data, or the mistake is a type the agent does not check | Confirm the reference data, then report the gap to the agent owner |
| The volume test shows anything other than 100% and 0 | A recent change affected a check | Undo the most recent change, rerun, and investigate before using the agent on real posts |

### Errors when running the code

Read the **last line** of the error first: it says what went wrong. Then look a few lines up for the first file that belongs to this project, such as `checks.py, line 12`, to find where.

| Error | Likely cause | Fix |
|---|---|---|
| `FileNotFoundError` | A file name is misspelled or in the wrong folder | Check the exact name and location, for example `data/approved_assets.csv` |
| `KeyError: 'column_name'` | A CSV header was changed or a file is from an older version | Restore the header shown in Section 3, or rerun `generate_data.py` |
| `ModuleNotFoundError` | The `qa_agent` environment is not active | Run `conda activate qa_agent` |
| `CRASH in check_...` in the volume test | A check failed on unusual input | Note the post ID and check name, then notify the agent owner. Never ignore a crash: a crashed check sends no alert |

### Escalation path

| Situation | Who to contact |
|---|---|
| A content mistake that is already live | [Content owner name and contact] |
| A reference data question (which link or file is approved) | [Content owner name and contact] |
| A false alarm, missed mistake, or crash | [Agent owner name and contact] |
| Access to Webflow, LinkedIn, or X | [Platform admin name and contact] |

Fill in the contacts above before handing off.