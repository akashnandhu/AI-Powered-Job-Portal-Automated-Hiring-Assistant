# Adaptive Questioning Framework & Decision Tree

## 1. Overview
The Adaptive Questioning Framework empowers the AI Interviewer to dynamically generate follow-up questions based on the quality and depth of the candidate's initial response. This ensures a conversational flow that feels natural while thoroughly assessing the candidate's competencies.

## 2. Follow-Up Triggers

When an answer is evaluated, it falls into one of several categories, which triggers a specific follow-up strategy:

1. **Clarification Trigger**:
   - **Condition**: Answer is too brief, vague, or missing key intents.
   - **Action**: Ask the candidate to elaborate or clarify specific points.
   - *Example*: "Could you expand a bit more on what your specific role was in that project?"

2. **Example-Based Trigger**:
   - **Condition**: Answer provides a high-level concept but lacks concrete evidence.
   - **Action**: Prompt the candidate to provide a real-world example.
   - *Example*: "You mentioned you're good at conflict resolution. Can you give me a specific example of when you used this skill?"

3. **Deepening Probe Trigger**:
   - **Condition**: Answer is adequate but simple.
   - **Action**: Dig deeper into the 'how' or 'why'.
   - *Example*: "Why did you choose that specific framework over other alternatives?"

4. **Scenario-Based Follow-up Trigger**:
   - **Condition**: Answer is confident, complete, and covers all intents.
   - **Action**: Increase difficulty by introducing a hypothetical edge case.
   - *Example*: "That's a great approach. How would your strategy change if the deadline was cut in half?"

## 3. Decision Tree Logic

```mermaid
graph TD
    A[Candidate Provides Response] --> B{Analyze Completeness & Depth}
    
    B -->|Score < 0.4 (Vague/Incomplete)| C[Clarification Trigger]
    B -->|Missing Expected Intents| D[Example-Based Trigger]
    B -->|Score 0.5 - 0.7 (Simple/Adequate)| E[Deepening Probe Trigger]
    B -->|Score > 0.8 (Confident/Complete)| F[Scenario-Based Follow-up]
    
    C --> G[Generate Follow-up Question]
    D --> G
    E --> G
    F --> G
    
    G --> H{Follow-up Count > Max Limit?}
    H -->|Yes| I[Move to Next Core Question]
    H -->|No| J[Ask Follow-up & Await Response]
    J --> A
```

## 4. Repetition Prevention & State Tracking

To maintain a human-like flow and prevent interrogating the candidate in a loop:
- **Follow-up Limits**: The `InterviewState` tracks a maximum of 2 follow-ups per base question.
- **Intent Tracking**: Once an intent (e.g., "collaboration_example") is satisfied, the engine stops probing for it.
- **Memory Check**: The Follow-Up Engine hashes prior prompts to ensure the same phrasing or exact angle isn't repeated.
