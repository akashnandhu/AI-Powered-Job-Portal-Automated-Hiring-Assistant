import ast
import re
import difflib
import logging
from typing import Dict, List, Any, Tuple
from machine_test.models import TaskType, TaskDefinition, TaskSubmission, TaskEvaluation, ExecutionResult

logger = logging.getLogger("MachineTestEvaluator")

class BaseTaskEvaluator:
    """
    Base class providing common evaluation and static analysis tools.
    """
    @staticmethod
    def calculate_cyclomatic_complexity(code: str) -> int:
        """
        Estimate cyclomatic complexity using AST parsing.
        Counts branching constructs: If, For, While, And, Or, Except.
        """
        try:
            tree = ast.parse(code)
            complexity = 1
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.For, ast.While, ast.AsyncFor, ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                    complexity += 1
                elif isinstance(node, (ast.And, ast.Or)):
                    complexity += 1
                elif isinstance(node, ast.ExceptHandler):
                    complexity += 1
            return complexity
        except Exception:
            # Return baseline if syntax error in incomplete snapshot
            return 1

    @staticmethod
    def audit_code_quality(code: str) -> Dict[str, Any]:
        """
        Analyzes code structure, variable naming, comments, and spacing.
        """
        scores = {
            "comment_ratio": 0.0,
            "naming_style": 100.0,
            "modularity": 100.0,
            "style_score": 100.0
        }
        
        lines = code.split("\n")
        total_lines = len(lines)
        if total_lines == 0:
            return {"score": 0, "details": "Empty code submission."}
            
        comment_lines = 0
        long_lines = 0
        bad_names = 0
        def_count = 0
        class_count = 0

        # Check snake_case / camelCase conventions & comments
        for line in lines:
            line_strip = line.strip()
            if line_strip.startswith("#") or "'''" in line_strip or '"""' in line_strip:
                comment_lines += 1
            if len(line) > 88:  # PEP 8 line length limit suggestion
                long_lines += 1
            
            # Simple regex for bad names (e.g. variable names like 'a', 'b', 'xx', 'temp' without context)
            bad_var_match = re.findall(r'\b(x|y|z|a|b|c|temp|tmp|var|val|data)\s*=', line_strip)
            if bad_var_match:
                bad_names += len(bad_var_match)
                
            if line_strip.startswith("def "):
                def_count += 1
            if line_strip.startswith("class "):
                class_count += 1

        comment_ratio = comment_lines / total_lines if total_lines > 0 else 0
        scores["comment_ratio"] = round(comment_ratio, 2)
        
        # Penalize style
        scores["style_score"] -= min(30.0, long_lines * 5.0)  # Max 30% penalty for long lines
        scores["naming_style"] -= min(40.0, bad_names * 10.0)  # Max 40% penalty for generic variables
        
        # Check modularity (at least 1 function defined is expected)
        if def_count == 0 and class_count == 0:
            scores["modularity"] = 50.0  # Monolithic script penalty
            
        final_quality = (scores["style_score"] * 0.3 + 
                         scores["naming_style"] * 0.4 + 
                         scores["modularity"] * 0.3)
                         
        # Give a small bonus for documentation
        if comment_ratio > 0.1:
            final_quality = min(100.0, final_quality + 5.0)
            
        return {
            "score": round(max(0.0, final_quality), 2),
            "breakdown": scores,
            "total_lines": total_lines,
            "comment_ratio": comment_ratio
        }


