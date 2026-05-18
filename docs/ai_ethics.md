# AI Ethics Documentation

## 1. Consent Requirements
- **Explicit Consent**: All candidates must provide explicit, informed consent before their data (resumes, interview transcripts, etc.) is processed by the AI system.
- **Transparency**: Candidates must be informed about what data is collected, how it is used to score them, and the role of AI in the decision-making process.
- **Opt-out Options**: Candidates must be provided with a clear option to opt out of automated AI screening and request a human review.

## 2. Explainability
- **Scoring Transparency**: Explainability notes are generated for every candidate score to clarify the AI's reasoning, indicating which skills, experience, or education factors contributed to the final score.
- **Accessibility**: These notes should be made accessible to HR reviewers and optionally to the candidates to ensure transparent decision-making.

## 3. Mitigating Bias
- **Demographic Signal Removal**: The AI pipeline incorporates a data normalization step that masks sensitive demographic signals such as gender pronouns, age, marital status, religion, and other potentially biasing information from unstructured text.
- **Experience Capping**: To prevent implicit age bias, the scoring engine limits the advantage of excessive years of experience, ensuring a level playing field for candidates of varying age groups.
