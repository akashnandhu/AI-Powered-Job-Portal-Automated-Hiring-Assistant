# Behavioral Indicators & Communication Quality Report

## Overview
This report demonstrates the capabilities of the `BehavioralAnalyzer` to detect hesitation, measure sentiment, assess confidence, and generate communication style indicators from candidate responses.

## Test Cases

### Test Case 1: Introduction (Confident)
- **Transcript**: `Hi, I'm Akash AA. I'm a Data Science student with experience in Python, machine learning, and building web applications using Django.`
- **Duration**: `12.0 seconds`
#### Sentiment Analysis
- **Label**: `Neutral`
- **Score**: `0.0`
- **Positive Words**: `0` | **Negative Words**: `0`
#### Confidence Analysis
- **Overall Confidence Score**: `1.0`
- **Hesitation Fillers Found**: `0`
- **Uncertain Phrases Found**: `0`
- **Contradictions Detected**: `False`
#### Behavioral Indicators
- **Word Count**: `21` words
- **Estimated Pace**: `105.0` WPM
- **Communication Style**: `Slow-paced, Confident`
#### Overall Assessment
> The candidate communicated with a neutral tone. They appeared highly confident with minimal hesitation. The speech pace was slow and deliberate.

### Test Case 2: Experience (Structured)
- **Transcript**: `I'm currently interning at Scope India, where I've built models using Linear Regression and Decision Trees.`
- **Duration**: `8.0 seconds`
#### Sentiment Analysis
- **Label**: `Neutral`
- **Score**: `0.0`
- **Positive Words**: `0` | **Negative Words**: `0`
#### Confidence Analysis
- **Overall Confidence Score**: `1.0`
- **Hesitation Fillers Found**: `0`
- **Uncertain Phrases Found**: `0`
- **Contradictions Detected**: `False`
#### Behavioral Indicators
- **Word Count**: `16` words
- **Estimated Pace**: `120.0` WPM
- **Communication Style**: `Confident`
#### Overall Assessment
> The candidate communicated with a neutral tone. They appeared highly confident with minimal hesitation.

### Test Case 3: Salary Expectations (Hesitant proxy example)
- **Transcript**: `Um, well, I guess I'm open to industry standard packages for entry-level data science roles.`
- **Duration**: `7.0 seconds`
#### Sentiment Analysis
- **Label**: `Neutral`
- **Score**: `0.0`
- **Positive Words**: `0` | **Negative Words**: `0`
#### Confidence Analysis
- **Overall Confidence Score**: `0.8`
- **Hesitation Fillers Found**: `2`
- **Uncertain Phrases Found**: `1`
- **Contradictions Detected**: `False`
#### Behavioral Indicators
- **Word Count**: `15` words
- **Estimated Pace**: `128.6` WPM
- **Communication Style**: `Confident`
#### Overall Assessment
> The candidate communicated with a neutral tone. They appeared highly confident with minimal hesitation.

### Test Case 4: Cloud Platforms (Uncertainty proxy example)
- **Transcript**: `I mean, I haven't used cloud platforms extensively yet, mostly focused on local development, I guess.`
- **Duration**: `9.0 seconds`
#### Sentiment Analysis
- **Label**: `Neutral`
- **Score**: `0.0`
- **Positive Words**: `0` | **Negative Words**: `0`
#### Confidence Analysis
- **Overall Confidence Score**: `0.9`
- **Hesitation Fillers Found**: `0`
- **Uncertain Phrases Found**: `1`
- **Contradictions Detected**: `False`
#### Behavioral Indicators
- **Word Count**: `16` words
- **Estimated Pace**: `106.7` WPM
- **Communication Style**: `Slow-paced, Confident`
#### Overall Assessment
> The candidate communicated with a neutral tone. They appeared highly confident with minimal hesitation. The speech pace was slow and deliberate.

### Test Case 5: Notice Period (Terse)
- **Transcript**: `I can start immediately.`
- **Duration**: `2.0 seconds`
#### Sentiment Analysis
- **Label**: `Neutral`
- **Score**: `0.0`
- **Positive Words**: `0` | **Negative Words**: `0`
#### Confidence Analysis
- **Overall Confidence Score**: `1.0`
- **Hesitation Fillers Found**: `0`
- **Uncertain Phrases Found**: `0`
- **Contradictions Detected**: `False`
#### Behavioral Indicators
- **Word Count**: `4` words
- **Estimated Pace**: `120.0` WPM
- **Communication Style**: `Terse, Confident`
#### Overall Assessment
> The candidate communicated with a neutral tone. They appeared highly confident with minimal hesitation.

---
## Deliverables Achieved
1. **Confidence analysis logic**: Implemented heuristics measuring hesitations, contradictions, and uncertainty.
2. **Sentiment scoring module**: Assesses the polarity (Positive, Negative, Neutral) of the candidate's word choice.
3. **Behavioral indicators report**: Encapsulates and structures all analyzed behavioral data for explainability.
