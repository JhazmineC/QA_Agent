
# Handoff QA Agent

## The Problem

I am currently responsible for quality assurance across 50 to 60 pieces of client content each week, including Webflow articles, social media posts, and supporting digital assets.

The challenge is not simply the volume. The workflow relies heavily on one reviewer, with limited standardized guardrails, automated validation, or institutional support. When quality assurance depends on one person's knowledge and availability, mistakes can slip through, and the process becomes difficult to sustain or transfer.

I am building the Handoff QA Agent to address that single point of failure. My goal is to establish a repeatable, documented QA process that reduces preventable errors and gives the next project manager the tools to manage quality assurance without starting from scratch.

## Built From Real Failures

The initial validation rules address recurring issues I have encountered in the existing workflow. I have since expanded the prototype to include name verification and missing-information checks.

| Failure | How the Agent Catches It | Severity |
|---|---|---|
| Wrong link on a client's Webflow blog | Compares submitted URLs against approved links for that content | Escalate |
| Wrong LinkedIn account tagged | Matches tags against verified profile URLs rather than display names | Escalate |
| X handle not used | Checks whether named speakers and companies use their verified X handles | Flag |
| Archived asset used instead of the final version | Compares referenced assets against approved final versions | Escalate |
| Industry terminology misspelled | Compares spelling and capitalization against an approved terminology dictionary | Flag |
| Speaker or company name misspelled | Uses fuzzy matching to identify possible errors in verified names | Flag |
| Missing required information | Checks whether the required fields for each publishing platform are present | Escalate |

## How It Works

- **Source of truth:** Four editable CSV files in `data/` maintain approved contacts, links, assets, and industry terminology. Reference information can be updated without modifying the Python validation logic.

- **Rule-based validation:** Python compares submitted content against approved reference data. Since many recurring errors involve information with a known correct value, deterministic validation is more appropriate than generative AI for these checks.

- **Platform-specific checks:** The agent applies validation rules according to the publishing platform. Webflow posts receive link and asset checks, LinkedIn posts receive profile-tag checks, and X posts receive handle checks. Spelling, name, and completeness checks are applied where relevant.

- **Severity tiers:** Findings are classified according to operational risk:
  - **Pass:** The applicable validation requirement is satisfied.
  - **Flag:** A discrepancy requires human review.
  - **Escalate:** A critical discrepancy requires confirmation or correction before publishing.

- **Human oversight:** The agent identifies potential publishing issues and recommends corrective action. The current prototype does not automatically prevent publication or replace editorial judgment.

- **Maintainability:** Separating reference data from validation logic reduces the technical knowledge required to update the system and supports future operational handoff.

## Project Structure

