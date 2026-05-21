# HR Interview AI Developer Handbook & Integration Runbook

Welcome to the developer onboarding manual for the **HR Interview AI System**. This handbook provides engineers with setup guidance, architectural integration protocols, scoring coefficient controls, and step-by-step operational troubleshooting runbooks.

---

## 1. Directory Blueprint & Core Codebase Map

The HR Interview AI codebase is modular, keeping conversation management separate from language analysis and scoring.

```text
├── interview_ai/                  # Conversational Management Modules
│   ├── hr_question_bank.json      # Structured questions, target profiles, and expected intents
│   ├── hr_interview.py            # InterviewState, ResponseCapture, and RoleBasedQuestionGenerator
│   ├── call_state_machine.py      # Finite State Machine (FSM) managing turn-taking & recovery
│   ├── followup_engine.py         # Heuristic Decision Tree prompting for vague answers
│   └── understanding_engine.py    # AnswerUnderstandingEngine (NLU intent/entity classification)
│
├── scoring/                       # Evaluation & Rating Engines
│   ├── weights_config.py          # Category and Multi-round Unified weight coefficients
│   ├── hr_interview_scorer.py     # Relevance, Communication, Confidence, and Consistency scorers
│   └── unified_scorer.py          # Unified round aggregations with dynamic role weighting
│
├── api/                           # Web Access Layer
│   ├── main.py                    # FastAPI entrypoint
│   └── routers/                   # Router classes (/upload-resume, /status, etc.)
│
└── run_hr_interview_test.py       # Integration simulation testing utility
```

---

## 2. Environment Setup & Launch Guide

### Prerequisites
*   **Python**: Version 3.10 or higher.
*   **Virtual Environment**: Configured via `venv` or `conda`.

### Installation Steps
1.  **Initialize Environment & Install Dependencies**:
    ```powershell
    # Create virtual environment if not present
    python -m venv venv
    venv\Scripts\activate
    
    # Install dependencies
    pip install -r requirements.txt
    ```
2.  **Verify Setup via Candidate Simulation Suite**:
    ```powershell
    python run_hr_interview_test.py
    ```
    *This runs pre-configured candidate profiles (Confident, Hesitant, Inexperienced, Overqualified) through the NLU processors and dumps metrics reports into `reports/hr_interview_test_report.md`.*

3.  **Run FastAPI Web Server**:
    ```powershell
    uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    Open your browser and navigate to `http://localhost:8000/docs` to test endpoints via the interactive Swagger UI.

---

## 3. Developer Integration & Customization Guide

### A. How to Add a New Question to the Question Bank
Questions are structured in `interview_ai/hr_question_bank.json` to allow dynamic matching based on candidate profile metadata.

To add a new question, append a structured JSON block like the following to the `questions` array:
```json
{
  "id": "HR_LEAD_005",
  "category": "Teamwork & culture fit",
  "text": "Describe a situation where you had to guide a team through a major project pivot. What steps did you take?",
  "target_experience": ["experienced"],
  "target_role": ["technical", "non-technical"],
  "follow_up_eligible": true,
  "expected_intents": ["leadership_mentoring", "adaptability", "project_delivery"]
}
```
*   `id`: A unique alphanumeric string prefixing the category (`HR_LEAD_...`).
*   `target_experience` / `target_role`: Used by `RoleBasedQuestionGenerator` to filter eligible questions dynamically.
*   `expected_intents`: Probing engines analyze candidate transcript semantic intents against this array. If intents are missing, the system will trigger an **Example-based Probe**.

---

### B. Customizing Scoring Weights & Unified Weights
All scoring thresholds and category weights are defined inside `scoring/weights_config.py`.

#### Modifying HR Interview Scoring Ratios:
To change how much communication, relevance, confidence, or consistency impact the final HR score, update the `"hr_interview"` dictionary in `scoring/weights_config.py`:
```python
    "hr_interview": {
        "answer_relevance": 0.40,  # Increased from 0.35
        "communication": 0.20,     # Reduced from 0.25
        "confidence": 0.20,
        "consistency": 0.20
    }
```

#### Modifying Dynamic Role Weights in Multi-Round Unified Scorer:
Dynamic weights adjust the contribution of the Resume ATS Score, Voice Screening, and HR Interview based on the role. Update `UNIFIED_WEIGHTS_CONFIG` in `scoring/weights_config.py`:
```python
UNIFIED_WEIGHTS_CONFIG = {
    "technical": {
        "ats_score": 0.50,           # Prioritize matching tech stack
        "screening_score": 0.30,
        "hr_interview_score": 0.20   # Lower impact of HR rounds for devs
    },
    "leadership": {
        "ats_score": 0.20,
        "screening_score": 0.20,
        "hr_interview_score": 0.60   # Heavily prioritize emotional intelligence and HR behavioral rounds
    }
}
```

---

### C. Modifying FSM States & Error Max Retries
If the telephone integration requires longer recovery thresholds or new error types:
1.  **Add a State or Error Type**: Update `CallState` or `ErrorType` Enums in `interview_ai/call_state_machine.py`.
2.  **Adjust Max Retries**: Update the threshold limits in the constructor of `ConversationStateMachine`:
    ```python
    class ConversationStateMachine:
        def __init__(self, questions: List[str]):
            self.state = CallState.INIT
            self.questions = questions
            self.consecutive_errors = 0
            self.max_retries = 3  # Increased from 2 for bad-network channels
    ```

