import json
from parsers.experience_parser import ExperienceParser
from scoring.experience_scorer import ExperienceScorer

def test_experience():
    text = """
    Software Engineer at Google
    Jan 2018 - Dec 2021
    Worked on backend services using Python and Go.
    
    Data Scientist, Facebook
    Jan 2022 - Present
    Built recommendation models.
    
    Independent Consultant 
    Oct 2021 - Mar 2022
    Consulted on AI projects.
    """
    
    parser = ExperienceParser()
    experiences = parser.parse(text)
    print("Parsed Experiences:")
    print(json.dumps([e for e in experiences if 'parsed_start' not in e], default=str, indent=2))
    
    scorer = ExperienceScorer()
    # Let's say target role is 'Data Scientist' requiring 48 months (4 years) of experience
    result = scorer.score_experience(experiences, target_role="Data Scientist", target_required_months=48)
    
    print("\nScoring Result:")
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    test_experience()
