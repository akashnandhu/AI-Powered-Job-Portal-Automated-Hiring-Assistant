# Zecpath AI Technical Handbook

Welcome to the **Zecpath AI Technical Handbook**. This master index provides standard operational clarity, API mappings, data model signatures, and logic explanations bridging all aspects of the automated hiring environment. 

### Core Required Reading
Before contributing to modules, familiarize yourself with:
1. **[System Architecture Guide](ZECPATH_SYSTEM_ARCHITECTURE.md)**: End-to-end module flow and layout design.
2. **[Developer Onboarding Guide](ZECPATH_ONBOARDING_GUIDE.md)**: Bootstrapping instructions, pipelines, and coding standards.
3. **[AI Observability Plan](ai_observability_plan.md)**: Telemetry structure and debugging paths.

---

## 1. Central Data Models

Zecpath utilizes strictly defined `dataclasses` to assure reliable context passing between machine learning agents and scoring frameworks. Key entities include:

### `UnifiedCandidateScore`
The heartbeat data model holding the aggregated evaluation of a candidate post-processing.
- **Attributes**:
  - `candidate_id` *(str)* 
  - `final_hiring_fit_score` *(float)*: Scaled 0-100 metric.
  - `risk_tag` *(str)*: `GREEN`, `YELLOW`, `RED` (Integrity Flag).
  - `cross_round_breakdown` *(Dict)*: Weights and raw scores ingested from sub-models.
  - `integrity_insights` *(List[str])*

### `HiringDecision`
Emmited primarily by the `DecisionEngine`. Translates mathematical fits into business outcomes for HR review.
- **Attributes**:
  - `decision` *(str)*: Enum (`Selected`, `Hold / Review`, `Rejected`).
  - `confidence_score` *(float)*: Probability backing the decision.
  - `reasoning` *(List[str])*
  - `risk_factors` *(List[str])*

---

## 2. Dynamic Scoring Logic Definition

The Zecpath scoring infrastructure prevents monolithic model bias by dissecting logic mathematically across multiple steps.

### A. Stage-Level Scoring (The Extractors)
- **ATS Semantic Score**: Evaluates Resume vs. Job Description matching embedding similarities minus specific skill omission penalties.
- **Screening Fit Score**: Binary verification (Yes/No metrics scaling up/down baseline scores).
- **Technical Competency Score**: Graded purely on coding problem correctness metrics weighted by complexity hierarchical ladders.

### B. The Cross-Round Engine Aggregation
In the `scoring/cross_round_engine.py`, sub-module scores are compiled. The `CrossRoundEngine` operates mathematically using role-based weighting configurations.
**Formula Example (Backend Engineer):**
`Unified Score = (ATS * 0.15) + (Screening * 0.20) + (HR_Interview * 0.25) + (Tech_Interview * 0.40)`

### C. The Decision Engine Checkmate
The `DecisionEngine` runs the `Unified Score` alongside risk tagging to define the outcome.
- **Hard Nullifications**: If `Risk == RED` (severe suspected integrity/cheating flag), the engine triggers an automatic override to `Rejected` independent of their math score exceeding 95%.
- **Confidence Calibration**: Margins near thresholds penalize confidence. A score of 78% (Threshold limit) yields lower confidence than an 89%.

---

## 3. General API Structure

Our internal agent-to-agent operations resolve via standardized API footprints. Sub-agents communicate strictly via POST JSON packets.

### Evaluate Complete Profile Endpoint
**Action Protocol:** Submits a compiled representation of pipeline tracking for Final AI Ruling.
- **Pseudo-Endpoint**: `/api/v1/hiring/evaluate/{candidate_id}`
- **Payload Input**: 
  ```json
  {
     "candidate_profile": { ... },
     "scores": {
         "ats_round": 92.0,
         "technical_interview_round": 95.0
     },
     "integrity_flags": []
  }
  ```
- **Payload Return** (`HiringDecision` Schema):
  ```json
  {
      "candidate_id": "Cand-123",
      "decision": "Selected",
      "confidence_score": 93.5,
      "reasoning": ["Strong overall performance", "Exceptional technical execution"]
  }
  ```

---
*For direct maintenance, access `tests/` to trace these API mappings against the expected JSON representations.*
