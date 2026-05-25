import os
import sys
import codecs
import json
import time
from datetime import datetime

# Reconfigure stdout to use UTF-8 to prevent charmap crashes with emojis on Windows terminals
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# Add the base directory to the Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from machine_test.models import TaskType, TestCase, TaskDefinition, CodeSnapshot, ExecutionResult, TaskSubmission
from machine_test.scoring_engine import MachineTestScoringEngine
from scoring.machine_test_scorer import MachineTestScorer
from scoring.unified_scorer import UnifiedScorer

def create_mock_tasks() -> list:
    """
    Creates four mock technical tasks representing the four major machine test tracks.
    """
    # 1. CODING task
    coding_task = TaskDefinition(
        task_id="TASK_CODING_01",
        title="Custom Matrix Vector Dot-Product with Outlier Filtering",
        task_type=TaskType.CODING,
        description="Write a function `dot_product_filtered(v1, v2, threshold)` that calculates the dot product of two numerical vectors. If any element exceeds the absolute threshold value, filter it out from both vectors prior to dot product calculations. Raise a ValueError if vectors are of mismatched sizes after outlier filtering.",
        difficulty=3,
        languages=["python"],
        code_template="""def dot_product_filtered(v1: list, v2: list, threshold: float) -> float:
    # TODO: Implement vector outlier filtering and dot product
    pass
""",
        reference_solution="""def dot_product_filtered(v1: list, v2: list, threshold: float) -> float:
    if len(v1) != len(v2):
        raise ValueError("Mismatched dimensions before filtering.")
    
    filtered_v1 = []
    filtered_v2 = []
    
    for val1, val2 in zip(v1, v2):
        if abs(val1) <= threshold and abs(val2) <= threshold:
            filtered_v1.append(val1)
            filtered_v2.append(val2)
            
    if len(filtered_v1) != len(filtered_v2):
        raise ValueError("Mismatched dimensions after filtering.")
        
    dot_prod = sum(a * b for a, b in zip(filtered_v1, filtered_v2))
    return float(dot_prod)
""",
        target_time_seconds=1200,  # 20 mins
        max_time_seconds=2400,     # 40 mins
        hints=[
            "Use standard Python zip() to iterate both vectors simultaneously.",
            "Verify outlier filter logic checks absolute values of elements."
        ]
    )

    # 2. DEBUGGING task
    debugging_task = TaskDefinition(
        task_id="TASK_DEBUGGING_01",
        title="Surgical Patches to a Buggy Binary Search",
        task_type=TaskType.DEBUGGING,
        description="The following binary search implementation contains a logical off-by-one error causing infinite loops, and fails to handle empty lists correctly. Patch it with minimal modifications.",
        difficulty=2,
        languages=["python"],
        code_template="""def binary_search(arr: list, target: int) -> int:
    if arr is None:
        return -1
    
    low = 0
    high = len(arr) # BUG: Should be len(arr) - 1
    
    while low <= high:
        mid = (low + high) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid # BUG: Should be mid + 1
        else:
            high = mid # BUG: Should be mid - 1
            
    return -1
""",
        reference_solution="""def binary_search(arr: list, target: int) -> int:
    if not arr:
        return -1
        
    low = 0
    high = len(arr) - 1
    
    while low <= high:
        mid = (low + high) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
            
    return -1
""",
        target_time_seconds=900,  # 15 mins
        max_time_seconds=1800,    # 30 mins
        hints=["Review loop bounds carefully, and check indices updated on mismatch matches."]
    )

    # 3. FILE-BASED task
    file_task = TaskDefinition(
        task_id="TASK_FILE_01",
        title="JSON Analytics Log Aggregator and Schema Validator",
        task_type=TaskType.FILE_BASED,
        description="Implement an analytics parser that streams log entries from a file line-by-line, aggregates total errors, filter actions by severity, and returns schema counts. Must handle corrupted files gracefully.",
        difficulty=3,
        languages=["python"],
        code_template="""def aggregate_analytics_logs(filepath: str) -> dict:
    # TODO: Read log files, count events, handle exceptions
    return {}
""",
        reference_solution="""import json
def aggregate_analytics_logs(filepath: str) -> dict:
    summary = {"total_lines": 0, "errors": 0, "success": 0, "corrupted_entries": 0}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                summary["total_lines"] += 1
                try:
                    data = json.loads(line)
                    if data.get("status") == "error":
                        summary["errors"] += 1
                    else:
                        summary["success"] += 1
                except json.JSONDecodeError:
                    summary["corrupted_entries"] += 1
    except FileNotFoundError:
        return {"error": "File not found"}
    return summary
""",
        target_time_seconds=1500,  # 25 mins
        max_time_seconds=3000,     # 50 mins
        hints=["Use a line-by-line stream iteration loop instead of .read() for scalability."]
    )

    # 4. SYSTEM DESIGN task
    design_task = TaskDefinition(
        task_id="TASK_DESIGN_01",
        title="Distributed Real-time Messaging Queue and Notification Gateway",
        task_type=TaskType.SYSTEM_DESIGN,
        description="Design a scalable, highly available notification architecture that processes 10,000 requests/sec, enforces active user throttling, handles third-party SMS failures, and supports schema template routing.",
        difficulty=4,
        languages=["markdown"],
        code_template="""# Title: Notification Gateway Architecture
## Core System Elements
Define services, APIs, databases.

## Scale & Performance
Specify load balancing and caching.

## Failure Resilience
Explain fault tolerance.
""",
        reference_solution="",  # Structural / keyword analyzed
        target_time_seconds=1800,  # 30 mins
        max_time_seconds=3600      # 60 mins
    )

    return [coding_task, debugging_task, file_task, design_task]


