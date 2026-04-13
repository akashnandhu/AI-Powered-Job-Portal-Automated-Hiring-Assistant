from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ResumeBase(BaseModel):
    resume_id: str

class ParsedResumeResponse(ResumeBase):
    skills: List[str] = []
    experience: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []

class MatchRequest(ResumeBase):
    jd_id: str

class SimilarityScores(BaseModel):
    skills: float
    experience: float
    projects: float

class ScoringResponse(ResumeBase):
    jd_id: str
    similarity_scores: SimilarityScores
    final_score: float
    decision: str

class ErrorDetail(BaseModel):
    code: str
    message: str

class ErrorResponse(BaseModel):
    error: ErrorDetail

class UploadResponse(BaseModel):
    job_id: str
    message: str
    status_url: str
