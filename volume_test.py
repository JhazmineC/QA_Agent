"""Volume test: run the QA agent on a full generated week and grade it against the answer key."""

# 1. Imports
import json
import time
from pathlib import Path

import pandas as pd

from checks import (load_data, check_blog_links, check_linkedin_tags,
                    check_x_handles, check_final_assets, check_spelling, check_names)

# 2. Checks per platform
checks = {
    "webflow": [check_blog_links, check_final_assets, check_spelling, check_names],
    "linkedin": [check_linkedin_tags, check_spelling, check_names],
    "x": [check_x_handles, check_spelling, check_names],
}

# 3. Load data and start the timer
start = time.perf_counter()
data = load_data("data_volume")
key = pd.read_csv("test_cases/volume/answer_key.csv")

# 4. Run the agent on every post
rows = []
for _, row in key.iterrows():
    post = json.loads(Path(f"test_cases/volume/{row['post_id']}.json").read_text())
    findings = [f for check in checks[post["platform"]] for f in check(post, data)]
    flagged = any(f["level"] != "Pass" for f in findings)
    rows.append({"post_id": row["post_id"], "planted_error": row["planted_error"], "flagged": flagged})
elapsed = time.perf_counter() - start

# 5. Grade against the answer key
df = pd.DataFrame(rows)
has_error = df["planted_error"] != "none"
caught = (has_error & df["flagged"]).sum()
missed = (has_error & ~df["flagged"]).sum()
false_alarms = (~has_error & df["flagged"]).sum()

# 6. Print the scorecard
print(f"Posts checked:     {len(df)}")
print(f"Planted mistakes:  {has_error.sum()}")
print(f"Caught:            {caught}  ({caught / has_error.sum():.0%} detection rate)")
print(f"Missed:            {missed}")
print(f"False alarms:      {false_alarms}  (clean posts wrongly flagged)")
print(f"Total time:        {elapsed:.2f} seconds")
if missed or false_alarms:
    print("\nPosts to investigate:")
    print(df[(has_error & ~df["flagged"]) | (~has_error & df["flagged"])].to_string(index=False))