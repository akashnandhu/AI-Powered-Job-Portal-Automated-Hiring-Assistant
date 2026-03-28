"""
skills_dict.py
Master skill dictionary mapping for technical, business, and creative categories,
as well as synonyms and tech stacks.
"""

SKILL_CATEGORIES = {
    "technical": [
        "Python", "Java", "C++", "C#", "JavaScript", "TypeScript", 
        "SQL", "NoSQL", "MongoDB", "PostgreSQL", "MySQL", "SQLite", "MSSQL",
        "Django", "Flask", "FastAPI", "React", "Angular", "Vue", "Node.js", "Express",
        "HTML", "CSS", "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git",
        "Machine Learning", "Deep Learning", "Data Science", "Pandas", "NumPy", "Scikit-Learn",
        "TensorFlow", "PyTorch", "Matplotlib", "Seaborn", "Power BI", "Tableau", "Data Analysis",
        "Predictive Modeling", "Feature Engineering"
    ],
    "business": [
        "Management", "Marketing", "Sales", "Project Management", "Agile",
        "Scrum", "Business Analysis", "Leadership", "Communication", "Strategic Planning",
        "Customer Service", "Operations"
    ],
    "creative": [
        "Design", "Photoshop", "Video Editing", "Illustration", "UI/UX",
        "Graphic Design", "Figma", "Adobe Premiere", "Copywriting", "Creative Writing"
    ]
}

# Normalization mapping for variations and abbreviations
SYNONYMS = {
    "js": "JavaScript",
    "py": "Python",
    "nodejs": "Node.js",
    "node js": "Node.js",
    "node": "Node.js",
    "reactjs": "React",
    "react.js": "React",
    "ml": "Machine Learning",
    "dl": "Deep Learning",
    "ai": "Artificial Intelligence",
    "html5": "HTML",
    "css3": "CSS",
    "postgres": "PostgreSQL",
    "sql server": "MSSQL"
}

# Tech stacks that unpack into multiple individual skills
STACKS = {
    "mern": ["MongoDB", "Express", "React", "Node.js"],
    "mean": ["MongoDB", "Express", "Angular", "Node.js"],
    "lamp": ["Linux", "Apache", "MySQL", "PHP"]
}
