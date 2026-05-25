# Malpractice Detection Logic

This document specifies the concrete **mathematical boundaries, logical detection algorithms, and pattern templates** that identify cheating or external assistance during online interviews. It also outlines the core logic integrated inside the integrity scoring systems.

---

## 1. Malpractice Thresholds & Logical Rules

The system evaluates telemetry indexes chronologically against predefined threshold envelopes:

| Telemetry Signal | GREEN (Passing Envelope) | YELLOW (Warning Trigger) | RED (Violation Trigger) |
| :--- | :--- | :--- | :--- |
| **Tab Minimization ($N_{tab}$)** | $\le 1$ switch | $2 - 3$ switches | $\ge 4$ switches |
| **Screen Focus Loss ($T_{blur}$)** | $\le 8.0$ seconds | $8.0 - 20.0$ seconds | $\ge 20.0$ seconds |
| **Off-Screen Gaze Shifts ($G_{away}$)** | $\le 3$ shifts | $4 - 7$ shifts | $\ge 8$ shifts |
| **Acoustic Speaker Diarization ($V_{ext}$)**| $0$ detections | $\ge 1$ ($>65\%$ confidence) | $\ge 2$ ($>80\%$ confidence) |

---

## 2. Advanced Pattern Recognition (Coordinated Cheating)

To eliminate false alerts from natural user actions, we apply two complex multi-modal pattern detectors:

### A. Coordinated Search Pattern (CSP)
Detects candidates copy-pasting and searching for question answers immediately upon delivery:
*   *Sequence Definition*:
    1. System registers `question_asked` timestamp ($t_q$) $\rightarrow$
    2. A `browser_blur` event is recorded at $t_b$ where $t_b - t_q \le 5.0$ seconds $\rightarrow$
    3. The screen remains out of focus until `browser_focus` returns at $t_f$, where $4.0 \le t_f - t_b \le 15.0$ seconds $\rightarrow$
    4. A `speech_started` event is recorded at $t_s$ where $t_s - t_f \le 8.0$ seconds.
*   *Score Deduction*: High CSP match triggers **-20.0% penalty** per occurrence.

### B. Accomplice Cue Pattern (ACP)
Detects candidates reading pre-typed solutions fed by an accomplice on another screen while speaking:
*   *Sequence Definition*:
    1. Vocal speech is active (`speech_intervals` contains $[s_i, e_i]$) $\rightarrow$
    2. A visual gaze deviation occurs at $g_i$ with duration $d_i \ge 4.0$ seconds $\rightarrow$
    3. The overlap duration is significant: $\min(g_i + d_i, e_i) - \max(g_i, s_i) \ge 3.0$ seconds.
*   *Score Deduction*: Sustained ACP reading triggers **-20.0% penalty** per occurrence.
