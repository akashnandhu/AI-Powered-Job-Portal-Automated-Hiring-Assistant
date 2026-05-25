import json
import os
import sys
import time
import numpy as np
from typing import Dict, List, Any

# Resolve import paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from scoring.behavioral_scorer import BehavioralScorer
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
    border = "=" * 90
    print(f"\n{color}{border}")
    print(f"{CLR_BOLD}  {text}{CLR_RESET}{color}")
    print(f"{border}{CLR_RESET}")

def print_section(title, color=CLR_BLUE):
    print(f"\n{color}{CLR_BOLD}>>> {title} <<<{CLR_RESET}")

def generate_telemetry_frames(profile_type: str, duration_sec: float, fps: int = 10) -> List[Dict[str, Any]]:
    """
    Generates high-fidelity simulated frame-by-frame video telemetry based on candidate behavioral profiles.
    Profiles: 'focused', 'script_reader', 'neurodivergent', 'highly_distracted'
    """
    num_frames = int(duration_sec * fps)
    frames = []
    
    np.random.seed(42) # Ensure deterministic results for the demo
    
    for i in range(num_frames):
        timestamp = float(i) / fps
        
        # Defaults
        gaze = [0.02 + np.random.normal(0, 0.01), 0.01 + np.random.normal(0, 0.01)]
        head_pose = [0.5 + np.random.normal(0, 0.2), -0.2 + np.random.normal(0, 0.2), 0.1 + np.random.normal(0, 0.1)]
        blink_rate = 14.0 + np.random.normal(0, 0.5)
        expressiveness = 0.32 + np.random.normal(0, 0.02)
        face_in_frame = True
        
        if profile_type == 'focused':
            # Stable central gaze, active head nods (vertical oscillations in Pitch)
            gaze = [0.03 + np.random.normal(0, 0.01), 0.02 + np.random.normal(0, 0.01)]
            # Add dynamic vertical head nodding every 3 seconds (Pitch oscillation)
            pitch_mod = 2.5 * np.sin(2 * np.pi * timestamp / 3.0)
            head_pose = [0.8 + np.random.normal(0, 0.1), -0.5 + pitch_mod, 0.1 + np.random.normal(0, 0.05)]
            expressiveness = 0.38 + np.random.normal(0, 0.03) # High expressiveness (smiling AU12)
            
        elif profile_type == 'script_reader':
            # Frozen head (low variance), horizontal eye sweeps (scanning X-axis back and forth)
            # Sweep X-coordinate from -0.15 to +0.15 every 4 seconds
            sweep_x = 0.18 * np.sin(2 * np.pi * timestamp / 4.0)
            gaze = [sweep_x, -0.28 + np.random.normal(0, 0.01)] # Eyes cast down (-0.28 Y-axis)
            head_pose = [0.1 + np.random.normal(0, 0.02), -0.1 + np.random.normal(0, 0.02), 0.05 + np.random.normal(0, 0.01)]
            blink_rate = 48.0 + np.random.normal(0, 1.0) # High blink rate due to tension/reading strain
            expressiveness = 0.12 + np.random.normal(0, 0.01) # Rigid face expression
            
        elif profile_type == 'neurodivergent':
            # Extremely unstable / shifted gaze vector (looking away continuously to think)
            # But head is kept oriented straight, stable in frame, and blinking is normal
            gaze_angle = np.random.choice([0.0, 0.5, -0.5, 0.3])
            gaze = [gaze_angle + np.random.normal(0, 0.05), 0.25 + np.random.normal(0, 0.05)]
            head_pose = [1.2 + np.random.normal(0, 0.3), -0.4 + np.random.normal(0, 0.2), 0.15 + np.random.normal(0, 0.05)]
            expressiveness = 0.22 + np.random.normal(0, 0.02)
            
        elif profile_type == 'highly_distracted':
            # Large sideways gaze offset (looking at a second monitor) for long stretches
            if 3.0 <= timestamp <= 7.0:
                gaze = [0.55 + np.random.normal(0, 0.02), 0.15 + np.random.normal(0, 0.02)]
                head_pose = [28.5 + np.random.normal(0, 0.5), 1.2 + np.random.normal(0, 0.3), 0.5 + np.random.normal(0, 0.1)]
            else:
                gaze = [0.05 + np.random.normal(0, 0.02), 0.01 + np.random.normal(0, 0.02)]
                head_pose = [0.9 + np.random.normal(0, 0.3), -0.3 + np.random.normal(0, 0.2), 0.1 + np.random.normal(0, 0.05)]
            
            # Briefly goes out of camera frame around second 8-9
            if 8.0 <= timestamp <= 9.2:
                face_in_frame = False
                gaze = [0.0, 0.0]
                head_pose = [0.0, 0.0, 0.0]
                
            expressiveness = 0.25 + np.random.normal(0, 0.02)
            
        frames.append({
            "timestamp": timestamp,
            "gaze_vector": gaze,
            "head_pose": head_pose,
            "blink_rate": max(1.0, blink_rate),
            "facial_expressiveness": max(0.0, expressiveness),
            "face_in_frame": face_in_frame
        })
        
    return frames

