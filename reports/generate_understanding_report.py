import sys
import os
import json

# Ensure we can import from the root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from interview_ai.understanding_engine import AnswerUnderstandingEngine

def generate_report():
    engine = AnswerUnderstandingEngine()
    
    test_cases = [
        {
            "category": "Experience & Skills",
            "raw": "Uh, yeah, I have 5.5 years of experience working with Python and AWS.",
            "cleaned": "I have 5.5 years of experience working with Python and AWS.",
            "expected_intent": "direct_answer"
        },
        {
            "category": "Salary",
            "raw": "My salary expectation is around $120K.",
            "cleaned": "My salary expectation is around $120K.",
            "expected_intent": "direct_answer"
        },
        {
            "category": "Availability",
            "raw": "I can join immediately, or within 2 weeks notice if needed.",
            "cleaned": "I can join immediately, or within 2 weeks notice if needed.",
            "expected_intent": "direct_answer"
        },
        {
            "category": "General",
            "raw": "I don't know, maybe some stuff about that.",
            "cleaned": "I don't know, maybe some stuff about that.",
            "expected_intent": "refusal_to_answer"
        },
        {
            "category": "General",
            "raw": "What do you mean by that?",
            "cleaned": "What do you mean by that?",
            "expected_intent": "clarification_needed"
        },
        {
            "category": "General",
            "raw": "The weather is really nice today, I love baseball.",
            "cleaned": "The weather is really nice today, I love baseball.",
            "expected_intent": "off_topic"
        },
        {
            "category": "General",
            "raw": "Yes.",
            "cleaned": "Yes.",
            "expected_intent": "partial_answer"
        }
    ]

    report_content = "# Answer Intent & Understanding Engine Test Report\n\n"
    report_content += "## Overview\nThis report demonstrates the capabilities of the Answer Understanding Engine to classify candidate intent, detect off-topic or vague answers, and extract structured semantic entities from unstructured interview transcripts.\n\n"
    
    report_content += "## Test Cases\n\n"
    
    for idx, case in enumerate(test_cases, 1):
        structured_answer = engine.process_answer(case["raw"], case["cleaned"], question_category=case["category"])
        
        report_content += f"### Test Case {idx}: {case['category']}\n"
        report_content += f"- **Raw Transcript**: `{structured_answer.raw_transcript}`\n"
        report_content += f"- **Detected Intent**: `{structured_answer.intent}` (Expected: `{case['expected_intent']}`)\n"
        report_content += f"- **Off-Topic Detected**: `{structured_answer.is_off_topic}`\n"
        report_content += f"- **Vague/Missing Detected**: `{structured_answer.is_vague_or_missing}`\n"
        report_content += f"- **Confidence Score**: `{structured_answer.confidence_score}`\n"
        
        # Display extracted entities nicely
        entities = structured_answer.extracted_data.model_dump(exclude_none=True)
        if entities:
            report_content += "- **Extracted Entities**:\n"
            for k, v in entities.items():
                if v: # don't show empty lists
                    report_content += f"  - **{k.replace('_', ' ').title()}**: `{v}`\n"
        else:
            report_content += "- **Extracted Entities**: `None`\n"
        
        report_content += "\n"

    report_content += "## Deliverables Achieved\n"
    report_content += "1. **Answer Understanding Engine**: Fully implemented in `interview_ai/understanding_engine.py`.\n"
    report_content += "2. **Intent Classifier**: Maps answers into actionable AI states (`direct_answer`, `clarification_needed`, `refusal_to_answer`, etc.).\n"
    report_content += "3. **Structured Answer Format**: Encapsulates raw text, cleaned text, intent, flags, and extracted entities into a strongly-typed Pydantic model (`StructuredAnswer`).\n"

    report_path = os.path.join(os.path.dirname(__file__), 'day25_understanding_engine_report.md')
    with open(report_path, 'w') as f:
        f.write(report_content)
        
    print(f"Report generated at {report_path}")

if __name__ == '__main__':
    generate_report()
