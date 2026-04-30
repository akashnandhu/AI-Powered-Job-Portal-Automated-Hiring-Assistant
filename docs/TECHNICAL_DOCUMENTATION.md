# AI-Powered ATS Technical Documentation

## 1. Overview
The AI-Powered Applicant Tracking System (ATS) is an automated resume screening and shortlisting engine. It is designed to parse candidate resumes, extract relevant skills, experience, and education, measure them against job descriptions (JDs), evaluate semantic similarity, and generate a final fair score for shortlisting candidates.

## 2. System Architecture
The ATS operates on a modular, asynchronous pipeline architecture built with Python and FastAPI. The architecture separates parsing, scoring, bias mitigation, and ranking into distinct lifecycle phases.

### Core Architecture Components:
*   **API Layer (FastAPI):** Exposes asynchronous REST endpoints (`/upload-resume`, `/status`, `/results`) for handling file uploads, initiating background processing jobs, and fetching completed results.
*   **Parsing Layer:** Consists of specific parsers (`pdf_parser.py`, `docx_parser.py`, `education_parser.py`, `experience_parser.py`) to systematically extract metadata and raw text from candidate resumes.
*   **Information Extraction Layer:** Uses Natural Language Processing (NLP) to extract skills (`skill_extractor.py`), calculate experience timelines (in months), and structure education data.
*   **Semantic Matching Layer:** Employs NLP models to generate semantic scores representing the alignment between the candidate's resume and the raw job descriptions (`semantic_matcher.py`).
*   **Scoring & Fairness Engine:** Computes categorical scores (skills, experience, education, semantic) and normalizes the results through a fairness algorithm to minimize demographic or keyword bias (`ats_scorer.py`, `fairness_engine.py`).
*   **Ranking & Shortlisting Engine:** Evaluates the final scores against configurable thresholds and categorizes matches into priorities (`shortlisting_engine.py`).
*   **Interview AI & Voice Screening Engine:** Manages dynamic conversation logic through a state machine, handles confusion/repetition, and evaluates live candidate responses using an NLU-based understanding engine (`call_state_machine.py`, `understanding_engine.py`).
*   **Screening Evaluator:** Scores live interview answers against clarity, completeness, relevance, and consistency, aggregating them into an explainable normalized score (`scoring_engine.py`).

## 3. Data Flow

1.  **Ingestion:** A candidate uploads a resume (PDF/DOCX) via the FastAPI upload endpoint. An asynchronous background task is created.
2.  **Normalization & Masking:** The text is extracted, normalized, and sensitive PII (Personally Identifiable Information) masking is applied.
3.  **Parsing & Extraction:** 
    *   Skills are extracted and assigned a confidence score.
    *   Experience dates are parsed to compute the total candidate experience in months.
    *   Educational degrees are normalized (e.g., M.Pharm, PharmD, B.S.).
4.  **Matching:** The parsed profile is mapped against available Job Descriptions (stored in JSON format).
5.  **Scoring pipeline execution:** The `ATSScorer` aggregates component scores and dynamically adjusts them based on penalty/boost logic.
6.  **Fairness Adjustment:** The `Fairness Engine` reviews the initial scoring array, normalizes it based on domain proxy and standard deviation checks, and produces a final adjusted dataset.
7.  **Shortlisting:** The `ShortlistingEngine` assigns candidates to statuses: Priority Shortlisted, Shortlisted, Review, or Rejected. Output is bundled as JSON and a Recruiter Text Report.

## 4. Scoring Logic Explained

The ATS utilizes a weighted Multi-variable Scoring Logic defined in `scoring/ats_scorer.py`. The final score percentage is an aggregation of multiple sub-scores multiplied by specific category weights.

### A. Sub-Scores Analysis
1.  **Skill Match Score (Weight: 30%)**
    *   **Logic:** Computes the overlap between the candidate's skills and JD-required skills using synonym expansion (e.g., "ml" maps to "machine learning"). Uses a confidence multiplier for each matched skill.
    *   **Adjustment:** 
        *   Penalty (-15%) if the candidate lacks 30% of the expected critical skills.
        *   Boost (+10%) if the candidate possesses more skills than the expected baseline.

2.  **Experience Match Score (Weight: 20%)**
    *   **Logic:** Compares candidate's total months of experience against the JD extraction.
    *   **Fallback:** If JD years are undefined, a baseline of 3.5 years is assumed. Freshers (0 years required) automatically score 1.0.

3.  **Semantic Score (Weight: 50%)**
    *   **Logic:** A high-level contextual similarity metric usually derived externally (`semantic_scores.json`). It evaluates the general contextual fitness of the candidate's profile to the target job description.

4.  **Education Score (Tie-breaker/Boost)**
    *   **Logic:** Analyzes `normalized_degree`. Highest scores (1.0) are granted for exact degree domain matches (e.g., `PharmD`, `Master of Pharmacy`). Related fields (e.g., `Science`, `Biology`) receive a moderate score (0.7).

### B. Aggregation
Final scores are combined using configurable weights.
```python
# Pseudo calculation
computed_score = (skill_score * 0.3) + (exp_score * 0.2) + (sem_score * 0.5)
final_score_raw = computed_score / available_weights
final_percentage = round(final_score_raw * 100, 2)
```

## 5. Fairness & Bias Mitigation

To ensure equitable hiring practices, the system parses all results through `scoring/fairness_engine.py` and `ranking/run_final_pipeline.py`.
*   **PII Masking:** Names, locations, and sensitive identifiers are stripped pre-scoring.
*   **Bias Evaluation:** The pipeline creates a bias report checking for standard deviations exceeding thresholds and detects domain-proxy biases (e.g., heavily skewing toward strict "pharmacy" titles versus general technical roles).
*   **Score Adjustments (Fairness Score):** Scales the raw scores on an adjusted bell curve to minimize extreme keyword bias penalties.

## 6. Ranking Thresholds

The output of the scoring module is directed to the `ShortlistingEngine`, which operates on predefined thresholds (usually maintained in `threshold_config.py`):
*   **Priority Shortlisted:** Score typically > 85%
*   **Shortlisted:** Score typically 75% - 85%
*   **Review:** Score typically 60% - 74%
*   **Rejected:** Score < 60%
