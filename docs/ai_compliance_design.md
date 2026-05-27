# AI Compliance & Ethical Design

## 1. Overview
The Automated Hiring Assistant operates under a strict compliance design to adhere to modern data privacy laws (GDPR, CCPA) and ethical AI frameworks (e.g., EU AI Act). The goal is to ensure all automated hiring decisions are auditable, fair, and transparent.

## 2. Consent-Based Data Usage
Before any AI processing begins (ATS Parsing, HR Interviewing, Technical Evaluation), explicit candidate consent must be verified.
- **Requirement:** Candidates must opt-in to AI evaluation and video/audio recording.
- **Enforcement:** Managed by `ComplianceGuard` (`compliance/compliance_guard.py`). If `consent_to_ai_processing` is False, the pipeline halts immediately.

## 3. Auditable Decision Making
Every AI-driven decision must leave a secure, immutable trace.
- **Score Logs:** All raw and normalized scores from individual modules (ATS, HR, Technical) are logged via the `AuditLogger` (`compliance/audit_logger.py`).
- **Decision Logs:** Final hiring decisions (Selected, Hold/Review, Rejected) along with their confidence scores and specific reasoning are logged to `logs/audit/ai_decisions.log`.
- **Transparency:** The generated Candidate Evaluation Reports (`reports/candidates/`) are fully explainable, mapping the exact criteria and thresholds used for the decision.

## 4. Bias Mitigation & Fairness
To prevent systemic bias:
- **Demographic Blindness:** The semantic matcher and scoring engines are strictly forbidden from processing demographic markers (Age, Gender, Race).
- **Consistent Evaluation:** All candidates for a given role are evaluated against the identical `weights_config.py` schema to prevent subjective human drift.

## 5. Candidate Rights
- **Right to Explanation:** Candidates have the right to request the reasoning behind their automated rejection. The `reasoning` array in `decision_outputs.json` facilitates this.
- **Right to Erasure (Right to be Forgotten):** Facilitated by the `DataRetentionManager`.
