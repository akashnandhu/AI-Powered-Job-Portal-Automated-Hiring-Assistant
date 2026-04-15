import time
import uuid

# In-memory store for simulating DB
JOB_STORE = {}

def process_resume_pipeline(job_id: str, filename: str, jd_id: str = None):
    # This is an asynchronous background task
    JOB_STORE[job_id] = {"status": "PROCESSING", "filename": filename}
    
    # 1. Parse Simulation
    time.sleep(2)
    resume_id = f"res_{uuid.uuid4().hex[:8]}"
    JOB_STORE[job_id]["status"] = "EXTRACTING"
    
    # 2. Extract Simulation
    time.sleep(2)
    parsed_data = {
        "skills": [
          "CSS", "Data Analysis", "Django", "HTML", "JavaScript", 
          "Machine Learning", "Matplotlib", "NumPy", "Pandas", "Power BI"
        ],
        "experience_years": 0,
        "education": [
          "Bachelor"
        ]
    }
    JOB_STORE[job_id]["parsed_data"] = parsed_data
    
    if jd_id:
        JOB_STORE[job_id]["status"] = "MATCHING"
        # 3. Match Simulation
        time.sleep(2)
        
        JOB_STORE[job_id]["status"] = "SCORING"
        # 4. Score Simulation
        time.sleep(2)
    
    scoring = {
        "skills": 0.99,
        "experience": 0,
        "education": 0.5
    }
    
    # Calculate mock final score (weighted average)
    final_score = (scoring["skills"] * 100 * 0.6) + (scoring["experience"] * 100 * 0.25) + (scoring["education"] * 100 * 0.15)
    
    from ranking.threshold_config import get_category
    category = get_category(final_score)
    
    JOB_STORE[job_id]["similarity_scores"] = scoring
    JOB_STORE[job_id]["shortlisting_status"] = category
    JOB_STORE[job_id]["jd_id"] = jd_id
        
    JOB_STORE[job_id]["resume_id"] = filename
    from datetime import datetime
    JOB_STORE[job_id]["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    JOB_STORE[job_id]["target_role"] = "Data Analyst"
    JOB_STORE[job_id]["status"] = "COMPLETED"
