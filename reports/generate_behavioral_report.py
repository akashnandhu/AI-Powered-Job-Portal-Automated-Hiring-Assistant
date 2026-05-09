import sys
import os

# Ensure we can import from the root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from screening_ai.behavioral_analysis import BehavioralAnalyzer

def generate_report():
    analyzer = BehavioralAnalyzer()
    
    test_cases = [
        {
            "description": "Introduction (Confident)",
            "text": "Hi, I'm Akash AA. I'm a Data Science student with experience in Python, machine learning, and building web applications using Django.",
            "duration": 12.0
        },
        {
            "description": "Experience (Structured)",
            "text": "I'm currently interning at Scope India, where I've built models using Linear Regression and Decision Trees.",
            "duration": 8.0
        },
        {
            "description": "Salary Expectations (Hesitant proxy example)",
            "text": "Um, well, I guess I'm open to industry standard packages for entry-level data science roles.",
            "duration": 7.0
        },
        {
            "description": "Cloud Platforms (Uncertainty proxy example)",
            "text": "I mean, I haven't used cloud platforms extensively yet, mostly focused on local development, I guess.",
            "duration": 9.0
        },
        {
            "description": "Notice Period (Terse)",
            "text": "I can start immediately.",
            "duration": 2.0
        }
    ]

    report_content = "# Behavioral Indicators & Communication Quality Report\n\n"
    report_content += "## Overview\nThis report demonstrates the capabilities of the `BehavioralAnalyzer` to detect hesitation, measure sentiment, assess confidence, and generate communication style indicators from candidate responses.\n\n"
    
    report_content += "## Test Cases\n\n"
    
    for idx, case in enumerate(test_cases, 1):
        report = analyzer.analyze_response(case["text"], duration_seconds=case["duration"])
        
        report_content += f"### Test Case {idx}: {case['description']}\n"
        report_content += f"- **Transcript**: `{report.response_text}`\n"
        report_content += f"- **Duration**: `{case['duration']} seconds`\n"
        
        report_content += f"#### Sentiment Analysis\n"
        report_content += f"- **Label**: `{report.sentiment.label.capitalize()}`\n"
        report_content += f"- **Score**: `{report.sentiment.score}`\n"
        report_content += f"- **Positive Words**: `{report.sentiment.positive_words_detected}` | **Negative Words**: `{report.sentiment.negative_words_detected}`\n"
        
        report_content += f"#### Confidence Analysis\n"
        report_content += f"- **Overall Confidence Score**: `{report.confidence.confidence_score}`\n"
        report_content += f"- **Hesitation Fillers Found**: `{report.confidence.hesitation_count}`\n"
        report_content += f"- **Uncertain Phrases Found**: `{report.confidence.uncertainty_count}`\n"
        report_content += f"- **Contradictions Detected**: `{report.confidence.contradiction_detected}`\n"
        
        report_content += f"#### Behavioral Indicators\n"
        report_content += f"- **Word Count**: `{report.indicators.response_length_words}` words\n"
        if report.indicators.estimated_pace_wpm:
            report_content += f"- **Estimated Pace**: `{report.indicators.estimated_pace_wpm}` WPM\n"
        report_content += f"- **Communication Style**: `{', '.join(report.indicators.communication_style)}`\n"
        
        report_content += f"#### Overall Assessment\n"
        report_content += f"> {report.overall_assessment}\n\n"

    report_content += "---\n## Deliverables Achieved\n"
    report_content += "1. **Confidence analysis logic**: Implemented heuristics measuring hesitations, contradictions, and uncertainty.\n"
    report_content += "2. **Sentiment scoring module**: Assesses the polarity (Positive, Negative, Neutral) of the candidate's word choice.\n"
    report_content += "3. **Behavioral indicators report**: Encapsulates and structures all analyzed behavioral data for explainability.\n"

    report_path = os.path.join(os.path.dirname(__file__), 'behavioral_indicators_report.md')
    with open(report_path, 'w') as f:
        f.write(report_content)
        
    print(f"Report successfully generated at {report_path}")

if __name__ == '__main__':
    generate_report()
