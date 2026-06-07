# Zecpath AI - Automated Hiring Assistant

An end-to-end AI-powered hiring pipeline designed to automate candidate ingestion, ATS matching, interview evaluation, and unbiased shortlisting. 

Built as a highly scalable Python backend, this system strips away the friction of manual screening and replaces it with an objective, data-driven *Cross-Round Aggregation Engine*.

## 🚀 Key Features
- **Intelligent Ingestion:** Modular parsing engine (PyMuPDF & pdfplumber) to extract and clean unstructured text from messy Resume PDFs and DOCXs.
- **Dynamic Skill Extraction:** Uses NLP techniques to normalize text, standardize headings, and classify candidates into structured JSON schemas.
- **ATS Matching Capability:** Algorithmically compares extracted profiles against active Job Descriptions to generate a baseline strength score.
- **Cross-Round AI Engine:** Simulates Screening, HR, and Technical interviews, assigning discrete scores for behavioral and technical competencies.
- **Bias Mitigation (Smoothing Algorithm):** Dynamically penalizes candidates with high score variance across rounds to prevent "paper tigers" from passing technical evaluations.
- **Unbiased Output:** Outputs a final decision (`Selected`, `Hold / Review`, `Rejected`) with full text-based explainability and confidence metrics.

## 📂 Repository Structure

```text
zecpath_ai/
├── ats_engine/           # Core ATS scoring and heuristic matching algorithm
├── data/                 # Local data storage for PDFs, processed TXTs, and system logs
├── docs/                 # Internal architecture documentation
├── parsers/              # Multi-format parsing scripts (PDF, DOCX) and ingestion modules
├── reports/              # Generation endpoints for Shortlisting JSON and txt reports
├── scoring/              # The mathematical core: DecisionEngine and CrossRoundEngine
├── screening_ai/         # Simulation modules for screening and behavioral interviews
├── tests/                # PyTest suite guaranteeing parser robustness and edge-case handling
├── utils/                # Text cleaners, logging configuration, and file handlers
├── main.py               # Core utility tests
└── run_batch_pipeline.py # End-to-End Execution Script
```

## ⚙️ Setup & Installation

1. **Clone the Repository** (or extract the package).
2. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   # Execute on Windows:
   .\venv\Scripts\activate
   # Execute on Unix/MacOS:
   source venv/bin/activate
   ```
3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🧪 Usage & Execution

**1. Running the Automated Pipeline:**
Ensure raw resumes are located in `/data/resumes/` as `.pdf` files.
Execute the batch processor to watch the AI ingest, score, and rank candidates live.
```bash
python run_batch_pipeline.py
```
> Outputs will automatically generate in the `/outputs/` directory as structured JSON and TXT reports.

**2. Running the Test Suite:**
Ensure your parser logic and edge cases are protected using the standard testing framework.
```bash
pytest tests/ -v
```

## 🔐 Observability & Auditing
All system commands execute logs into `data/logs/` and explicitly track ML latency, throughput, and risk anomalies. The Decision Engine logs every `Decision` and its underlying `reasoning` securely to ensure HR Compliance audibility.
