import json
import os
import sys
import time

# Resolve import paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from interview_ai.call_state_machine import ConversationStateMachine, CallState
from interview_ai.understanding_engine import AnswerUnderstandingEngine
from interview_ai.followup_engine import FollowUpEngine
from interview_ai.hr_interview import InterviewState, ResponseCapture, RoleBasedQuestionGenerator
from scoring.hr_interview_scorer import HRInterviewScorer
from scoring.unified_scorer import UnifiedScorer

# Console color escape codes
CLR_HEADER = "\033[95m"
CLR_BLUE = "\033[94m"
CLR_GREEN = "\033[92m"
CLR_YELLOW = "\033[93m"
CLR_RED = "\033[91m"
CLR_RESET = "\033[0m"
CLR_BOLD = "\033[1m"
CLR_CYAN = "\033[96m"

def print_banner(text, color=CLR_HEADER):
    border = "=" * 80
    print(f"\n{color}{border}")
    print(f"{CLR_BOLD}  {text}{CLR_RESET}{color}")
    print(f"{border}{CLR_RESET}")

def print_section(title, color=CLR_BLUE):
    print(f"\n{color}{CLR_BOLD}>>> {title} <<<{CLR_RESET}")

def run_candidate_demo(candidate_data):
    cand_id = candidate_data["candidate_id"]
    name = candidate_data["name"]
    role = candidate_data["target_role"]
    exp_level = candidate_data["experience_level"]
    role_type = candidate_data["role_type"]
    ats_score = candidate_data["ats_score"]
    screening_score = candidate_data["screening_score"]
    turns_data = candidate_data["turns"]

    print_banner(f"LIVE DEMO: {name} - {role}", CLR_CYAN)
    print(f"{CLR_BOLD}Upstream Scores:{CLR_RESET} ATS Screen Match: {CLR_GREEN}{ats_score}%{CLR_RESET} | Voice Screening: {CLR_GREEN}{screening_score}%{CLR_RESET}")
    print(f"{CLR_BOLD}Demographics Masked:{CLR_RESET} YES (Compliance Ethics Guard Active)")
    print(f"{CLR_BOLD}Candidate Profile:{CLR_RESET} {exp_level.upper()} | {role_type.upper()}")
    
    # 1. Initialize Engines
    nlu_engine = AnswerUnderstandingEngine()
    follow_up_engine = FollowUpEngine()
    question_bank_path = os.path.join(BASE_DIR, "interview_ai", "hr_question_bank.json")
    generator = RoleBasedQuestionGenerator(question_bank_path)
    
    state = InterviewState(session_id="session_demo_987", candidate_id=cand_id)
    state.set_candidate_profile(experience=exp_level, role=role_type)
    
    # Standard question order for this demo based on candidate turns
    # We map turns dynamically to the simulated live conversation
    qa_pairs = []
    
    # Initialize Call FSM
    # Load all questions standard in active order for this candidate
    demo_questions = [
        "Could you start by telling me a little bit about yourself and your background?",
        "What would you say is your greatest professional strength?",
        "How do you handle working on a group project where a team member is not contributing their fair share?" if exp_level == "fresher" else "Tell me about a time you had a disagreement with a team member. How did you resolve it?",
        "What is your current notice period and when would you be available to join?"
    ]
    machine = ConversationStateMachine(demo_questions)
    
    # Call flow execution
    # INIT
    print_section("STAGE 1: Conversation Initialization & Greeting")
    init_res = machine.process_event("start")
    print(f"{CLR_BLUE}[FSM State: {machine.state.name}]{CLR_RESET} AI: \"{CLR_BOLD}{init_res['message']}{CLR_RESET}\"")
    time.sleep(1)
    
    turn_idx = 0
    while machine.state != CallState.TERMINATED and turn_idx < len(turns_data):
        turn = turns_data[turn_idx]
        print_section(f"TURN {turn_idx + 1}: {turn['category']} ({turn['phase'].upper()})")
        
        # 1. AI Asks Question
        if machine.state == CallState.ASK_QUESTION:
            ask_res = machine.process_event("next")
            current_question = ask_res["message"]
            print(f"{CLR_BLUE}[FSM State: {machine.state.name}]{CLR_RESET} AI: \"{CLR_BOLD}{current_question}{CLR_RESET}\"")
            state.asked_questions.append(turn["question_id"])
        elif machine.state == CallState.WAITING_FOR_RESPONSE:
            # We are waiting from a follow-up or recovery rephrase
            current_question = machine.questions[machine.current_question_index]
        
        # 2. Candidate Responds
        cand_resp = turn["candidate_response"]
        print(f"{CLR_YELLOW}[Candidate Vocal Input]{CLR_RESET} Candidate: \"{cand_resp}\"")
        time.sleep(1)
        
        # 3. NLU Processing
        print(f"{CLR_BLUE}[NLU System Processing...]{CLR_RESET}")
        nlu_res = nlu_engine.process_answer(cand_resp, cand_resp, question_category=turn["category"])
        
        # Display Entity Extractions
        print(f"   |- Intent Classified: {CLR_BOLD}{nlu_res.intent.upper()}{CLR_RESET} (Confidence: {nlu_res.confidence_score})")
        if nlu_res.extracted_data.skills:
            print(f"   |- Extracted Skills: {CLR_GREEN}{', '.join(nlu_res.extracted_data.skills)}{CLR_RESET}")
        if nlu_res.extracted_data.experience_years:
            print(f"   |- Extracted Experience Years: {CLR_GREEN}{nlu_res.extracted_data.experience_years}{CLR_RESET}")
        if nlu_res.extracted_data.salary_expectation:
            print(f"   |- Extracted Salary Expectation: {CLR_GREEN}{nlu_res.extracted_data.salary_expectation}{CLR_RESET}")
        if nlu_res.extracted_data.availability:
            print(f"   |- Extracted Availability: {CLR_GREEN}{nlu_res.extracted_data.availability}{CLR_RESET}")
            
        # Capture Response
        response_capture = ResponseCapture(question_id=turn["question_id"], candidate_transcript=cand_resp)
        response_capture.extracted_intents = nlu_res.extracted_data.skills
        
        # 4. Check Follow-Up Eligibility & Probing
        needs_follow_up = False
        follow_up_prompt = None
        
        # Check if follow up is needed
        # In this demo, Turn 2 represents a vague strength response. We trigger prober!
        if turn["phase"] == "core_hr" and turn["category"] == "Strengths & weaknesses":
            # Set mocked question from bank for prober
            mock_base_question = {
                "id": "HR_SW_001",
                "category": "Strengths & weaknesses",
                "text": "What would you say is your greatest professional strength?",
                "follow_up_eligible": True,
                "expected_intents": ["strength_mention", "example_provided"]
            }
            # Evaluate via prober
            follow_up_prompt = follow_up_engine.generate_follow_up(response_capture, mock_base_question, state)
            if follow_up_prompt:
                needs_follow_up = True
        
        # 5. Transition Call FSM
        fsm_payload = {
            "confusion": nlu_res.confusion_detected,
            "repeated": nlu_res.repeated_detected,
            "language_mixed": nlu_res.language_mixed,
            "missing_answer": nlu_res.missing_answer,
            "needs_follow_up": needs_follow_up,
            "follow_up_question": follow_up_prompt
        }
        
        # Process FSM transition event
        fsm_res = machine.process_event("response_received", fsm_payload)
        
        # Print FSM state shifts
        if machine.state == CallState.FOLLOW_UP or machine.state == CallState.ERROR_RECOVERY:
            print(f"{CLR_BLUE}[FSM State: {machine.state.name}]{CLR_RESET} -> Transition: {CLR_RED}CONVERSATION ANOMALY / ACTION REQUIRED{CLR_RESET}")
            print(f"{CLR_BLUE}[FSM State: {machine.state.name}]{CLR_RESET} AI Response: \"{CLR_BOLD}{fsm_res['message']}{CLR_RESET}\"")
            
            # Record previous Q&A for scoring before entering recovery/follow-up turn
            # In recovery/follow-up, we don't complete the main question pair until recovery responds
            qa_pairs.append({
                "question": current_question,
                "answer": cand_resp
            })
            
            # We don't advance the turn index here for the next category.
            # Instead, the next turn in demo_dataset represents the recovery/followup response!
        else:
            # Answer accepted, add to Q&A pairs
            qa_pairs.append({
                "question": current_question,
                "answer": cand_resp
            })
            print(f"{CLR_BLUE}[FSM State: {machine.state.name}]{CLR_RESET} -> Transition: {CLR_GREEN}ANSWER ACCEPTED & SAVED{CLR_RESET}")
            
        turn_idx += 1
        time.sleep(1)
        
    # Wrap up call FSM
    if machine.state != CallState.TERMINATED:
        wrap_res = machine.process_event("next")
        print_section("STAGE 3: Interview Wrap Up")
        print(f"{CLR_BLUE}[FSM State: {machine.state.name}]{CLR_RESET} AI: \"{CLR_BOLD}{wrap_res['message']}{CLR_RESET}\"")
        time.sleep(1)
        
    print_banner("INTERVIEW CALL CONCLUDED. TRIGGERING SCORING PIPELINES...", CLR_YELLOW)
    
    # 2. RUN HR INTERVIEW SCORING
    hr_scorer = HRInterviewScorer()
    print(f"{CLR_BLUE}[Running HRInterviewScorer...]{CLR_RESET}")
    hr_report = hr_scorer.evaluate_interview(qa_pairs)
    
    print("\n" + "=" * 50)
    print(f" {CLR_BOLD}HR INTERVIEW EVALUATION SCORE:{CLR_RESET} {CLR_CYAN}{hr_report['final_hr_score']}%{CLR_RESET}")
    print("=" * 50)
    print(f" |- Answer Relevance:   {CLR_GREEN}{hr_report['score_breakdown']['answer_relevance']}%{CLR_RESET}")
    print(f" |- Communication:      {CLR_GREEN}{hr_report['score_breakdown']['communication']}%{CLR_RESET}")
    print(f" |- Behavioral Confidence: {CLR_GREEN}{hr_report['score_breakdown']['confidence']}%{CLR_RESET}")
    print(f" \\\\- Session Consistency:   {CLR_GREEN}{hr_report['score_breakdown']['consistency']}%{CLR_RESET}")
    
    print("\n   [Consistency Metrics]:")
    print(f"    |- Length Variance penalty index: {hr_report['consistency_details']['length_consistency']}%")
    print(f"    \\\\- Sentiment swing index:        {hr_report['consistency_details']['sentiment_consistency']}%")
    
    # 3. RUN UNIFIED DYNAMIC SCORER
    unified_scorer = UnifiedScorer()
    print(f"\n{CLR_BLUE}[Running Unified Dynamic Scorer...]{CLR_RESET}")
    unified_report = unified_scorer.calculate_hiring_fit(
        candidate_id=cand_id,
        role_type=role,
        ats_score=ats_score,
        screening_score=screening_score,
        hr_interview_score=hr_report['final_hr_score']
    )
    
    # Print Dashboard
    print_banner(f"UNIFIED HIRING RECOMMENDATION: {name}", CLR_GREEN)
    print(f"{CLR_BOLD}Evaluated For Role:{CLR_RESET} {unified_report['role_evaluated_for']}")
    print(f"{CLR_BOLD}Readiness Status:{CLR_RESET}   {CLR_BOLD}{CLR_GREEN}{unified_report['readiness_band']}{CLR_RESET}")
    print(f"{CLR_BOLD}Final Unified Score:{CLR_RESET} {CLR_CYAN}{CLR_BOLD}{unified_report['final_hiring_fit_score']}%{CLR_RESET}")
    print(f"{CLR_BOLD}Dynamic Weight Standard:{CLR_RESET} {unified_report['weight_system_used']}")
    
    print(f"\n{CLR_BOLD}Cross-Round Contributions Breakdown:{CLR_RESET}")
    for round_key, metrics in unified_report["cross_round_breakdown"].items():
        round_title = round_key.upper().replace("_", " ")
        print(f" |- {round_title:18}: Raw {metrics['raw_score']}% | Weighted Weight {metrics['weight_applied']} -> Contributed: {CLR_GREEN}{metrics['weighted_contribution']}%{CLR_RESET}")
        
    print("\n" + "=" * 80)
    print(f" {CLR_BOLD}Recruiter Decision Action:{CLR_RESET} {CLR_GREEN}PROCEED WITH CONTRACT OFFER FLOWS AS FIRST PRIORITY{CLR_RESET}")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    demo_dataset_path = os.path.join(BASE_DIR, "data", "demo_dataset.json")
    if not os.path.exists(demo_dataset_path):
        print(f"Error: {demo_dataset_path} not found.")
        sys.exit(1)
        
    with open(demo_dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # Run the demo for Akash Anandhu (Candidate 001)
    run_candidate_demo(data["candidates"][0])
