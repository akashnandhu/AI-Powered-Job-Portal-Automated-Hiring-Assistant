# Technical Interview AI Blueprint & Architectural Specification

This blueprint defines the architecture, data models, and adaptive decision engines for the **Technical Interview AI System**. This module is designed to conduct role-based, tenure-adapted, and skill-specific technical evaluations of software engineering and operations candidates.

---

## 1. Modular Architecture Overview

The Technical Interview AI operates as a feedback-driven pipeline, extending the standard call flow with technical parsers, coding-concepts analyzers, and dynamic difficulty routers:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Candidate Audio/Text Input                        │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AnswerUnderstandingEngine                          │
│  ├─ Keyword Extraction (e.g., "Kafka", "indexes", "Singleton")             │
│  ├─ Conceptual Completeness Scoring                                         │
│  └─ Semantic Intent & Accuracy Auditing                                     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Adaptive Difficulty Controller                      │
│  ├─ Dynamic Difficulty Scaling (+1 / 0 / -1 Level Adjustment)               │
│  ├─ Core Skill State Matrix (Tracks pass/fail per technical node)            │
│  └─ Experience Routing (0-2 Yrs Basics, 3-5 Yrs Intermediate, 5+ Yrs Design) │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Role-Based Question Generator                        │
│  ├─ Maps candidate role (e.g., DevOps) to Domain (e.g., Kubernetes, CI/CD)  │
│  ├─ Queries hierarchically (Junior Basics -> Mid Concept -> Senior Scenario)│
│  └─ Asks next adaptive technical question                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Technical Interview Structure

A technical session is divided into four distinct phases to evaluate the candidate's journey from execution to high-level system reasoning:

### Phase 1: Greeting & Context Warmup (5% of duration)
*   **Objective**: Confirm environment stability, establish communication, and perform a lightweight review of self-declared experience.
*   **Format**: Light resume-verifying question. No heavy technical assessment.

### Phase 2: Experience-Based Technical Review (25% of duration)
*   **Objective**: Audit the candidate's understanding of projects they have previously delivered, validating actual hands-on involvement.
*   **Format**: Behavioral-technical questions focused on tools or libraries declared in the candidate's ATS resume (e.g., *"In your bus management project, why did you decide to implement SQLite over MongoDB?"*).

### Phase 3: Conceptual Tech Deep-Dive (30% of duration)
*   **Objective**: Evaluate raw computer science fundamentals, runtime engines, memory layouts, syntax features, and framework behaviors.
*   **Format**: Topic-focused questions with progressive depth (e.g., MERN concurrency, JVM garbage collection, Git branching mechanics).

### Phase 4: Scenario-Based System Design (40% of duration)
*   **Objective**: Evaluate real-world problem-solving, architectural reasoning, scale optimization, failure handling, and operational security.
*   **Format**: High-level problem statements (e.g., designing a distributed notification system, handling database replication lag, setting up self-healing Kubernetes clusters).

---

## 3. Experience-Based Routing Logic

The engine initializes the baseline difficulty and routing tracks based on the candidate's years of experience:

### A. Junior Tier (0–2 Years Experience) -> Focus: Basics & Implementation
*   **Skill Goal**: Verify that the candidate can write correct, standard, clean syntax, use standard library features, understand relational databases, and operate Git and fundamental web concepts.
*   **Baseline Difficulty**: **Level 1 (Entry)** to **Level 2 (Junior)**.
*   **Core Concepts**: Basic data structures, HTTP methods (GET/POST/PUT/DELETE), SQL joins, basic loops, CSS layouts, OOP principles (encapsulation, inheritance).

### B. Mid-Level Tier (3–5 Years Experience) -> Focus: Intermediate Concepts & Optimization
*   **Skill Goal**: Evaluate intermediate patterns, database index optimization, REST API designs, caching, security middleware, asynchronous processing, and test-driven development.
*   **Baseline Difficulty**: **Level 3 (Mid)**.
*   **Core Concepts**: Design patterns (Factory, Strategy, Observer), database indexing and normalization, JWT/OAuth authentication, concurrency/multithreading, unit/integration testing, Redis/caching basics, Docker containerization.

