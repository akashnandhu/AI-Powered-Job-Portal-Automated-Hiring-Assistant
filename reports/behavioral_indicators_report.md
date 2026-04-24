# Behavioral Indicators & Communication Quality Report

## Overview
This report demonstrates the capabilities of the `BehavioralAnalyzer` to detect hesitation, measure sentiment, assess confidence, and generate communication style indicators from candidate responses.

## Test Cases

### Test Case 1: Confident, positive, and structured
- **Transcript**: `I am very excited to achieve great success in this innovative role. I always lead with passion and clear goals.`
- **Duration**: `10.0 seconds`
#### Sentiment Analysis
- **Label**: `Positive`
- **Score**: `1.0`
- **Positive Words**: `7` | **Negative Words**: `0`
#### Confidence Analysis
- **Overall Confidence Score**: `1.0`
- **Hesitation Fillers Found**: `0`
- **Uncertain Phrases Found**: `0`
- **Contradictions Detected**: `False`
#### Behavioral Indicators
- **Word Count**: `20` words
- **Estimated Pace**: `120.0` WPM
- **Communication Style**: `Confident`
#### Overall Assessment
> The candidate communicated with a positive tone. They appeared highly confident with minimal hesitation.

### Test Case 2: Hesitant with multiple fillers
- **Transcript**: `Um, well, I guess I could, like, you know, try to manage the project. It's kinda hard to say.`
- **Duration**: `15.0 seconds`
#### Sentiment Analysis
- **Label**: `Negative`
- **Score**: `-1.0`
- **Positive Words**: `0` | **Negative Words**: `1`
#### Confidence Analysis
- **Overall Confidence Score**: `0.65`
- **Hesitation Fillers Found**: `5`
- **Uncertain Phrases Found**: `1`
- **Contradictions Detected**: `False`
#### Behavioral Indicators
- **Word Count**: `19` words
- **Estimated Pace**: `76.0` WPM
- **Communication Style**: `Slow-paced, Hesitant`
#### Overall Assessment
> The candidate communicated with a negative tone. Confidence was moderate, with some filler usage. The speech pace was slow and deliberate.

### Test Case 3: Uncertain with potential contradictions
- **Transcript**: `I mean, yes, I have used it, but no, not really. Maybe I could be good at it, I guess.`
- **Duration**: `12.0 seconds`
#### Sentiment Analysis
- **Label**: `Positive`
- **Score**: `1.0`
- **Positive Words**: `1` | **Negative Words**: `0`
#### Confidence Analysis
- **Overall Confidence Score**: `0.5`
- **Hesitation Fillers Found**: `0`
- **Uncertain Phrases Found**: `3`
- **Contradictions Detected**: `True`
#### Behavioral Indicators
- **Word Count**: `20` words
- **Estimated Pace**: `100.0` WPM
- **Communication Style**: `Slow-paced`
#### Overall Assessment
> The candidate communicated with a positive tone. Confidence was moderate, with some filler usage. The speech pace was slow and deliberate.

### Test Case 4: Negative sentiment and fast-paced
- **Transcript**: `Unfortunately that was a terrible fail. It was the worst struggle and very difficult.`
- **Duration**: `3.0 seconds`
#### Sentiment Analysis
- **Label**: `Negative`
- **Score**: `-1.0`
- **Positive Words**: `0` | **Negative Words**: `6`
#### Confidence Analysis
- **Overall Confidence Score**: `1.0`
- **Hesitation Fillers Found**: `0`
- **Uncertain Phrases Found**: `0`
- **Contradictions Detected**: `False`
#### Behavioral Indicators
- **Word Count**: `14` words
- **Estimated Pace**: `280.0` WPM
- **Communication Style**: `Fast-paced, Confident`
#### Overall Assessment
> The candidate communicated with a negative tone. They appeared highly confident with minimal hesitation. The speech pace was faster than average.

### Test Case 5: Terse response
- **Transcript**: `I think so. Yes.`
- **Duration**: `2.0 seconds`
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
