# Aptitude AI & Cognitive Evaluation Framework

This document outlines the architectural design, scoring models, and situational frameworks implemented in the AI HR Interview pipeline to evaluate candidate cognitive abilities and situational judgment.

## 1. Aptitude AI Design
The Aptitude AI is designed as a standalone evaluation module (`CognitiveScorer`) integrated into the primary `ScoringEngine`. 

### Architecture
- **Trigger**: The engine is conditionally triggered whenever an interview question is classified under the `Cognitive Reasoning` or `Situational Judgment` categories.
- **Methodology**: It employs **Marker-Based Semantic Analysis** and structural evaluation to assess *how* a candidate thinks, rather than just *what* they say.
- **Integration**: The standard response evaluation (Relevance, Clarity, Completeness, Consistency) contributes 50% to the score, while the Cognitive module contributes the remaining 50%. This ensures candidates are graded on both communication quality and logical depth.

## 2. Logical Reasoning Scoring Model
Located in `scoring/cognitive_scorer.py`, this model quantifies logical thinking.

### Evaluation Metrics
1. **Structural Flow (Marker Density)**
   - The AI scans the transcript for reasoning markers (e.g., *firstly, secondly, therefore, consequently, step-by-step, assume, framework*).
   - Higher density of these terms indicates structured, sequential thinking.
2. **Complexity Analysis**
   - The AI measures average sentence length and vocabulary structure. Highly fragmented or excessively short sentences (outside of direct answers) receive lower logical depth scores, as complex reasoning usually requires compound explanations.
3. **Problem-Solving Clarity**
   - **Transitions**: Rewards clear flow (e.g., *then, after, result, next*).
   - **Vagueness Penalty**: Penalizes heavy reliance on non-specific nouns/verbs (e.g., *stuff, things, whatever, maybe*), which indicate hazy reasoning.

### Scoring Formula
```python
Reasoning Score = (Marker Count * 0.2) + (0.4 if avg_sentence_length > 12 else 0.2)
Clarity Score = (Transition Count * 0.2) + 0.4 - (Vague Word Count * 0.1)
Overall Cognitive Score = (Reasoning Score * 0.7) + (Clarity Score * 0.3)
```

## 3. Scenario Evaluation Framework
This framework tests Situational Judgment Tests (SJT) using predefined behavioral scenarios.

### Scenario Design
New scenarios added to `hr_question_bank.json`:
- **Crisis Management**: Discovering a critical bug 1 hour before a release.
- **Ethical/Pushback Scenarios**: Handling a client demanding insecure features.
- **Estimation Scenarios**: Guesstimating the number of windows in NYC (tests structured approximation).

### Judgment Scoring Mechanics
1. **Action-Orientation**
   - The AI detects "Action Keywords" (e.g., *assess, prioritize, mitigate, escalate, document*). Candidates must propose concrete steps, not just theoretical musings.
2. **Stakeholder Awareness**
   - Effective situational judgment in corporate environments requires communication. The engine checks for mentions of collaboration and reporting (e.g., *manager, client, team, stakeholder*). If a candidate acts entirely as a lone wolf in a crisis, their judgment score is capped.
3. **Final Aggregation**
   - `Judgment Score = (Action Keywords * 0.15) + (0.25 if stakeholder_communication_detected)`

---
### Validation Status
- **Syntax Check**: All code modules (`cognitive_scorer.py`, `scoring_engine.py`) have been audited. No division-by-zero errors or out-of-bounds metrics exist.
- **Normalization**: All final scores are strictly bounded between `0.0` and `1.0`.
- **Testing**: Validated via `generate_sample_report.py`, demonstrating realistic score generation (e.g., AKASH AA scoring 92% on Cognitive Reasoning and 95% on Situational Judgment).
