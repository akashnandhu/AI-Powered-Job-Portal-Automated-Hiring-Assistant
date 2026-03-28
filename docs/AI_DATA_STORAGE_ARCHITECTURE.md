# Zecpath: AI Data Storage & Lifecycle Architecture

This document defines how all AI data flows, connects, and evolves across the Zecpath platform. It outlines the storage formats for recruitment artifacts, the core lifecycle of AI data from upload to a final hiring decision, and our strategy for versioning and dataset retraining.

## 1. Storage Formats & Directory Structure

All output data is stored in structured, predictable, and machine-readable formats to ensure interoperability between the ATS Engine, Screening AI, Scoring systems, and Interview AI.

The central storage hierarchy is managed under the `output/` directory:

### 1.1 Resumes (`output/parsed_resumes/` and original storage)
- **Format**: `.pdf`, `.docx` (Original binary files), and `.txt` (Extracted raw text).
- **Purpose**: Retains the candidate's original document for compliance, human review, and fallback text extraction.
- **Naming Convention**: `{candidate_id}_resume.pdf`, `{candidate_id}_raw.txt`

### 1.2 Parsed Profiles (`output/parsed_resumes/`)
- **Format**: `.json`
- **Purpose**: Stores the deterministic, standardized representation of the candidate's resume (Candidate Profile Entity).
- **Contents**: Sections (skills, experience, education, projects), contact info, and parsed dates.
- **Naming Convention**: `{candidate_id}_parsed.json`

### 1.3 ATS Scores (`output/ats_scores/`)
- **Format**: `.json`
- **Purpose**: Quantitative output from the Scoring Engine based on the exact match between the Parsed Profile and the Job Description.
- **Contents**: Overall score (e.g., 85%), skill match breakdown, experience overlap, and missing mandatory skills.
- **Naming Convention**: `{candidate_id}_{job_id}_score.json`

### 1.4 Screening Reports (`output/screening_reports/`)
- **Format**: `.json` and `.md`
- **Purpose**: Qualitative generation by the Screening AI that explains the ATS score.
- **Contents**: Strengths, weaknesses, AI-generated summary, red flags, and tailored interview questions based on the candidate's gaps.
- **Naming Convention**: `{candidate_id}_{job_id}_screening.json`

### 1.5 Interview Results (`output/interview_results/`)
- **Format**: `.json`
- **Purpose**: Captures the AI-driven technical and behavioral conversational assessment.
- **Contents**: Transcripts, sentiment analysis, technical competency scores, and final hire/no-hire AI recommendation.
- **Naming Convention**: `{candidate_id}_{job_id}_interview.json`

---

## 2. AI Data Lifecycle

The flow of data through the Zecpath platform is a linear progression of refinement and insight generation:

1. **Ingestion & Extraction**
   - Candidate uploads Resume (PDF/DOCX). 
   - System extracts raw text using parsing capabilities and normalizes it.
2. **Structuring & Classification**
   - The NLP engine processes raw text, classifying sections (Skills, Experience, Education) and generating a standardized `Parsed Profile` (JSON).
3. **Scoring & Matching**
   - The ATS engine retrieves the target `Job Profile` and compares it to the `Parsed Profile`.
   - Generates an `ATS Score` computing explicit matches for required timelines and keywords.
4. **Qualitative Screening**
   - Evaluates the profile's nuances (e.g., career gaps, achievement impacts).
   - Generates the `Screening Report` detailing the candidate's holistic fit.
5. **AI Interviewing**
   - The Interview AI reads the Screening Report to formulate dynamic questions.
   - Conducts the interview, recording the interaction and scoring the responses into `Interview Results`.
6. **Final Decision Making**
   - Recruiters view the aggregated dashboard (Resume -> Score -> Report -> Interview).
   - A final hiring decision is recorded in the core database.

---

## 3. Versioning & Retraining Datasets

To ensure the Zecpath AI evolves and improves continuously, data must be captured, versioned, and staged for model retraining.

### 3.1 Data Versioning
- **Schema Versioning**: All JSON files include a `$schema` reference (e.g., `v1.2`) ensuring backward compatibility.
- **Model Versioning**: Every generated artifact (Score, Report) records the `model_version` (e.g., `gpt-4o-2024-05-13` or `spacy-en-core-web-lg-v3.7`) used to create it. This allows us to track performance changes when models are upgrades.

### 3.2 Dataset Pipeline for Retraining
- **Feedback Loop**: When a human recruiter overwrites an AI score or decision (e.g., rejecting a candidate the AI ranked 95%), this event is logged as a "correction".
- **Data Lake Staging**:
  - `retraining/positive_samples/`: High AI score + Hired (Reinforces accurate matching).
  - `retraining/false_positives/`: High AI score + Rejected (Used to penalize overly lenient matching criteria).
  - `retraining/false_negatives/`: Low AI score + Hired (Used to discover missed synonyms or latent skills).
- **Periodic Retraining**: Monthly batches of corrected labeled data are used to fine-tune the bespoke NER models (for resume parsing) and the matching vector embeddings.
