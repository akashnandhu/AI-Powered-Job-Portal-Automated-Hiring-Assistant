import logging
from typing import Dict, List, Any, Tuple

class IntegrityScorer:
    """
    Evaluates interview session integrity by checking browser blur events, 
    tab navigation frequency, second speaker acoustic diarization, and gaze outliers.
    Identifies coordinated malpractice patterns (CSP/ACP) and outputs recruiter risk tagging.
    """
    def __init__(self):
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("IntegrityScorer")
        
        # Malpractice threshold limits
        self.thresholds = {
            "max_tab_switches_green": 1,
            "max_tab_switches_yellow": 3,
            "max_blur_duration_green": 8.0,   # seconds
            "max_blur_duration_yellow": 20.0, # seconds
            "max_gaze_deviations_green": 3,
            "max_gaze_deviations_yellow": 7,
            "voice_diarization_confidence_limit": 0.70
        }

    def detect_coordinated_search_patterns(self, events: List[Dict[str, Any]]) -> int:
        """
        Pattern Recognition: Coordinated Search Pattern (CSP).
        Detects candidates searching for answers immediately after a question is asked.
        Sequence: Question Asked -> Browser Blur within 5s -> Blur for > 5s -> Focus returned -> Speech starts
        """
        csp_count = 0
        
        # Sort events by timestamp to ensure chronological analysis
        sorted_events = sorted(events, key=lambda x: x.get("timestamp", 0.0))
        
        for idx, event in enumerate(sorted_events):
            if event.get("type") == "question_asked":
                question_time = event.get("timestamp", 0.0)
                
                # Check for blur event within 5 seconds of the question being asked
                blur_found = False
                blur_time = 0.0
                focus_time = 0.0
                
                for j in range(idx + 1, len(sorted_events)):
                    next_event = sorted_events[j]
                    next_time = next_event.get("timestamp", 0.0)
                    
                    if next_time - question_time > 15.0:
                        break # Too long after question, pattern invalid
                        
                    if next_event.get("type") == "browser_blur" and not blur_found:
                        if next_time - question_time <= 5.0:
                            blur_found = True
                            blur_time = next_time
                            
                    elif next_event.get("type") == "browser_focus" and blur_found:
                        focus_time = next_time
                        blur_duration = focus_time - blur_time
                        
                        # Verify the blur lasted for a significant searching duration (e.g. 4 - 15 seconds)
                        if 4.0 <= blur_duration <= 15.0:
                            # Verify candidate starts speaking shortly after focus returns
                            for k in range(j + 1, len(sorted_events)):
                                speech_event = sorted_events[k]
                                speech_time = speech_event.get("timestamp", 0.0)
                                if speech_time - focus_time > 8.0:
                                    break
                                if speech_event.get("type") == "speech_started":
                                    csp_count += 1
                                    self.logger.warning(
                                        f"Coordinated Search Pattern (CSP) detected at timestamp {question_time:.2f}s."
                                    )
                                    break
                        break
        return csp_count

    def detect_accomplice_cue_patterns(
        self, 
        gaze_deviations: List[Dict[str, Any]], 
        speech_intervals: List[Dict[str, Any]]
    ) -> int:
        """
        Pattern Recognition: Accomplice Cue Pattern (ACP).
        Detects candidates reading pre-typed answers fed by an accomplice on another screen.
        Sequence: Candidate is actively speaking + Eye gaze shifted off-center for > 4s concurrently.
        """
        acp_count = 0
        
        for dev in gaze_deviations:
            start_time = dev.get("start", 0.0)
            duration = dev.get("duration", 0.0)
            
            # Gaze deviation must be sustained to represent reading
            if duration >= 4.0:
                # Check if this deviation overlaps with an active speech interval
                for speech in speech_intervals:
                    s_start = speech.get("start", 0.0)
                    s_end = speech.get("end", 0.0)
                    
                    # Calculate overlap duration
                    overlap_start = max(start_time, s_start)
                    overlap_end = min(start_time + duration, s_end)
                    overlap_dur = overlap_end - overlap_start
                    
                    if overlap_dur >= 3.0: # Significant overlap of reading while speaking
                        acp_count += 1
                        self.logger.warning(
                            f"Accomplice Cue Pattern (ACP) detected: Gaze shifted off-screen while speaking at {start_time:.2f}s."
                        )
                        break
                        
        return acp_count

    def evaluate_session_integrity(
        self, 
        tab_switches: int, 
        blur_duration: float, 
        second_speakers: int, 
        gaze_deviations: int,
        session_events: List[Dict[str, Any]],
        gaze_dev_intervals: List[Dict[str, Any]] = None,
        speech_intervals: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Performs holistic multi-modal integrity evaluation.
        Calculates Integrity Index (0-100%) and returns a Recruiter Risk Tag (GREEN, YELLOW, RED).
        """
        gaze_dev_intervals = gaze_dev_intervals or []
        speech_intervals = speech_intervals or []
        
        integrity_score = 100.0
        deductions = []
        insights = []
        
        # 1. Evaluate Tab Navigation Frequency
        if tab_switches > 0:
            tab_penalty = min(30.0, tab_switches * 7.5)
            integrity_score -= tab_penalty
            deductions.append(f"Tab Switching Penalty: -{tab_penalty:.1f} (Count: {tab_switches})")
            if tab_switches >= self.thresholds["max_tab_switches_yellow"]:
                insights.append("Frequent tab switching indicates active browser navigation away from interview.")

        # 2. Evaluate Screen Focus Loss Duration
        if blur_duration > 0:
            # Scale penalty relative to total duration outside of the screen
            blur_penalty = min(40.0, blur_duration * 1.5)
            integrity_score -= blur_penalty
            deductions.append(f"Screen Focus Loss Penalty: -{blur_penalty:.1f} (Duration: {blur_duration:.1f}s)")
            if blur_duration >= self.thresholds["max_blur_duration_yellow"]:
                insights.append("Extended periods of screen focus loss indicate long interactions with other local files/apps.")

        # 3. Evaluate Gaze Deviations Off-screen
        if gaze_deviations > 0:
            gaze_penalty = min(25.0, gaze_deviations * 3.0)
            integrity_score -= gaze_penalty
            deductions.append(f"Off-Screen Gaze Penalty: -{gaze_penalty:.1f} (Count: {gaze_deviations})")
            if gaze_deviations >= self.thresholds["max_gaze_deviations_yellow"]:
                insights.append("Frequent looking away off-screen; suggests reading external monitors or accomplices.")

        # 4. Evaluate Acoustic Speaker Diarization
        if second_speakers > 0:
            voice_penalty = min(50.0, second_speakers * 25.0)
            integrity_score -= voice_penalty
            deductions.append(f"External Speaker Penalty: -{voice_penalty:.1f} (Count: {second_speakers})")
            insights.append("Acoustic diarization flagged multiple speakers present in the same audio track.")

        # 5. Evaluate Coordinated Malpractice Patterns
        csp_count = self.detect_coordinated_search_patterns(session_events)
        if csp_count > 0:
            csp_penalty = min(40.0, csp_count * 20.0)
            integrity_score -= csp_penalty
            deductions.append(f"Coordinated Search Pattern (CSP) Penalty: -{csp_penalty:.1f} (Count: {csp_count})")
            insights.append("Coordinated search pattern: candidate switched tabs immediately after questions to look up answers.")

        acp_count = self.detect_accomplice_cue_patterns(gaze_dev_intervals, speech_intervals)
        if acp_count > 0:
            acp_penalty = min(40.0, acp_count * 20.0)
            integrity_score -= acp_penalty
            deductions.append(f"Accomplice Cue Pattern (ACP) Penalty: -{acp_penalty:.1f} (Count: {acp_count})")
            insights.append("Accomplice cue reading: candidate consistently read off-screen while speaking fluently.")

        # Ensure score boundaries [0.0, 100.0]
        integrity_score = max(0.0, round(integrity_score, 2))

        # 6. Assign Risk Category
        # Trigger RED risk on direct acoustic cheating, pattern match, or extremely low scores
        if second_speakers > 0 or csp_count > 0 or acp_count > 0 or integrity_score < 70.0:
            risk_tag = "RED"
            action_req = "REJECT / MANDATORY HUMAN VIDEO AUDIT REQUIRED (High Integrity Risk)"
        elif integrity_score < 90.0 or tab_switches >= 2 or blur_duration >= 8.0:
            risk_tag = "YELLOW"
            action_req = "PROCEED WITH CAUTION (Integrity Warning; logs flagged for manual audit)"
        else:
            risk_tag = "GREEN"
            action_req = "CLEAN SESSION (No malpractice detected)"

        if not insights:
            insights.append("Clean session. Gaze, focus, and audio signatures align perfectly with standard assessment parameters.")

        return {
            "integrity_index": integrity_score,
            "risk_tag": risk_tag,
            "recruiter_action": action_req,
            "metrics": {
                "tab_switch_count": tab_switches,
                "total_blur_duration_sec": round(blur_duration, 2),
                "second_speakers_detected": second_speakers,
                "gaze_offscreen_count": gaze_deviations,
                "coordinated_search_patterns": csp_count,
                "accomplice_cue_patterns": acp_count
            },
            "score_deductions": deductions,
            "insights": insights
        }

if __name__ == "__main__":
    scorer = IntegrityScorer()
    
    # Simple Mock telemetry testing
    mock_events = [
        {"type": "question_asked", "timestamp": 10.0},
        {"type": "browser_blur", "timestamp": 12.0},
        {"type": "browser_focus", "timestamp": 18.0},
        {"type": "speech_started", "timestamp": 20.0}
    ]
    
    mock_gaze_devs = [{"start": 35.0, "duration": 5.0}]
    mock_speech = [{"start": 30.0, "end": 45.0}]
    
    res = scorer.evaluate_session_integrity(
        tab_switches=1,
        blur_duration=6.0,
        second_speakers=0,
        gaze_deviations=2,
        session_events=mock_events,
        gaze_dev_intervals=mock_gaze_devs,
        speech_intervals=mock_speech
    )
    
    import json
    print(json.dumps(res, indent=4))