def simulate_candidate_submissions(tasks: list) -> list:
    """
    Simulates high-quality technical submissions for a strong candidate.
    Includes snapshots history showing structured coding progression.
    """
    submissions = []

    # 1. Simulate CODING submission
    # Candidate solves it perfectly, early, with structured snapshots
    coding_task = tasks[0]
    
    snap1 = CodeSnapshot(
        timestamp=time.time() - 600,
        code="""def dot_product_filtered(v1: list, v2: list, threshold: float) -> float:
    # First draft, filtering not done
    return sum(a*b for a,b in zip(v1, v2))
""",
        language="python",
        compile_status=True,
        edit_distance=120,
        active_time_spent=120
    )
    
    snap2 = CodeSnapshot(
        timestamp=time.time() - 300,
        code="""def dot_product_filtered(v1: list, v2: list, threshold: float) -> float:
    # Second draft, added filtering
    f1 = [x for x in v1 if abs(x) <= threshold]
    f2 = [y for y in v2 if abs(y) <= threshold]
    if len(f1) != len(f2):
        raise ValueError()
    return float(sum(a*b for a,b in zip(f1, f2)))
""",
        language="python",
        compile_status=True,
        edit_distance=210,
        active_time_spent=180
    )
    
    snap3 = CodeSnapshot(
        timestamp=time.time(),
        code="""def dot_product_filtered(v1: list, v2: list, threshold: float) -> float:
    \"\"\"
    Calculates the dot product after filtering outliers using absolute threshold bounds.
    Raises ValueError if lengths mismatch after processing.
    \"\"\"
    if len(v1) != len(v2):
        raise ValueError("Original vectors must have identical dimensions.")
        
    filtered_v1 = []
    filtered_v2 = []
    
    for val1, val2 in zip(v1, v2):
        if abs(val1) <= threshold and abs(val2) <= threshold:
            filtered_v1.append(val1)
            filtered_v2.append(val2)
            
    # Explicit dimensional audit
    if len(filtered_v1) != len(filtered_v2):
        raise ValueError("Dimensional mismatch after filtering process.")
        
    try:
        result = sum(a * b for a, b in zip(filtered_v1, filtered_v2))
        return float(result)
    except Exception as e:
        raise RuntimeError(f"Error calculating dot product: {e}")
""",
        language="python",
        compile_status=True,
        edit_distance=350,
        active_time_spent=200
    )

    exec1 = ExecutionResult(
        timestamp=time.time() - 300,
        stdout="",
        stderr="",
        exit_code=0,
        tests_passed=2,
        total_tests=5,
        runtime_ms=12.5,
        memory_usage_mb=42.3,
        passed=False
    )
    
    exec2 = ExecutionResult(
        timestamp=time.time(),
        stdout="All unit tests passed successfully.",
        stderr="",
        exit_code=0,
        tests_passed=5,
        total_tests=5,
        runtime_ms=8.2,
        memory_usage_mb=44.1,
        passed=True
    )

    coding_sub = TaskSubmission(
        task_id=coding_task.task_id,
        final_code=snap3.code,
        language="python",
        snapshots=[snap1, snap2, snap3],
        executions=[exec1, exec2],
        time_taken_seconds=500,  # 500 seconds (Target: 1200, huge early finish bonus!)
        hints_used=0,
        test_run_count=2
    )
    submissions.append(coding_sub)

    # 2. Simulate DEBUGGING submission
    # Candidate fixes it precisely with a surgical patch
    debugging_task = tasks[1]
    
    d_snap1 = CodeSnapshot(
        timestamp=time.time() - 200,
        code=debugging_task.code_template,
        language="python",
        compile_status=True,
        edit_distance=0,
        active_time_spent=100
    )
    
    d_snap2 = CodeSnapshot(
        timestamp=time.time(),
        code="""def binary_search(arr: list, target: int) -> int:
    if not arr:  # Safe check
        return -1
    
    low = 0
    high = len(arr) - 1  # Corrected off-by-one bound
    
    while low <= high:
        mid = (low + high) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1  # Corrected index increment
        else:
            high = mid - 1  # Corrected index decrement
            
    return -1
""",
        language="python",
        compile_status=True,
        edit_distance=180,
        active_time_spent=250
    )

    d_exec = ExecutionResult(
        timestamp=time.time(),
        stdout="All edge cases and array size tests passed.",
        stderr="",
        exit_code=0,
        tests_passed=8,
        total_tests=8,
        runtime_ms=1.5,
        memory_usage_mb=32.2,
        passed=True
    )

    debugging_sub = TaskSubmission(
        task_id=debugging_task.task_id,
        final_code=d_snap2.code,
        language="python",
        snapshots=[d_snap1, d_snap2],
        executions=[d_exec],
        time_taken_seconds=350,  # 350 seconds (Target: 900)
        hints_used=0,
        test_run_count=1
    )
    submissions.append(debugging_sub)

    # 3. Simulate FILE-BASED submission
    # Candidate writes a highly scalable file streams calculator
    file_task = tasks[2]
    
    f_snap1 = CodeSnapshot(
        timestamp=time.time(),
        code="""import json
import logging

def aggregate_analytics_logs(filepath: str) -> dict:
    \"\"\"
    Streams analytical events from logs line-by-line.
    Catches file reading errors and structural corruption safely.
    \"\"\"
    summary = {
        "total_lines": 0, 
        "errors": 0, 
        "success": 0, 
        "corrupted_entries": 0
    }
    
    try:
        # Open file as stream generator (memory efficient)
        with open(filepath, "r", encoding="utf-8") as file:
            for line in file:
                summary["total_lines"] += 1
                try:
                    data = json.loads(line.strip())
                    # Audit status metrics
                    status = data.get("status")
                    if status == "error" or data.get("severity") == "FATAL":
                        summary["errors"] += 1
                    else:
                        summary["success"] += 1
                except (json.JSONDecodeError, TypeError):
                    summary["corrupted_entries"] += 1
                    
    except FileNotFoundError:
        logging.error(f"Target log file not found at path: {filepath}")
        return {"error": f"Log file not found at {filepath}"}
    except PermissionError:
        return {"error": "Insufficient permissions to read target logs."}
        
    return summary
""",
        language="python",
        compile_status=True,
        edit_distance=520,
        active_time_spent=600
    )

    f_exec = ExecutionResult(
        timestamp=time.time(),
        stdout="Generated and successfully verified output schema.",
        stderr="",
        exit_code=0,
        tests_passed=6,
        total_tests=6,
        runtime_ms=45.2,
        memory_usage_mb=49.1,
        passed=True
    )

    file_sub = TaskSubmission(
        task_id=file_task.task_id,
        final_code=f_snap1.code,
        language="python",
        snapshots=[f_snap1],
        executions=[f_exec],
        time_taken_seconds=600,  # 10 mins (Target: 25 mins)
        hints_used=0,
        test_run_count=1
    )
    submissions.append(file_sub)

    # 4. Simulate SYSTEM DESIGN submission
    # Candidate writes a detailed, premium distributed systems design
    design_task = tasks[3]
    
    design_code = """# Title: Distributed Real-time Notification Gateway Architecture

## 1. Core System Elements
We propose a decoupled event-driven architecture using microservices:
- **Notification Gateway API (Ingress Service)**: Exposes endpoints `/v1/send` accepting JSON notifications. Acts as a lightweight proxy validation layer that authenticates clients via OAuth2 tokens.
- **Message Broker (Kafka Cluster)**: Handles ingestion of high-throughput notifications. Employs partitioning on `user_id` to guarantee message ordering per user.
- **Worker Pools (Notification Dispatchers)**: Asynchronous consumer services that pull events from Kafka partitions, apply user template parsing, and coordinate SMS/email delivery via third-party providers.
- **State Store (Redis Cache)**: Caches active rate-limits (Token Bucket Algorithm) and tracks user template metadata.
- **Transactional Database (PostgreSQL with read replicas)**: Persists notification logs and audit records.

## 2. Scale & Performance (10,000 requests/sec)
- **Ingress Load Balancing**: Employ an AWS ALB (Application Load Balancer) to steer ingress API traffic uniformly across API Gateways.
- **Caching Layer**: Redis keeps in-memory rate limit maps to throttle abusive clients in <2ms.
- **Asynchronous Decoupling**: Offloading API requests directly into Kafka ensures low latency response (~15ms) for the client while shielding third-party endpoints from spike loads.
- **Read Replicas**: Denormalize user configurations and query replicas to bypass transactional database bottlenecks.

## 3. Failure Resilience & Fault Tolerance
- **Circuit Breakers**: Worker pools implement a Circuit Breaker (using Resilience4j or similar pattern). If a third-party SMS gateway goes down (success rate <50%), the circuit trips and falls back to a secondary vendor.
- **Retry policies with Exponential Backoff**: Avoid thread locking by employing retries with jitter limits.
- **Dead Letter Queues (DLQ)**: If a notification fails 3 retries, it is routed to a Kafka Dead Letter Queue (`dlq-notifications`) for auditing and manual resolution.
- **Rate Limiting**: Integrated leaky bucket rate limits on third-party channels to strictly respect vendor capacity bounds.

```mermaid
graph TD
    Client[API Client] -->|HTTPS Requests| LB[AWS Load Balancer]
    LB --> Gate[API Gateways]
    Gate -->|Verify Token/Rate Limit| Cache[Redis Cache]
    Gate -->|Push Message| Broker[Apache Kafka Partition]
    Broker -->|Pull Task| Workers[Notification Worker Pools]
    Workers -->|DB Logging| DB[(PostgreSQL Main)]
    Workers -->|Failover Fallback| Gateways{SMS/Email Gateways}
    Gateways -->|Success| End[Notification Delivered]
    Gateways -->|Repeated Fails| DLQ[Kafka DLQ Broker]
```
"""

    design_snap = CodeSnapshot(
        timestamp=time.time(),
        code=design_code,
        language="markdown",
        compile_status=True,
        edit_distance=1200,
        active_time_spent=1400
    )

    # Conceptual tasks do not compile/execute in standard test suites
    design_exec = ExecutionResult(
        timestamp=time.time(),
        stdout="Conceptual diagram verified successfully.",
        stderr="",
        exit_code=0,
        tests_passed=1,
        total_tests=1,
        runtime_ms=0.0,
        memory_usage_mb=0.0,
        passed=True
    )

    design_sub = TaskSubmission(
        task_id=design_task.task_id,
        final_code=design_snap.code,
        language="markdown",
        snapshots=[design_snap],
        executions=[design_exec],
        time_taken_seconds=1400,  # 23 mins (Target: 30 mins)
        hints_used=0,
        test_run_count=1
    )
    submissions.append(design_sub)

    return submissions


