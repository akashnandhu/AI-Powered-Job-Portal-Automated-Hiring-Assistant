import sys
import os

# Ensure we can import from the root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from screening_ai.behavioral_analysis import BehavioralAnalyzer

def generate_report():
    analyzer = BehavioralAnalyzer()
    
    test_cases = [
        {
            "description": "Confident, positive, and structured",
            "text": "I am very excited to achieve great success in this innovative role. I always lead with passion and clear goals.",
            "duration": 10.0
        },
        {
            "description": "Hesitant with multiple fillers",
            "text": "Um, well, I guess I could, like, you know, try to manage the project. It's kinda hard to say.",
            "duration": 15.0
        },
        {
            "description": "Uncertain with potential contradictions",
            "text": "I mean, yes, I have used it, but no, not really. Maybe I could be good at it, I guess.",
            "duration": 12.0
        },
        {
            "description": "Negative sentiment and fast-paced",
            "text": "Unfortunately that was a terrible fail. It was the worst struggle and very difficult.",
            "duration": 3.0
        },
        {
            "description": "Terse response",
            "text": "I think so. Yes.",
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
