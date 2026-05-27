# Security Framework

## 1. Data Protection & Secure Storage
The hiring system handles sensitive PII (Personally Identifiable Information) and interview transcripts.
- **Storage Locations:**
  - AI Output & Reports: `reports/candidates/`
  - Audit Logs: `logs/audit/`
  - Parsed CVs: `data/processed/`
- **PII Masking:** The `ComplianceGuard` implements basic PII masking (`mask_pii()`), stripping raw emails and phone numbers from raw transcripts before they are passed to analytical models or stored long-term.
- **Encryption:** In a production environment, all data at rest must be encrypted via AES-256, and data in transit secured via TLS 1.3.

## 2. Access Control (RBAC)
Access to candidate scores, interview transcripts, and audit logs is strictly governed by Role-Based Access Control (RBAC).
- **Recruiters:** Can view Candidate Reports, Scores, and Decisions.
- **Interviewers:** Can only view Technical Scores (cannot view HR behavioral flags or overall decision until authorized).
- **Auditors:** Can view Audit Logs, Reports, and Decisions to verify compliance.
- **Admins:** Full system access, including manual execution of data retention wipes.
*Implemented via `ComplianceGuard.check_access(role, permission)` in `compliance_guard.py`.*

## 3. Immutability of Audit Trails
To prevent tampering with AI decisions:
- The `AuditLogger` appends data securely to `.log` files.
- In production, these logs should be shipped to a centralized, write-once-read-many (WORM) logging server (e.g., AWS CloudWatch, Datadog, or Splunk).

## 4. Prompt Injection & Malicious Input
Candidates may attempt to "jailbreak" the ATS or AI interview.
- **Defenses:** The `AnswerUnderstandingEngine` acts as an intermediary, filtering out non-contextual or anomalous text before it affects the final score.
- **Integrity Tags:** Unusual behavior during testing (e.g., tab switching) directly influences the `risk_tag`, flagging the profile for manual review.
