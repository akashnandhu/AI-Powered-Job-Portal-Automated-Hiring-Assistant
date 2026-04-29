import json
from interview_ai.call_state_machine import ConversationStateMachine, CallState
from interview_ai.understanding_engine import AnswerUnderstandingEngine
from screening_ai.scoring_engine import ScreeningScoringEngine

def simulate_call():
    questions = [
        "Can you describe your experience with Python and machine learning?",
        "What are your salary expectations?"
    ]
    
    state_machine = ConversationStateMachine(questions)
    understanding_engine = AnswerUnderstandingEngine()
    scoring_engine = ScreeningScoringEngine()
    
    # Candidate persona behavior
    candidate_responses = [
        "Um, I am a bit confused, what do you mean by machine learning experience?", # Confusion
        "I have 5 years of experience in Python and building ML models.",           # Good answer to Q1
        "As I said, I have 5 years.",                                               # Repeated answer to Q1 (should trigger error recovery)
        "120k"                                                                      # Partial but valid answer to Q2
    ]
    
    response_idx = 0
    history = []
    
    # INIT
    output = state_machine.process_event("start")
    history.append({"state": "INIT", "AI": output["message"]})
    
    # loop until terminated
    while state_machine.state != CallState.TERMINATED and response_idx < len(candidate_responses):
        if state_machine.state == CallState.WAITING_FOR_RESPONSE:
            candidate_text = candidate_responses[response_idx]
            history.append({"state": "CANDIDATE_SPEAKS", "Candidate": candidate_text})
            
            # Process via understanding engine
            # We assume current question category is general
            category = "Experience" if "experience" in questions[state_machine.current_question_index].lower() else "Salary"
            structured_answer = understanding_engine.process_answer(candidate_text, candidate_text, category)
            
            payload = {
                "confusion": structured_answer.confusion_detected,
                "repeated": structured_answer.repeated_detected,
                "needs_follow_up": structured_answer.is_vague_or_missing and not structured_answer.confusion_detected
            }
            
            output = state_machine.process_event("response_received", payload)
            history.append({"state": state_machine.state.name, "AI": output["message"], "Internal_Payload": payload})
            
            if state_machine.state != CallState.ERROR_RECOVERY:
                response_idx += 1
            else:
                # Need candidate to retry, we will feed next response
                response_idx += 1
                
            # If AI transitions back to ask question or wrap up, get the message
            if state_machine.state in [CallState.ASK_QUESTION, CallState.WRAP_UP, CallState.TERMINATED]:
                output = state_machine.process_event("continue")
                history.append({"state": state_machine.state.name, "AI": output["message"]})
        else:
            output = state_machine.process_event("continue")
            if output["message"]:
                 history.append({"state": state_machine.state.name, "AI": output["message"]})
                 
    # Run Scoring
    print("--- Conversation History ---")
    for event in history:
        print(f"[{event['state']}] {list(event.keys())[-1]}: {event[list(event.keys())[-1]]}")
        
    print("\n--- Scoring Engine Test ---")
    q1_score = scoring_engine.score_single_question("q1", questions[0], "Experience", candidate_responses[1], "high")
    q2_score = scoring_engine.score_single_question("q2", questions[1], "Salary", candidate_responses[3], "medium")
    
    print(f"Q1 Score ({candidate_responses[1]}): {q1_score.normalized_score}")
    print(f"Q1 Explain: {q1_score.completeness.explanation}, {q1_score.clarity.explanation}")
    
    print(f"Q2 Score ({candidate_responses[3]}): {q2_score.normalized_score}")
    print(f"Q2 Explain: {q2_score.completeness.explanation}, {q2_score.clarity.explanation}")

if __name__ == "__main__":
    simulate_call()
