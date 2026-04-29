# AI Screening: Edge-Case Handling & Error Recovery

To ensure system stability in real-world conditions, the AI screening call flow implements robust retry and clarification logic for several edge cases. This framework ensures that the AI can gracefully handle difficult scenarios and provide a smooth experience for the candidate before executing a safety fallback (polite failure).

## 1. Edge Cases Handled

### 1.1 Poor Audio & Background Noise
**Detection Engine:** `interview_ai.stt_processor.STTService`
- **Trigger:** If the Speech-to-Text engine returns an overall confidence score `< 0.6` or a background noise level `> 0.7`.
- **Logic:**
  - **Retry 1:** "I'm having a little trouble hearing you clearly due to some background noise. Could you repeat that?"
  - **Retry 2:** "The audio is still a bit fuzzy. Let's try one more time."
  - **Fallback:** If poor audio persists, the call transitions to `WRAP_UP` (polite failure).

### 1.2 Language Mixing
**Detection Engine:** `interview_ai.understanding_engine.AnswerUnderstandingEngine`
- **Trigger:** Non-English words or phrases detected during the candidate's response (simulated via heuristic matching or language identification models).
- **Logic:**
  - **Retry 1:** "I'm sorry, I primarily understand English. Could you please answer in English?"
  - **Retry 2:** "Could you try phrasing that in English again?"
  - **Fallback:** If the candidate continues to speak in a foreign language, the call wraps up.

### 1.3 Missing Answers / Silence
**Detection Engine:** `interview_ai.stt_processor` (Silence Timeout) & `interview_ai.understanding_engine` (Empty Response)
- **Trigger:** Either the system detects no audio for `X` seconds, or the candidate's normalized transcript is completely empty.
- **Logic:**
  - **Retry 1:** "I didn't quite catch that. Are you still there?"
  - **Retry 2:** "Just checking if you are still connected. To repeat the question..."
  - **Fallback:** If max retries are exceeded, the call ends politely due to technical difficulties.

### 1.4 Confusion
**Detection Engine:** `interview_ai.understanding_engine.AnswerUnderstandingEngine`
- **Trigger:** Candidate asks for clarification ("what do you mean", "can you repeat", "I'm confused").
- **Logic:**
  - **Retry 1:** The AI rephrases the question using simpler terms.
  - **Retry 2:** The AI attempts a predefined simpler fallback question on the same topic.
  - **Fallback:** AI acknowledges the difficulty and moves on to the next topic to avoid frustrating the candidate.

### 1.5 Repeated Answers
**Detection Engine:** `interview_ai.understanding_engine.AnswerUnderstandingEngine`
- **Trigger:** Candidate uses phrases indicating repetition ("as I said", "like I mentioned before").
- **Logic:**
  - **Retry 1:** AI redirects: "It sounds like we touched on that. Could you elaborate specifically on another aspect?"
  - **Fallback:** If repeated again, the AI forces a transition to the next question.

## 2. Safety Fallbacks

The `ConversationStateMachine` implements a `consecutive_errors` counter. If the candidate triggers `ERROR_RECOVERY` consecutively for more than the `max_retries` (default: 2), the AI executes a **Polite Failure**:

> "It seems we might be experiencing some technical difficulties or having trouble connecting clearly. Let's pause here. Our recruitment team will reach out to you via email to continue this process. Thank you for your time today!"

This ensures the AI never gets stuck in infinite loops, and candidates who legitimately have poor connections or hardware issues are not subjected to a broken experience.
