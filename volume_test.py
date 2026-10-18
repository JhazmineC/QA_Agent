"""Run the QA agent against synthetic posts and grade the findings."""

import json
import time
from pathlib import Path

import pandas as pd

from checks import (
    load_data,
    check_blog_links,
    check_linkedin_tags,
    check_x_handles,
    check_final_assets,
    check_spelling,
    check_names,
    check_completeness,
)

ROOT = Path(__file__).parent

# 1. Define the applicable checks for each platform.
# Each check is paired with its corresponding error category.

CHECKS = {
    "webflow": [
        ("missing_info", check_completeness),
        ("wrong_link", check_blog_links),
        ("archive_file", check_final_assets),
        ("spelling", check_spelling),
        ("company_name", check_names),
    ],
    "linkedin": [
        ("missing_info", check_completeness),
        ("wrong_tag", check_linkedin_tags),
        ("spelling", check_spelling),
        ("company_name", check_names),
    ],
    "x": [
        ("missing_info", check_completeness),
        ("missing_handle", check_x_handles),
        ("spelling", check_spelling),
        ("company_name", check_names),
    ],
}

# 2. Define the severity expected for each planted error.

EXPECTED_LEVELS = {
    "wrong_link": "Escalate",
    "wrong_tag": "Escalate",
    "missing_handle": "Flag",
    "archive_file": "Escalate",
    "spelling": "Flag",
    "company_name": "Flag",
    "missing_info": "Escalate",
}

# 3. Load reference data and the generated answer key.

start = time.perf_counter()

data = load_data(ROOT / "data_volume")

key = pd.read_csv(
    ROOT / "test_cases" / "volume" / "answer_key.csv"
).fillna("")

# 4. Evaluate each generated post.

rows = []
error_rows = []

for _, row in key.iterrows():

    post_path = (
        ROOT / "test_cases" / "volume"
        / f"{row['post_id']}.json"
    )

    post = json.loads(post_path.read_text())

    findings = []
    crashed = False

    for category, check_function in CHECKS[post["platform"]]:
        try:
            for finding in check_function(post, data):
                findings.append({
                    "category": category,
                    "level": finding["level"],
                    "message": finding["message"],
                })
        except Exception as error:
            # A crash means no alert gets sent, so record it instead of stopping.
            crashed = True
            print(f"CRASH in {check_function.__name__} on {row['post_id']}: {error}")

    # Only non-Pass findings are errors requiring review.
    errors = [
        finding for finding in findings
        if finding["level"] != "Pass"
    ]

    # A post can now have zero, one, or several planted errors.
    planted = set(filter(None, row["planted_errors"].split(";")))
    has_error = len(planted) > 0
    found_categories = {finding["category"] for finding in errors}

    # Did any rule flag the post?
    flagged = len(errors) > 0

    # Did the correct rule identify every planted error?
    correct_category = (
    (planted <= found_categories if has_error else not flagged)
    and not crashed
    )

    # Did each planted error get the expected severity?
    correct_severity = (
    (
        all(
            any(
                finding["category"] == error
                and finding["level"] == EXPECTED_LEVELS[error]
                for finding in errors
            )
            for error in planted
        ) if has_error else not flagged
    )
    and not crashed
)

    # Identify findings from rules that were not expected to fire.
    unexpected_findings = [
        finding for finding in errors
        if finding["category"] not in planted
    ]

    rows.append({
        "post_id": row["post_id"],
        "platform": post["platform"],
        "scenario": row["scenario"],
        "planted_errors": ";".join(sorted(planted)) or "none",
        "has_error": has_error,
        "flagged": flagged,
        "correct_category": correct_category,
        "correct_severity": correct_severity,
        "unexpected_findings": len(unexpected_findings),
        "crashed": crashed,
    })
    
   
    # Grade each planted error individually.
    for planted_error in planted:
        matching_findings = [
            finding for finding in errors
            if finding["category"] == planted_error
        ]

        error_detected = len(matching_findings) > 0

        severity_matched = any(
            finding["level"] == EXPECTED_LEVELS[planted_error]
            for finding in matching_findings
        )

        error_rows.append({
            "post_id": row["post_id"],
            "platform": post["platform"],
            "scenario": row["scenario"],
            "error": planted_error,
            "detected": error_detected and not crashed,
            "correct_severity": severity_matched and not crashed,
        })


