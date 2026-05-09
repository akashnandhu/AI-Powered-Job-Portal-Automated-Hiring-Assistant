import os
import sys

# Ensure the parent directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from screening_ai.scoring_engine import ScreeningScoringEngine
from reports.screening_report_builder import ScreeningReportBuilder

def generate_sample():
    # 1. Initialize scoring engine
    engine = ScreeningScoringEngine()

    # 2. Mock candidate responses based on sample_resume_2 (AKASH AA)
    responses = [
        {
            "question_id": "q1",
            "question_text": "Please introduce yourself and your background.",
            "category": "Introduction",
            "candidate_response": "Hi, I'm Akash AA. I'm a Data Science student with experience in Python, machine learning, and building web applications using Django.",
            "importance": "medium"
        },
        {
            "question_id": "q2",
            "question_text": "What is your experience with Machine Learning?",
            "category": "Experience",
            "candidate_response": "I'm currently interning at Scope India, where I've built models using Linear Regression and Decision Trees.",
            "importance": "high"
        },
        {
            "question_id": "q3",
            "question_text": "Can you rate your proficiency in Python?",
            "category": "Skills",
            "candidate_response": "I am highly proficient in Python, especially for data analysis and web development.",
            "importance": "critical"
        },
        {
            "question_id": "q4",
            "question_text": "What are your salary expectations for this role?",
            "category": "Salary",
            "candidate_response": "I'm open to industry standard packages for entry-level data science roles.",
            "importance": "high"
        },
        {
            "question_id": "q5",
            "question_text": "What is your notice period or availability to start?",
            "category": "Notice period",
            "candidate_response": "I can start immediately.",
            "importance": "high"
        },
        {
            "question_id": "q6",
            "question_text": "Are you willing to relocate?",
            "category": "Location",
            "candidate_response": "Yes, I am open to relocating.",
            "importance": "critical"
        },
        {
            "question_id": "q7",
            "question_text": "Do you have experience with Cloud platforms?",
            "category": "Skills",
            "candidate_response": "I haven't used cloud platforms extensively yet, mostly focused on local development.",
            "importance": "medium",
            "is_vague": True
        }
    ]

    # 3. Evaluate responses
    candidate_id = "sample_resume_2"
    candidate_name = "AKASH AA"
    score_result = engine.evaluate_screening(candidate_id, responses)

    # 4. Generate report
    builder = ScreeningReportBuilder()
    output_path = os.path.join(os.path.dirname(__file__), "sample_screening_report.json")
    
    # 5. Export
    generated_path = builder.export_report(candidate_name, score_result, output_path)
    print(f"Sample report generated at: {generated_path}")

if __name__ == "__main__":
    generate_sample()
