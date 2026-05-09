# Answer Intent & Understanding Engine Test Report

## Overview
This report demonstrates the capabilities of the Answer Understanding Engine to classify candidate intent, detect off-topic or vague answers, and extract structured semantic entities from unstructured interview transcripts.

## Test Cases

### Test Case 1: Introduction
- **Raw Transcript**: `Hi, I'm Akash AA. I'm a Data Science student with experience in Python, machine learning, and building web applications using Django.`
- **Detected Intent**: `direct_answer` (Expected: `direct_answer`)
- **Off-Topic Detected**: `False`
- **Vague/Missing Detected**: `False`
- **Confidence Score**: `0.95`
- **Extracted Entities**:
  - **Skills**: `['Python', 'Machine Learning']`

### Test Case 2: Experience
- **Raw Transcript**: `I'm currently interning at Scope India, where I've built models using Linear Regression and Decision Trees.`
- **Detected Intent**: `direct_answer` (Expected: `direct_answer`)
- **Off-Topic Detected**: `False`
- **Vague/Missing Detected**: `False`
- **Confidence Score**: `0.95`
- **Extracted Entities**:

### Test Case 3: Salary
- **Raw Transcript**: `I'm open to industry standard packages for entry-level data science roles.`
- **Detected Intent**: `direct_answer` (Expected: `direct_answer`)
- **Off-Topic Detected**: `False`
- **Vague/Missing Detected**: `False`
- **Confidence Score**: `0.95`
- **Extracted Entities**:

### Test Case 4: Notice period
- **Raw Transcript**: `I can start immediately.`
- **Detected Intent**: `direct_answer` (Expected: `direct_answer`)
- **Off-Topic Detected**: `False`
- **Vague/Missing Detected**: `False`
- **Confidence Score**: `0.95`
- **Extracted Entities**:
  - **Availability**: `immediately`

### Test Case 5: Location
- **Raw Transcript**: `Yes, I am open to relocating.`
- **Detected Intent**: `direct_answer` (Expected: `direct_answer`)
- **Off-Topic Detected**: `False`
- **Vague/Missing Detected**: `False`
- **Confidence Score**: `0.95`
- **Extracted Entities**:

### Test Case 6: Skills
- **Raw Transcript**: `I haven't used cloud platforms extensively yet, mostly focused on local development.`
- **Detected Intent**: `direct_answer` (Expected: `direct_answer`)
- **Off-Topic Detected**: `False`
- **Vague/Missing Detected**: `False`
- **Confidence Score**: `0.95`
- **Extracted Entities**:

## Deliverables Achieved
1. **Answer Understanding Engine**: Fully implemented in `interview_ai/understanding_engine.py`.
2. **Intent Classifier**: Maps answers into actionable AI states (`direct_answer`, `clarification_needed`, `refusal_to_answer`, etc.).
3. **Structured Answer Format**: Encapsulates raw text, cleaned text, intent, flags, and extracted entities into a strongly-typed Pydantic model (`StructuredAnswer`).
