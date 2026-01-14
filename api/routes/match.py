"""
Matching routes (gap analysis and cover letter).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import asyncio

from ..db import get_db, User, Profile, Job, GapAnalysis, CoverLetter
from ..schemas import (
    GapAnalysisRequest, GapAnalysisResponse, GapAnalysisHistoryItem,
    CoverLetterRequest, CoverLetterResponse, ResumeOptimizationRequest
)
from ..deps import get_current_user
from engine.matcher import analyze_gaps, analyze_match, generate_cover_letter, combine_profiles, optimize_resume
from engine.job import extract_full_job_context

router = APIRouter()


# ... existing code ...

@router.post("/resume-optimize")
async def optimize_resume_endpoint(
    request: ResumeOptimizationRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate resume optimizations strictly using RESUME data.
    Ignores LinkedIn/Portfolio profiles even if provided.
    """
    # 1. Fetch ONLY the Resume profile
    result = await db.execute(
        select(Profile).where(
            Profile.user_id == user.id,
            Profile.source_type == 'resume',
            Profile.id == request.resume_id
        )
    )
    resume_profile = result.scalar_one_or_none()
    
    if not resume_profile:
        raise HTTPException(status_code=404, detail="No resume found. Please upload a PDF resume first.")
        
    # 2. Get Job
    result = await db.execute(
        select(Job).where(Job.id == request.job_id, Job.user_id == user.id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # 3. Check for existing optimization
    # Import ResumeOptimization inside function or at top if available (Assuming imported from ..db)
    from ..db import ResumeOptimization
    
    print(f"🔍 DEBUG: Checking cache for Job {job.id} and Resume {resume_profile.id}")
    result = await db.execute(
        select(ResumeOptimization).where(
            ResumeOptimization.job_id == job.id,
            ResumeOptimization.resume_id == resume_profile.id
        ).order_by(ResumeOptimization.created_at.desc())
    )
    existing_opt = result.scalars().first()
    
    if existing_opt:
        print("✅ DEBUG: Found cached resume optimization!")
        return existing_opt.optimization_data
    
    print("❌ DEBUG: Cache miss - running optimization...")
        
    # 4. Optimize (if not found) - run in thread pool to avoid blocking
    try:
        opt_result = await asyncio.to_thread(
            optimize_resume,
            resume_data=resume_profile.parsed_data,
            job_context={
                "job_posting": job.parsed_data,
                "company_intel": {} 
            }
        )
        
        if 'error' in opt_result:
            raise HTTPException(status_code=500, detail=opt_result['error'])
            
        # 5. Save to DB
        new_opt = ResumeOptimization(
            user_id=user.id,
            job_id=job.id,
            resume_id=resume_profile.id,
            optimization_data=opt_result
        )
        db.add(new_opt)
        await db.commit()
        await db.refresh(new_opt)
        
        return opt_result
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume optimization failed: {str(e)}")


async def get_profiles_data(profile_ids: List[str], user_id: str, db: AsyncSession) -> dict:
    """Fetch and organize profiles by source type."""
    profiles = {}
    
    for pid in profile_ids:
        result = await db.execute(
            select(Profile).where(Profile.id == pid, Profile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        
        if profile:
            profiles[profile.source_type] = profile.parsed_data
    
    return profiles


async def get_combined_profile(profile_ids: List[str], user_id: str, db: AsyncSession) -> dict:
    """Fetch and combine all profiles into single JSON."""
    profiles = await get_profiles_data(profile_ids, user_id, db)
    return combine_profiles(
        resume=profiles.get('resume'),
        linkedin=profiles.get('linkedin'),
        portfolio=profiles.get('portfolio')
    )


@router.post("/gaps", response_model=GapAnalysisResponse)
async def analyze_gaps_endpoint(
    request: GapAnalysisRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze gaps between profile(s) and a job posting.
    
    Uses analyze_gaps function with job posting data.
    """
    print(f"📥 DEBUG: Received Gap Analysis Request for Job {request.job_id}")
    
    # Get combined profile
    profile_data = await get_combined_profile(request.profile_ids, user.id, db)
    
    if not profile_data.get("sources_used"):
        raise HTTPException(status_code=404, detail="No profiles found")
    
    # Get job
    result = await db.execute(
        select(Job).where(Job.id == request.job_id, Job.user_id == user.id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Analyze gaps using job posting data and combined profile - run in thread pool
    try:
        analysis = await asyncio.to_thread(
            analyze_gaps,
            job_data=job.parsed_data or {},
            combined_profile=profile_data
        )
        
        if 'error' in analysis:
            raise HTTPException(status_code=500, detail=analysis['error'])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gap analysis failed: {str(e)}")
    
    # Save to database
    print(f"💾 DEBUG: Saving Gap Analysis for Job {request.job_id}")
    gap_analysis = GapAnalysis(
        user_id=user.id,
        job_id=job.id,
        profile_ids=request.profile_ids,
        match_score=analysis.get('match_score', 0),
        analysis_data=analysis
    )
    db.add(gap_analysis)
    await db.commit()
    await db.refresh(gap_analysis)
    print(f"✅ DEBUG: Saved Gap Analysis ID: {gap_analysis.id}")
    
    return gap_analysis


@router.post("/cover-letter", response_model=CoverLetterResponse)
async def generate_cover_letter_endpoint(
    request: CoverLetterRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a tailored cover letter.
    
    Uses profile data and job requirements.
    """
    # Get profiles
    profiles = await get_profiles_data(request.profile_ids, user.id, db)
    
    if not profiles:
        raise HTTPException(status_code=404, detail="No profiles found")
    
    # Get job
    result = await db.execute(
        select(Job).where(Job.id == request.job_id, Job.user_id == user.id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Generate cover letter - run in thread pool
    try:
        result = await asyncio.to_thread(
            generate_cover_letter,
            job_data=job.parsed_data,
            resume=profiles.get('resume'),
            linkedin=profiles.get('linkedin'),
            portfolio=profiles.get('portfolio'),
            style=request.style
        )
        
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cover letter generation failed: {str(e)}")
    
    # Save to database
    cover_letter = CoverLetter(
        user_id=user.id,
        job_id=job.id,
        style=request.style,
        letter=result.get('letter', ''),
        letter_metadata={
            'key_points_highlighted': result.get('key_points_highlighted', []),
            'gaps_addressed': result.get('gaps_addressed', []),
            'word_count': result.get('word_count', 0)
        }
    )
    db.add(cover_letter)
    await db.commit()
    await db.refresh(cover_letter)
    
    return cover_letter


@router.get("/gaps/by-job/{job_id}", response_model=GapAnalysisResponse)
async def get_gap_analysis_by_job(
    job_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the most recent gap analysis for a specific job."""
    print(f"🔍 DEBUG: Fetching Gap Analysis for Job {job_id}")
    result = await db.execute(
        select(GapAnalysis)
        .where(GapAnalysis.job_id == job_id, GapAnalysis.user_id == user.id)
        .order_by(GapAnalysis.created_at.desc())
    )
    analysis = result.scalars().first()
    
    if not analysis:
        print(f"❌ DEBUG: No analysis found for Job {job_id}")
        raise HTTPException(status_code=404, detail="No gap analysis found for this job")
    
    print(f"✅ DEBUG: Found Analysis {analysis.id} for Job {job_id}")
    return analysis


@router.get("/gaps/{analysis_id}", response_model=GapAnalysisResponse)
async def get_gap_analysis(
    analysis_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a saved gap analysis."""
    result = await db.execute(
        select(GapAnalysis).where(GapAnalysis.id == analysis_id, GapAnalysis.user_id == user.id)
    )
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Gap analysis not found")
    
    return analysis


@router.get("/cover-letter/{letter_id}", response_model=CoverLetterResponse)
async def get_cover_letter(
    letter_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a saved cover letter."""
    result = await db.execute(
        select(CoverLetter).where(CoverLetter.id == letter_id, CoverLetter.user_id == user.id)
    )
    letter = result.scalar_one_or_none()
    
    if not letter:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    
    return letter


@router.get("/cover-letters/", response_model=List[CoverLetterResponse])
async def list_cover_letters(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all cover letters for the current user."""
    result = await db.execute(
        select(CoverLetter).where(CoverLetter.user_id == user.id).order_by(CoverLetter.created_at.desc())
    )
    return result.scalars().all()


@router.delete("/cover-letter/{letter_id}")
async def delete_cover_letter(
    letter_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a cover letter by ID."""
    result = await db.execute(
        select(CoverLetter).where(CoverLetter.id == letter_id, CoverLetter.user_id == user.id)
    )
    letter = result.scalar_one_or_none()
    
    if not letter:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    
    await db.delete(letter)
    await db.commit()
    
    return {"message": "Cover letter deleted"}
