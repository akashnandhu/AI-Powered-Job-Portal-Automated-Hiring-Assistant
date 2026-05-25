# Risk Flagging System Design

This document details the **alert mechanisms, risk categorization workflows, and core integration points** that enforce interview integrity within the Unified Scoring engine. It highlights how visual and browser violations trigger warnings and automatically block hiring automation.

---

## 1. Multi-layered Flagging Workflow

Our flagging architecture implements a dual-layer strategy to secure assessments: **Real-Time Client Deflection** and **Hiring pipeline hold integration**.

```
                        [ Telemetry Stream Parser ]
                                     |
                +--------------------+--------------------+
                |                                         |
     [ Real-Time Warnings ]                    [ Recruiter Risk Tagging ]
     - Popups during focus loss                - Green: Low Risk
     - FSM rephrase recovery triggers          - Yellow: Proceed with Caution
                                               - Red: Reject / Hold pipeline
```

### A. Real-Time Warnings (Client Deflection)
To prevent candidates from continuing focus-loss, browser violations trigger interactive prompts:
*   *1st Event*: Visual popup warning on current page: *"Screen focus lost. Please maintain this window active."*
*   *2nd Event*: Aggressive popup alert: *"Action logged. Continued screen blur will invalidate your assessment."*
*   *FSM Verbal Warning*: If tab switches $\ge 2$, the conversational State Machine transitions to `ERROR_RECOVERY` to vocalize a prompt:
    *   *AI Audio*: *"I noticed you have switched tabs multiple times. To preserve assessment validity, please keep the interview active."*

---

## 2. Recruiter Risk Categorization

At the conclusion of the interview, the `IntegrityScorer` calculates a final **Integrity Index (0-100%)** and groups candidates into one of three risk tag categories:

### Risk Tag: GREEN (Low Risk)
*   **Threshold Criteria**: Integrity Index $\ge 90\%$. Under $2$ tab switches, zero acoustic speaker overlaps, and zero coordinated search patterns.
*   **Operational Path**: Clean Profile. Candidate proceeds along the standard automated shortlisting pipeline.

### Risk Tag: YELLOW (Medium Risk)
*   **Threshold Criteria**: Integrity Index $70\% - 89\%$. Minor focus navigation ($2-3$ blurs) or slight offscreen shifts.
*   **Operational Path**: Log Warning. Recruiter dashboard displays a yellow caution tag showing focus loss metrics, prompting human review before standard confirmation.

### Risk Tag: RED (High Risk)
*   **Threshold Criteria**: Integrity Index $< 70\%$ or any detection of speaker overlaps ($V_{ext}$), CSP, or ACP patterns.
*   **Operational Path**: Automated Hold. Automatic hiring actions are immediately blocked. Unified Score is capped, and the profile is sent to a mandatory recruiter video review queue.

---

## 3. Automated Integrity Hold & Capping (Integration)

We integrate the risk tag directly within our unified evaluation pipeline to block automated processes (such as automated shortlisting or direct offer emails) for candidates with RED risk tags:
*   **Automatic Score Capping**: If the risk tag evaluates as RED, the system immediately overrides and caps the candidate's HR Interview score contribution at a maximum of $40\%$.
*   **Hiring Decision Block (Integrity Hold)**: A boolean flag `hold_automated_decision` is marked true. In `unified_scorer.py`, this overrides the final readiness status to **"HOLD (Integrity Check Failed; Manual Audit Required)"** and clamps the candidate's Unified Hiring Fit percentage at $45\%$ maximum, preventing automated shortlists and guaranteeing recruiter review.
