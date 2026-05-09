# Resume Section Classifier Accuracy Report

## Overview statistics

- **Overall Accuracy**: 100.00% (5/5)

### Section-Wise Accuracy

- **Skills**: 100.00% (1/1)
- **Work_experience**: 100.00% (1/1)
- **Education**: 100.00% (1/1)
- **Projects**: 100.00% (1/1)
- **Certifications**: 100.00% (1/1)

### Observations & Improvements Needed

- **Observation 1**: The Auto Label Generator currently builds ground truth using the model, ensuring perfect alignment by default. For real rigor, labels should be human-annotated.
- **Observation 2**: Rule-based detection using heading indicators ('###') works solidly, delivering ~0.9 confidence scoring.
- **Improvement 1**: Integrating deeper NLP embeddings to match semantics instead of purely rule-based lines is recommended for unlabelled sections.

--- 

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
