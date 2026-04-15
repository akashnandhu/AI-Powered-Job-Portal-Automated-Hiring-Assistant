from fastapi import APIRouter, HTTPException
from ..services.background import JOB_STORE

router = APIRouter()

@router.get("/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in JOB_STORE:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "NOT_FOUND", "message": "Job ID not found"}}
        )
    return {
        "job_id": job_id,
        "status": JOB_STORE[job_id]["status"]
    }

@router.get("/results/{job_id}")
async def get_results(job_id: str):
    if job_id not in JOB_STORE:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "NOT_FOUND", "message": "Job ID not found"}}
        )
    
    job_data = JOB_STORE[job_id]
    if job_data["status"] != "COMPLETED":
        return {
            "job_id": job_id,
            "status": job_data["status"],
            "message": "Results not ready yet."
        }
        
    return {
        "job_id": job_id,
        "status": "COMPLETED",
        "timestamp": job_data.get("timestamp", ""),
        "resume_id": job_data.get("resume_id", "Unknown"),
        "target_role": job_data.get("target_role", "Unknown"),
        "parsed_data": job_data.get("parsed_data", {}),
        "similarity_scores": job_data.get("similarity_scores", {}),
        "shortlisting_status": job_data.get("shortlisting_status", "Unknown")
    }
