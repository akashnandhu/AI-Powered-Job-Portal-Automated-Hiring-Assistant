import os
import sys

# Ensure the parent directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from screening_ai.scoring_engine import ScreeningScoringEngine
from reports.screening_report_builder import ScreeningReportBuilder

def generate_sample():
    # 1. Initialize scoring engine
    engine = ScreeningScoringEngine()

    # 2. Mock candidate responses
    responses = [
        {
            "question_id": "q1",
            "question_text": "Please introduce yourself and your background.",
            "category": "Introduction",
            "candidate_response": "Hi, I'm Alex. I've been a software engineer for about 5 years, mostly working with Python and React on web applications.",
            "importance": "medium"
        },
        {
            "question_id": "q2",
            "question_text": "What is your experience with cloud platforms like AWS or Azure?",
            "category": "Experience",
            "candidate_response": "I have used AWS for the last 3 years. Mostly EC2, S3, and Lambda for deploying our backend services.",
            "importance": "high"
        },
        {
            "question_id": "q3",
            "question_text": "Can you rate your proficiency in Python?",
            "category": "Skills",
            "candidate_response": "I would say I'm very proficient. I use it daily.",
            "importance": "critical"
        },
        {
            "question_id": "q4",
            "question_text": "What are your salary expectations for this role?",
            "category": "Salary",
            "candidate_response": "I am looking for around $120,000 per year.",
            "importance": "high"
        },
        {
            "question_id": "q5",
            "question_text": "What is your notice period or availability to start?",
            "category": "Notice period",
            "candidate_response": "I can start in 2 weeks after an offer is made.",
            "importance": "high"
        },
        {
            "question_id": "q6",
            "question_text": "Are you willing to relocate to San Francisco?",
            "category": "Location",
            "candidate_response": "No, I am looking for remote work only right now.",
            "importance": "critical"
        },
        {
            "question_id": "q7",
            "question_text": "Do you have any experience with Kubernetes?",
            "category": "Skills",
            "candidate_response": "Not much, just played around with it a bit.",
            "importance": "medium",
            "is_vague": True
        }
    ]

    # 3. Evaluate responses
    candidate_id = "CAND-9012"
    candidate_name = "Alex Johnson"
    score_result = engine.evaluate_screening(candidate_id, responses)

    # 4. Generate report
    builder = ScreeningReportBuilder()
    output_path = os.path.join(os.path.dirname(__file__), "sample_screening_report.md")
    
    # 5. Export
    builder.export_report(candidate_name, score_result, output_path)
    print(f"Sample report generated at: {output_path}")

if __name__ == "__main__":
    generate_sample()
