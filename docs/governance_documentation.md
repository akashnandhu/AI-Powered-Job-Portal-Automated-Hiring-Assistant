# Governance & Data Retention Documentation

## 1. Data Lifecycle Management
Candidate data must not be kept indefinitely. The Automated Hiring Assistant implements an automated data lifecycle.

### Retention Policy
- **Maximum Retention Period:** 90 Days (configurable).
- **Scope:** Includes parsed resumes, AI-generated reports (`reports/candidates/`), interview transcripts, and audit logs.
- **Enforcement:** The `DataRetentionManager` (`compliance/data_retention.py`) automatically scans configured directories and securely wipes files that exceed the retention limit based on their modification timestamps.

## 2. Model Governance
The models powering this system require strict oversight.
- **Versioning:** Any changes to `DecisionEngine` thresholds or `weights_config.py` must be committed to version control and documented in the Optimization Report.
- **Performance Audits:** Bi-annual audits must be conducted using the `AuditLogger` outputs to verify that the "Selected" vs "Rejected" ratios remain consistent and free of demographic skew.

## 3. Incident Response
If a security breach or compliance violation occurs:
1. **Halt AI Pipeline:** Immediately revoke API keys and stop the `main.py` orchestrator.
2. **Review Logs:** Security teams will review `logs/audit/ai_decisions.log` and `logs/audit/ai_scores.log` to identify the scope of exposed data.
3. **Notify:** Affected candidates must be notified within 72 hours per GDPR guidelines.

## 4. Compliance Checklist for Deployment
- [ ] Ensure `DataRetentionManager` is scheduled via a CRON job (e.g., running daily at 00:00).
- [ ] Ensure `ComplianceGuard.verify_candidate_consent()` is hooked into the initial application submission API.
- [ ] Confirm all directories in `logs/audit` are restricted at the OS-level to admin accounts only.
