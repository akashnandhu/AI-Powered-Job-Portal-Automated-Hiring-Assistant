import json
import os
import sys

# Add base directory to path to fix import errors
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from interview_ai.understanding_engine import AnswerUnderstandingEngine
from pydantic import BaseModel

class CandidateSimulation:
    def __init__(self):
        self.engine = AnswerUnderstandingEngine()
        self.test_cases = [
            {
                "id": "cand_confident",
                "type": "Confident",
                "transcript": "I have 5 years of experience in Python and AWS. I can start immediately and my salary expectation is $120K. I have led multiple projects delivering robust backend systems.",
                "expected": {
                    "intent": "direct_answer",
                    "is_vague": False,
                    "confidence_min": 0.8
                }
            },
            {
                "id": "cand_hesitant",
                "type": "Hesitant",
                "transcript": "Could you clarify what you mean? I guess I know some stuff... maybe 2 years of experience. I'm not sure.",
                "expected": {
                    "intent": "clarification_needed", # or partial
                    "is_vague": True,
                    "confidence_max": 0.8
                }
            },
            {
                "id": "cand_inexperienced",
                "type": "Inexperienced",
                "transcript": "Well, the weather is nice today. I like to watch movies.",
                "expected": {
                    "intent": "off_topic",
                    "is_vague": False,
                    "confidence_max": 0.8
                }
            },
            {
                "id": "cand_overqualified",
                "type": "Overqualified",
                "transcript": "I have 15 years of experience architecting large scale distributed systems using Java, Python, AWS, Docker, and Kubernetes. I was a Principal Engineer at my last job, leading a team of 50. I am available in 30 days and expect $250K.",
                "expected": {
                    "intent": "direct_answer",
                    "is_vague": False,
                    "confidence_min": 0.8
                }
            }
        ]
        
    def run_tests(self):
        results = []
        inconsistencies = []
        correct = 0
        total = len(self.test_cases)
        
        for case in self.test_cases:
            res = self.engine.process_answer(
                raw_transcript=case["transcript"],
                cleaned_transcript=case["transcript"],
                question_category="General"
            )
            
            # Evaluate against expectations
            is_match = True
            expected = case["expected"]
            
            # Intent check
            if expected.get("intent") and res.intent != expected["intent"]:
                # If hesitant expected clarification but got something else, just check if it flagged vague
                if case["type"] == "Hesitant" and res.is_vague_or_missing:
                    pass # Acceptable
                else:
                    is_match = False
                    inconsistencies.append(f"{case['type']}: Expected intent '{expected['intent']}', got '{res.intent}'")
                
            # Vague check
            if "is_vague" in expected and res.is_vague_or_missing != expected["is_vague"]:
                is_match = False
                inconsistencies.append(f"{case['type']}: Expected is_vague '{expected['is_vague']}', got '{res.is_vague_or_missing}'")
                
            # Confidence check
            if "confidence_min" in expected and res.confidence_score < expected["confidence_min"]:
                is_match = False
                inconsistencies.append(f"{case['type']}: Expected confidence >= {expected['confidence_min']}, got {res.confidence_score}")
                
            if "confidence_max" in expected and res.confidence_score > expected["confidence_max"]:
                is_match = False
                inconsistencies.append(f"{case['type']}: Expected confidence <= {expected['confidence_max']}, got {res.confidence_score}")
                
            if is_match:
                correct += 1
                
            results.append({
                "type": case["type"],
                "transcript": case["transcript"],
                "predicted_intent": res.intent,
                "is_vague": res.is_vague_or_missing,
                "confidence": res.confidence_score,
                "extracted_skills": res.extracted_data.skills,
                "extracted_exp": res.extracted_data.experience_years,
                "extracted_salary": res.extracted_data.salary_expectation,
                "extracted_avail": res.extracted_data.availability,
                "match": is_match
            })
            
        accuracy = (correct / total) * 100 if total > 0 else 0
        
        return {
            "results": results,
            "inconsistencies": inconsistencies,
            "accuracy": accuracy,
            "correct": correct,
            "total": total
        }

def generate_report(data, output_file="reports/hr_interview_test_report.md"):
    os.makedirs("reports", exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# HR Interview System Test Report\n\n")
        f.write("## 1. Overview\n")
        f.write("Simulated end-to-end testing of the HR Interview `AnswerUnderstandingEngine` using various candidate profiles.\n\n")
        
        f.write("## 2. Accuracy Evaluation\n")
        f.write(f"- **Total Scenarios**: {data['total']}\n")
        f.write(f"- **Successful Matches**: {data['correct']}\n")
        f.write(f"- **Overall Accuracy**: {data['accuracy']:.2f}%\n\n")
        
        f.write("## 3. Candidate Simulation Details\n\n")
        for res in data['results']:
            f.write(f"### Profile: {res['type']}\n")
            f.write(f"- **Transcript**: \"{res['transcript']}\"\n")
            f.write(f"- **Predicted Intent**: `{res['predicted_intent']}`\n")
            f.write(f"- **Is Vague**: `{res['is_vague']}`\n")
            f.write(f"- **Confidence Score**: `{res['confidence']}`\n")
            f.write(f"- **Extracted Skills**: `{res['extracted_skills']}`\n")
            f.write(f"- **Extracted Experience**: `{res['extracted_exp']}`\n")
            f.write(f"- **Extracted Salary**: `{res['extracted_salary']}`\n")
            f.write(f"- **Extracted Availability**: `{res['extracted_avail']}`\n")
            f.write(f"- **Match with Manual Eval**: `{'✅ Yes' if res['match'] else '❌ No'}`\n\n")
            
        f.write("## 4. Scoring Inconsistencies Identified\n")
        if data['inconsistencies']:
            for inc in data['inconsistencies']:
                f.write(f"- {inc}\n")
        else:
            f.write("- None detected. AI matched expected manual evaluations.\n")
            
        f.write("\n## 5. Improvement Recommendations\n")
        f.write("1. **LLM Integration for Intent Analysis**: Rule-based intent detection is rigid. For example, partial answers or clarification questions might not contain specific keywords but are contextually vague.\n")
        f.write("2. **Context-Aware Follow-ups**: Instead of general follow-ups, use extracted entities to dynamically ask specific follow-ups (e.g., 'I see you mentioned Python, what frameworks did you use?').\n")
        f.write("3. **Entity Extraction Robustness**: Improve regex/NLP rules for entity extraction (salary, availability) to handle more varied formats and conversational responses.\n")
        f.write("4. **Nuanced Confidence Scoring**: Base confidence score on the complexity of the sentence structure rather than just keyword presence.\n")

    json_output_file = output_file.replace(".md", ".json")
    with open(json_output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    sim = CandidateSimulation()
    results = sim.run_tests()
    generate_report(results)
    print(f"Test complete. Accuracy: {results['accuracy']}%. Report saved to reports/hr_interview_test_report.md")