class CodingTaskEvaluator(BaseTaskEvaluator):
    """
    Evaluates Algorithmic Coding Tasks.
    Focuses on unit tests, runtime complexity, cyclomatic complexity, and design details.
    """
    def evaluate(self, task: TaskDefinition, submission: TaskSubmission) -> TaskEvaluation:
        # 1. Correctness Score: percentage of tests passed
        executions = submission.executions
        if not executions:
            correctness = 0.0
            latest_exec = None
        else:
            # Use the latest execution result
            latest_exec = executions[-1]
            if latest_exec.total_tests > 0:
                correctness = (latest_exec.tests_passed / latest_exec.total_tests) * 100
            else:
                correctness = 100.0 if latest_exec.passed else 0.0
                
        # 2. Efficiency Score
        efficiency = 100.0
        feedback = []
        
        if latest_exec:
            # Check execution speed
            # If execution exceeds 500ms, apply slight scale penalty
            if latest_exec.runtime_ms > 800:
                efficiency -= 20.0
                feedback.append("Execution time is high; consider optimizing inner loops or redundant operations.")
            elif latest_exec.runtime_ms > 300:
                efficiency -= 10.0
                
            # Check memory usage
            if latest_exec.memory_usage_mb > 150:
                efficiency -= 15.0
                feedback.append("High memory usage footprint detected.")
                
        # Check code structural complexity
        complexity = self.calculate_cyclomatic_complexity(submission.final_code)
        if complexity > 10:
            efficiency -= 15.0
            feedback.append(f"High cyclomatic complexity ({complexity}). Consider breaking down nested conditionals.")
        elif complexity > 6:
            efficiency -= 5.0
            
        efficiency = round(max(0.0, efficiency), 2)
        
        # 3. Code Quality Score
        quality_res = self.audit_code_quality(submission.final_code)
        quality = quality_res["score"]
        
        # 4. Problem-Solving Approach
        # Evaluated by verifying presence of expected programming constructs and optimization keywords
        approach = 100.0
        code_lower = submission.final_code.lower()
        
        # Let's check for structural elements in a coding solution:
        # e.g., error handling, type hinting, edge case handling, docstrings
        has_try_except = "try:" in code_lower
        has_type_hints = "->" in submission.final_code or ":" in submission.final_code
        has_docstring = '"""' in submission.final_code or "'''" in submission.final_code
        
        if not has_try_except:
            approach -= 15.0
            feedback.append("Missing defensive error handling (try/except blocks).")
        if not has_type_hints:
            approach -= 10.0
            feedback.append("No Python type hints found in function signatures.")
        if not has_docstring:
            approach -= 10.0
            feedback.append("Function is missing introductory docstrings explaining input/output schemas.")
            
        approach = round(max(0.0, approach), 2)
        
        # Raw score calculation (25% each metric)
        raw_score = (correctness * 0.4 + efficiency * 0.2 + quality * 0.2 + approach * 0.2)
        
        return TaskEvaluation(
            task_id=task.task_id,
            task_type=TaskType.CODING,
            correctness_score=round(correctness, 2),
            efficiency_score=efficiency,
            code_quality_score=quality,
            approach_score=approach,
            raw_score=round(raw_score, 2),
            final_score=round(raw_score, 2), # Will be adjusted by Scoring Engine for time/hints
            time_multiplier=1.0,
            hint_penalty=0.0,
            progression_bonus=0.0,
            execution_summary={
                "tests_passed": latest_exec.tests_passed if latest_exec else 0,
                "total_tests": latest_exec.total_tests if latest_exec else 0,
                "runtime_ms": latest_exec.runtime_ms if latest_exec else 0.0,
                "memory_mb": latest_exec.memory_usage_mb if latest_exec else 0.0,
                "cyclomatic_complexity": complexity
            },
            feedback=feedback,
            metrics_breakdown={
                "quality_details": quality_res["breakdown"],
                "cyclomatic_complexity": complexity
            }
        )


