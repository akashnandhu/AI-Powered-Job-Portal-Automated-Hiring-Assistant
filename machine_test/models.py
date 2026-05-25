import enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

class TaskType(enum.Enum):
    CODING = "CODING"
    DEBUGGING = "DEBUGGING"
    FILE_BASED = "FILE_BASED"
    SYSTEM_DESIGN = "SYSTEM_DESIGN"

@dataclass
class TestCase:
    input_data: Any
    expected_output: Any
    is_hidden: bool = False
    description: str = ""

@dataclass
class TaskDefinition:
    task_id: str
    title: str
    task_type: TaskType
    description: str
    difficulty: int  # 1 to 5
    languages: List[str]
    code_template: str
    reference_solution: str
    test_cases: List[TestCase] = field(default_factory=list)
    target_time_seconds: int = 1800  # Default 30 mins
    max_time_seconds: int = 3600  # Default 60 mins
    hints: List[str] = field(default_factory=list)

@dataclass
class CodeSnapshot:
    timestamp: float  # Epoch timestamp of capture
    code: str
    language: str
    compile_status: bool = True
    edit_distance: int = 0  # Character differences from previous snapshot
    active_time_spent: int = 0  # Seconds spent on this step

@dataclass
class ExecutionResult:
    timestamp: float
    stdout: str
    stderr: str
    exit_code: int
    tests_passed: int
    total_tests: int
    runtime_ms: float
    memory_usage_mb: float
    compilation_error: Optional[str] = None
    passed: bool = False

@dataclass
class TaskSubmission:
    task_id: str
    final_code: str
    language: str
    snapshots: List[CodeSnapshot] = field(default_factory=list)
    executions: List[ExecutionResult] = field(default_factory=list)
    time_taken_seconds: int = 0
    hints_used: int = 0
    test_run_count: int = 0

@dataclass
class TaskEvaluation:
    task_id: str
    task_type: TaskType
    correctness_score: float  # 0 to 100
    efficiency_score: float  # 0 to 100
    code_quality_score: float  # 0 to 100
    approach_score: float  # 0 to 100
    raw_score: float  # Weighted raw score before time/hint adjustments
    final_score: float  # Score after adjustments
    time_multiplier: float  # Speed bonus or decay penalty multiplier
    hint_penalty: float  # Penalty applied for hints
    progression_bonus: float  # Bonus for structured iteration (snapshots check)
    execution_summary: Dict[str, Any] = field(default_factory=dict)
    feedback: List[str] = field(default_factory=list)
    metrics_breakdown: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MachineTestReport:
    candidate_id: str
    role_type: str
    overall_machine_test_score: float  # 0 to 100
    evaluations: Dict[str, TaskEvaluation] = field(default_factory=dict)
    total_time_spent_seconds: int = 0
    total_tasks_attempted: int = 0
    overall_band: str = ""
    strengths: List[str] = field(default_factory=list)
    development_areas: List[str] = field(default_factory=list)
    timeline_summary: List[Dict[str, Any]] = field(default_factory=list)
