import math
import logging
from typing import List, Dict, Any
from machine_test.models import TaskDefinition, TaskSubmission, TaskEvaluation, MachineTestReport, TaskType
from machine_test.task_evaluators import (
    CodingTaskEvaluator,
    DebuggingTaskEvaluator,
    FileBasedTaskEvaluator,
    SystemDesignTaskEvaluator
)

logger = logging.getLogger("MachineTestScoringEngine")

class MachineTestScoringEngine:
    """
    Orchestrates the evaluation of multiple machine test tasks, applies
    time-based multipliers, hint penalties, and snapshot progression analyses,
    and consolidates them into a final report.
    """
    def __init__(self):
        self.evaluators = {
            TaskType.CODING: CodingTaskEvaluator(),
            TaskType.DEBUGGING: DebuggingTaskEvaluator(),
            TaskType.FILE_BASED: FileBasedTaskEvaluator(),
            TaskType.SYSTEM_DESIGN: SystemDesignTaskEvaluator()
        }

    def calculate_time_multiplier(self, time_taken: int, target_time: int, max_time: int, correctness: float) -> float:
        """
        Calculates time-based scoring multiplier.
        - If candidate finishes early AND correctness is >= 75%:
          They receive a speed bonus, up to +10% (multiplier 1.10).
        - If candidate finishes within target time:
          Multiplier is 1.0.
        - If candidate exceeds target time:
          A gradual decay is applied down to 0.75 at max_time.
        """
        if time_taken <= 0:
            return 1.0
            
        if time_taken < target_time:
            if correctness >= 75.0:
                # Early finish bonus formula: linear scaling up to +10%
                percent_saved = (target_time - time_taken) / target_time
                bonus = percent_saved * 0.10
                return round(1.0 + bonus, 3)
            return 1.0
        elif time_taken <= max_time:
            # Overtime decay formula: linear decay from 1.0 to 0.75
            total_overtime_window = max_time - target_time
            if total_overtime_window <= 0:
                return 1.0
            overtime = time_taken - target_time
            decay = (overtime / total_overtime_window) * 0.25
            return round(1.0 - decay, 3)
        else:
            return 0.75  # Hard floor for taking more than max_time

    def analyze_snapshot_progression(self, submission: TaskSubmission) -> float:
        """
        Evaluates the iterative problem-solving approach by auditing snapshots.
        - Structured progression: Incremental changes (reasonable edit distances)
          paired with intermediate compile/test runs, leading to an upward trend in tests passed.
        - Unstructured progression: Huge character additions in a single step with zero intermediate compiles,
          or erratic code regressions (guesses).
        Returns a bonus up to +10% (0.0 to 10.0 points added to final score).
        """
        snapshots = submission.snapshots
        executions = submission.executions
        
        if len(snapshots) < 3 or len(executions) < 2:
            # Not enough iterative steps to grant progression bonus
            return 0.0
            
        bonus = 0.0
        feedback_notes = []
        
        # Heuristic 1: Verify incremental development (reasonable edit distance)
        # Large chunk copy-pasting is heavily penalized, while steady, step-by-step additions are rewarded.
        total_edit_distance = sum(snap.edit_distance for snap in snapshots)
        avg_edit_distance = total_edit_distance / len(snapshots) if snapshots else 0
        
        if 50 < avg_edit_distance < 800:
            # Steady typing
            bonus += 3.0
            
        # Heuristic 2: Verify active test execution loop
        # A candidate who compiles/runs their code frequently during development shows structural competence.
        execs_to_snaps_ratio = len(executions) / len(snapshots)
        if 0.3 <= execs_to_snaps_ratio <= 1.5:
            # Solid balance between editing and testing
            bonus += 3.0
            
        # Heuristic 3: Trend analysis of tests passed
        # Did their test pass rate generally increase or stabilize? Or did it jump erratically?
        pass_trends = []
        for ex in executions:
            if ex.total_tests > 0:
                pass_trends.append(ex.tests_passed / ex.total_tests)
            else:
                pass_trends.append(1.0 if ex.passed else 0.0)
                
        is_improving = True
        for i in range(1, len(pass_trends)):
            if pass_trends[i] < pass_trends[i-1] - 0.25:
                # Regressed by more than 25% passed, suggesting trial-and-error/guessing
                is_improving = False
                break
                
        if is_improving and pass_trends[-1] >= pass_trends[0]:
            bonus += 4.0
            
        return round(bonus, 2)

    def evaluate_submission(self, task: TaskDefinition, submission: TaskSubmission) -> TaskEvaluation:
        """
        Grades an individual task, factoring in correctness, efficiency, quality, approach,
        then modifying it using time multipliers, hint penalties, and progression rewards.
        """
        evaluator = self.evaluators.get(task.task_type)
        if not evaluator:
            raise ValueError(f"No evaluator registered for task type: {task.task_type}")
            
        # 1. Compute baseline evaluation metrics
        evaluation = evaluator.evaluate(task, submission)
        
        # 2. Time-based scoring logic
        time_mult = self.calculate_time_multiplier(
            time_taken=submission.time_taken_seconds,
            target_time=task.target_time_seconds,
            max_time=task.max_time_seconds,
            correctness=evaluation.correctness_score
        )
        evaluation.time_multiplier = time_mult
        
        # 3. Hint penalties (-5.0 points per hint used)
        hint_penalty = submission.hints_used * 5.0
        evaluation.hint_penalty = hint_penalty
        
        # 4. Snapshot progression analysis
        prog_bonus = self.analyze_snapshot_progression(submission)
        evaluation.progression_bonus = prog_bonus
        
        # 5. Apply modifiers to calculate the final adjusted score
        # Final Score = (Raw Score * Time Multiplier) - Hint Penalty + Progression Bonus
        adjusted_score = (evaluation.raw_score * time_mult) - hint_penalty + prog_bonus
        
        # Clamp between 0.0 and 100.0
        evaluation.final_score = round(max(0.0, min(100.0, adjusted_score)), 2)
        
        # Add feedback reflections on time and progression
        if time_mult > 1.0:
            evaluation.feedback.append(f"Completed early! Granted a speed bonus multiplier of {time_mult}x.")
        elif time_mult < 1.0:
            evaluation.feedback.append(f"Exceeded target completion time. Applied time-decay factor of {time_mult}x.")
            
        if hint_penalty > 0:
            evaluation.feedback.append(f"Used {submission.hints_used} hint(s), resulting in a -{hint_penalty} points penalty.")
            
        if prog_bonus >= 7.0:
            evaluation.feedback.append("Excellent iterative progression observed. Step-by-step refinements and proactive testing demonstrate senior habits.")
        elif prog_bonus >= 4.0:
            evaluation.feedback.append("Good disciplined editing. Applied logical edits and verified with standard compilation checks.")
            
        return evaluation

    def compile_report(self, candidate_id: str, role_type: str, task_pairs: List[tuple]) -> MachineTestReport:
        """
        Compiles evaluations of all attempted tasks into a final, unified report.
        Each task_pair is a tuple: (TaskDefinition, TaskSubmission)
        """
        evaluations = {}
        total_time = 0
        total_score_accum = 0.0
        total_tasks = len(task_pairs)
        
        timeline_summary = []
        strengths = []
        dev_areas = []
        
        # Grade each task
        for task, submission in task_pairs:
            eval_res = self.evaluate_submission(task, submission)
            evaluations[task.task_id] = eval_res
            
            total_time += submission.time_taken_seconds
            total_score_accum += eval_res.final_score
            
            # Map timeline snapshot records
            timeline_summary.append({
                "task_id": task.task_id,
                "title": task.title,
                "type": task.task_type.value,
                "difficulty": task.difficulty,
                "time_taken_seconds": submission.time_taken_seconds,
                "raw_score": eval_res.raw_score,
                "final_score": eval_res.final_score,
                "hints_used": submission.hints_used,
                "compiles_run": len(submission.executions)
            })
            
            # Generate strengths & development areas based on metric scores
            if eval_res.correctness_score >= 85.0:
                strengths.append(f"Outstanding execution accuracy on {task.title} ({task.task_type.value}).")
            if eval_res.efficiency_score >= 85.0 and task.task_type != TaskType.SYSTEM_DESIGN:
                strengths.append(f"High performance optimization skills in {task.title} (cyclomatic/execution profiling).")
            if eval_res.code_quality_score >= 85.0:
                strengths.append(f"Consistent clean code compliance and layout standards in {task.title}.")
            if eval_res.approach_score >= 85.0:
                strengths.append(f"Strategic structural design and exception handling on {task.title}.")
                
            if eval_res.correctness_score < 60.0:
                dev_areas.append(f"Refine syntax and logic in {task.title} to prevent failing critical test suites.")
            if eval_res.efficiency_score < 60.0:
                dev_areas.append(f"Reduce structural complexity and memory footprint in {task.title}.")
            if eval_res.code_quality_score < 60.0:
                dev_areas.append(f"Adopt stronger naming, modularity, and comment patterns in {task.title}.")
            if eval_res.approach_score < 60.0:
                dev_areas.append(f"Improve defensive validation, edge-case coverage, and structural planning in {task.title}.")

        # Calculate average machine test score
        overall_score = round(total_score_accum / total_tasks, 2) if total_tasks > 0 else 0.0
        
        # Readiness Banding
        if overall_score >= 85.0:
            band = "Exceptional Technical Ability (Advanced / Architect Level)"
        elif overall_score >= 70.0:
            band = "Strong Technical Ability (Highly Competent / Professional Level)"
        elif overall_score >= 55.0:
            band = "Borderline Tech Ability (Entry Level / Needs Core Mentoring)"
        else:
            band = "Poor Tech Ability (Unsuitable / Significant Gaps)"
            
        # Deduplicate recommendations and limit to top 4 for concise, clean representation
        strengths = list(dict.fromkeys(strengths))[:4]
        dev_areas = list(dict.fromkeys(dev_areas))[:4]
        
        if not strengths:
            strengths.append("Demonstrated basic task completion mechanics.")
        if not dev_areas:
            dev_areas.append("Maintain existing high programming standards and code review disciplines.")
            
        return MachineTestReport(
            candidate_id=candidate_id,
            role_type=role_type,
            overall_machine_test_score=overall_score,
            evaluations=evaluations,
            total_time_spent_seconds=total_time,
            total_tasks_attempted=total_tasks,
            overall_band=band,
            strengths=strengths,
            development_areas=dev_areas,
            timeline_summary=timeline_summary
        )