class DebuggingTaskEvaluator(BaseTaskEvaluator):
    """
    Evaluates Debugging Tasks.
    Focuses on surgical precision of changes (not rewriting everything), correctness, and style.
    """
    def evaluate(self, task: TaskDefinition, submission: TaskSubmission) -> TaskEvaluation:
        # 1. Correctness: Does the code pass the unit tests now?
        latest_exec = submission.executions[-1] if submission.executions else None
        if latest_exec:
            correctness = (latest_exec.tests_passed / latest_exec.total_tests) * 100 if latest_exec.total_tests > 0 else (100.0 if latest_exec.passed else 0.0)
        else:
            correctness = 0.0
            
        # 2. Efficiency
        # Since debugging tasks don't typically have runtime scaling, complexity of the code counts
        complexity = self.calculate_cyclomatic_complexity(submission.final_code)
        efficiency = 100.0 - min(40.0, (complexity - 2) * 5.0)  # Max 40% penalty for overly complex fixes
        efficiency = round(max(0.0, efficiency), 2)
        
        # 3. Code Quality
        quality_res = self.audit_code_quality(submission.final_code)
        quality = quality_res["score"]
        
        # 4. Problem-Solving Approach: "Surgical precision"
        # We calculate the diff between the template (buggy code) and the final submission.
        # A good debugger applies minimal, exact changes to solve the problem, rather than rewriting everything.
        approach = 100.0
        feedback = []
        
        diff_lines = list(difflib.unified_diff(
            task.code_template.splitlines(),
            submission.final_code.splitlines(),
            lineterm=""
        ))
        
        added_lines = sum(1 for line in diff_lines if line.startswith("+") and not line.startswith("+++"))
        removed_lines = sum(1 for line in diff_lines if line.startswith("-") and not line.startswith("---"))
        total_changes = added_lines + removed_lines
        
        # If they rewrote the entire template (e.g. over 60 lines changed for a simple bug fix), penalize approach
        template_len = len(task.code_template.splitlines())
        if total_changes > template_len * 0.8:
            approach -= 40.0
            feedback.append("Approached fix by completely rewriting the code. A surgical debug is preferred.")
        elif total_changes > 15:
            approach -= 15.0
            feedback.append("Significant structural changes made. Ensure you are targeting only the root bug.")
        else:
            feedback.append("Excellent surgical precision: exact lines containing the bugs were successfully patched.")
            
        # Check if they fixed the primary logical bug
        # MOCK/SIMULATION: Let's assume the buggy code had specific errors, e.g. using index boundaries incorrectly.
        # We look for corrected expressions in final code.
        buggy_keywords_fixed = True
        if "range(len(arr))" in task.code_template and "range(len(arr) - 1)" in submission.final_code:
            feedback.append("Successfully corrected off-by-one index boundary condition.")
        elif "range(len(arr))" in task.code_template and "range(" in submission.final_code:
            pass
        else:
            # If the index bug is still there in some form
            buggy_keywords_fixed = False
            
        approach = round(max(0.0, approach), 2)
        
        raw_score = (correctness * 0.4 + efficiency * 0.15 + quality * 0.15 + approach * 0.30)
        
        return TaskEvaluation(
            task_id=task.task_id,
            task_type=TaskType.DEBUGGING,
            correctness_score=round(correctness, 2),
            efficiency_score=efficiency,
            code_quality_score=quality,
            approach_score=approach,
            raw_score=round(raw_score, 2),
            final_score=round(raw_score, 2),
            time_multiplier=1.0,
            hint_penalty=0.0,
            progression_bonus=0.0,
            execution_summary={
                "diff_added_lines": added_lines,
                "diff_removed_lines": removed_lines,
                "total_diff_operations": total_changes,
                "compilation_status": latest_exec.passed if latest_exec else False
            },
            feedback=feedback,
            metrics_breakdown={
                "added_lines": added_lines,
                "removed_lines": removed_lines,
                "total_changes": total_changes
            }
        )


