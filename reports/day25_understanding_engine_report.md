# Answer Intent & Understanding Engine Test Report

## Overview
This report demonstrates the capabilities of the Answer Understanding Engine to classify candidate intent, detect off-topic or vague answers, and extract structured semantic entities from unstructured interview transcripts.

## Test Cases

### Test Case 1: Experience & Skills
- **Raw Transcript**: `Uh, yeah, I have 5.5 years of experience working with Python and AWS.`
- **Detected Intent**: `direct_answer` (Expected: `direct_answer`)
- **Off-Topic Detected**: `False`
- **Vague/Missing Detected**: `False`
- **Confidence Score**: `0.95`
- **Extracted Entities**:
  - **Skills**: `['Python', 'AWS']`
  - **Experience Years**: `5.5`

### Test Case 2: Salary
- **Raw Transcript**: `My salary expectation is around $120K.`
- **Detected Intent**: `direct_answer` (Expected: `direct_answer`)
- **Off-Topic Detected**: `False`
- **Vague/Missing Detected**: `False`
- **Confidence Score**: `0.95`
- **Extracted Entities**:
  - **Salary Expectation**: `$120K`

### Test Case 3: Availability
- **Raw Transcript**: `I can join immediately, or within 2 weeks notice if needed.`
- **Detected Intent**: `direct_answer` (Expected: `direct_answer`)
- **Off-Topic Detected**: `False`
- **Vague/Missing Detected**: `False`
- **Confidence Score**: `0.95`
- **Extracted Entities**:
  - **Availability**: `immediately`

### Test Case 4: General
- **Raw Transcript**: `I don't know, maybe some stuff about that.`
- **Detected Intent**: `refusal_to_answer` (Expected: `refusal_to_answer`)
- **Off-Topic Detected**: `False`
- **Vague/Missing Detected**: `True`
- **Confidence Score**: `0.45`
- **Extracted Entities**:

### Test Case 5: General
- **Raw Transcript**: `What do you mean by that?`
- **Detected Intent**: `clarification_needed` (Expected: `clarification_needed`)
- **Off-Topic Detected**: `False`
- **Vague/Missing Detected**: `False`
- **Confidence Score**: `0.75`
- **Extracted Entities**:

### Test Case 6: General
- **Raw Transcript**: `The weather is really nice today, I love baseball.`
- **Detected Intent**: `off_topic` (Expected: `off_topic`)
- **Off-Topic Detected**: `True`
- **Vague/Missing Detected**: `False`
- **Confidence Score**: `0.45`
- **Extracted Entities**:

### Test Case 7: General
- **Raw Transcript**: `Yes.`
- **Detected Intent**: `partial_answer` (Expected: `partial_answer`)
- **Off-Topic Detected**: `False`
- **Vague/Missing Detected**: `False`
- **Confidence Score**: `0.6`
- **Extracted Entities**:

## Deliverables Achieved
1. **Answer Understanding Engine**: Fully implemented in `interview_ai/understanding_engine.py`.
2. **Intent Classifier**: Maps answers into actionable AI states (`direct_answer`, `clarification_needed`, `refusal_to_answer`, etc.).
3. **Structured Answer Format**: Encapsulates raw text, cleaned text, intent, flags, and extracted entities into a strongly-typed Pydantic model (`StructuredAnswer`).
