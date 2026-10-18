
# Handoff QA Agent

## The Problem

I am currently responsible for quality assurance across 50 to 60 pieces of client content each week, including Webflow articles, social media posts, and supporting digital assets.

The challenge is not simply the volume. The workflow relies heavily on one reviewer, with limited standardized guardrails, automated validation, or institutional support. When quality assurance depends on one person's knowledge and availability, mistakes can slip through, and the process becomes difficult to sustain or transfer.

I am building the Handoff QA Agent to address that single point of failure. The goal is to establish a repeatable, documented QA process that reduces preventable errors and gives the next project manager the tools to manage quality assurance without having to start from scratch.

## Built From Real Failures

Every validation rule addresses an issue I have encountered in the existing workflow.

| Failure | How the Agent Catches It | Severity |
|---|---|---|
| Wrong link on a client's Webflow blog | Compares article URLs against an approved list of links specific to that content | Escalate |
| Wrong LinkedIn account tagged | Matches tags against verified profile URLs rather than display names, preventing confusion between individuals with similar names | Escalate |
| X handle not used | Checks whether named speakers and companies use their verified X handles | Flag |
| Archived asset used instead of the final version | Compares referenced assets against approved final versions | Escalate |
| Industry terminology misspelled | Validates spelling and capitalization against an approved terminology dictionary (e.g., Nvidia vs. NVIDIA) | Flag |

## How It Works

- **Source of truth:** Four editable spreadsheets in `data/` maintain approved contacts, links, assets, and industry terminology. Reference information can be updated without modifying the Python code.

- **Rule-based validation:** Python performs deterministic comparisons against approved reference data. Most recurring failures involve information that already has a known correct value, making rule-based automation more appropriate than generative AI for these checks.

- **Severity tiers:** Results are classified based on operational risk:
  - **Pass:** Validation requirements are satisfied. No further action is needed for that check.
  - **Flag:** A discrepancy requires human review.
  - **Escalate:** A critical discrepancy requires confirmation or correction before publishing.

- **Human oversight:** The agent supports quality assurance decisions rather than replacing editorial judgment. Escalated issues identify content that should be held for review; the current prototype does not automatically block publication.

- **Maintainability:** Separating reference data from validation logic makes the system easier to update, document, and transfer between team members.

## Run It

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Run the test suite:

```bash
python test_run.py
```

### Volume test
```bash
python generate_data.py
```
```bash
python volume_test.py
```

Each file in `test_cases/` recreates a known category of operational failure using fictional data.

The current prototype successfully identifies all five represented failure scenarios. These tests establish an initial validation baseline, not a production-level accuracy rate.

## Current Status and Roadmap

### Completed

- [x] Five rule-based validation checks
- [x] Four editable reference datasets
- [x] Severity classifications: Pass, Flag, and Escalate
- [x] Five test cases based on actual categories of publishing errors

### Next Steps

- [ ] Add valid-content test cases and evaluate false positives
- [ ] Compare approved content against the live published version
- [ ] Integrate Claude for contextual checks, including quote accuracy against source transcripts
- [ ] Develop a Streamlit interface for nontechnical users to submit and validate content
- [ ] Implement alerts within 120 seconds of a post going live
- [ ] Phase 2: Introduce automatic detection using Webflow webhooks and LinkedIn and X APIs
- [ ] Establish performance metrics to measure review time, errors detected, false positives, and post-publication corrections

## Intended Business Impact

The objective is to reduce the operational risk of a quality assurance process that depends on one individual.

By converting recurring manual checks into documented validation rules, this project is designed to:

- **Reduce preventable errors:** Identify incorrect links, tags, terminology, and assets before they reach clients or audiences.
- **Improve operational continuity:** Preserve critical QA knowledge in a system that can be maintained and used by other team members.
- **Reduce repetitive manual work:** Automate straightforward verification so reviewers can focus on issues requiring judgment.
- **Standardize quality controls:** Apply consistent validation requirements across high-volume client deliverables.
- **Support measurable improvement:** Establish a foundation for evaluating review efficiency, detection performance, and process reliability.

The prototype demonstrates the technical feasibility of the initial validation rules. Actual time savings and reductions in production errors remain to be measured through pilot testing.

## Why This Approach

I approached this as an operational problem before treating it as an AI use case.

The first step was identifying recurring failures and determining which could be addressed through process redesign, deterministic automation, or AI-assisted review.

For checks with known correct answers, Python-based validation provides a straightforward, low-cost solution without requiring generative AI.

For issues requiring contextual interpretation, such as determining whether a quote accurately reflects a transcript, an AI-assisted approach is planned for the next phase.

The larger objective is to build a sustainable process, not simply introduce another tool. A successful solution should be understandable, maintainable, and useful to the people responsible for the workflow after its original developer moves on.


## Results
On a generated week of 180 posts across 20 companies, with mistakes planted in 37:

| Measure | Result |
|---|---|
| Detection rate | 100% (37 of 37 caught) |
| False alarms | 0 |
| Total time | About 1.5 seconds |

The volume test also caught a bug during development: an early version of the name check flagged X handles like @vertexsolutions as misspelled company names, causing 7 false alarms. Fixing it brought false alarms to zero.

---
**Project Status:** Functional rule-based proof of concept. Not yet integrated into a live production publishing workflow.

**Data Disclosure:** All data in this repository is fictional. Test scenarios are reconstructed from real categories of operational failures. No confidential client information or proprietary employer data is included.