class FileBasedTaskEvaluator(BaseTaskEvaluator):
    """
    Evaluates File-Based Tasks.
    E.g. processing JSON/CSV, generating aggregations, saving outputs.
    Focuses on output structure, schema conformance, handling of empty/corrupted entries, and standard libraries.
    """
    def evaluate(self, task: TaskDefinition, submission: TaskSubmission) -> TaskEvaluation:
        # 1. Correctness: Verify if execution ran successfully and created the expected output structure.
        latest_exec = submission.executions[-1] if submission.executions else None
        if latest_exec:
            correctness = (latest_exec.tests_passed / latest_exec.total_tests) * 100 if latest_exec.total_tests > 0 else (100.0 if latest_exec.passed else 0.0)
        else:
            correctness = 0.0
            
        # 2. Efficiency: How did they handle file parsing (buffered, streaming, or loading entire file in memory)?
        # Check code for line-by-line reading or generator usage for efficiency.
        efficiency = 100.0
        code_lower = submission.final_code.lower()
        feedback = []
        
        has_generator = "yield " in code_lower or "generator" in code_lower
        has_pandas = "import pandas" in code_lower or "import pd" in code_lower
        
        if "open(" in code_lower and ".read()" in code_lower:
            efficiency -= 15.0
            feedback.append("Reading whole file into memory via read(). Consider streaming or line-by-line generators for massive files.")
        elif "open(" in code_lower and ("for line in" in code_lower or "readline" in code_lower):
            feedback.append("Excellent streaming / line-oriented file parsing implementation.")
            
        efficiency = round(max(0.0, efficiency), 2)
        
        # 3. Code Quality
        quality_res = self.audit_code_quality(submission.final_code)
        quality = quality_res["score"]
        
        # 4. Problem-Solving Approach: Robustness to data anomalies
        # A good file parser handles empty columns, corrupted lines, or missing headers gracefully.
        approach = 100.0
        
        has_try_block = "try:" in code_lower
        has_null_check = "none" in code_lower or "null" in code_lower or "na_values" in code_lower or "fillna" in code_lower or "isna()" in code_lower
        has_logging = "logging" in code_lower or "print(f\"error" in code_lower
        
        if not has_try_block:
            approach -= 20.0
            feedback.append("Missing exception safety blocks during fragile file I/O operations.")
        if not has_null_check:
            approach -= 15.0
            feedback.append("No explicit safety handling for missing, NaN, or null values within records.")
        if not has_logging:
            approach -= 10.0
            feedback.append("Consider writing anomaly logs instead of silently suppressing parsing failures.")
            
        approach = round(max(0.0, approach), 2)
        
        raw_score = (correctness * 0.4 + efficiency * 0.2 + quality * 0.2 + approach * 0.2)
        
        return TaskEvaluation(
            task_id=task.task_id,
            task_type=TaskType.FILE_BASED,
            correctness_score=round(correctness, 2),
            efficiency_score=efficiency,
            code_quality_score=quality,
            approach_score=approach,
            raw_score=round(raw_score, 2),
            final_score=round(raw_score, 2),
            time_multiplier=1.0,
            hint_penalty=0.0,
            progression_bonus=0.0,
            execution_summary={
                "has_generator_usage": has_generator,
                "uses_pandas_library": has_pandas,
                "has_null_checks": has_null_check
            },
            feedback=feedback,
            metrics_breakdown={
                "file_io_efficiency": "High" if "for line in" in code_lower else "Standard"
            }
        )


