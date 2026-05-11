from parsers.experience_parser import ExperienceParser
import json

parser = ExperienceParser()
text = """
John Doe
123 Main St | (555) 555-5555 | john.doe@email.com
Summary
Experienced developer with 10 years of experience.
### Experience
Software Engineer
Google
Jan 2015 - Present
Developed cool stuff.
Intern
Microsoft
2010 - 2014
Did some intern stuff.
"""

print(json.dumps(parser.parse(text, default=str), indent=2))