def generate_markdown_report(report: MachineTestReport, weighted_result: dict, unified_result: dict):
    """
    Generates a stunning, premium markdown report summarizing the evaluations.
    """
    reports_dir = os.path.join(BASE_DIR, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    report_path = os.path.join(reports_dir, "MACHINE_TEST_EVALUATION_REPORT.md")
    
    with open(report_path, "w", encoding="utf-8") as f:
        # Title Header
        f.write("# 🤖 Technical Skills Machine Test Evaluation Report\n\n")
        
        # Meta Card
        f.write("> [!NOTE]\n")
        f.write(f"> **Candidate Identifier**: `{report.candidate_id}`  \n")
        f.write(f"> **Evaluated Role Profile**: `{report.role_type}`  \n")
        f.write(f"> **Assessment Execution Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"> **Overall Band classification**: `{report.overall_band}`  \n\n")
        
        # Score Summary Table
        f.write("## 📊 Consolidated Evaluation Matrix\n\n")
        f.write("| Assessment Round | Raw Score | Role Weight | Weighted Contribution | Band / Status |\n")
        f.write("| :--- | :---: | :---: | :---: | :--- |\n")
        
        for task_id, cont in weighted_result["task_contributions"].items():
            metrics = cont["metrics"]
            f.write(f"| **{cont['task_type']} ({cont['task_title']})** | {cont['individual_final_score']:.2f}% | {cont['role_weight_applied']} | {cont['weighted_contribution']:.2f} points | C: {metrics['correctness']}% / E: {metrics['efficiency']}% / Q: {metrics['quality']}% |\n")
            
        f.write("|---\n")
        f.write(f"| **Unified Machine Test Score** | **{report.overall_machine_test_score:.2f}%** | **100%** | **{weighted_result['weighted_machine_test_score']:.2f} / 100** | `{weighted_result['readiness_band']}` |\n\n")
        
        # Unified Hiring Fit Integration
        f.write("## 🔮 Full-Pipeline Hiring Intelligence Integration\n")
        f.write("The Unified Scorer incorporates this machine test score alongside recruitment funnel signals to calculate the candidate's core hiring viability:\n\n")
        
        f.write("| Funnel Pipeline Round | Raw Candidate Score | Weight Applied | Weighted Score Contribution |\n")
        f.write("| :--- | :---: | :---: | :---: |\n")
        
        breakdown = unified_result["cross_round_breakdown"]
        f.write(f"| **ATS Keyword & Skill Extraction** | {breakdown['ats_round']['raw_score']:.2f}% | {breakdown['ats_round']['weight_applied']} | {breakdown['ats_round']['weighted_contribution']:.2f} points |\n")
        f.write(f"| **Screening Call NLU Engine** | {breakdown['screening_round']['raw_score']:.2f}% | {breakdown['screening_round']['weight_applied']} | {breakdown['screening_round']['weighted_contribution']:.2f} points |\n")
        f.write(f"| **Machine Test AI Framework** | {breakdown['machine_test_round']['raw_score']:.2f}% | {breakdown['machine_test_round']['weight_applied']} | {breakdown['machine_test_round']['weighted_contribution']:.2f} points |\n")
        f.write(f"| **HR Behavioral & Integrity Interview** | {breakdown['hr_interview_round']['raw_score']:.2f}% | {breakdown['hr_interview_round']['weight_applied']} | {breakdown['hr_interview_round']['weighted_contribution']:.2f} points |\n")
        f.write("|---\n")
        f.write(f"| **Final Unified Hiring Fit Score** | - | **100%** | **{unified_result['final_hiring_fit_score']:.2f} / 100** |\n\n")
        
        f.write(f"**Readiness Decision Summary**: `{unified_result['readiness_band']}`\n\n")
        
        # Strengths & Developments
        f.write("## 💡 Candidate Talent Insights\n\n")
        f.write("### 💪 Key Technical Strengths\n")
        for s in report.strengths:
            f.write(f"- {s}\n")
        f.write("\n### 🎯 Recommended Growth Areas\n")
        for d in report.development_areas:
            f.write(f"- {d}\n")
        f.write("\n")
        
        # Detailed task breakdown
        f.write("## 📝 Detailed Task Analyses & Execution Summaries\n\n")
        
        for task_id, evaluation in report.evaluations.items():
            f.write(f"### 📍 Task: {task_id} ({evaluation.task_type.value})\n")
            f.write(f"- **Correctness**: `{evaluation.correctness_score}/100`  \n")
            f.write(f"- **Efficiency**: `{evaluation.efficiency_score}/100`  \n")
            f.write(f"- **Code Quality**: `{evaluation.code_quality_score}/100`  \n")
            f.write(f"- **Problem-Solving Approach**: `{evaluation.approach_score}/100`  \n")
            f.write(f"- **Final Adjusted Task Score**: **`{evaluation.final_score}/100`**  \n\n")
            
            f.write("**AI Feedback & Audit Logs**:\n")
            for fback in evaluation.feedback:
                f.write(f"- 🗣️ *{fback}*\n")
            f.write("\n---\n")
            
        f.write("\n*Report compiled autonomously by the Antigravity Technical Skills Evaluation AI.*")

    print(f"Gorgeous Markdown report written successfully to: reports/MACHINE_TEST_EVALUATION_REPORT.md")


def run_demo():
    print("======================================================================")
    print("🚀 STARTING AI MACHINE TEST FRAMEWORK ASSESSMENT DEMO")
    print("======================================================================\n")
    
    # 1. Initialize Mock Tasks and Submission
    print("[1/5] Initializing Machine Test definition matrices (Coding, Debugging, File-I/O, Design)...")
    tasks = create_mock_tasks()
    
    print("[2/5] Simulating candidate iterative workspaces and snapshots timeline...")
    submissions = simulate_candidate_submissions(tasks)
    
    # Pair task definitions with corresponding candidate submissions
    task_pairs = list(zip(tasks, submissions))
    
    # 2. Run Evaluator & Scoring Engine
    print("[3/5] Launching Task Evaluators and computing timeline decay algorithms...")
    engine = MachineTestScoringEngine()
    report = engine.compile_report(
        candidate_id="sample_resume_2",
        role_type="Junior Data Scientist",
        task_pairs=task_pairs
    )
    
    # 3. Apply Role-based weighted scorer
    print("[4/5] Adjusting evaluation weights for Junior Data Scientist role profile...")
    scorer = MachineTestScorer()
    weighted_result = scorer.score_machine_test(report, role_type="Junior Data Scientist")
    
    # 4. Integrate into UnifiedScorer
    print("[5/5] Integrating results into full-pipeline hiring intelligence score...")
    unified_engine = UnifiedScorer()
    # Assume candidate did exceptionally well on ATS and Screening, and moderately well on HR
    unified_fit = unified_engine.calculate_hiring_fit(
        candidate_id=report.candidate_id,
        role_type=weighted_result["role_evaluated_for"],
        ats_score=94.2,
        screening_score=87.5,
        hr_interview_score=81.0,
        machine_test_score=weighted_result["weighted_machine_test_score"]
    )
    
    # 5. Output reports
    # A. JSON output
    outputs_dir = os.path.join(BASE_DIR, "reports")
    os.makedirs(outputs_dir, exist_ok=True)
    json_path = os.path.join(outputs_dir, "machine_test_evaluation.json")
    with open(json_path, "w") as f:
        # Custom JSON serializer for Enums
        def enum_converter(o):
            if isinstance(o, TaskType):
                return o.value
            return o.__dict__
        json.dump(weighted_result, f, indent=4, default=enum_converter)
        
    print(f"Structured JSON output cached to: reports/machine_test_evaluation.json")
    
    # B. Markdown output
    generate_markdown_report(report, weighted_result, unified_fit)
    
    # 6. Display Beautiful Console Summary
    print("\n" + "="*70)
    print("                   AI MACHINE TEST EVALUATION SUMMARY")
    print("="*70)
    print(f"• Candidate ID         : {report.candidate_id}")
    print(f"• Role Profile         : {weighted_result['role_evaluated_for']}")
    print(f"• Readiness Band       : {weighted_result['readiness_band']}")
    print(f"• Weighted MT Score   : {weighted_result['weighted_machine_test_score']}%")
    print(f"• Final Hiring Fit Score: {unified_fit['final_hiring_fit_score']}% ({unified_fit['readiness_band']})")
    print(f"• Total Time Taken     : {report.total_time_spent_seconds // 60} minutes")
    print(f"• Tasks Attempted      : {report.total_tasks_attempted} of 4")
    
    print("\n--- Individual Task Scores ---")
    for t_id, cont in weighted_result["task_contributions"].items():
        print(f"  • [{cont['task_type']}] {t_id:<18} -> Final: {cont['individual_final_score']:.1f}% (Weight: {cont['role_weight_applied']})")
        
    print("\n--- Key Strengths ---")
    for s in report.strengths[:3]:
        print(f"  ✅ {s}")
        
    print("\n--- Growth Areas ---")
    for d in report.development_areas[:3]:
        print(f"  🎯 {d}")
        
    print("="*70 + "\n")

if __name__ == "__main__":
    run_demo()