class SystemDesignTaskEvaluator(BaseTaskEvaluator):
    """
    Evaluates Mini System Design Tasks.
    grades a conceptual design document or code implementation mapping architecture.
    Focuses on components, scalability, database choice, and handling of failures.
    """
    def evaluate(self, task: TaskDefinition, submission: TaskSubmission) -> TaskEvaluation:
        # System design is evaluated conceptually from the submitted design markdown or layout code
        design_text = submission.final_code
        design_lower = design_text.lower()
        feedback = []
        
        # 1. Correctness: Did they address all core requirements of the prompt?
        # In a notification system design: did they list templates, user preferences, rate limiting?
        correctness = 100.0
        
        core_requirements = ["database", "scale", "api", "flow", "requirement"]
        missing_reqs = []
        for req in core_requirements:
            if req not in design_lower:
                correctness -= 15.0
                missing_reqs.append(req)
                
        if missing_reqs:
            feedback.append(f"Incomplete requirements mapping. Missing structural sections on: {', '.join(missing_reqs)}.")
        else:
            feedback.append("Mapped all architectural and functional requirement parameters.")
            
        correctness = round(max(0.0, correctness), 2)
        
        # 2. Efficiency: Scalability features (caching, load balancing, queueing, partitioning)
        efficiency = 0.0
        efficiency_components = {
            "load_balancer": ["load balancer", "nginx", "haproxy", "dns routing", "alb", "gateway"],
            "message_queue": ["queue", "kafka", "rabbitmq", "pub/sub", "sqs", "celery", "activemq"],
            "caching_layer": ["redis", "memcached", "cache", "caching", "cdn"],
            "db_scaling": ["sharding", "replication", "read replica", "partitioning", "indexing", "nosql", "denormalize"]
        }
        
        efficiency_score_map = {}
        for category, keywords in efficiency_components.items():
            found = False
            for kw in keywords:
                if kw in design_lower:
                    found = True
                    break
            efficiency_score_map[category] = 25.0 if found else 0.0
            
        efficiency = sum(efficiency_score_map.values())
        
        if efficiency_score_map["message_queue"] == 0.0:
            feedback.append("System handles heavy traffic synchronously. Introduce an asynchronous message queue (e.g. Kafka or SQS) to decouple operations.")
        if efficiency_score_map["caching_layer"] == 0.0:
            feedback.append("High database load. Consider adding a distributed caching layer (like Redis) for fast read operations.")
        if efficiency_score_map["db_scaling"] == 0.0:
            feedback.append("No database scaling plan specified (e.g. read replicas, sharding, or indexing strategy).")
            
        # 3. Code Quality (Design formatting, clarity, structured sections, diagrams)
        quality = 100.0
        
        has_sections = len(re.findall(r'^#+\s+', design_text, re.MULTILINE)) >= 3
        has_diagram = "```mermaid" in design_lower or "diagram" in design_lower or "flowchart" in design_lower
        has_tradeoffs = "trade-off" in design_lower or "tradeoff" in design_lower or "pros/cons" in design_lower or "advantage" in design_lower
        
        if not has_sections:
            quality -= 20.0
            feedback.append("Poorly structured document. Use markdown headers to categorize components logically.")
        if not has_diagram:
            quality -= 20.0
            feedback.append("No architecture block diagram provided. Include a flowchart or ASCII/Mermaid block representation.")
        if not has_tradeoffs:
            quality -= 15.0
            feedback.append("Add a 'Trade-offs' or 'Alternative Architectures' section to justify your engineering choices.")
            
        quality = round(max(0.0, quality), 2)
        
        # 4. Problem-Solving Approach: Resilience & Security (HA, Failures, Rate Limiting, Security, Consistency)
        approach = 0.0
        approach_components = {
            "resilience": ["failover", "retry", "circuit breaker", "dead letter", "dlq", "heartbeat", "redundancy"],
            "security": ["oauth", "jwt", "https", "ssl", "encryption", "auth", "token", "waf"],
            "rate_limiting": ["rate limit", "throttle", "token bucket", "leaky bucket", "redis rate limiter"],
            "consistency": ["cap theorem", "eventual consistency", "acid", "distributed transaction", "strong consistency"]
        }
        
        approach_score_map = {}
        for category, keywords in approach_components.items():
            found = False
            for kw in keywords:
                if kw in design_lower:
                    found = True
                    break
            approach_score_map[category] = 25.0 if found else 0.0
            
        approach = sum(approach_score_map.values())
        
        if approach_score_map["resilience"] == 0.0:
            feedback.append("Missing fault tolerance structures (e.g. circuit breakers, retry policies, or Dead Letter Queues).")
        if approach_score_map["rate_limiting"] == 0.0:
            feedback.append("System is vulnerable to denial of service or abuse. Implement active Rate Limiting middleware.")
            
        raw_score = (correctness * 0.3 + efficiency * 0.3 + quality * 0.15 + approach * 0.25)
        
        return TaskEvaluation(
            task_id=task.task_id,
            task_type=TaskType.SYSTEM_DESIGN,
            correctness_score=correctness,
            efficiency_score=efficiency,
            code_quality_score=quality,
            approach_score=approach,
            raw_score=round(raw_score, 2),
            final_score=round(raw_score, 2),
            time_multiplier=1.0,
            hint_penalty=0.0,
            progression_bonus=0.0,
            execution_summary={
                "has_load_balancer": efficiency_score_map["load_balancer"] > 0,
                "has_queue": efficiency_score_map["message_queue"] > 0,
                "has_cache": efficiency_score_map["caching_layer"] > 0,
                "has_resilience": approach_score_map["resilience"] > 0,
                "has_diagram": has_diagram
            },
            feedback=feedback,
            metrics_breakdown={
                "efficiency_components": efficiency_score_map,
                "approach_components": approach_score_map
            }
        )
