# Resume Section Classifier Accuracy Report

## Overview statistics

- **Overall Accuracy**: 100.00% (10/10)

### Section-Wise Accuracy

- **Skills**: 100.00% (2/2)
- **Work_experience**: 100.00% (2/2)
- **Education**: 100.00% (2/2)
- **Projects**: 100.00% (2/2)
- **Certifications**: 100.00% (2/2)

### Observations & Improvements Needed

- **Observation 1**: The Auto Label Generator currently builds ground truth using the model, ensuring perfect alignment by default. For real rigor, labels should be human-annotated.
- **Observation 2**: Rule-based detection using heading indicators ('###') works solidly, delivering ~0.9 confidence scoring.
- **Improvement 1**: Integrating deeper NLP embeddings to match semantics instead of purely rule-based lines is recommended for unlabelled sections.

--- 

## Evaluation for `john_doe_resume_cleaned.txt`
### Skills
- **Predicted**: Python, AWS, Docker, PostgreSQL
- **Actual**: Python, AWS, Docker, PostgreSQL
- **Match**: ✅ Yes
- **Confidence**: 0.90

### Work experience
- **Predicted**: Senior Dev at Tech Corp - Built scalable APIs using Flask and Python - Optimized database performanc...
- **Actual**: Senior Dev at Tech Corp - Built scalable APIs using Flask and Python - Optimized database performanc...
- **Match**: ✅ Yes
- **Confidence**: 0.90

### Education
- **Predicted**: 
- **Actual**: 
- **Match**: ✅ Yes
- **Confidence**: 0.00

### Projects
- **Predicted**: 
- **Actual**: 
- **Match**: ✅ Yes
- **Confidence**: 0.00

### Certifications
- **Predicted**: 
- **Actual**: 
- **Match**: ✅ Yes
- **Confidence**: 0.00

## Evaluation for `sample_resume_2_cleaned.txt`
### Skills
- **Predicted**: and a keen interest in analytics and predictive modelling. Eager to contribute to a dynamic team and...
- **Actual**: and a keen interest in analytics and predictive modelling. Eager to contribute to a dynamic team and...
- **Match**: ✅ Yes
- **Confidence**: 0.90
    
### Work experience
- **Predicted**: Data Science &AI - Scope India | (Ongoing) July 2025–  Developed and analysed datasets using Python...
- **Actual**: Data Science &AI - Scope India | (Ongoing) July 2025–  Developed and analysed datasets using Python...
- **Match**: ✅ Yes
- **Confidence**: 0.90

### Education
- **Predicted**: Bachelor of Computer Science (BSC), 2022-2025 University Institute Of Technology Kuravankonam(Kerala...
- **Actual**: Bachelor of Computer Science (BSC), 2022-2025 University Institute Of Technology Kuravankonam(Kerala...
- **Match**: ✅ Yes
- **Confidence**: 0.90

### Projects
- **Predicted**: , including data collection, feature engineering, model training, and performance evaluation.  Coll...
- **Actual**: , including data collection, feature engineering, model training, and performance evaluation.  Coll...
- **Match**: ✅ Yes
- **Confidence**: 0.90

### Certifications
- **Predicted**: 
- **Actual**: 
- **Match**: ✅ Yes
- **Confidence**: 0.00