elapsed = time.perf_counter() - start

# 5. Calculate performance metrics.

df = pd.DataFrame(rows)

error_posts = df[df["has_error"]]
clean_posts = df[~df["has_error"]]

caught = int(
    (error_posts["flagged"] & ~error_posts["crashed"]).sum()
)
missed = len(error_posts) - caught

category_correct = int(error_posts["correct_category"].sum())

severity_correct = int(error_posts["correct_severity"].sum())

false_alarms = int(clean_posts["flagged"].sum())

unexpected_total = int(df["unexpected_findings"].sum())

crashes = int(df["crashed"].sum())


def percentage(numerator, denominator):
    return numerator / denominator if denominator else 0


# 6. Print the overall scorecard.

print("\nHANDOFF QA AGENT | VOLUME TEST")
print("-" * 45)

print(f"Posts checked:          {len(df)}")
print(f"Planted-error posts:    {len(error_posts)}")
print(f"Detected posts:         {caught}")
print(f"Missed posts:           {missed}")
print(f"False-alarm posts:      {false_alarms}")
print(f"Crashes:                {crashes}")

print(
    f"Post detection rate:    "
    f"{percentage(caught, len(error_posts)):.1%}"
)

print(
    f"Correct error category: "
    f"{category_correct}/{len(error_posts)} "
    f"({percentage(category_correct, len(error_posts)):.1%})"
)

print(
    f"Correct category/level: "
    f"{severity_correct}/{len(error_posts)} "
    f"({percentage(severity_correct, len(error_posts)):.1%})"
)

print(f"Unexpected findings:    {unexpected_total}")
print(f"Total execution time:   {elapsed:.2f} seconds")

# 7. Print results by scenario.

print("\nRESULTS BY SCENARIO")
print("-" * 45)

scenario_summary = (
    df.groupby("scenario")
    .agg(
        posts=("post_id", "count"),
        flagged=("flagged", "sum"),
        correct_category=("correct_category", "sum"),
        correct_severity=("correct_severity", "sum"),
    )
)

print(scenario_summary.to_string())

# 8. Print results by error category.

print("\nRESULTS BY ERROR CATEGORY")
print("-" * 45)

error_df = pd.DataFrame(error_rows)

category_summary = (
    error_df.groupby("error")
    .agg(
        planted=("post_id", "count"),
        detected=("detected", "sum"),
        correct_severity=("correct_severity", "sum"),
    )
)

category_summary["detection_rate"] = (
    category_summary["detected"]
    / category_summary["planted"]
    * 100
).round(1)

print(category_summary.to_string())

print(
    f"\nIndividual errors detected: "
    f"{int(error_df['detected'].sum())}/{len(error_df)}"
)

# 9. Identify posts that need investigation.

problem_posts = df[
    (
        (df["has_error"] & ~df["correct_category"])
        | (df["has_error"] & ~df["correct_severity"])
        | (~df["has_error"] & df["flagged"])
        | (df["unexpected_findings"] > 0)
        | df["crashed"]
    )
]

if not problem_posts.empty:
    print("\nPOSTS REQUIRING INVESTIGATION")
    print("-" * 45)
    print(problem_posts.to_string(index=False))
else:
    print("\nNo classification discrepancies identified.")
    
    # 10. Fail the test when validation problems remain.

failed = (
    missed > 0
    or false_alarms > 0
    or crashes > 0
    or category_correct != len(error_posts)
    or severity_correct != len(error_posts)
    or unexpected_total > 0
    or not error_df["detected"].all()
    or not error_df["correct_severity"].all()
)

if failed:
    raise SystemExit(
        "\nFAILED: Review the validation results above."
    )

print("\nPASSED: All expected validations succeeded.")