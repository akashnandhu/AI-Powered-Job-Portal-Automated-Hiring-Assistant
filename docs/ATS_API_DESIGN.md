# ATS REST API Specification

## Overview
This document outlines the REST API design for the AI-powered Applicant Tracking System (ATS). It exposes the backend pipeline for resume parsing, skill extraction, semantic matching, scoring, and shortlisting.

## Integration Flow Diagram

```text
+----------+                           +-------------------+
|          | -- 1. POST /upload-resume -> |  FastAPI Backend  |
|          | <- 2. Returns job_id      -- |  (Input Val)      |
|          |                              +---------+---------+
|          |                                        | 3. Add to BackgroundTasks
|  Client  |                              +---------v---------+
|          |                              | Async Processing  |
|          |                              | Pipeline          |
|          |                              | - upload          |
|          | -- 4. GET /status/{job_id} -> | - parse           |
|          | <- 5. Returns processing  -- | - extract         |
|          |                              | - match           |
|          | -- 6. GET /results/{id} -- -> | - score           |
|          | <- 7. Returns Final Results  |-> Saves to DB/    |
+----------+                              |   Storage         |
                                          +-------------------+
```

## Folder Structure for API Project

```text
api/
├── main.py                 # FastAPI application entry point
├── config.py               # Environment variables and configurations
├── routers/                # API route definitions
│   ├── resume.py           # Endpoints: /upload-resume, /parse-resume, /match-jd, /score
│   └── jobs.py             # Endpoints: /status/{job_id}, /results/{job_id}
├── schemas/                # Pydantic models for request/response validation
│   ├── request.py          # Input schemas (e.g., MatchRequest)
│   ├── response.py         # Output schemas (e.g., ParsedResume, ScoreResponse)
│   └── error.py            # Standardized error formats
├── services/               # Core business logic and background workers
│   ├── pipeline.py         # Async pipeline orchestration
│   ├── extractor.py        # Logic for parsing and skill extraction
│   └── matcher.py          # Semantic matching and scoring logic
├── db/                     # Data persistence (or temporary in-memory store)
│   └── job_store.py        # Storage layer for job statuses and results
└── utils/                  # Helper utilities
    ├── logger.py           # Centralized logging configuration
    └── file_handler.py     # File validation and temporary storage
```

## API Endpoints

### 1. Upload Resume
**Endpoint:** `POST /upload-resume`
**Description:** Uploads a resume file and initiates the asynchronous background processing pipeline.
**Content-Type:** `multipart/form-data`
**Request Payload:**
- `file`: (File) The resume file (PDF/DOCX)
- `jd_id`: (String, Optional) ID of the job description to match against

**Response:** `202 Accepted`
```json
{
  "job_id": "job_123abc",
  "message": "Resume uploaded successfully. Processing started.",
  "status_url": "/status/job_123abc"
}
```

### 2. Parse Resume (Synchronous/Testing Tool)
**Endpoint:** `POST /parse-resume`
**Description:** Synchronous endpoint to parse user data (mostly for direct API usage outside the async flow).
**Content-Type:** `application/json`
**Request:**
```json
{
  "resume_id": "res_987xyz"
}
```
**Response:** `200 OK`
```json
{
  "resume_id": "res_987xyz",
  "skills": ["Python", "FastAPI", "Machine Learning"],
  "experience": [
    {
      "company": "Tech Corp",
      "title": "Software Engineer",
      "duration": "2 years"
    }
  ],
  "education": [
    {
      "degree": "B.S. Computer Science",
      "institution": "University of Technology"
    }
  ]
}
```

### 3. Match Job Description (Synchronous/Testing Tool)
**Endpoint:** `POST /match-jd`
**Description:** Compares a parsed resume with a job description.
**Content-Type:** `application/json`
**Request:**
```json
{
  "resume_id": "res_987xyz",
  "jd_id": "jd_456def"
}
```
**Response:** `200 OK`
```json
{
  "resume_id": "res_987xyz",
  "jd_id": "jd_456def",
  "match_status": "COMPLETED",
  "matched_skills": ["Python", "FastAPI"]
}
```

### 4. Score Candidate (Synchronous/Testing Tool)
**Endpoint:** `POST /score`
**Description:** Generates the final score and determines the shortlisting decision.
**Content-Type:** `application/json`
**Request:**
```json
{
  "resume_id": "res_987xyz",
  "jd_id": "jd_456def"
}
```
**Response:** `200 OK`
```json
{
  "resume_id": "res_987xyz",
  "jd_id": "jd_456def",
  "similarity_scores": {
    "skills": 0.85,
    "experience": 0.70,
    "projects": 0.90
  },
  "final_score": 0.82,
  "decision": "SHORTLISTED"
}
```

### 5. Check Processing Status
**Endpoint:** `GET /status/{job_id}`
**Description:** Checks the current status of an async resume processing job.
**Response:** `200 OK`
```json
{
  "job_id": "job_123abc",
  "status": "PROCESSING",
  "progress": "Matching JD",
  "updated_at": "2026-04-13T10:00:00Z"
}
```

### 6. Fetch Final Results
**Endpoint:** `GET /results/{job_id}`
**Description:** Retrieves the complete JSON response of the pipeline processing.
**Response:** `200 OK`
```json
{
  "job_id": "job_123abc",
  "status": "COMPLETED",
  "resume_id": "res_987xyz",
  "jd_id": "jd_456def",
  "parsed_data": {
    "skills": ["Python", "FastAPI"],
    "experience": [],
    "education": []
  },
  "scoring": {
    "similarity_scores": {
      "skills": 0.88,
      "experience": 0.75,
      "projects": 0.80
    },
    "final_score": 0.81,
    "decision": "SHORTLISTED"
  }
}
```

## Standard Error Response
Returns standard HTTP status codes (e.g., `400 Bad Request`, `404 Not Found`, `500 Internal Server Error`).

```json
{
  "error": {
    "code": "INVALID_FILE",
    "message": "Unsupported file format. Please upload PDF or DOCX."
  }
}
```
