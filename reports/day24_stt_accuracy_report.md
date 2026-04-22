# STT Accuracy & Normalization Test Report

## Overview
This report evaluates the accuracy of the STT normalization pipeline across various simulated conditions including different accents, noise levels, and speech patterns (filler words, interrupted speech, partial answers).

## Test Results

### Test Case 1: Standard American Accent, Clean Audio
- **Notes**: Testing basic filler word removal.
- **Raw STT Output**: `Uh, I have five years of experience in Python.`
- **Expected Normalization**: `I have five years of experience in Python.`
- **Actual Normalization**: `I have five years of experience in Python.`
- **Word Error Rate (WER vs Expected)**: `0.00%`

### Test Case 2: Heavy Accent, Background Noise
- **Notes**: Testing filler words + interrupted speech.
- **Raw STT Output**: `Yes um, I worked there for like, two years but then I-`
- **Expected Normalization**: `Yes I worked there for two years but then I...`
- **Actual Normalization**: `Yes I worked there for two years but then I...`
- **Word Error Rate (WER vs Expected)**: `0.00%`

### Test Case 3: Interrupted Speech
- **Notes**: Testing 'you know' removal and trailing dash replacement.
- **Raw STT Output**: `I think the best approach is to, you know, use a microservice architecture and-`
- **Expected Normalization**: `I think the best approach is to use a microservice architecture and...`
- **Actual Normalization**: `I think the best approach is to use a microservice architecture and...`
- **Word Error Rate (WER vs Expected)**: `0.00%`

### Test Case 4: Partial Answer with Silence
- **Notes**: Testing partial answers with hanging 'well,'.
- **Raw STT Output**: `My biggest strength is um... problem solving. And my weakness is, well,`
- **Expected Normalization**: `My biggest strength is... Problem solving. And my weakness is, well...`
- **Actual Normalization**: `My biggest strength is... Problem solving. And my weakness is, well...`
- **Word Error Rate (WER vs Expected)**: `0.00%`

### Test Case 5: Case Normalization and Punctuation
- **Notes**: Testing case adjustment and weird space/punctuation fixes.
- **Raw STT Output**: `i love coding . it is , like , my passion`
- **Expected Normalization**: `I love coding. It is my passion.`
- **Actual Normalization**: `I love coding. It is my passion.`
- **Word Error Rate (WER vs Expected)**: `0.00%`

## Silence Detection Mock Test
We also simulate an STT output with segment timestamps to detect silence gaps.

### Segments Detected
- [0.0s - 2.5s]: `Uh, I have five years of experience in Python.`
- [5.0s - 7.0s]: `And, like, I also know...`
- [8.0s - 9.5s]: `um, React but-`

### Silences Detected (>2.0s)
- Silence from 2.5s to 5.0s (Duration: 2.5s)

## Conclusion
- **Average Word Error Rate (vs Expected text)**: `0.00%`
- The transcript normalization module successfully cleans up filler words, corrects punctuation, handles partial answers, and normalizes cases.
- Silence detection is managed via STT chunking. Interrupted speech is properly formatted with ellipses.
