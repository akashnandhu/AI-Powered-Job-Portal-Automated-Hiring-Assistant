# AI Observability and Monitoring Plan

## 1. Overview
This document outlines the strategy for tracking, debugging, and performance monitoring of the Zecpath AI hiring system. The goal is to ensure end-to-end visibility of model inferences, APIs, and business decisions, while keeping false positives/negatives in check.

## 2. Expanded Logging Structure
A specialized logging system has been implemented within `utils/logger.py` to route critical telemetry to distinct destinations (JSON-lines format) for easy digestion by log aggregators (e.g., ELK stack, Datadog, Prometheus/Grafana).

- **`logs/api.log`**: API Requests and metrics.
  - Fields: `timestamp`, `endpoint`, `method`, `response_time_ms`, `status_code`
- **`logs/models.log`**: AI Model Inferences and latency.
  - Fields: `timestamp`, `model_name`, `candidate_id`, `output_score`, `latency_ms`, `metadata`
- **`logs/errors.log`**: System and AI Errors.
  - Fields: `timestamp`, `component`, `error_detail`, `traceback`
- **`logs/audit.log`**: Decision Tracking (Traceability for HR and Compliance).
  - Fields: `timestamp`, `candidate_id`, `final_decision`, `confidence_score`, `mechanisms`

## 3. Key Metrics & Alerting Rules

### Performance & Latency Metrics
- **API Response Time**: Target < 500ms for lightweight endpoints, < 3s for full model processing.
  - *Alert Rule*: Trigger P2 alert if `p95` latency exceeds 4s over a 5-minute window.
- **Model Inference Latency**: Track individual model execution time (e.g., ATS scoring, Screening logic).
  - *Alert Rule*: Alert if model inference time goes > 2s per candidate.

### Accuracy & Quality Metrics
- **Pass/Reject Rates**: Track the global % of candidates accepted vs. rejected by the `DecisionEngine`.
  - *Alert Rule*: Trigger P3 alert if rejection rate fluctuates > 30% from the 7-day trailing average (indicates potential pipeline drift or biased weights).
- **Match Rates**: Monitor semantic matching distributions to prevent threshold decay.
- **Integrity Tags**: Ratio of `Risk=RED` candidates.
  - *Alert Rule*: Anomalous spikes in integrity flags triggers investigation.

### Reliability & Error Rates
- **Model/API Failure Rates**: `5xx` errors or Internal Model crashes.
  - *Alert Rule*: Trigger P1 alert if failure rate > 1% in any 15-minute window.

## 4. Monitoring Dashboard Design
The dashboard (suggested implementation: Grafana/Kibana) is structured into three primary views:

1. **Executive Hiring Overview (Business)**
   - Total Candidates Processed (Daily/Weekly)
   - Decision Breakdown (Selected vs. Hold vs. Rejected)
   - Overall Interview Success Rates & "Funnel Drop-off"

2. **AI Telemetry & Performance (Engineering)**
   - API Latency Graph (p50, p90, p99)
   - Inference Time Distributions per Model (CrossRoundEngine, AtsScorer, etc.)
   - Error Rate Timeline by Component
   - Real-time Log Stream for AI Exceptions

3. **Audit & Compliance (HR/Legal)**
   - Searchable log of `candidate_id` -> `decision` with confidence scores
   - Distribution of Integrity Flags (Malformed Resumes vs. Cheating Detection)
   - Weight Usage & Override Logs

## 5. Audit Trail for Decisions
Audit logs provide a non-repudiable mechanism for tracking how AI derived a decision. 
In the `DecisionEngine`, the `UnifiedCandidateScore` inputs (ATS/Screening/HR/Tech scores) and calculated unified score are logged at the exact moment of decision creation. The audit trail captures:
- Weight configurations applied.
- Exact breakdown scores per round.
- Overrides/Tags that forced a given output (e.g., `Risk=RED` causing auto-rejection).
