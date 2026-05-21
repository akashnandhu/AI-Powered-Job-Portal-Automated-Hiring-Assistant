# HR Interview AI REST & WebSocket API Specification

This document defines the interface endpoints for integrating the **HR Interview AI Engine** with external clients (e.g., mobile apps, web dialers, or voice gateways like Twilio/WebRTC). 

It exposes REST endpoints for transactional session controls and a high-performance WebSocket endpoint for real-time streaming audio and NLU conversational evaluation.

---

## 1. Interaction Lifecycle Diagram

```text
+--------+                    +-------------+                    +------------------+
| Client |                    | FastAPI App |                    | HR AI FSM Engine |
+--------+                    +-------------+                    +------------------+
    |                                |                                    |
    | 1. POST /interview/session    |                                    |
    |------------------------------->|                                    |
    |                                | 2. Init State & Load Question Bank |
    |                                |----------------------------------->|
    | 3. Returns Session ID          |                                    |
    |<-------------------------------|                                    |
    |                                |                                    |
    | 4. Connect WebSockets          |                                    |
    |    /interview/stream/{id}      |                                    |
    |<==============================>|                                    |
    |                                |                                    |
    | 5. Send Audio/Text payload     |                                    |
    |----------------===============>|                                    |
    |                                | 6. Process NLU & Transition FSM    |
    |                                |----------------------------------->|
    |                                |                                    |
    |                                | 7. Yield next prompt / follow-up   |
    |                                |<-----------------------------------|
    | 8. Speak TTS response          |                                    |
    |<===============----------------|                                    |
    |                                |                                    |
    | 9. POST /session/{id}/evaluate |                                    |
    |------------------------------->|                                    |
    |                                | 10. Run Scoring Engines            |
    |                                |----------------------------------->|
    | 11. Returns Final Report & Fits|                                    |
    |<-------------------------------|                                    |
```

---

## 2. API Reference Index

| Protocol | Endpoint Path | Method | Description |
| :--- | :--- | :---: | :--- |
| **HTTP** | `/api/v1/interview/session` | `POST` | Initializes a new interview session and loads appropriate questions. |
| **HTTP** | `/api/v1/interview/session/{session_id}` | `GET` | Retrieves the real-time state,asked questions, and responses. |
| **HTTP** | `/api/v1/interview/session/{session_id}/respond` | `POST` | Transactional HTTP interface to submit a candidate transcript. |
| **HTTP** | `/api/v1/interview/session/{session_id}/evaluate`| `POST` | Concludes the interview, scores candidate answers, and averages metrics. |
| **HTTP** | `/api/v1/interview/session/{session_id}/unified-fit`| `GET` | Merges ATS, voice screening, and HR scores using role-based weights. |
| **WS** | `/api/v1/interview/stream/{session_id}` | `CONNECT` | Real-time WebSocket connection for streaming audio/text signals. |

---

## 3. Detailed Endpoint Specifications

### A. Initialize Interview Session
*   **Endpoint**: `POST /api/v1/interview/session`
*   **Description**: Creates a unique interview session, mapping candidate profiles and dynamically filtering questions.
*   **Request Headers**: `Content-Type: application/json`
*   **Request Body**:
    ```json
    {
      "candidate_id": "cand_948aef",
      "candidate_experience": "experienced",
      "candidate_role": "technical",
      "target_role": "Senior Python Developer"
    }
    ```
*   **Success Response**: `201 Created`
    ```json
    {
      "session_id": "sess_83bd1c5a",
      "status": "INIT",
      "current_phase": "introduction",
      "message": "Hello! Welcome to the interview. Are you ready to begin?",
      "websocket_stream_url": "ws://api.atsplatform.local/api/v1/interview/stream/sess_83bd1c5a",
      "created_at": "2026-05-21T12:00:00Z"
    }
    ```

---

### B. Get Session State
*   **Endpoint**: `GET /api/v1/interview/session/{session_id}`
*   **Description**: Returns telemetry on the conversation phase, asked questions, and raw answers collected so far.
*   **Success Response**: `200 OK`
    ```json
    {
      "session_id": "sess_83bd1c5a",
      "candidate_id": "cand_948aef",
      "current_phase": "core_hr",
      "turn_count": 3,
      "asked_questions": [
        "HR_INTRO_001",
        "HR_TW_002"
      ],
      "responses": [
        {
          "question_id": "HR_INTRO_001",
          "candidate_transcript": "Hi, I am Akash. I am a software engineer with 3 years of experience specializing in Python and FastAPI.",
          "extracted_intents": ["self_introduction", "python_mention"],
          "sentiment": "positive",
          "completeness_score": 0.85
        }
      ]
    }
    ```

---

### C. Submit Candidate Answer (HTTP Transactional)
*   **Endpoint**: `POST /api/v1/interview/session/{session_id}/respond`
*   **Description**: Submits the candidate's transcript for NLU processing, FSM progression, and Follow-up evaluations. Use this endpoint for chat-based integrations or external STT processing.
*   **Request Body**:
    ```json
    {
      "candidate_transcript": "I had a conflict last month where we disagreed on Database architectures, but we resolved it by testing both in staging."
    }
    ```