### C. Senior Tier (5+ Years Experience) -> Focus: Advanced & System Design
*   **Skill Goal**: Assess full system architecture, distributed consistency (CAP theorem), horizontal scaling, messaging brokers, high availability, failover strategies, and pipeline orchestration.
*   **Baseline Difficulty**: **Level 4 (Senior)** to **Level 5 (Principal/Architect)**.
*   **Core Concepts**: Microservices communication (gRPC, Event-driven), message queues (Kafka, RabbitMQ), load balancing, sharding/replication, CI/CD automation, cloud-native deployments, disaster recovery, system performance optimization.

---

## 4. Role-to-Skill Domain Mapping Matrix

The system dynamically loads skill-domain questions based on the candidate's role type.

| Target Role | Primary Domain | Core Conceptual Area | Tool / Framework Stack | Scenario Challenge Profile |
| :--- | :--- | :--- | :--- | :--- |
| **MERN Stack Developer** | Frontend & NodeJS Backend | Event loop, asynchronous execution, virtual DOM, API integrations, state management. | React, Node.js, Express, MongoDB, Redux. | Design an real-time collaborative document editor or chat dashboard with high concurrent connections. |
| **Java Backend Engineer** | Enterprise Backend | JVM memory management, garbage collection, multithreading, relational transactions, JPA. | Java, Spring Boot, Hibernate, PostgreSQL, JUnit. | Design a high-throughput financial ledger processing system with strict consistency requirements. |
| **DevOps Engineer** | Cloud & Operations | Container orchestration, CI/CD pipelining, Infrastructure as Code, monitoring. | Docker, Kubernetes, Terraform, Jenkins/GitHub Actions, Prometheus. | Troubleshoot and redesign a rolling-update deployment that is causing database locks and service drops. |
| **Data Scientist** | Analytics & ML | Linear algebra, statistical inference, feature engineering, model training, ML pipelines. | Python, Pandas, NumPy, Scikit-Learn, TensorFlow, PyTorch. | Design an end-to-end real-time recommendation model pipeline handling millions of catalog items. |

---

## 5. Dynamic Difficulty Progression Heuristics

Rather than keeping difficulty static, the AI dynamically adapts the complexity of the questions based on real-time grading of candidate answers:

```text
       [Candidate response graded]
                  │
                  ├─── Score >= 85% (Exceptional/Highly Detailed)
                  │    └─► Action: Increment Difficulty Level (+1)
                  │
                  ├─── Score 55% - 84% (Adequate/Correct)
                  │    └─► Action: Keep Level Stable (Ask Peer Question)
                  │
                  └─── Score < 55% (Struggling/Vague)
                       └─► Action: Decrement Difficulty Level (-1)
                           └─► If consecutive failures == 2:
                               └─► Action: Lock Level, Pivot to Next Skill Category
```

### Heuristic Adjustment Formula:

$$\text{Difficulty}_{n+1} = \text{Clamp}\left(\text{Difficulty}_{n} + \Delta, \; \text{MinDifficulty}, \; \text{MaxDifficulty}\right)$$

*   Where $\Delta$ is determined by NLU response score:
    *   $\Delta = +1$ if $\text{Score} \geq 0.85$ (Prompts next question at higher complexity tier).
    *   $\Delta = 0$ if $0.55 \leq \text{Score} < 0.85$ (Prompts peer question at the same difficulty tier).
    *   $\Delta = -1$ if $\text{Score} < 0.55$ (Prompts a simpler fallback question to test fundamental understanding).
*   **Max Limit Constraint**: The system clamps the difficulty rating between Level 1 (lowest) and Level 5 (highest).
