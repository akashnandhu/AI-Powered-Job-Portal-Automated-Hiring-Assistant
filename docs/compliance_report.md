# Compliance Readiness Report

## 1. Data Retention & Deletion (GDPR/CCPA Alignment)
- **Automated Data Purge**: Implemented a `cleanup_stale_jobs` mechanism within `api/services/background.py`. The system automatically purges candidate data and job artifacts from in-memory and persistent stores once the retention period (e.g., 24 hours for temporary processing data) expires.
- **Compliance Status**: This guarantees that temporary candidate parsing data is not stored indefinitely, adhering to data minimization and storage limitation principles.

## 2. Algorithmic Accountability
- **Traceability**: All automated decisions (e.g., shortlisting categorization) include transparent `similarity_scores` and `explainability_notes` that detail exactly why a candidate received their specific score.
- **Human-in-the-Loop (HITL)**: The system is designed to augment, not replace, human recruiters. AI-generated insights serve as recommendations, keeping the final hiring decision in human hands to meet regulatory expectations.

## 3. Consent Management
- Outlined explicit consent protocols in the AI Ethics documentation, requiring frontend portals to obtain candidate approval prior to data ingestion.

## 4. Next Steps for Full Certification
- Implement encrypted at-rest storage for long-term candidate records.
- Establish an annual third-party algorithmic bias audit.
- Provide a candidate-facing portal for "Right to be Forgotten" (data deletion) requests.