---

## 4. Operational Troubleshooting Runbook

This guide covers common integration failure modes, their root causes, and clear steps for resolving them.

### Issue 1: FSM Deadlocks & Conversational Loop-Locks
*   **Symptom**: The virtual interviewer repeats the exact same question infinitely, or the candidate gets trapped in an endless loop of follow-up probes.
*   **Root Cause**:
    1.  The FSM does not append the active question ID to the state's `asked_questions` list, causing `RoleBasedQuestionGenerator.get_next_question()` to select the same question next turn.
    2.  `FollowUpEngine` fails to increment the turn-count or key prefix when generating a follow-up, bypassing the `max_follow_ups_per_question` (2) ceiling check.
*   **Resolution Runbook**:
    1.  Verify that your calling router explicitly triggers:
        ```python
        # Record the question ID as asked immediately before reading it to the user
        state.asked_questions.append(current_question_id)
        ```
    2.  Check that the follow-up generator formats IDs with the `FU_` prefix:
        ```python
        # In followup_engine.py
        new_fu_id = f"FU_{base_question['id']}_{follow_up_count + 1}"
        state.asked_questions.append(new_fu_id)
        ```
    3.  Confirm that `max_follow_ups_per_question` is set to a healthy default (e.g., 2).

---

### Issue 2: NLU Sentiment Misclassification & Vague Intents (False Positives)
*   **Symptom**: Substantive, highly detailed answers are penalized as "vague" or "off-topic", triggering unnecessary and frustrating follow-up probes.
*   **Root Cause**:
    1.  Rule-based keyword pattern match matches common synonyms out of context (e.g., matching "depends" in *"It depends on how the database scales"* as a vague response).
    2.  Word count floor thresholds are configured too high, meaning comprehensive answers that are brief are flagged as inadequate.
*   **Resolution Runbook**:
    1.  Adjust the heuristic length check in `AnswerUnderstandingEngine.check_vague_or_missing()`:
        ```python
        # Lower the length threshold for vague responses
        if self.vague_pattern.search(text) and len(text.split()) < 15: # Reduced from 25
            return True
        ```
    2.  Expand the positive word patterns list or integrate LLM/semantic intent classifiers to prevent simple regex collisions.

---

### Issue 3: Speech-to-Text Buffer Overflow / Telephony Drop Error
*   **Symptom**: Client receives `TELEPHONY_DROP_ERR` (HTTP 500) or WebSocket connections time out after a few minutes of continuous audio streaming.
*   **Root Cause**:
    1.  Acoustic audio buffer blocks are sent synchronously, blocking the FastAPI event loop.
    2.  Telemetry records fail to write back to temporary storage, causing buffer queues to overflow.
*   **Resolution Runbook**:
    1.  Ensure all file writes and telemetry db queries are awaited asynchronously (`async`/`await`).
    2.  Increase the thread pool sizes of the gateway using `uvicorn` arguments:
        ```powershell
        uvicorn api.main:app --workers 4 --timeout-keep-alive 30
        ```
    3.  Review `api/services/background.py` and ensure large simulations utilize async queuing mechanisms.

---

### Issue 4: Dynamic Role-Based Score Mismatches
*   **Symptom**: Candidates receive unified scoring percentages that do not align with their actual performance.
*   **Root Cause**:
    1.  `UnifiedScorer.get_role_weights()` fails to match role strings due to trailing whitespaces or capitalization differences (e.g., `"Senior Engineer "` failing to match the `"technical"` category).
    2.  `weights_config.py` weights do not sum to exactly 1.0 (e.g., `0.33 + 0.33 + 0.33 = 0.99`), leading to calculated final score skew.
*   **Resolution Runbook**:
    1.  Validate that the role string is normalized when fetched:
        ```python
        role_key = role_type.lower().strip()
        ```
    2.  Run calculations to ensure weight coefficients inside `UNIFIED_WEIGHTS_CONFIG` sum to exactly 1.0. For example:
        ```python
        # Confirm that
        ats_score + screening_score + hr_interview_score == 1.00
        ```

---

### Issue 5: Code-Switching & Language Mixing Detection Failures
*   **Symptom**: Non-English responses are accepted and scored as valid, leading to anomalous communication and confidence ratings.
*   **Root Cause**: The regex pattern lists inside `AnswerUnderstandingEngine.detect_language_mixing()` are too brief or fail to identify common non-English phrases.
*   **Resolution Runbook**:
    1.  Expand the list of foreign patterns inside the `foreign_words` list in the `AnswerUnderstandingEngine` constructor.
    2.  In production systems, replace the heuristic regex patterns with a lightweight language identification package (e.g., `fasttext` or `langdetect`):
        ```python
        from langdetect import detect
        
        def detect_language_mixing(self, text: str) -> bool:
            try:
                return detect(text) != 'en'
            except:
                return False
        ```

---

### Issue 6: Missing `skills_output_{id}.json` Error
*   **Symptom**: Background processor throws a `FileNotFoundError` when initiating the matching score.
*   **Root Cause**: The NLP entity/skill extraction module failed to write the generated JSON file due to permission constraints or mismatched candidate IDs.
*   **Resolution Runbook**:
    1.  Verify that folders (`data/processed`, `data/resumes`, `logs`) exist or run the pipeline runner to let the system generate them.
    2.  Cross-reference that `CANDIDATE_ID` inside `config.py` is identical to your upload schema's input `candidate_id`.
