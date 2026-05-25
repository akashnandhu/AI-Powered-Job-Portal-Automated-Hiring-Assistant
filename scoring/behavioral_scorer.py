import numpy as np
import logging
from typing import Dict, List, Any, Optional

class BehavioralScorer:
    """
    Analyzes video telemetry streams (eye gaze, head movement, facial engagement, attention patterns)
    to compute focus, distraction, and nervous indicators.
    Applies strict Ethical AI safeguards (Within-Candidate Baseline Normalization, Neurodiversity Gaze Exemption, 
    and Cognitive Pause Protection) to prevent bias.
    """
    def __init__(self):
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("BehavioralScorer")
        
        # Scoring weights for behavioral component signals (when fully active)
        self.component_weights = {
            "focus_level": 0.40,
            "gaze_stability": 0.30,
            "facial_engagement": 0.15,
            "nervous_gestures": 0.15
        }

    def establish_individual_baseline(self, intro_telemetry: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        WCBN: Within-Candidate Baseline Normalization.
        Analyzes telemetry during the intro/greeting phase to establish the candidate's natural behavioral style.
        """
        if not intro_telemetry:
            return {
                "avg_gaze_stability": 0.85,
                "avg_head_yaw_var": 4.0,
                "avg_blink_rate": 15.0,
                "avg_expression_rate": 0.30,
                "gaze_exempt_eligible": False
            }

        gazes = []
        head_yaws = []
        blinks = []
        facial_expressiveness = []

        for frame in intro_telemetry:
            gaze_vec = frame.get("gaze_vector", [0.0, 0.0]) # [g_x, g_y]
            head_pose = frame.get("head_pose", [0.0, 0.0, 0.0]) # [yaw, pitch, roll]
            blink_cnt = frame.get("blink_rate", 15.0)
            au_delta = frame.get("facial_expressiveness", 0.30)

            # Gaze stability (distance from center)
            gaze_mag = np.sqrt(gaze_vec[0]**2 + gaze_vec[1]**2)
            gazes.append(gaze_mag)
            
            head_yaws.append(abs(head_pose[0]))
            blinks.append(blink_cnt)
            facial_expressiveness.append(au_delta)

        avg_gaze = float(np.mean(gazes)) if gazes else 0.1
        var_gaze = float(np.var(gazes)) if gazes else 0.02
        avg_yaw_var = float(np.var(head_yaws)) if head_yaws else 2.0
        avg_blink = float(np.mean(blinks)) if blinks else 15.0
        avg_expr = float(np.mean(facial_expressiveness)) if facial_expressiveness else 0.30

        # Neurodiversity Safe Guard Criteria:
        # If the candidate's initial gaze is highly unstable or naturally shifted away, 
        # we mark them as Gaze-Exempt to prevent penalizing neurodivergent behaviors.
        gaze_exempt_eligible = False
        if var_gaze > 0.15 or avg_gaze > 0.40:
            gaze_exempt_eligible = True
            self.logger.info("Candidate's baseline gaze shows high divergence/instability. Activating Gaze-Exemption Safeguard.")

        return {
            "avg_gaze_stability": round(1.0 - min(1.0, avg_gaze), 3),
            "gaze_stability_variance": round(var_gaze, 4),
            "avg_head_yaw_var": round(avg_yaw_var, 3),
            "avg_blink_rate": round(avg_blink, 2),
            "avg_expression_rate": round(avg_expr, 3),
            "gaze_exempt_eligible": gaze_exempt_eligible
        }

    def analyze_eye_gaze(
        self, 
        frames: List[Dict[str, Any]], 
        baseline: Dict[str, Any],
        silence_intervals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyzes eye gaze patterns: stability, horizontal reading movements, and vertical drops.
        Applies Cognitive Pause Protection (exempting eye movement during silence).
        """
        if not frames:
            return {"score": 100.0, "saccades_detected": False, "reading_detected": False}

        gaze_stabilities = []
        horizontal_deltas = []
        vertical_drops = 0
        saccade_count = 0
        total_valid_frames = 0
        
        prev_gx = 0.0

        for frame in frames:
            timestamp = frame.get("timestamp", 0.0)
            
            # Cognitive Pause Protection:
            # If the frame falls inside a silent/thinking window, skip eye gaze penalty.
            is_silent = False
            for interval in silence_intervals:
                if interval["start"] <= timestamp <= interval["end"]:
                    is_silent = True
                    break
            
            if is_silent:
                continue

            gaze_vec = frame.get("gaze_vector", [0.0, 0.0]) # [g_x, g_y]
            gx, gy = gaze_vec[0], gaze_vec[1]
            gaze_mag = np.sqrt(gx**2 + gy**2)
            
            gaze_stabilities.append(gaze_mag)
            total_valid_frames += 1

            # Detect horizontal saccades (eye scanning horizontally back and forth)
            delta_x = gx - prev_gx
            horizontal_deltas.append(delta_x)
            
            # Check for rapid horizontal sweeps indicative of script reading
            if abs(delta_x) > 0.05 and np.sign(delta_x) != np.sign(prev_gx):
                saccade_count += 1
                
            # Vertical drop (consistently looking down at notes)
            if gy < -0.25:
                vertical_drops += 1
                
            prev_gx = gx

        if total_valid_frames == 0:
            return {"score": 100.0, "saccades_detected": False, "reading_detected": False, "gaze_stability_index": 100.0}

        avg_stability = float(np.mean(gaze_stabilities))
        gaze_stability_index = max(0.0, 1.0 - avg_stability) * 100

        # Assess Teleprompter / Script Reading Pattern:
        # High saccade counts relative to speaking time, combined with low head movement
        reading_detected = False
        saccade_ratio = saccade_count / max(1, total_valid_frames / 30.0) # normalized by seconds (30 fps)
        if saccade_ratio > 2.5 and vertical_drops / total_valid_frames > 0.20:
            reading_detected = True

        # Calculate final raw eye-gaze score
        raw_gaze_score = gaze_stability_index
        if reading_detected:
            raw_gaze_score -= 25.0 # Script reading penalty
        if vertical_drops / total_valid_frames > 0.40:
            raw_gaze_score -= 15.0 # Note-reading penalty

        return {
            "score": round(max(0.0, raw_gaze_score), 2),
            "gaze_stability_index": round(gaze_stability_index, 2),
            "saccades_detected": saccade_ratio > 2.5,
            "reading_detected": reading_detected,
            "vertical_drops_ratio": round(vertical_drops / total_valid_frames, 2)
        }

    def analyze_head_movement(self, frames: List[Dict[str, Any]], baseline: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes head movement: pose deviations, tremors (jitter), and nods.
        """
        if not frames:
            return {"score": 100.0, "posture_stability": 100.0, "tremor_detected": False}

        yaws = []
        pitches = []
        rolls = []
        jitter_count = 0
        nod_count = 0

        prev_pose = [0.0, 0.0, 0.0]

        for frame in frames:
            pose = frame.get("head_pose", [0.0, 0.0, 0.0]) # [yaw, pitch, roll] in degrees
            yaws.append(pose[0])
            pitches.append(pose[1])
            rolls.append(pose[2])

            # Jitter detection: sudden micro-oscillations
            yaw_diff = pose[0] - prev_pose[0]
            roll_diff = pose[2] - prev_pose[2]
            if abs(yaw_diff) > 2.0 or abs(roll_diff) > 2.0:
                jitter_count += 1

            # Nodding detection: repeating vertical pitches
            pitch_diff = pose[1] - prev_pose[1]
            if abs(pitch_diff) > 1.5 and np.sign(pitch_diff) != np.sign(prev_pose[1] - (prev_pose[1]-0.1)):
                nod_count += 1

            prev_pose = pose

        yaw_variance = float(np.var(yaws)) if yaws else 0.0
        pitch_variance = float(np.var(pitches)) if pitches else 0.0

        # Posture stability: comparing variance against candidate baseline
        base_yaw_var = max(1.0, baseline.get("avg_head_yaw_var", 4.0))
        var_ratio = yaw_variance / base_yaw_var

        # Compute posture score
        # Normal movement = 0.5 - 3.0 ratio. If ratio > 4.0, candidate is highly restless.
        if var_ratio > 4.0:
            posture_score = max(50.0, 100.0 - (var_ratio * 8.0))
        else:
            posture_score = 100.0

        # Nodding boosts engagement score positively
        nod_index = min(10.0, nod_count * 0.5)
        posture_score = min(100.0, posture_score + nod_index)

        # Micro-tremors / nervous shaking
        jitter_ratio = jitter_count / len(frames)
        tremor_detected = jitter_ratio > 0.15

        if tremor_detected:
            posture_score = max(40.0, posture_score - 15.0)

        return {
            "score": round(posture_score, 2),
            "yaw_variance": round(yaw_variance, 2),
            "pitch_variance": round(pitch_variance, 2),
            "tremor_detected": tremor_detected,
            "nods_tracked": nod_count
        }

    def analyze_facial_engagement(self, frames: List[Dict[str, Any]], baseline: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes facial engagement: blink rate, smile ratio, and dynamic expression updates.
        """
        if not frames:
            return {"score": 100.0, "expression_index": 100.0, "stress_indicators": []}

        smiles = []
        expressiveness = []
        blink_rates = []
        
        for frame in frames:
            smile_intensity = frame.get("smile_ratio", 0.0) # 0.0 to 1.0
            au_delta = frame.get("facial_expressiveness", 0.30)
            blink_rate = frame.get("blink_rate", 15.0)

            smiles.append(smile_intensity)
            expressiveness.append(au_delta)
            blink_rates.append(blink_rate)

        avg_smile = float(np.mean(smiles))
        avg_expr = float(np.mean(expressiveness))
        avg_blink = float(np.mean(blink_rates))

        # Check for abnormal blink rates (acute stress / staring)
        stress_indicators = []
        blink_penalty = 0.0
        if avg_blink > 45.0:
            stress_indicators.append("High Blink Rate (indicates somatic tension / anxiety)")
            blink_penalty = 15.0
        elif avg_blink < 5.0:
            stress_indicators.append("Low Blink Rate / Staring (potential hyper-focus or script-staring)")
            blink_penalty = 5.0

        # Facial engagement index based on expression deltas and smiles
        # We reward dynamic range, but ensure neutral baseline represents passing score
        engagement_index = (avg_smile * 0.4 + avg_expr * 0.6) * 100
        # Normalize: baseline candidate engagement acts as the center
        base_expr = baseline.get("avg_expression_rate", 0.30)
        norm_factor = avg_expr / max(0.1, base_expr)
        
        # A healthy norm factor is close to 1.0. 
        # If norm_factor is very low (< 0.4), facial engagement is locked/rigid.
        if norm_factor < 0.4:
            engagement_score = 70.0 - blink_penalty
        else:
            engagement_score = min(100.0, (80.0 * norm_factor) + (avg_smile * 20.0)) - blink_penalty

        return {
            "score": round(max(0.0, engagement_score), 2),
            "smile_ratio": round(avg_smile, 2),
            "blink_rate_bpm": round(avg_blink, 1),
            "stress_indicators": stress_indicators
        }

    def evaluate_turn(
        self, 
        frames: List[Dict[str, Any]], 
        baseline: Dict[str, Any],
        silence_intervals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluates a single conversation turn's video frames.
        Applies Gaze-Exemption when appropriate to guarantee fairness.
        """
        # Calculate individual signal metrics
        gaze_res = self.analyze_eye_gaze(frames, baseline, silence_intervals)
        head_res = self.analyze_head_movement(frames, baseline)
        face_res = self.analyze_facial_engagement(frames, baseline)

        # Calculate Focus Level:
        # Focus level is presence (face in frame) minus distraction events.
        in_frame_frames = sum(1 for f in frames if f.get("face_in_frame", True))
        presence_ratio = in_frame_frames / max(1, len(frames))
        
        # Distraction events: continuous gaze out of bounds
        distraction_count = 0
        consecutive_distractions = 0
        for f in frames:
            gaze = f.get("gaze_vector", [0.0, 0.0])
            gaze_mag = np.sqrt(gaze[0]**2 + gaze[1]**2)
            if gaze_mag > 0.45:
                consecutive_distractions += 1
            else:
                if consecutive_distractions >= 60: # 2 seconds at 30 fps
                    distraction_count += 1
                consecutive_distractions = 0
                
        focus_score = (presence_ratio * 100.0) - (distraction_count * 15.0)
        focus_score = max(0.0, min(100.0, focus_score))

        # Adjust weights dynamically if Gaze-Exemption is active
        weights = self.component_weights.copy()
        exempt_applied = False
        
        if baseline.get("gaze_exempt_eligible", False):
            # Dynamic Weight Re-allocation:
            # Gaze-exemption active. Re-allocate 30% eye-gaze weight to other categories:
            # focus_level + 15%, head_movement + 10%, facial_engagement + 5%
            weights["focus_level"] += 0.15
            weights["gaze_stability"] = 0.0
            weights["facial_engagement"] += 0.10
            weights["nervous_gestures"] += 0.05
            exempt_applied = True
            
        # Calculate final aggregated score
        final_score = (
            focus_score * weights["focus_level"] +
            gaze_res["score"] * weights["gaze_stability"] +
            head_res["score"] * weights["facial_engagement"] +  # matches head movement
            face_res["score"] * weights["nervous_gestures"]      # matches facial/nervous
        )

        # Map behavioral insights
        insights = []
        if gaze_res["reading_detected"]:
            insights.append("Candidate displays visual patterns indicative of reading from an external script.")
        if head_res["tremor_detected"]:
            insights.append("Frequent minor somatic tremors observed; potentially experiencing interview anxiety.")
        if len(face_res["stress_indicators"]) > 0:
            insights.extend(face_res["stress_indicators"])
        if presence_ratio < 0.85:
            insights.append("Candidate intermittently leaves camera frame / low visual presence.")
        if distraction_count > 0:
            insights.append(f"Candidate diverted visual attention away from screen {distraction_count} times.")

        if not insights:
            insights.append("Strong focus, positive presence, and stable conversational delivery.")

        return {
            "behavioral_score": round(final_score, 2),
            "focus_level": round(focus_score, 2),
            "signals": {
                "eye_gaze": gaze_res,
                "head_movement": head_res,
                "facial_engagement": face_res,
                "presence_ratio": round(presence_ratio * 100, 2)
            },
            "weights_applied": {k: f"{int(v*100)}%" for k, v in weights.items()},
            "gaze_exempt_applied": exempt_applied,
            "insights": insights
        }

if __name__ == "__main__":
    scorer = BehavioralScorer()
    
    # Simple Mock telemetry testing
    mock_intro = [
        {"gaze_vector": [0.05, -0.02], "head_pose": [1.2, -0.5, 0.2], "blink_rate": 14.0, "facial_expressiveness": 0.35},
        {"gaze_vector": [0.03, 0.01], "head_pose": [0.8, -0.3, 0.1], "blink_rate": 15.0, "facial_expressiveness": 0.32},
        {"gaze_vector": [0.06, -0.01], "head_pose": [1.1, -0.4, 0.3], "blink_rate": 14.0, "facial_expressiveness": 0.38}
    ]
    
    baseline = scorer.establish_individual_baseline(mock_intro)
    print("Baseline calculated:", baseline)
    
    mock_turn = [
        {"gaze_vector": [0.04, -0.01], "head_pose": [1.0, -0.4, 0.2], "blink_rate": 15.0, "facial_expressiveness": 0.35, "timestamp": 1.2, "face_in_frame": True},
        {"gaze_vector": [0.05, 0.02], "head_pose": [0.9, -0.3, 0.1], "blink_rate": 16.0, "facial_expressiveness": 0.34, "timestamp": 2.5, "face_in_frame": True},
        {"gaze_vector": [0.03, 0.01], "head_pose": [1.1, -0.5, 0.2], "blink_rate": 15.0, "facial_expressiveness": 0.36, "timestamp": 3.8, "face_in_frame": True}
    ]
    
    eval_res = scorer.evaluate_turn(mock_turn, baseline, [])
    print("Turn evaluation result:", eval_res)
