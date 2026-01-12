"""
Pydantic schemas for API request/response models.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# USER SCHEMAS
# ============================================================================

class UserCreate(BaseModel):
    email: str
    name: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# PROFILE SCHEMAS
# ============================================================================

class ProfileCreate(BaseModel):
    source_type: str  # 'resume', 'linkedin', 'portfolio'
    file_name: Optional[str] = None


class ProfileResponse(BaseModel):
    id: str
    user_id: str
    source_type: str
    file_name: Optional[str]
    parsed_data: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# JOB SCHEMAS
# ============================================================================

class JobPostingRequest(BaseModel):
    job_text: str
    job_title: Optional[str] = None
    company_name: Optional[str] = None


class CompanyIntelRequest(BaseModel):
    company_name: str
    max_jobs: int = 50
    include_website: bool = True
    include_news: bool = True


class JobResponse(BaseModel):
    id: str
    user_id: str
    job_title: Optional[str]
    company_name: Optional[str]
    parsed_data: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# MATCH SCHEMAS
# ============================================================================

class GapAnalysisHistoryItem(BaseModel):
    id: str
    match_score: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ResumeOptimizationRequest(BaseModel):
    resume_id: str
    job_id: str


class GapAnalysisRequest(BaseModel):
    profile_ids: List[str]
    job_id: str


class GapAnalysisResponse(BaseModel):
    id: str
    job_id: str
    match_score: int
    analysis_data: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


class CoverLetterRequest(BaseModel):
    profile_ids: List[str]
    job_id: str
    style: str = "professional"  # professional, enthusiastic, concise


class CoverLetterResponse(BaseModel):
    id: str
    job_id: str
    style: str
    letter: str
    letter_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# DISCREPANCY SCHEMAS
# ============================================================================

class DiscrepancyRequest(BaseModel):
    profile_ids: List[str]  # 2-3 profile IDs to compare


class DiscrepancyResponse(BaseModel):
    consistency_score: int
    discrepancies: List[Dict[str, Any]]
    skill_comparison: List[Dict[str, Any]]
    missing_in_resume: List[str]
    missing_online: List[str]
    recommendations: List[str]
    table_data: Optional[Dict[str, Any]] = None


class DiscrepancyHistoryItem(BaseModel):
    id: str
    consistency_score: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class DiscrepancyReportResponse(BaseModel):
    id: str
    profile_ids: List[str]
    consistency_score: int
    report_data: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============================================================================
# APPLICATION SCHEMAS
# ============================================================================

class ApplicationCreate(BaseModel):
    job_id: str
    cover_letter_id: Optional[str] = None
    status: str = "saved"
    notes: Optional[str] = None


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    applied_at: Optional[datetime] = None


class ApplicationResponse(BaseModel):
    id: str
    user_id: str
    job_id: str
    cover_letter_id: Optional[str]
    status: str
    notes: Optional[str]
    applied_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True
