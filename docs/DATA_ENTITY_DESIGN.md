# Hiring Intelligence System: Data Entity Design

This document outlines the architecture, entities, and structural relationships involved in parsing and matching Candidate Profiles (Resumes) and Job Profiles (Job Descriptions) for our AI-driven Hiring Intelligence System. 

## 1. Core Data Entities

The system revolves around four primary standard objects used uniformly across modules (Parsing, Screening, AI Evaluation, and Scoring):

### A) Candidate Profile Entity
Represents the unified structure extracted from unstructured resume data (e.g., PDFs).
- **Identifier**: `candidate_id` 
- **Sub-Objects**: Contains lists of `ExperienceObject`, `SkillObject`, Education Records, and Certifications.
- **Why useful?**: Standardizes varied real-world resume layouts into a rigid structure. By mapping unstructured attributes (like "Worked as dev for 3 yrs") into measurable attributes (`duration_months`), the AI can deterministically filter and rank resumes.

### B) Job Profile Entity
Represents the structural breakdown of a Job Description.
- **Identifier**: `job_id`
- **Sub-Objects**: Contains scalar requirements like minimum education, structured arrays of `SkillObject` (with a distinction between "mandatory" and "nice-to-have"), and experience expectations.
- **Why useful?**: It creates an exact mathematical counterpart to the `Candidate Profile`. Parsing a JD into rigid nodes allows the Screening AI to convert the job requirement into a deterministic query or vector mapping constraint.

### C) Skill Object Entity
A normalized representation of a single professional skill.
- **Properties**: `name` (e.g., Python), `category` (technical/soft), `proficiency` (beginner to expert), and `years_of_experience`.
- **Why useful?**: Skills in resumes or JDs are often described conversationally ("Experienced in Python"). Converting them to standalone entities ensures the system can use graph relationships, ontologies, and direct intersections. The system compares the candidate's `SkillObject` precisely against the JD's `SkillObject`.

### D) Experience Object Entity
The atomic unit representing an employment stint.
- **Properties**: `job_title`, `company`, `duration_months`, `description`, and a list of quantifiable `achievements`.
- **Why useful?**: AI scoring requires measuring the actual time spent doing a specific role. Extrapolating `start_date` and `end_date` into `duration_months` allows numerical matching against a Job Profile's `min_years`. The `achievements` array enables NLP models to rank the qualitative impact of a candidate independent of simply counting the timeline.

## 2. Entity Relationships & System Flow

1. **Extraction Pipeline (parsers/)**: The ATS engine processes PDFs, running layout-aware parsers. Output is validated against `CandidateProfile` JSON Schema.
2. **Standardization (data/)**: NLP models normalize attributes. For example, "Py" or "Python3" resolves to `SkillObject: {"name": "Python"}` based on a core ontology.
3. **Screening AI (screening_ai/)**: The Candidate entity is placed parallel to the Job Profile entity over our matching engine.
   - **Intersection mapping**: Candidate's `skills[]` against JD's `required_skills[]`.
   - **Validation checks**: The sum of `duration_months` in relevant `ExperienceObjects` against JD's `experience_requirements.min_years`.
4. **Scoring Engine (scoring/)**: ML algorithms ingest this highly relational data to construct a robust score (e.g., "Fit Index: 87%").

## 3. Benefits of this Data Structure

- **Interoperability**: Strict JSON schemas ensure that parsing modules, scoring engines, and UI dashboards send heavily-typed payloads to one another without failure.
- **Scalability**: Subdividing experience and skills into arrays allows for nested Elasticsearch queries or vectorized embedding without breaking the standard shape.
- **Explainable AI**: Because the system breaks evaluations into `SkillObjects` and `ExperienceObjects`, it's easy to explain to an end-user exactly *why* a candidate received a 90% match. (e.g., "Matched 4/5 mandatory skills").
