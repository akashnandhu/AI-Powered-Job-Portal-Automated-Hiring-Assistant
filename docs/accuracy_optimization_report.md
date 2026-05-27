# AI Accuracy & Optimization Report

## Objective
To improve AI accuracy, reduce incorrect hiring decisions (false positives/negatives), and enhance the overall reliability of the Automated Hiring Assistant.

## 1. Intent Detection Refinement
**Problem:** The `AnswerUnderstandingEngine` was occasionally classifying valid but concise answers as "vague" or missing core intents, leading to false negatives in the HR Interview round.
**Solution:**
- Reduced the vague response word-count threshold from `< 25` to `< 12` words to accommodate concise, direct answers.
- Expanded the vague keywords list to capture more edge cases (e.g., "whatever").
- This ensures candidates are penalized for truly vague content, not just conciseness.

## 2. Consistency & Cross-Round Accuracy
**Problem:** Candidates who cheated on one round (e.g., Technical) but performed poorly on others (e.g., ATS/Screening) could still achieve a high average score, resulting in false positives.
**Solution:**
- Introduced a **Cross-Round Consistency Penalty** in `CrossRoundEngine`.
- The system now calculates the standard deviation across all completed rounds. 
- If the variance exceeds the acceptable threshold (std dev > 15.0), a penalty (up to 5.0 points) is deducted from the `unified_score`. This flags highly inconsistent performance often indicative of malpractice or narrow skill sets.

## 3. Stricter Decision Thresholds
**Problem:** The `DecisionEngine` was too lenient, passing borderline candidates.
**Solution:**
- **Selected Threshold** raised from `75.0` to `78.0`. This ensures only high-quality candidates receive the "Selected" tag.
- **Reject Threshold** raised from `55.0` to `60.0`. This aggressively filters out underperformers, saving recruiter time.
- Borderline candidates (60.0 - 77.9) are safely routed to "Hold / Review".

## 4. Processing Speed Optimization
**Problem:** Repeated NLP embedding calculations were slowing down ATS scoring.
**Solution:**
- Confirmed that `semantic_matcher.py` successfully utilizes precomputed caching for Job Description embeddings. By maintaining these tensor caches (`jd_embeddings_cache.pkl`), the system avoids re-encoding identical documents, ensuring rapid candidate evaluation at scale.
- Memory handling was verified to ensure rapid batch inference.

## Summary of Deliverables
- ✅ Refined Scoring Logic (Cross-round variance penalties).
- ✅ Improved AI Intent Detection (Stricter heuristics, fewer false negatives).
- ✅ Updated Thresholds (78.0 for Selection, 60.0 for Rejection).
- ✅ Optimization Report.