*   **Success Response**: `200 OK`
    *   *Scenario A: Answer accepted, moving to next standard question:*
        ```json
        {
          "session_id": "sess_83bd1c5a",
          "action": "CONTINUE",
          "state": "ASK_QUESTION",
          "fsm_telemetry": {
            "intent_detected": "direct_answer",
            "is_vague": false,
            "errors_logged": 0
          },
          "tts_prompt": "Great, let's move on to the next question. What are your expectations in terms of salary?"
        }
        ```
    *   *Scenario B: Vague answer, dynamic follow-up probe triggered:*
        ```json
        {
          "session_id": "sess_83bd1c5a",
          "action": "SPEAK_AND_WAIT",
          "state": "FOLLOW_UP",
          "fsm_telemetry": {
            "intent_detected": "partial_answer",
            "is_vague": true,
            "errors_logged": 0
          },
          "tts_prompt": "That's interesting. Can you provide a specific real-world example related to conflict resolution?"
        }
        ```

---

### D. Evaluate Interview
*   **Endpoint**: `POST /api/v1/interview/session/{session_id}/evaluate`
*   **Description**: Concludes the session, stops state tracking, executes categorical scorers, and generates average telemetry.
*   **Success Response**: `200 OK`
    ```json
    {
      "session_id": "sess_83bd1c5a",
      "candidate_id": "cand_948aef",
      "final_hr_score": 81.25,
      "score_breakdown": {
        "answer_relevance": 85.0,
        "communication": 78.5,
        "confidence": 82.0,
        "consistency": 80.0
      },
      "weights_applied": {
        "answer_relevance": 0.35,
        "communication": 0.25,
        "confidence": 0.20,
        "consistency": 0.20
      },
      "consistency_details": {
        "length_consistency": 85.0,
        "sentiment_consistency": 75.0
      },
      "insights": {
        "filler_words_density": "2.4 per 100 words",
        "primary_sentiment": "Confident / Structured"
      }
    }
    ```

---

### E. Get Unified Hiring Fit
*   **Endpoint**: `GET /api/v1/interview/session/{session_id}/unified-fit`
*   **Description**: Pulls applicant round scores (ATS score, screening score, and HR score) and merges them dynamically by role weights.
*   **Success Response**: `200 OK`
    ```json
    {
      "candidate_id": "cand_948aef",
      "role_evaluated_for": "Senior Python Developer",
      "final_hiring_fit_score": 84.15,
      "readiness_band": "Strong Fit (Proceed to Offer)",
      "weight_system_used": "Technical",
      "cross_round_breakdown": {
        "ats_round": {
          "raw_score": 90.0,
          "weight_applied": "45%",
          "weighted_contribution": 40.5
        },
        "screening_round": {
          "raw_score": 85.0,
          "weight_applied": "35%",
          "weighted_contribution": 29.75
        },
        "hr_interview_round": {
          "raw_score": 69.5,
          "weight_applied": "20%",
          "weighted_contribution": 13.9
        }
      }
    }
    ```

---

## 4. WebSocket Streaming Protocol Specification

The WebSocket endpoint provides high-frequency, bidirectional communication for sub-second conversational turn-taking.

*   **Endpoint**: `WS /api/v1/interview/stream/{session_id}`
*   **Payload Protocol**: JSON-wrapped text frames or raw binary audio streams.

### A. Client-to-Server Messages
1.  **Readiness Signal (Event)**:
    ```json
    {
      "event": "start",
      "payload": {
        "stream_format": "audio/l16;rate=8000"
      }
    }
    ```
2.  **Streaming Audio Frames (Binary/Base64)**:
    *   Clients stream continuous raw voice frames (e.g., 20ms chunks).
3.  **Manual STT Interruption (For fast turn-taking)**:
    ```json
    {
      "event": "candidate_speaking_detected",
      "timestamp": 1716298510
    }
    ```

### B. Server-to-Client Messages
1.  **NLU Interim Telemetry**:
    ```json
    {
      "event": "processing_state",
      "state": "ANALYZING_RESPONSE",
      "interim_transcript": "I worked on FastAPI and built some..."
    }
    ```
2.  **State Machine Decision & Prompt**:
    ```json
    {
      "event": "speak_prompt",
      "session_id": "sess_83bd1c5a",
      "action": "SPEAK_AND_WAIT",
      "state": "FOLLOW_UP",
      "text": "What specifically did you build using FastAPI?",
      "audio_payload": "BASE64_ENCODED_TTS_WAV_DATA"
    }
    ```
3.  **Conversation Timeout Warning**:
    ```json
    {
      "event": "silence_warning",
      "message": "Are you still there? The connection is open."
    }
    ```

---

## 5. Error & Exception Handling Schema

All REST and WebSocket endpoints conform to standard API error contracts:

### A. Standard REST Error Envelope
```json
{
  "error": {
    "code": "SESSION_EXPIRED",
    "message": "The requested interview session has terminated or timed out.",
    "details": {
      "session_id": "sess_83bd1c5a",
      "duration_seconds": 1205
    }
  }
}
```

### B. REST Error Codes Mapping

| HTTP Status | Error Code | Description |
| :--- | :--- | :--- |
| `400 Bad Request` | `INVALID_TRANSCRIPT` | Spoken text contains un-parseable symbols or violates size rules. |
| `403 Forbidden` | `DATA_MOCKED_LOCKED` | Scorer is executed under mock environments without valid credentials. |
| `404 Not Found` | `SESSION_NOT_FOUND` | `session_id` does not match active databases or Redis stores. |
| `422 Unprocessable`| `MISSING_PROFILE_DATA`| Attempting scoring calculations before configuring role or experience types. |
| `500 Internal Error`| `TELEPHONY_DROP_ERR` | Background socket disconnect from the telephony carrier gateway. |
