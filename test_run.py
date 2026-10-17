import json
from checks import (load_data, check_blog_links, check_linkedin_tags,
                    check_x_handles, check_final_assets, check_spelling)

data = load_data()

# Which checks run for each platform
checks = {
    "webflow": [check_blog_links, check_final_assets, check_spelling],
    "linkedin": [check_linkedin_tags, check_spelling],
    "x": [check_x_handles, check_spelling],
}

test_cases = ["wrong_blog_link", "wrong_linkedin_tag", "missing_x_handle",
              "archive_file", "spelling"]

for name in test_cases:
    post = json.load(open(f"test_cases/{name}.json"))
    print(f"\n=== {name} ===")
    for check in checks[post["platform"]]:
        for f in check(post, data):
            print(f'{f["level"]:9} {f["message"]}')
            if f["fix"]:
                print(f'          Fix: {f["fix"]}')