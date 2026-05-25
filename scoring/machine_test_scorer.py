import logging
from typing import Dict, Any, List
from machine_test.models import TaskType, TaskEvaluation, MachineTestReport
from scoring.weights_config import WEIGHTS_CONFIG

logger = logging.getLogger("MachineTestScorer")

class MachineTestScorer:
    """
    Integrates the machine test engine evaluation results with overall role profiling weights.
    Applies role-specific weights to Coding, Debugging, File-Based, and System Design tasks.
    """
    # Define task weights based on role brackets
    ROLE_TASK_WEIGHTS = {
        "technical": {
            TaskType.CODING: 0.40,
            TaskType.DEBUGGING: 0.30,
            TaskType.FILE_BASED: 0.15,
            TaskType.SYSTEM_DESIGN: 0.15
        },
        "leadership": {
            TaskType.CODING: 0.10,
            TaskType.DEBUGGING: 0.10,
            TaskType.FILE_BASED: 0.20,
            TaskType.SYSTEM_DESIGN: 0.60
        },
        "customer_facing": {
            TaskType.CODING: 0.20,
            TaskType.DEBUGGING: 0.20,
            TaskType.FILE_BASED: 0.30,
            TaskType.SYSTEM_DESIGN: 0.30
        },
        "entry_level": {
            TaskType.CODING: 0.50,
            TaskType.DEBUGGING: 0.30,
            TaskType.FILE_BASED: 0.10,
            TaskType.SYSTEM_DESIGN: 0.10
        },
        "default": {
            TaskType.CODING: 0.30,
            TaskType.DEBUGGING: 0.30,
            TaskType.FILE_BASED: 0.20,
            TaskType.SYSTEM_DESIGN: 0.20
        }
    }

    def __init__(self):
        self.weights = self.ROLE_TASK_WEIGHTS

    def get_role_weights(self, role_type: str) -> Dict[TaskType, float]:
        """
        Retrieves matching task-type weights for the given role title.
        """
        role_key = role_type.lower().strip()
        
        if "engineer" in role_key or "developer" in role_key or "data" in role_key or "technical" in role_key:
            if "senior" in role_key or "lead" in role_key or "principal" in role_key or "architect" in role_key:
                # Seniors focus heavily on System Design and Coding
                return {
                    TaskType.CODING: 0.25,
                    TaskType.DEBUGGING: 0.20,
                    TaskType.FILE_BASED: 0.15,
                    TaskType.SYSTEM_DESIGN: 0.40
                }
            return self.weights["technical"]
        elif "manager" in role_key or "lead" in role_key or "director" in role_key or "head" in role_key or "architect" in role_key:
            return self.weights["leadership"]
        elif "sales" in role_key or "support" in role_key or "customer" in role_key or "marketing" in role_key:
            return self.weights["customer_facing"]
        elif "intern" in role_key or "junior" in role_key or "entry" in role_key or "trainee" in role_key:
            return self.weights["entry_level"]
            
        return self.weights["default"]

    def score_machine_test(self, report: MachineTestReport, role_type: str) -> Dict[str, Any]:
        """
        Re-calculates the unified machine test score by applying role-specific task-type weights,
        enabling adaptive evaluation of candidates based on their target seniority and role.
        """
        role_weights = self.get_role_weights(role_type)
        evaluations = report.evaluations
        
        weighted_score_accum = 0.0
        applied_weights_sum = 0.0
        breakdown = {}

        # Log details
        logger.info(f"Scoring Machine Test for candidate role '{role_type}' using task-type weights...")

        for task_id, evaluation in evaluations.items():
            task_type = evaluation.task_type
            weight = role_weights.get(task_type, 0.25)
            
            weighted_score = evaluation.final_score * weight
            weighted_score_accum += weighted_score
            applied_weights_sum += weight
            
            breakdown[task_id] = {
                "task_title": task_id,
                "task_type": task_type.value,
                "individual_final_score": evaluation.final_score,
                "role_weight_applied": f"{int(weight * 100)}%",
                "weighted_contribution": round(weighted_score, 2),
                "metrics": {
                    "correctness": evaluation.correctness_score,
                    "efficiency": evaluation.efficiency_score,
                    "quality": evaluation.code_quality_score,
                    "approach": evaluation.approach_score
                }
            }

        # Normalize score in case not all four types are present
        final_score = weighted_score_accum / applied_weights_sum if applied_weights_sum > 0 else report.overall_machine_test_score
        final_score = round(final_score, 2)
        
        # Determine Readiness Band
        if final_score >= 85:
            band = "Exceptional Tech Capability (Offer Immediately)"
        elif final_score >= 70:
            band = "Strong Tech Capability (Proceed with Interview)"
        elif final_score >= 55:
            band = "Borderline Tech Capability (Requires Technical Follow-up)"
        else:
            band = "Poor Tech Capability (Reject)"
            
        return {
            "candidate_id": report.candidate_id,
            "role_evaluated_for": role_type,
            "weighted_machine_test_score": final_score,
            "readiness_band": band,
            "task_contributions": breakdown,
            "weight_distribution_used": {t.value: f"{int(w * 100)}%" for t, w in role_weights.items()}
        }
