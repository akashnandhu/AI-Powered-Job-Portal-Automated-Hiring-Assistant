# Fairness Review Notes

## 1. Overview
This review assessed the AI scoring mechanisms (ATS Scorer, Understanding Engine) to identify and mitigate potential biases, ensuring fairness across all candidate demographics.

## 2. Identified Risks & Actions Taken
- **Age Bias via Experience**: 
  - *Risk*: Uncapped experience scoring linearly rewards candidates with more years of experience, potentially disadvantaging younger candidates while implicitly favoring older demographics unnecessarily.
  - *Action*: Implemented an experience cap within the `fairness_engine.py`. Experience beyond 15 years yields no additional advantage, explicitly mitigating implicit age bias.
- **Gender & Demographic Bias**:
  - *Risk*: Resumes and transcripts often contain gender pronouns (he/she/him/her) or implicit demographic signals (age, marital status).
  - *Action*: Enhanced the `mask_sensitive_info` utility in `utils/normalization.py` to aggressively mask gender terms and demographic keywords prior to semantic processing.
- **Keyword Stuffing Penalty**:
  - *Risk*: Candidates who "game" the system by stuffing keywords could unfairly outrank highly qualified candidates.
  - *Action*: A fairness penalty is applied for candidates listing over 30 skills, enforcing a quality-over-quantity evaluation.

## 3. Explainability Integration
Added explicit `explainability_notes` to the candidate scoring schema (`api/schemas/common.py`). This guarantees that each scoring decision is accompanied by human-readable insights, aiding in bias audits and human oversight.
