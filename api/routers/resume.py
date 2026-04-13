import uuid
import time
from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Form, HTTPException
from ..schemas.common import ParsedResumeResponse, MatchRequest, ScoringResponse, UploadResponse
from ..services.background import process_resume_pipeline

router = APIRouter()

@router.post("/upload-resume", response_model=UploadResponse, status_code=202)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    jd_id: str = Form(None)
):
    if not file.filename.endswith(('.pdf', '.docx')):
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "INVALID_FILE", "message": "Unsupported file format"}}
        )
    
    job_id = f"job_{uuid.uuid4().hex[:8]}"
    
    # Save file temporarily here in real logic, then pass path to background task
    # For now, simulate background task
    background_tasks.add_task(process_resume_pipeline, job_id, file.filename, jd_id)
    
    return {
        "job_id": job_id,
        "message": "Resume uploaded successfully. Processing started.",
        "status_url": f"/status/{job_id}"
    }

@router.post("/parse-resume", response_model=ParsedResumeResponse)
async def parse_resume(request: MatchRequest):
    # Synchronous parse
    return ParsedResumeResponse(
        resume_id=request.resume_id,
        skills=["Python", "FastAPI"],
        experience=[],
        education=[]
    )

@router.post("/match-jd")
async def match_jd(request: MatchRequest):
    return {
        "resume_id": request.resume_id,
        "jd_id": request.jd_id,
        "match_status": "COMPLETED"
    }

@router.post("/score", response_model=ScoringResponse)
async def score_candidate(request: MatchRequest):
    return ScoringResponse(
        resume_id=request.resume_id,
        jd_id=request.jd_id,
        similarity_scores={"skills": 0.8, "experience": 0.7, "projects": 0.9},
        final_score=0.8,
        decision="SHORTLISTED"
    )
