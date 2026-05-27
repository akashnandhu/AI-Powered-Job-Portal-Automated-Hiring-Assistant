from typing import Dict, Any, List

class ComplianceGuard:
    """
    Ensures consent-based data usage and applies access control logic to sensitive information.
    """
    def __init__(self):
        # RBAC (Role-Based Access Control) Matrix
        self.role_permissions = {
            "recruiter": ["view_reports", "view_scores", "view_decisions"],
            "interviewer": ["view_technical_scores"],
            "auditor": ["view_audit_logs", "view_reports", "view_decisions"],
            "admin": ["view_reports", "view_scores", "view_decisions", "view_audit_logs", "manage_retention"]
        }

    def verify_candidate_consent(self, candidate_data: Dict[str, Any]) -> bool:
        """
        Validates if the candidate explicitly consented to AI processing and data storage.
        """
        consent_flag = candidate_data.get("consent_to_ai_processing", False)
        if not consent_flag:
            # Raise exception or reject processing in production
            return False
        return True

    def check_access(self, user_role: str, required_permission: str) -> bool:
        """
        Checks if the given role has the required permission.
        """
        if user_role not in self.role_permissions:
            return False
        return required_permission in self.role_permissions[user_role]

    def mask_pii(self, text: str) -> str:
        """
        Simple PII masking for secure storage (e.g., masking emails or phone numbers).
        """
        import re
        # Mask Emails
        text = re.sub(r'[\w\.-]+@[\w\.-]+', '[REDACTED EMAIL]', text)
        # Mask Phone numbers (simple heuristic)
        text = re.sub(r'\+?\d{10,14}', '[REDACTED PHONE]', text)
        return text