```text
QA_Agent/
├── data/
│   ├── roster.csv
│   ├── approved_links.csv
│   ├── approved_assets.csv
│   └── terms.csv
├── data_volume/
│   ├── roster.csv
│   ├── approved_links.csv
│   ├── approved_assets.csv
│   └── terms.csv
├── test_cases/
│   ├── volume/
│   │   ├── answer_key.csv
│   │   └── [generated JSON test posts]
│   ├── archive_file.json
│   ├── missing_x_handle.json
│   ├── spelling.json
│   ├── wrong_blog_link.json
│   └── wrong_linkedin_tag.json
├── checks.py
├── generate_data.py
├── test_run.py
├── volume_test.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Run It

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Run the original validation scenarios:

```bash
python test_run.py
```

### Generate Synthetic Test Data

```bash
python generate_data.py
```

The generator creates fictional company and speaker records, approved reference datasets, platform-specific content, and an answer key identifying the intentionally introduced errors.

A fixed random seed supports reproducible testing.

### Run the Expanded Volume Test

```bash
python volume_test.py
```

The expanded test evaluates both post-level and individual error-level detection, including whether each planted error receives the expected classification and severity.

It also reports false alarms, unexpected findings, and execution failures.

## Testing Methodology

I developed the testing framework in stages to evaluate the agent beyond the original five failure scenarios.

### Initial Validation

The first test suite recreated five recurring publishing errors using fictional content.

These tests established whether the individual validation rules could identify the problems they were designed to catch.

### Initial Volume Testing

I expanded testing to 180 generated posts across Webflow, LinkedIn, and X.

The initial volume test identified all 37 error-containing posts. However, testing also exposed false positives caused by X handles being interpreted as misspelled company names.

I corrected the name-validation behavior and reran the evaluation, eliminating the seven false alarms observed during development.

### Expanded Validation Testing

The second round introduced more complex scenarios:

- **Clean content:** Posts containing no intentionally introduced errors.
- **Single errors:** Posts containing one known publishing mistake.
- **Multiple errors:** Posts containing multiple intentionally introduced mistakes.
- **Missing information:** Posts missing fields required to complete validation.

I also updated the evaluation logic to measure whether the agent identifies the specific planted error and assigns the expected severity, rather than simply counting a post as successfully detected whenever any rule returns a warning.

The expanded test includes exception handling so validation failures can be identified and investigated.

## Results

### Expanded Volume Test

The final recorded Round 2 test evaluated 180 synthetic posts.

| Measure | Result |
|---|---|
| Total posts evaluated | 180 |
| Clean posts | 107 |
| Posts containing errors | 73 |
| Individual planted error instances | 100 |
| Error-containing posts detected | 73/73 (100%) |
| Individual errors detected | 100/100 (100%) |
| Correct error category | 73/73 posts (100%) |
| Correct category and severity | 73/73 posts (100%) |
| False-alarm posts | 0 |
| Unexpected findings | 0 |
| Validation crashes | 0 |
| Total execution time | 1.47 seconds |

### Results by Scenario

| Scenario | Posts | Correctly Evaluated |
|---|---:|---:|
| Clean | 107 | 107 |
| Single error | 35 | 35 |
| Multiple errors | 27 | 27 |
| Missing information | 11 | 11 |
| **Total** | **180** | **180** |

### Results by Error Category

| Error Category | Planted | Detected | Correct Severity |
|---|---:|---:|---:|
| Archived asset | 9 | 9 | 9 |
| Incorrect company or speaker name | 14 | 14 | 14 |
| Missing X handle | 15 | 15 | 15 |
| Missing required information | 11 | 11 | 11 |
| Incorrect industry terminology | 36 | 36 | 36 |
| Incorrect Webflow link | 8 | 8 | 8 |
| Incorrect LinkedIn tag | 7 | 7 | 7 |
| **Total** | **100** | **100** | **100** |

### What Testing Revealed

Testing identified problems that were not apparent during the initial development of the validation rules.

An early version of the name check incorrectly interpreted X handles as misspelled company names, resulting in seven false alarms.

Expanded testing also identified three unexpected findings associated with a LinkedIn post containing missing information. After reviewing and adjusting the validation behavior, the subsequent test returned no unexpected findings.

These iterations improved the agent's ability to distinguish actual discrepancies from valid content and incomplete submissions.

The final controlled test identified all 100 planted error instances without false alarms or validation crashes.

### Interpreting the Results

The results demonstrate successful detection and classification within the generated test dataset.

They do not establish production-level accuracy or confirm reductions in manual review time.

The reported execution time represents the synthetic batch evaluation, including data loading, validation, and result calculation. It does not represent the time required to gather, submit, or manually resolve content issues.

## Independent Project Ownership

I am developing this project independently in response to operational challenges I encounter in my current role.

My work includes identifying recurring QA failures, translating those issues into validation requirements, organizing approved reference data, developing the Python validation approach, creating fictional test scenarios, and evaluating the system's results.

The project is a personal proof of concept and is not deployed within my employer's production publishing environment.

## Operational Handoff and Maintainability

The project's central objective is to reduce the dependency created when quality assurance relies on one person's knowledge and availability.

The agent uses external reference files so approved information can be maintained without modifying its validation logic.

| Reference File | Purpose |
|---|---|
| `roster.csv` | Verified speaker, company, and social account information |
| `approved_links.csv` | Approved URLs associated with content IDs |
| `approved_assets.csv` | Approved final asset versions |
| `terms.csv` | Approved industry terminology and capitalization |

Reviewers can use the validation results to identify discrepancies and determine which issues require editorial review or escalation.

The current completeness rules also define required fields by publishing platform. These are prototype requirements and should be reviewed against actual publishing standards before production deployment.

Future governance improvements will include reference-data ownership, change logs, documented approval procedures, and a consistent record of validation and reviewer decisions.

## Intended Business Impact

My objective is to reduce the operational risk of a QA process that depends on one individual.

The agent is designed to:

- **Reduce preventable errors:** Identify incorrect links, profiles, terminology, names, and assets.
- **Improve operational continuity:** Preserve recurring verification requirements in a documented system that other reviewers can use.
- **Reduce repetitive manual work:** Automate straightforward comparisons so reviewers can spend more time on issues requiring judgment.
- **Standardize quality controls:** Apply consistent validation rules across different publishing platforms.
- **Support measurable improvement:** Establish a foundation for evaluating review efficiency, error rates, and process reliability.

Production-level time savings and error reduction remain to be measured.

## Why This Approach

I approached this as an operational problem before treating it as an AI use case.

I started by identifying the failures occurring in the existing publishing process and determining which could be resolved through standardized reference data and automated comparisons.

Most of these checks involve information that already has a known correct answer. For those problems, Python-based validation provides a straightforward, low-cost solution without introducing unnecessary language-model calls.

AI becomes more useful when the task requires interpreting meaning rather than comparing fixed values. For example, determining whether a quote accurately represents a source transcript requires contextual evaluation that the current validation rules do not provide.

By separating those requirements, I can introduce AI where it provides a practical benefit without adding complexity to checks that are already well suited to deterministic automation.

## Current Status and Roadmap

### Completed

- [x] Rule-based validation for seven error categories
- [x] Four editable reference datasets
- [x] Platform-specific validation rules
- [x] Pass, Flag, and Escalate classifications
- [x] Original five failure-scenario tests
- [x] Synthetic test-data generation
- [x] Post-level detection and classification reporting
- [x] Individual error-level detection and severity reporting
- [x] Multi-error test scenarios
- [x] Missing-information validation
- [x] False-positive identification and correction
- [x] Exception tracking in the expanded test
- [x] Expanded 180-post test with 100 planted errors

### Next Steps

- [ ] Expand edge-case testing for ambiguous names, unusual formatting, and malformed inputs
- [ ] Introduce a dedicated content inventory for reference validation
- [ ] Compare approved content against the live published version
- [ ] Integrate Claude for contextual checks, including quote accuracy against transcripts
- [ ] Develop a Streamlit interface for nontechnical users
- [ ] Implement post-publication alerts with a target response time of 120 seconds
- [ ] Evaluate Webflow webhooks and LinkedIn and X API integrations
- [ ] Establish baseline QA review times and post-publication correction rates
- [ ] Develop maintenance SOPs and governance procedures for reference updates
- [ ] Measure pilot adoption, review efficiency, and operational outcomes

---

**Project Status:** Functional Python-based, rule-driven quality assurance proof of concept. Not yet deployed to a live publishing environment.

**Data Disclosure:** All repository data is fictional. Test scenarios are reconstructed from real categories of operational failures. No confidential client information or proprietary employer data is included.