def run_behavioral_evaluation_demo():
    print_banner("INITIALIZING ETHICAL BEHAVIORAL AI EVALUATION PIPELINE", CLR_CYAN)
    print(f"{CLR_BOLD}Active Frameworks:{CLR_RESET} Eye Gaze Tracker | Head Pose Estimator | Expression Analyzer")
    print(f"{CLR_BOLD}Ethical Safeguards:{CLR_RESET} WCBN Baselines | Neuro-Shield Guard | Gaze-Exemption active")
    
    # Initialize scorers
    behavioral_scorer = BehavioralScorer()
    hr_scorer = HRInterviewScorer()
    unified_scorer = UnifiedScorer()
    
    # 4 Mock Candidates representing our profiles
    candidates = [
        {
            "id": "CAND_001",
            "name": "AKASH AA",
            "role": "Junior Data Scientist",
            "role_type": "technical",
            "ats_score": 88.5,
            "screening_score": 82.0,
            "profile_type": "focused",
            "description": "Demonstrates high visual attention, stable orientation, and strong conversational nodding.",
            "qa_pairs": [
                {
                    "question": "Could you start by telling me a little bit about yourself and your background?",
                    "answer": "Hi, I am AKASH AA. I recently graduated with a Bachelor of Computer Science and I am currently a Data Science intern at Scope India, working on Python, Machine Learning models, and data analytics tools."
                },
                {
                    "question": "What would you say is your greatest professional strength?",
                    "answer": "I think my greatest strength is my analytical capability. In my internship at Scope India, my analytical skills allowed me to build and clean datasets using Pandas and NumPy, then train predictive machine learning models using Decision Trees, which improved overall prediction accuracy by 15%."
                },
                {
                    "question": "How do you handle working on a group project where a team member is not contributing their fair share?",
                    "answer": "If a team member isn't contributing, I would first speak with them privately to check if they need help or are facing difficulties. Then, we can partition the workload more equitably so they feel supported."
                }
            ]
        },
        {
            "id": "CAND_002",
            "name": "Jane Smith",
            "role": "Junior Data Analyst",
            "role_type": "technical",
            "ats_score": 78.0,
            "screening_score": 82.5,
            "profile_type": "script_reader",
            "description": "Shows systematic horizontal eye movements (saccades) scanning left-to-right, frozen posture, and downcast eyes (reading an off-screen teleprompter).",
            "qa_pairs": [
                {
                    "question": "Could you start by telling me a little bit about yourself and your background?",
                    "answer": "Hello, I am Jane Smith. I recently graduated with a degree in Statistics. I have worked on academic projects using Python, Pandas, Matplotlib, and SQL for analytical tasks."
                },
                {
                    "question": "What would you say is your greatest professional strength?",
                    "answer": "My greatest strength is my attention to detail. During my final year capstone project, I noticed a data entry error that skewed our entire forecasting chart, and I fixed it before presentation."
                },
                {
                    "question": "How do you handle working on a group project where a team member is not contributing their fair share?",
                    "answer": "I would partition the workload equitably. I would outline clear deadlines and report to the supervisor if they consistently fail to meet their personal objectives."
                }
            ]
        },
        {
            "id": "CAND_003",
            "name": "Rahul Sharma",
            "role": "Python Full Stack Engineer",
            "role_type": "technical",
            "ats_score": 82.0,
            "screening_score": 85.0,
            "profile_type": "neurodivergent",
            "description": "Neurodivergent profile: Exhibits high gaze aversion (looks away continuously), which standard AI triggers as disengaged. Gaze-Exemption activates to evaluate him fairly based on head presence and verbal excellence.",
            "qa_pairs": [
                {
                    "question": "Could you start by telling me a little bit about yourself and your background?",
                    "answer": "I am Rahul. I have spent the last three years building scalable backend services in Django and Flask. I've designed relational database schemas in PostgreSQL and integrated Celery queues for asynchronous mail processing."
                },
                {
                    "question": "What would you say is your greatest professional strength?",
                    "answer": "My core strength is my algorithmic reasoning. I'm able to identify efficiency bottlenecks, reduce quadratic algorithms to linear time complexities, and optimize memory footprints in database queries."
                },
                {
                    "question": "How do you handle working on a group project where a team member is not contributing their fair share?",
                    "answer": "I focus on open, non-judgmental communication. I establish a shared checklist of technical goals, offer pairing sessions to unblock their development, and make sure we collaborate directly on complex API contracts."
                }
            ]
        },
        {
            "id": "CAND_004",
            "name": "Sarah Jenkins",
            "role": "Sales Lead",
            "role_type": "customer_facing",
            "ats_score": 72.0,
            "screening_score": 70.0,
            "profile_type": "highly_distracted",
            "description": "Restless posture: Frequently shifts gaze to a secondary screen for extended periods and briefly steps out of the frame.",
            "qa_pairs": [
                {
                    "question": "Could you start by telling me a little bit about yourself and your background?",
                    "answer": "Hi there! I'm Sarah, and I've spent the past four years leading customer support and success teams in fast-paced software environments."
                },
                {
                    "question": "What would you say is your greatest professional strength?",
                    "answer": "I'm extremely persuasive and highly empathetic. I can build immediate trust, handle angry customers easily, and retain accounts during renewals."
                },
                {
                    "question": "How do you handle working on a group project where a team member is not contributing their fair share?",
                    "answer": "I would organize a team sync, re-align everyone on our quarterly commission structure, and divide tasks transparently so everyone stays accountable."
                }
            ]
        }
    ]
    
    # Process each candidate
    for cand in candidates:
        print_banner(f"EVALUATING CANDIDATE: {cand['name']} - {cand['role']}", CLR_BLUE)
        print(f"{CLR_BOLD}Upstream Scores:{CLR_RESET} ATS Screen Match: {CLR_GREEN}{cand['ats_score']}%{CLR_RESET} | Voice Screening: {CLR_GREEN}{cand['screening_score']}%{CLR_RESET}")
        print(f"{CLR_BOLD}Behavioral Profile:{CLR_RESET} {cand['description']}")
        
        # 1. Establish Baseline (using introduction turn telemetry simulation)
        print(f"\n{CLR_CYAN}[FSM: Welcome & Greeting turn - Initializing Video Baseline]{CLR_RESET}")
        intro_telemetry = generate_telemetry_frames(cand["profile_type"], duration_sec=5.0) # 5 seconds greeting
        baseline = behavioral_scorer.establish_individual_baseline(intro_telemetry)
        
        print(f" |- [WCBN Established]:")
        print(f"    |- Baseline Gaze Stability: {CLR_GREEN}{baseline['avg_gaze_stability'] * 100}%{CLR_RESET}")
        print(f"    |- Head Pose Variance:     {CLR_GREEN}{baseline['avg_head_yaw_var']}{CLR_RESET}")
        print(f"    |- Baseline Blink Rate:     {CLR_GREEN}{baseline['avg_blink_rate']} BPM{CLR_RESET}")
        if baseline["gaze_exempt_eligible"]:
            print(f"    |- {CLR_YELLOW}[ETHICAL ALERT]: Baseline indicates high natural gaze shift. Gaze-Exemption Guard Triggered!{CLR_RESET}")
        else:
            print(f"    |- [Safeguard Check]: Gaze profile aligns with standard baseline parameters.")
            
        # 2. Evaluate conversational turns
        turn_behavioral_reports = []
        
        # Evaluate standard textual components
        text_report = hr_scorer.evaluate_interview(cand["qa_pairs"])
        
        # Simulate video frames for each turn
        for i, turn in enumerate(cand["qa_pairs"]):
            # Generate simulated frames for 10 seconds of answer time
            turn_frames = generate_telemetry_frames(cand["profile_type"], duration_sec=10.0)
            
            # Simple mock silence intervals (cognitive thinking pauses around second 1-2)
            mock_silence = [{"start": 1.0, "end": 2.2}]
            
            turn_rep = behavioral_scorer.evaluate_turn(turn_frames, baseline, mock_silence)
            turn_behavioral_reports.append(turn_rep)
            
        # Aggregate behavioral scores across turns
        avg_behavioral_score = np.mean([r["behavioral_score"] for r in turn_behavioral_reports])
        avg_focus_level = np.mean([r["focus_level"] for r in turn_behavioral_reports])
        
        # Consolidate turn-level insights
        all_insights = []
        for r in turn_behavioral_reports:
            for insight in r["insights"]:
                if insight not in all_insights:
                    all_insights.append(insight)
                    
        # Apply Neuro-Shield Bias Dampener (Ethical Safeguard)
        # Behavioral score cannot lower final score dramatically due to pure nervousness.
        # We calculate the delta between the pure textual HR score and the behavioral composite score.
        raw_textual_hr_score = text_report["final_hr_score"]
        
        # Final HR score with behavioral component included:
        # We apply the updated weights config:
        # Relevance: 30%, Comm: 20%, Conf: 15%, Consistency: 15%, Behavioral: 20%
        behavioral_weight = 0.20
        textual_weight = 0.80
        
        weighted_text_contribution = (
            text_report["score_breakdown"]["answer_relevance"] * 0.30 +
            text_report["score_breakdown"]["communication"] * 0.20 +
            text_report["score_breakdown"]["confidence"] * 0.15 +
            text_report["score_breakdown"]["consistency"] * 0.15
        )
        
        raw_composite_score = weighted_text_contribution + (avg_behavioral_score * behavioral_weight)
        
        # Neuro-Shield Safeguard check:
        # If behavioral score is lower than textual score, cap the negative adjustment to -5% max!
        score_diff = raw_composite_score - raw_textual_hr_score
        ethical_safeguard_applied = False
        final_hr_score = raw_composite_score
        
        if score_diff < -5.0:
            final_hr_score = raw_textual_hr_score - 5.0
            ethical_safeguard_applied = True
            
        # 3. Calculate Unified Hiring Fit Fit Score
        unified_report = unified_scorer.calculate_hiring_fit(
            candidate_id=cand["id"],
            role_type=cand["role"],
            ats_score=cand["ats_score"],
            screening_score=cand["screening_score"],
            hr_interview_score=final_hr_score
        )
        
        # Display Results Dashboard
        print_section("STAGE 2: Consolidating Multi-Modal Scores")
        print(f" |- Textual HR metrics score:     {CLR_BOLD}{raw_textual_hr_score}%{CLR_RESET}")
        print(f" |- Simulated Behavioral AI score: {CLR_BOLD}{CLR_CYAN}{round(avg_behavioral_score, 2)}%{CLR_RESET}")
        print(f" |- Raw Composite HR Score:       {round(raw_composite_score, 2)}%")
        
        if ethical_safeguard_applied:
            print(f" |- {CLR_YELLOW}[NEURO-SHIELD ACTIVE]: Capped behavioral penalty to -5.0% to protect candidate.{CLR_RESET}")
            print(f"    |- Final Adjusted HR Score:   {CLR_BOLD}{CLR_GREEN}{round(final_hr_score, 2)}%{CLR_RESET}")
        else:
            print(f" |- [Neuro-Shield Status]: Active (No threshold violation. Clean calculation applied.)")
            print(f"    |- Final Adjusted HR Score:   {CLR_BOLD}{CLR_GREEN}{round(final_hr_score, 2)}%{CLR_RESET}")
            
        # Print Signal telemetry aggregates
        print(f"\n   [Video Telemetry Aggregates]:")
        avg_eye = np.mean([r["signals"]["eye_gaze"]["score"] for r in turn_behavioral_reports])
        avg_head = np.mean([r["signals"]["head_movement"]["score"] for r in turn_behavioral_reports])
        avg_face = np.mean([r["signals"]["facial_engagement"]["score"] for r in turn_behavioral_reports])
        avg_pres = np.mean([r["signals"]["presence_ratio"] for r in turn_behavioral_reports])
        
        gaze_exempt_status = "ACTIVE (Eye-gaze metrics exempted & weights re-allocated)" if baseline["gaze_exempt_eligible"] else "INACTIVE"
        print(f"    |- Focus Level Index:   {CLR_GREEN}{round(avg_focus_level, 2)}%{CLR_RESET}")
        print(f"    |- Eye Gaze Stability:  {round(avg_eye, 2)}% | Gaze-Exemption Guard: {CLR_YELLOW}{gaze_exempt_status}{CLR_RESET}")
        print(f"    |- Posture Stability:   {round(avg_head, 2)}%")
        print(f"    |- Facial Engagement:   {round(avg_face, 2)}%")
        print(f"    |- Camera Frame Presence:{round(avg_pres, 2)}%")
        
        # Display insights
        print(f"\n   [Behavioral AI Insights]:")
        for ins in all_insights:
            icon = "[ALERT]" if "reading" in ins or "distraction" in ins or "leaves" in ins else "[INFO]"
            print(f"    {icon} {ins}")
            
        # Print Unified hiring dashboard
        print_banner(f"FINAL UNIFIED HIRING INTELLIGENCE: {cand['name']}", CLR_GREEN)
        print(f"{CLR_BOLD}Target Job Role:    {CLR_RESET}{unified_report['role_evaluated_for']}")
        print(f"{CLR_BOLD}Hiring Readiness:   {CLR_BOLD}{CLR_GREEN}{unified_report['readiness_band']}{CLR_RESET}")
        print(f"{CLR_BOLD}Final Hiring Fit:   {CLR_CYAN}{CLR_BOLD}{unified_report['final_hiring_fit_score']}%{CLR_RESET}")
        print(f"{CLR_BOLD}Role Weight Standard:{CLR_RESET} {unified_report['weight_system_used']}")
        
        print(f"\n{CLR_BOLD}Rounds Contribution Breakdown:{CLR_RESET}")
        for round_key, metrics in unified_report["cross_round_breakdown"].items():
            round_title = round_key.upper().replace("_", " ")
            print(f" |- {round_title:18}: Raw {metrics['raw_score']}% | Weighted {metrics['weight_applied']} -> Contributed: {CLR_GREEN}{metrics['weighted_contribution']}%{CLR_RESET}")
            
        print("-" * 90)
        time.sleep(1)

if __name__ == "__main__":
    run_behavioral_evaluation_demo()
