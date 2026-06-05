# Zecpath AI Developer Onboarding Guide

Welcome to the Zecpath AI Engineering team! This guide covers everything you need to get your local development environment running, understand our module layouts, and run end-to-end tests securely.

## 1. Setup & Installation

### Step 1: Clone the Repository
Ensure you are operating in a protected network given the sensitive compliance logic contained here.
*(Note: Active git integration might be disabled or managed via discrete tarballs depending on current operations.)*

### Step 2: Set Up Virtual Environment
Always run tests isolated inside a virtual environment to prevent dependency conflicts (especially with PyTorch/TensorFlow and NLP processing dependencies).
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```
*(If `requirements.txt` is missing specific module requirements, look for the pip install logs in `docs/` or install primarily: `pytest`, `pandas`, `numpy` depending on the models used.)*

## 2. Codebase Organization

Explore the root directory. You'll interface primarily with these packages:
- `ats_engine/`: Parsed keyword matching and semantic comparisons.
- `screening_ai/`: Early vetting logic.
- `interview_ai/`: Technical and HR conversational intelligence.
- `scoring/`: The central cross-round dynamic weighting and final AI Decision logic (`cross_round_engine.py`, `decision_engine.py`).
- `utils/`: Common helpers (`text_cleaner.py`, `logger.py`).
- `logs/`: Application telemetry. **Important:** Local debugging traces appear here. Do not check logs into version control.

## 3. Running & Testing Pipelines

The best way to understand how the data flows is to run the internal simulation scripts. 

### End-to-End Test Pipeline
Run the mock candidates to simulate how ATS data merges with HR Round data to formulate a unified `HiringDecision`.
```bash
python run_e2e_pipeline.py
```
**Expected Output**: The terminal will print out aggregated AI Scores, alignment comparisons (AI vs. Human judgment), and generate JSON telemetry.

### Batch Processing Scripts
To run batch simulation against folders of mocked JDs/Resumes:
```bash
python run_batch_pipeline.py
```

## 4. Engineering Standards & Observability

### Logging Protocol
You **must not** use standard `print()` statements for core application state. We rely on a central Observability manager.
To trace activity, import the observability instance:
```python
from utils.logger import obs

# For API endpoints
obs.log_api_request("/api/test", "POST", latency_ms, 200)

# For Model execution
obs.log_model_inference("MyNewModel", "Cand-123", output_score=85, latency_ms=45.2)

# For Exceptions (Never suppress exceptions silently!)
obs.log_error("ComponentX", "Failed to parse dictionary", traceback_str)
```

### Working with Data Objects
When moving data between rounds, always utilize the strongly-typed `dataclass` representations documented in data model specifications (e.g. `UnifiedCandidateScore`, `HiringDecision`). DO NOT use raw untyped dictionaries bridging `interview_ai/` and `scoring/`.

## 5. Troubleshooting
- **No Logs appearing?** Ensure `logs/` directory permissions allow read/write. Check the exact filename paths in `utils/logger.py`.
- **Import Errors?** From the root `anti/` folder, assure directory packages are recognized. If testing sub-modules directly, verify your `sys.path`.
- **False Positive Metrics?** If the decision engine unexpectedly passes everyone, verify `weights_config.py` scaling overrides.

Reach out to the lead architect for further environment token setups (e.g., LLM keys, Database strings).
