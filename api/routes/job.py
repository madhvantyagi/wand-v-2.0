"""
Job intelligence routes.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import asyncio

from ..db import get_db, User, Job, Company, Application, GapAnalysis
from ..schemas import JobPostingRequest, CompanyIntelRequest, JobResponse, JobListResponse
from ..deps import get_current_user
from engine.job import extract_company_intelligence
from engine.job.sources.posting import parse_job_posting

router = APIRouter()


@router.post("/posting", response_model=JobResponse)
async def parse_job_posting_endpoint(
    request: JobPostingRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Parse a job posting text.
    
    Extracts title, requirements, skills, etc.
    """
    # Run in thread pool to avoid blocking
    try:
        parsed_data = await asyncio.to_thread(parse_job_posting, request.job_text)
        
        if 'error' in parsed_data:
            raise HTTPException(status_code=500, detail=parsed_data['error'])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse job posting: {str(e)}")
    
    # Save to database
    job = Job(
        user_id=user.id,
        job_title=parsed_data.get('job_title') or request.job_title,
        company_name=parsed_data.get('company_name') or request.company_name,
        job_text=request.job_text,
        parsed_data=parsed_data
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    return job


@router.post("/company")
async def extract_company_intel(
    request: CompanyIntelRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Extract comprehensive company intelligence.
    
    Gathers data from job postings, company website, and news.
    """
    # Check cache
    result = await db.execute(
        select(Company).where(Company.name == request.company_name)
    )
    cached = result.scalar_one_or_none()
    
    if cached:
        return {
            "source": "cached",
            "company": request.company_name,
            "intelligence": cached.intelligence
        }
    
    # Extract fresh data
    try:
        intelligence = extract_company_intelligence(
            company_name=request.company_name,
            max_jobs=request.max_jobs,
            include_website=request.include_website,
            include_news=request.include_news
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract company intelligence: {str(e)}")
    
    # Cache the result
    company = Company(
        name=request.company_name,
        website=intelligence.get('website', {}).get('website_url', ''),
        intelligence=intelligence
    )
    db.add(company)
    await db.commit()
    
    return {
        "source": "fresh",
        "company": request.company_name,
        "intelligence": intelligence
    }


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a saved job by ID."""
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.user_id == user.id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job


@router.get("/", response_model=List[JobListResponse])
async def get_user_jobs(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all jobs for the current user with application status and match score."""
    # Get all jobs
    result = await db.execute(
        select(Job).where(Job.user_id == user.id).order_by(Job.created_at.desc())
    )
    jobs = result.scalars().all()
    
    # Get all applications for this user's jobs
    job_ids = [job.id for job in jobs]
    
    # Query applications
    app_result = await db.execute(
        select(Application).where(
            Application.user_id == user.id,
            Application.job_id.in_(job_ids) if job_ids else False
        )
    )
    applications = {app.job_id: app for app in app_result.scalars().all()}
    
    # Query gap analyses
    gap_result = await db.execute(
        select(GapAnalysis).where(
            GapAnalysis.user_id == user.id,
            GapAnalysis.job_id.in_(job_ids) if job_ids else False
        )
    )
    gap_analyses = {gap.job_id: gap.match_score for gap in gap_result.scalars().all()}
    
    # Build response with additional data
    job_list = []
    for job in jobs:
        app = applications.get(job.id)
        job_data = JobListResponse(
            id=job.id,
            user_id=job.user_id,
            job_title=job.job_title,
            company_name=job.company_name,
            parsed_data=job.parsed_data or {},
            created_at=job.created_at,
            application_status=app.status if app else None,
            application_notes=app.notes if app else None,
            match_score=gap_analyses.get(job.id)
        )
        job_list.append(job_data)
    
    return job_list


@router.delete("/{job_id}")
async def delete_job(
    job_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a job by ID."""
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.user_id == user.id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    await db.delete(job)
    await db.commit()
    
    return {"message": "Job deleted"}
