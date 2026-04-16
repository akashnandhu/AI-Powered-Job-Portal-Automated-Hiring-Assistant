# ATS Developer Guide & Troubleshooting Notes

## 1. Introduction
This guide contains practical information for developers and integrators working with the AI-Powered Applicant Tracking System (ATS). It covers how to set up, extend, and troubleshoot the core engine.

## 2. Directory Structure

Understanding the repository structure is critical for extending the application.

*   `api/`: FastAPI web server implementation and REST schemas.
*   `parsers/`: Script files dedicated to extracting raw text from binary document formats (PDF, DOCX) and logical modules (Education, Experience).
*   `scoring/`: Core algorithms defining how well a candidate matches a job description (Skills, Experience, Education) and the `fairness_engine.py` for bias mitigation.
*   `ranking/`: Scripts that generate the final shortlisting matrices (`shortlisting_engine.py`) and orchestrate the final pipeline scoring run (`run_final_pipeline.py`).
*   `utils/`: Shared helper functions (logging, text normalization, masking).
*   `output/` & `outputs/` & `reports/`: Directories utilized by the system to cache intermediate extraction files and dump final JSON result reports.

## 3. Extending the ATS

### A. Modifying Scoring Weights
Scoring logic weights are heavily centralized but can be dynamically tweaked.
1.  Navigate to `scoring/ats_scorer.py`
2.  Locate `score_all_jobs()` method.
3.  Adjust the variables `skill_w = 0.3`, `exp_w = 0.2`, `sem_w = 0.5`. 
4.  If you add a new metric (e.g., `cultural_fit_score`), remember to register it into the `available_weights` denominator to ensure mathematical normalization.

### B. Adding a New Parser Format (e.g., Markdown)
If you need the system to parse `.md` files or `.txt` files directly:
1.  Create a parser file in the `parsers/` directory (e.g., `parsers/md_parser.py`).
2.  Implement a standard extraction method (e.g., `extract_text(filepath: str) -> str`).
3.  Update the `api/routers/resume.py` upload check to permit the new MIME/File type.
4.  Inject the parser router logic inside the background task worker (`api/services/pipeline.py` or equivalent).

### C. Adding a New API Endpoint
Adding endpoints should conform to the project’s FastAPI router structure.
1. Define your input/output schemas in `api/schemas/`.
2. Create or extend a file in `api/routers/` (e.g., `api/routers/analytics.py`).
3. Inject the router into the main FastAPI app inside `api/main.py`:
   ```python
   from .routers import analytics
   app.include_router(analytics.router, tags=["Analytics"])
   ```

## 4. Troubleshooting & Common Issues

### Issue 1: Missing `skills_output_{id}.json` Error
*   **Symptom:** Pipeline fails at `ATSScorer` initialization with a `FileNotFoundError`.
*   **Cause:** The Skill Extractor (`skill_extractor.py`) failed to run, failed to extract any skills, or saved them under a mismatched candidate ID.
*   **Fix:** Ensure the NLP extraction step completed successfully before triggering the scoring pipeline. Verify `candidate_id` variables match upstream and downstream.

### Issue 2: Poor Performant Scoring (Latency)
*   **Symptom:** `/upload-resume` is fast but fetching results times out or takes several minutes.
*   **Cause:** The semantic matcher or ML entity extraction is executing synchronously holding thread locks, or loading heavy HuggingFace models into memory repeatedly on every request.
*   **Fix:** Check that models are pre-loaded at the module level or FastAPI startup event, and verify background tasks are successfully offloaded.

### Issue 3: All Candidate Scores are Zero or Overly Low
*   **Symptom:** Final percentages stick tightly to bounds under 30%.
*   **Cause:** The Synonym Mapping logic is failing due to case sensitivity, or JSON Job Descriptions are missing mandatory data blocks (`skills_required`).
*   **Fix:** Review `output/jd_files/*.json` structures to ensure fields aren't null. Review `extract_jd_skills` inside `ats_scorer.py` to ensure fallback logic operates.

### Issue 4: Domain Bias Flagging True
*   **Symptom:** `domain_bias_detected: true` in the Bias Report.
*   **Cause:** The algorithm observed a >15% variance between Domain-specific jobs vs standard jobs.
*   **Fix:** This is designed behavior for monitoring. If the bias is unacceptably impacting hiring decisions, consider tweaking the fairness engine standard deviation curves in `scoring/fairness_engine.py` to assert a stronger modifier.

## 5. Development Best Practices
*   **Logging:** Always utilize the central `utils/logger.py` rather than print statements for API routes to track telemetry gracefully in production.
*   **Mocking ML Models:** In local development, if you do not possess massive GPU compute, consider mocking the output of `semantic_matcher.py` or defaulting semantic similarity to `0.5` configuration to speed up CI/CD testing loops.
