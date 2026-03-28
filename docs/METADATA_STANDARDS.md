# Zecpath: Metadata Standards Document

This document defines the core metadata standards used across all AI-generated assets and JSON files within the Zecpath system. Uniform metadata guarantees horizontal traceability, data integrity, and pipeline observability.

## 1. The Core Metadata Envelope

Every output JSON produced by an AI or parsing module (Parsed Profiles, ATS Scores, Screening Reports, Interview Results) must include a unified root-level `metadata` object. 

### Standard JSON Schema Envelope

```json
{
  "metadata": {
    "candidate_id": "UUID-string",
    "job_id": "UUID-string | null",
    "model_version": "string",
    "timestamp": "ISO-8601-string"
  },
  "data": { 
    // Domain-specific payload goes here
  }
}
```

## 2. Field Definitions

### 2.1 Candidate ID (`candidate_id`)
- **Type**: `String` (UUIDv4)
- **Description**: The globally unique identifier for a specific human applicant.
- **Persistence**: Generated upon the candidate's first interaction or resume upload. Survives across multiple job applications.
- **Requirement**: Mandatory in all AI-generated documents related to a candidate.
- **Example**: `"e3b0c442-989b-464c-8650-6819eb74b391"`

### 2.2 Job ID (`job_id`)
- **Type**: `String` (UUIDv4) or `null`
- **Description**: The unique identifier for the specific job requisition the candidate is being evaluated against.
- **Persistence**: Maps directly to a standardized `Job Profile` entity.
- **Requirement**: Conditional. 
  - `null` during context-free processes like initial Resume Parsing (`output/parsed_resumes/`).
  - Mandatory during comparative processes like ATS Scoring, Screening, and Interviewing.
- **Example**: `"f47ac10b-58cc-4372-a567-0e02b2c3d479"`

### 2.3 Model Version (`model_version`)
- **Type**: `String`
- **Description**: Identifies the specific machine learning model, LLM, or precise rule-set algorithm used to generate the payload.
- **Purpose**: Critical for debugging. If a parsing bug is discovered, `model_version` allows us to instantly query all affected profiles. Essential for A/B testing different matching engines.
- **Format Convention**: `{family}-{architecture}-{version}`
- **Examples**: 
  - `"spacy-ner-v3.1"` (For resume parsing)
  - `"gpt-4o-2024-05-13"` (For screening reports)
  - `"rule-based-regex-v1.0"` (For fallback extraction)

### 2.4 Timestamp (`timestamp`)
- **Type**: `String`
- **Description**: The exact date and time the data artifact was generated.
- **Format**: ISO 8601 extended format with UTC offset (`YYYY-MM-DDTHH:mm:ssZ`).
- **Purpose**: Essential for designing the timeline of the AI Data Lifecycle. Helps enforce expiration policies (e.g., re-parsing resumes older than 6 months).
- **Example**: `"2026-03-28T12:15:00Z"`

---

## 3. Implementation Guidelines

- **Immutability**: Once an AI-generated JSON file is written to storage, its metadata block must never be mutated. If the artifact requires reprocessing, an entirely new file (or a new versioned entry in the database) must be created with a fresh `timestamp` and potentially a new `model_version`.
- **Validation**: All components reading intermediate AI outputs (e.g., the Screening AI reading the Parsed Resume) MUST throw an exception if the `metadata` envelope is missing or fails UUID/ISO validation.
- **Logging**: The core fields (`candidate_id`, `job_id`, `model_version`) should be attached to every telemetry and logging event emitted by the `utils/logger.py` module during processing.
