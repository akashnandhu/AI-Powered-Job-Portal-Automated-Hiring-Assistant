import json
import os
import sys
import time
from typing import Dict, List, Any

# Resolve import paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from scoring.integrity_scorer import IntegrityScorer
from scoring.unified_scorer import UnifiedScorer
from scoring.hr_interview_scorer import HRInterviewScorer

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

def run_integrity_evaluation_demo():
    print_banner("INITIALIZING MULTI-MODAL MALPRACTICE & INTEGRITY DETECTION SYSTEM", CLR_CYAN)
    print(f"{CLR_BOLD}Active Trackers:{CLR_RESET} HTML5 Tab Switch | Screen Focus Blur | Acoustic Diarization | Eye/Yaw Shifts")
    print(f"{CLR_BOLD}Pattern Recognition:{CLR_RESET} Coordinated Search Pattern (CSP) | Accomplice Cue Pattern (ACP) active")
    
    # Initialize scorers
    integrity_scorer = IntegrityScorer()
    hr_scorer = HRInterviewScorer()
    unified_scorer = UnifiedScorer()
    
    # Mock Candidates representing our integrity profiles
    candidates = [
        {
            "id": "CAND_001",
            "name": "AKASH AA",
            "role": "Junior Data Scientist",
            "ats_score": 88.5,
            "screening_score": 82.0,
            "hr_raw_score": 88.0,
            "telemetry": {
                "tab_switches": 0,
                "blur_duration": 0.0,
                "second_speakers": 0,
                "gaze_deviations": 1,
                "session_events": [
                    {"type": "question_asked", "timestamp": 10.0},
                    {"type": "speech_started", "timestamp": 12.0},
                    {"type": "question_asked", "timestamp": 50.0},
                    {"type": "speech_started", "timestamp": 52.0}
                ],
                "gaze_dev_intervals": [{"start": 12.5, "duration": 1.2}],
                "speech_intervals": [{"start": 12.0, "end": 45.0}]
            },
            "description": "Standard ideal candidate: completely focused, zero tab navigations or second speaker crossovers."
        },
        {
            "id": "CAND_002",
            "name": "Jane Smith",
            "role": "Junior Data Analyst",
            "ats_score": 78.0,
            "screening_score": 82.5,
            "hr_raw_score": 85.0,
            "telemetry": {
                "tab_switches": 2,
                "blur_duration": 11.5,
                "second_speakers": 0,
                "gaze_deviations": 4,
                "session_events": [
                    {"type": "question_asked", "timestamp": 10.0},
                    {"type": "speech_started", "timestamp": 12.0},
                    # Tab switched later during a passive silent pause
                    {"type": "browser_blur", "timestamp": 30.0},
                    {"type": "browser_focus", "timestamp": 41.5},
                    {"type": "question_asked", "timestamp": 60.0},
                    {"type": "speech_started", "timestamp": 63.0}
                ],
                "gaze_dev_intervals": [
                    {"start": 13.0, "duration": 2.5},
                    {"start": 64.0, "duration": 3.0}
                ],
                "speech_intervals": [
                    {"start": 12.0, "end": 28.0},
                    {"start": 63.0, "end": 80.0}
                ]
            },
            "description": "Medium risk candidate: switched tabs twice and lost screen focus briefly, but not directly linked to looking up question answers."
        },
        {
            "id": "CAND_003",
            "name": "Rahul Sharma",
            "role": "Python Full Stack Engineer",
            "ats_score": 82.0,
            "screening_score": 85.0,
            "hr_raw_score": 90.0,
            "telemetry": {
                "tab_switches": 3,
                "blur_duration": 25.0,
                "second_speakers": 0,
                "gaze_deviations": 2,
                "session_events": [
                    # CSP 1: Switched tab immediately after question asked to search answers, and started speaking right after return
                    {"type": "question_asked", "timestamp": 10.0},
                    {"type": "browser_blur", "timestamp": 11.5},
                    {"type": "browser_focus", "timestamp": 19.5},
                    {"type": "speech_started", "timestamp": 21.0},
                    
                    # CSP 2: Switched tab again on second question
                    {"type": "question_asked", "timestamp": 50.0},
                    {"type": "browser_blur", "timestamp": 52.0},
                    {"type": "browser_focus", "timestamp": 60.0},
                    {"type": "speech_started", "timestamp": 62.0}
                ],
                "gaze_dev_intervals": [{"start": 22.0, "duration": 1.5}],
                "speech_intervals": [{"start": 21.0, "end": 45.0}]
            },
            "description": "High risk cheater (CSP Match): Switched tabs and blur-searched on another window immediately after each question was asked before speaking."
        },
        {
            "id": "CAND_004",
            "name": "Sarah Jenkins",
            "role": "Sales Lead",
            "ats_score": 72.0,
            "screening_score": 70.0,
            "hr_raw_score": 89.0,
            "telemetry": {
                "tab_switches": 1,
                "blur_duration": 4.0,
                "second_speakers": 2, # Flagged twice by speaker acoustic diarization
                "gaze_deviations": 8,
                "session_events": [
                    {"type": "question_asked", "timestamp": 10.0},
                    {"type": "speech_started", "timestamp": 13.0}
                ],
                # ACP: Gaze off-screen for 6 seconds continuously while actively speaking (reading answers off accomplice monitor)
                "gaze_dev_intervals": [
                    {"start": 15.0, "duration": 6.5},
                    {"start": 30.0, "duration": 7.0}
                ],
                "speech_intervals": [{"start": 13.0, "end": 45.0}]
            },
            "description": "High risk cheater (ACP & Audio Match): Multi-speaker diarization matches another person in the room feeding answers, and eye gaze maps to long periods of off-screen script reading while speaking."
        }
    ]
    
    # Process each candidate
    for cand in candidates:
        print_banner(f"INTEGRITY PROFILE CHECK: {cand['name']}", CLR_BLUE)
        print(f"{CLR_BOLD}Target Role:{CLR_RESET}      {cand['role']}")
        print(f"{CLR_BOLD}Assigned Profile:{CLR_RESET} {cand['description']}")
        
        tel = cand["telemetry"]
        
        # 1. Run Integrity Evaluation Scorer
        print(f"\n{CLR_CYAN}[Running IntegrityScorer Event Pattern Matching Engine...]{CLR_RESET}")
        integrity_report = integrity_scorer.evaluate_session_integrity(
            tab_switches=tel["tab_switches"],
            blur_duration=tel["blur_duration"],
            second_speakers=tel["second_speakers"],
            gaze_deviations=tel["gaze_deviations"],
            session_events=tel["session_events"],
            gaze_dev_intervals=tel["gaze_dev_intervals"],
            speech_intervals=tel["speech_intervals"]
        )
        
        # Display scoring report
        risk_color = CLR_GREEN if integrity_report["risk_tag"] == "GREEN" else (
            CLR_YELLOW if integrity_report["risk_tag"] == "YELLOW" else CLR_RED
        )
        
        print(f"\n   {CLR_BOLD}INTEGRITY SCORE:{CLR_RESET} {risk_color}{integrity_report['integrity_index']}%{CLR_RESET} | {CLR_BOLD}RISK CATEGORY:{CLR_RESET} {risk_color}{integrity_report['risk_tag']}{CLR_RESET}")
        print(f"   {CLR_BOLD}Operational Action:{CLR_RESET} {risk_color}{integrity_report['recruiter_action']}{CLR_RESET}")
        
        print(f"\n   [Malpractice Telemetry Counts]:")
        metrics = integrity_report["metrics"]
        print(f"    |- Tab Switches recorded:    {metrics['tab_switch_count']}")
        print(f"    |- Screen focus blur time:   {metrics['total_blur_duration_sec']} seconds")
        print(f"    |- Acoustic Second Speakers: {metrics['second_speakers_detected']}")
        print(f"    |- Off-screen gaze counts:   {metrics['gaze_offscreen_count']}")
        print(f"    |- Coordinated Search (CSP): {CLR_RED if metrics['coordinated_search_patterns'] > 0 else CLR_GREEN}{metrics['coordinated_search_patterns']}{CLR_RESET}")
        print(f"    |- Accomplice Cue (ACP):     {CLR_RED if metrics['accomplice_cue_patterns'] > 0 else CLR_GREEN}{metrics['accomplice_cue_patterns']}{CLR_RESET}")
        
        if integrity_report["score_deductions"]:
            print(f"\n   [Scoring Deductions]:")
            for ded in integrity_report["score_deductions"]:
                print(f"    |- {CLR_RED}{ded}{CLR_RESET}")
                
        print(f"\n   [Recruiter System Insights]:")
        for ins in integrity_report["insights"]:
            icon = "[ALERT]" if integrity_report["risk_tag"] == "RED" else (
                "[WARN]" if integrity_report["risk_tag"] == "YELLOW" else "[INFO]"
            )
            print(f"    {icon} {ins}")
            
        # 2. Integrate with project workflow (Unified Dynamic Scorer)
        print(f"\n{CLR_CYAN}[Connecting to Unified Scorer pipeline (with Risk Engine Integration)...]{CLR_RESET}")
        
        ats = cand["ats_score"]
        scr = cand["screening_score"]
        hr_raw = cand["hr_raw_score"]
            
        unified_report = unified_scorer.calculate_hiring_fit(
            candidate_id=cand["id"],
            role_type=cand["role"],
            ats_score=ats,
            screening_score=scr,
            hr_interview_score=hr_raw,
            integrity_report=integrity_report
        )
        
        # Override the readiness band for RED risk to prevent automated offers
        final_fit_score = unified_report["final_hiring_fit_score"]
        readiness_status = unified_report["readiness_band"]
        risk_tag = unified_report["risk_tag"]
            
        print_banner(f"FINAL INTEGRATED DECISION: {cand['name']}", risk_color)
        print(f"{CLR_BOLD}Candidate ID:        {CLR_RESET}{cand['id']}")
        print(f"{CLR_BOLD}Readiness Status:    {risk_color}{CLR_BOLD}{readiness_status}{CLR_RESET}")
        print(f"{CLR_BOLD}Unified hiring fit:  {risk_color}{CLR_BOLD}{final_fit_score}%{CLR_RESET}")
        print(f"{CLR_BOLD}Session Integrity:   {risk_color}{integrity_report['integrity_index']}% ({risk_tag} RISK){CLR_RESET}")
        
        print(f"\n{CLR_BOLD}Pipeline Score Contributions Breakdown:{CLR_RESET}")
        for round_key, metrics in unified_report["cross_round_breakdown"].items():
            round_title = round_key.upper().replace("_", " ")
            raw_score = metrics['raw_score']
            if round_key == "hr_interview_round" and hr_raw != raw_score:
                raw_score = f"{raw_score}% (Capped from {hr_raw}%)"
            else:
                raw_score = f"{raw_score}%"
            print(f" |- {round_title:18}: Raw {raw_score:18} | Weighted {metrics['weight_applied']} -> Contributed: {CLR_GREEN}{metrics['weighted_contribution']}%{CLR_RESET}")
            
        print("-" * 90)
        time.sleep(1)

if __name__ == "__main__":
    run_integrity_evaluation_demo()
