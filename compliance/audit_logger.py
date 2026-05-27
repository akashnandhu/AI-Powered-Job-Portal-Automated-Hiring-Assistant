import logging
import json
import os
from datetime import datetime

class AuditLogger:
    """
    Secure, immutable audit trail system for AI scores and hiring decisions.
    Ensures that every AI decision is transparent, auditable, and traceable.
    """
    def __init__(self, log_dir="logs/audit"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Configure decision logger
        self.decision_logger = logging.getLogger("DecisionAudit")
        self.decision_logger.setLevel(logging.INFO)
        decision_handler = logging.FileHandler(os.path.join(self.log_dir, "ai_decisions.log"))
        decision_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        if not self.decision_logger.handlers:
            self.decision_logger.addHandler(decision_handler)

        # Configure score logger
        self.score_logger = logging.getLogger("ScoreAudit")
        self.score_logger.setLevel(logging.INFO)
        score_handler = logging.FileHandler(os.path.join(self.log_dir, "ai_scores.log"))
        score_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        if not self.score_logger.handlers:
            self.score_logger.addHandler(score_handler)

    def log_decision(self, candidate_id: str, decision: str, confidence: float, reasoning: list):
        """Logs the final AI hiring decision."""
        log_entry = {
            "candidate_id": candidate_id,
            "decision": decision,
            "confidence": confidence,
            "reasoning": reasoning,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.decision_logger.info(f"DECISION_RECORD: {json.dumps(log_entry)}")

    def log_score(self, candidate_id: str, stage: str, score: float, metadata: dict = None):
        """Logs AI-generated scores for any specific stage (ATS, HR, Technical)."""
        log_entry = {
            "candidate_id": candidate_id,
            "stage": stage,
            "score": score,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        self.score_logger.info(f"SCORE_RECORD: {json.dumps(log_entry)}")

audit_logger = AuditLogger()
