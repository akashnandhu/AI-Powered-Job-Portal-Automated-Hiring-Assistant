# Technical Interview Flow & Transition Design Diagram

This document contains visual diagrams and behavioral state specs for the **Technical Interview AI System**. It maps the core call states, the real-time adaptive difficulty grading loop, and exception-recovery transitions.

---

## 1. Complete Conversational & Difficulty FSM

This state diagram maps how the FSM transitions between interview phases, tracks years of experience, adjusts query difficulty level, and coordinates dynamic follow-up probing:

```mermaid
stateDiagram-v2
    [*] --> INIT
    
    state INIT {
        [*] --> GREETING
        GREETING --> VERIFY_TENURE : Extract Candidate Meta
    }
    
    INIT --> ROUTING_DECI
    
    state ROUTING_DECI {
        [*] --> BASELINE_CHECK
        BASELINE_CHECK --> JUNIOR_ROUTE : 0-2 yrs Exp (Baseline Level 1-2)
        BASELINE_CHECK --> MID_ROUTE : 3-5 yrs Exp (Baseline Level 3)
        BASELINE_CHECK --> SENIOR_ROUTE : 5+ yrs Exp (Baseline Level 4-5)
    }
    
    ROUTING_DECI --> ACTIVE_INTERVIEW
    
    state ACTIVE_INTERVIEW {
        [*] --> ASK_TECH_QUESTION
        ASK_TECH_QUESTION --> AWAIT_CANDIDATE_INPUT : TTS Prompt Spoken
        
        AWAIT_CANDIDATE_INPUT --> RUN_TECHNICAL_NLU : Voice Transcript Recv
        AWAIT_CANDIDATE_INPUT --> TIMEOUT_RECOVERY : 10s Silence Detected
        
        state RUN_TECHNICAL_NLU {
            [*] --> KEYWORD_MATCH
            KEYWORD_MATCH --> CONCEPT_COMPLETENESS : Compute Jaccard/Synonym Score
        }
        
        RUN_TECHNICAL_NLU --> EVALUATE_PERFORMANCE
        
        state EVALUATE_PERFORMANCE {
            [*] --> CHECK_GRADE
            CHECK_GRADE --> LEVEL_UP : Score >= 85% (Diff + 1)
            CHECK_GRADE --> LEVEL_STABLE : Score 55%-84% (Diff + 0)
            CHECK_GRADE --> LEVEL_DOWN : Score < 55% (Diff - 1)
            
            LEVEL_UP --> NEXT_QUESTION
            LEVEL_STABLE --> NEXT_QUESTION
            LEVEL_DOWN --> CHECK_RETRY_LIMITS
            
            CHECK_RETRY_LIMITS --> FALLBACK_QUESTION : Consecutive Fails < 2
            CHECK_RETRY_LIMITS --> NEXT_SKILL_PIVOT : Consecutive Fails >= 2
        }
        
        NEXT_QUESTION --> ASK_TECH_QUESTION
        FALLBACK_QUESTION --> ASK_TECH_QUESTION
        NEXT_SKILL_PIVOT --> ASK_TECH_QUESTION
    }
    
    ACTIVE_INTERVIEW --> WRAP_UP : Phase 4 Completed / Terminate
    
    state WRAP_UP {
        [*] --> RUN_SCORERS
        RUN_SCORERS --> GENERATE_REPORT : Compile HR + Technical Metrics
        GENERATE_REPORT --> COLD_DISCONNECT : Say Goodbye
    }
    
    WRAP_UP --> [*]
```

---

## 2. Adaptive Difficulty Decision Tree Logic

This tree diagrams the exact logical path the AI takes after receiving the candidate's technical answer:

```mermaid
graph TD
    Start[Candidate Submits Answer] --> Clean[Clean Transcript & Filter PII]
    Clean --> Match[NLU Extracts Keywords & Concepts]
    Match --> Grade[Compute Completeness & Depth Score]
    
    Grade --> CheckScore{Check Score Threshold}
    
    CheckScore -->|Excellent: Score >= 85%| Up[Increment Difficulty: Level + 1]
    CheckScore -->|Acceptable: Score 55% to 84%| Same[Keep Difficulty: Level + 0]
    CheckScore -->|Struggling: Score < 55%| Down[Decrement Difficulty: Level - 1]
    
    Up --> ClampUp{Is Difficulty > Max Level 5?}
    ClampUp -->|Yes| SetMax[Clamp to Level 5]
    ClampUp -->|No| NextCoreUp[Query Next Skill Question at Level + 1]
    
    Same --> NextCoreSame[Query Next Skill Question at Level 3/Current]
    
    Down --> RetryCheck{Consecutive Struggles = 2?}
    RetryCheck -->|No| Fallback[Query Simpler Fallback Question same Skill]
    RetryCheck -->|Yes| Pivot[Lock Level, Pivot to Next Tech Category]
    
    SetMax --> NextCoreUp
    Fallback --> Loop[Await Next Answer]
    Pivot --> NextCoreSame
    NextCoreUp --> Loop
    NextCoreSame --> Loop
```

---

## 3. Interview Phase Progressions

The interview operates as a sequential progression of phases:

```mermaid
gantt
    title Technical Interview Timeline (60 Minutes Allocation)
    dateFormat  X
    axisFormat %s
    
    section Stage 1
    Warmup & Identity Verification   :active, 0, 3
    
    section Stage 2
    Experience-Based project review  :crit, 3, 18
    
    section Stage 3
    Conceptual Core Deep-dive        : 18, 36
    
    section Stage 4
    Scenario System Design Problem   : 36, 57
    
    section Stage 5
    Session Scorer & Wrap-Up         :active, 57, 60
```
