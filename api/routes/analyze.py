"""
Unified Analysis Routes - Single endpoint for complete job analysis pipeline.

Phase 1: Synchronous processing (deprecated, kept for backwards compatibility)
Phase 2: Background tasks with WebSocket updates (current)
"""

import asyncio
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..db import get_db, async_session, User, Job, Profile, Company, GapAnalysis, ResumeOptimization, AnalysisTask
from ..schemas import AnalyzeRequest, AnalyzeResponse, AnalyzeTaskResponse, AnalyzeStatusResponse
from ..deps import get_current_user
from ..websocket import manager

# Engine imports
from engine.job.sources.posting import parse_job_posting
from engine.job import extract_company_intelligence
from engine.matcher import analyze_match, combine_profiles, optimize_resume

router = APIRouter()

# Configuration
MAX_CONCURRENT_TASKS = 3
TASK_RETENTION_DAYS = 7


async def get_profiles_data(profile_ids: list, user_id: str, db: AsyncSession) -> dict:
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


async def count_active_tasks(user_id: str, db: AsyncSession) -> int:
    """Count active (non-complete, non-failed) tasks for a user."""
    result = await db.execute(
        select(func.count(AnalysisTask.id)).where(
            AnalysisTask.user_id == user_id,
            AnalysisTask.status.notin_(['complete', 'failed'])
        )
    )
    return result.scalar() or 0


async def update_task_status(
    task_id: str,
    user_id: str,
    status: str,
    message: str,
    progress: int,
    result_job_id: str = None,
    result_analysis_id: str = None,
    result_data: dict = None,
    error_message: str = None,
    job_title: str = None
):
    """Update task status in DB and broadcast via WebSocket."""
    async with async_session() as db:
        result = await db.execute(
            select(AnalysisTask).where(AnalysisTask.id == task_id)
        )
        task = result.scalar_one_or_none()
        
        if task:
            task.status = status
            task.progress_message = message
            task.progress = progress
            task.updated_at = datetime.utcnow()
            
            if job_title:
                task.job_title = job_title
            
            if result_job_id:
                task.result_job_id = result_job_id
            if result_analysis_id:
                task.result_analysis_id = result_analysis_id
            if result_data:
                task.result_data = result_data
            if error_message:
                task.error_message = error_message
            
            await db.commit()
    
    # Broadcast via WebSocket
    match_score = result_data.get('analysis', {}).get('match_score') if result_data else None
    
    # Calculate duration if complete/failed
    total_duration = None
    if status in ['complete', 'failed'] and task and task.created_at:
        # Use updated_at (just set) as end time
        end_time = datetime.utcnow()
        total_duration = (end_time - task.created_at).total_seconds()

    await manager.broadcast_status(
        user_id=user_id,
        task_id=task_id,
        status=status,
        message=message,
        progress=progress,
        job_id=result_job_id,
        match_score=match_score,
        error=error_message,
        total_duration=total_duration,
        job_title=job_title or (task.job_title if task else None)
    )


async def run_analysis_pipeline(task_id: str, user_id: str, job_text: str, company_name: str, profile_ids: list):
    """
    Background worker that runs the full analysis pipeline.
    
    Updates status via WebSocket at each step.
    """
    job_id = None  # Initialize for atomicity rollback
    
    try:
        # Get profiles
        async with async_session() as db:
            profiles_data = await get_profiles_data(profile_ids, user_id, db)
        
        if not profiles_data:
            await update_task_status(task_id, user_id, "failed", "No profiles found", 0, error_message="No valid profiles")
            return
        
        # =====================================================================
        # STEP 1: Parse Job Posting (0-25%)
        # =====================================================================
        await update_task_status(task_id, user_id, "parsing", "Parsing job posting...", 10)
        
        try:
            parsed_job = await asyncio.to_thread(parse_job_posting, job_text)
            if 'error' in parsed_job:
                await update_task_status(task_id, user_id, "failed", "Failed to parse job posting", 0, error_message=parsed_job['error'])
                return
        except Exception as e:
            await update_task_status(task_id, user_id, "failed", "Failed to parse job posting", 0, error_message=str(e))
            return
        
        # Get company name from request or parsed data
        final_company_name = company_name or parsed_job.get('company_name')
        
        # Save job to database
        async with async_session() as db:
            job = Job(
                user_id=user_id,
                job_title=parsed_job.get('job_title'),
                company_name=final_company_name,
                job_text=job_text,
                parsed_data=parsed_job
            )
            db.add(job)
            await db.commit()
            await db.refresh(job)
            job_id = job.id
            
        await update_task_status(task_id, user_id, "parsing", "Job posting parsed successfully", 25, job_title=parsed_job.get('job_title'))
        
        # =====================================================================
        # STEP 2: Company Intelligence (25-50%)
        # =====================================================================
        company_intel = {}
        
        if final_company_name:
            await update_task_status(task_id, user_id, "intel", "Gathering company intelligence...", 30)
            
            async with async_session() as db:
                result = await db.execute(
                    select(Company).where(Company.name == final_company_name)
                )
                cached_company = result.scalar_one_or_none()
                
                if cached_company:
                    company_intel = cached_company.intelligence or {}
                    await update_task_status(task_id, user_id, "intel", "Company data found in cache", 45)
                else:
                    try:
                        company_intel = await asyncio.to_thread(
                            extract_company_intelligence,
                            company_name=final_company_name,
                            max_jobs=10,
                            include_website=True,
                            include_news=True
                        )
                        
                        # Cache it
                        company = Company(
                            name=final_company_name,
                            website=company_intel.get('website', {}).get('website_url', ''),
                            intelligence=company_intel
                        )
                        db.add(company)
                        await db.commit()
                        
                        await update_task_status(task_id, user_id, "intel", "Company intelligence gathered", 50)
                    except Exception as e:
                        print(f"⚠ Company intel failed: {e}")
                        await update_task_status(task_id, user_id, "intel", "Continuing without company intel...", 50)
        else:
            await update_task_status(task_id, user_id, "intel", "No company name - skipping intel", 50)
        
        # =====================================================================
        # STEP 3: Parallel Analysis & Optimization (50-95%)
        # =====================================================================
        await update_task_status(task_id, user_id, "analyzing", "Analyzing match and optimizing resume...", 55)
        
        job_context = {
            "job_posting": parsed_job,
            "company_intel": company_intel.get('aggregated', company_intel) if company_intel else {},
            "news": company_intel.get('news', {}).get('headlines', []) if company_intel else []
        }
        
        combined_profile = combine_profiles(
            resume=profiles_data.get('resume'),
            linkedin=profiles_data.get('linkedin'),
            portfolio=profiles_data.get('portfolio')
        )

        resume_data = profiles_data.get('resume')
        
        # Prepare coroutines
        analysis_task = asyncio.to_thread(
            analyze_match,
            job_context=job_context,
            profile_data=combined_profile
        )

        optimization_task = None
        if resume_data:
            optimization_task = asyncio.to_thread(
                optimize_resume,
                resume_data=resume_data,
                job_context=job_context
            )
        
        try:
            # Run concurrently
            results = await asyncio.gather(
                analysis_task, 
                optimization_task if optimization_task else asyncio.sleep(0),
                return_exceptions=True
            )
            
            analysis_result = results[0]
            optimization_result = results[1] if optimization_task else None

            # Handle Analysis Result
            if isinstance(analysis_result, Exception) or (isinstance(analysis_result, dict) and 'error' in analysis_result):
                error_msg = str(analysis_result) if isinstance(analysis_result, Exception) else analysis_result.get('error')
                # ROLLBACK: Delete job if analysis fails
                if job_id:
                    async with async_session() as db:
                        job_to_del = await db.get(Job, job_id)
                        if job_to_del:
                            await db.delete(job_to_del)
                            await db.commit()
                            print(f"🧹 Cleaned up job {job_id} after analysis error")
                            
                await update_task_status(task_id, user_id, "failed", "Analysis failed", 0, error_message=error_msg)
                return
            
            # Save analysis immediately
            async with async_session() as db:
                gap_analysis = GapAnalysis(
                    user_id=user_id,
                    job_id=job_id,
                    profile_ids=profile_ids,
                    match_score=analysis_result.get('match_score', 0),
                    analysis_data=analysis_result
                )
                db.add(gap_analysis)
                await db.commit()
                await db.refresh(gap_analysis)
                analysis_id = gap_analysis.id
                match_score = gap_analysis.match_score
            
            # Handle Optimization Result (Soft fail)
            if isinstance(optimization_result, Exception):
                print(f"⚠ Resume optimization failed: {optimization_result}")
                optimization_result = None
            elif isinstance(optimization_result, dict) and 'error' in optimization_result:
                 print(f"⚠ Resume optimization failed: {optimization_result['error']}")
                 optimization_result = None
            
            if optimization_result:
                async with async_session() as db:
                    # Find resume profile ID
                    resume_profile_id = None
                    for pid in profile_ids:
                        result = await db.execute(
                            select(Profile).where(
                                Profile.id == pid,
                                Profile.user_id == user_id,
                                Profile.source_type == 'resume'
                            )
                        )
                        profile = result.scalar_one_or_none()
                        if profile:
                            resume_profile_id = profile.id
                            break
                    
                    if resume_profile_id:
                        resume_opt = ResumeOptimization(
                            user_id=user_id,
                            job_id=job_id,
                            resume_id=resume_profile_id,
                            optimization_data=optimization_result
                        )
                        db.add(resume_opt)
                        await db.commit()

        except Exception as e:
             # ROLLBACK: Delete job if catastrophic exception
            if job_id:
                async with async_session() as db:
                    job_to_del = await db.get(Job, job_id)
                    if job_to_del:
                        await db.delete(job_to_del)
                        await db.commit()
                        print(f"🧹 Cleaned up job {job_id} after pipeline exception")
                        
            await update_task_status(task_id, user_id, "failed", "Analysis failed", 0, error_message=str(e))
            return
        
        # =====================================================================
        # COMPLETE
        # =====================================================================
        result_data = {
            "job": {
                "id": job_id,
                "job_title": parsed_job.get('job_title'),
                "company_name": final_company_name
            },
            "analysis": {
                "id": analysis_id,
                "match_score": match_score
            },
            "optimization": optimization_result
        }
        
        await update_task_status(
            task_id, user_id, "complete", "Analysis complete!",
            100, result_job_id=job_id, result_analysis_id=analysis_id, result_data=result_data
        )
        
    except Exception as e:
        print(f"❌ Pipeline error: {e}")
        # Final safety rollback
        if job_id:
             try:
                 async with async_session() as db:
                    job_to_del = await db.get(Job, job_id)
                    if job_to_del:
                        await db.delete(job_to_del)
                        await db.commit()
                        print(f"🧹 Cleaned up job {job_id} after pipeline crash")
             except Exception as cleanup_err:
                 print(f"⚠ Failed to cleanup job {job_id}: {cleanup_err}")
                 
        await update_task_status(task_id, user_id, "failed", "An unexpected error occurred", 0, error_message=str(e))


@router.post("/", response_model=AnalyzeTaskResponse)
async def analyze_job(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Start a job analysis task (async).
    
    Returns immediately with task_id. Connect to WebSocket for real-time updates.
    """
    # Check concurrent limit
    active_count = await count_active_tasks(user.id, db)
    if active_count >= MAX_CONCURRENT_TASKS:
        raise HTTPException(
            status_code=429,
            detail=f"Maximum {MAX_CONCURRENT_TASKS} concurrent analyses allowed. Please wait for current tasks to complete."
        )
    
    # Validate profiles exist
    profiles_data = await get_profiles_data(request.profile_ids, user.id, db)
    if not profiles_data:
        raise HTTPException(status_code=404, detail="No profiles found")
    
    # Create task record
    task = AnalysisTask(
        user_id=user.id,
        job_text=request.job_text,
        company_name=request.company_name,
        profile_ids=request.profile_ids,
        status="pending",
        progress_message="Queued for analysis...",
        progress=0
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    # Queue background task
    background_tasks.add_task(
        run_analysis_pipeline,
        task.id,
        user.id,
        request.job_text,
        request.company_name,
        request.profile_ids
    )
    
    return AnalyzeTaskResponse(task_id=task.id, status="pending")


@router.get("/tasks")
async def list_tasks(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all analysis tasks for the current user (active first, then recent)."""
    # Get all tasks from last 24 hours, ordered by status priority and creation time
    cutoff = datetime.utcnow() - timedelta(hours=24)
    
    result = await db.execute(
        select(AnalysisTask).where(
            AnalysisTask.user_id == user.id,
            AnalysisTask.created_at > cutoff
        ).order_by(
            # Active tasks first (pending, parsing, intel, analyzing, optimizing)
            # Then completed/failed
            AnalysisTask.status.desc(),
            AnalysisTask.created_at.desc()
        )
    )
    tasks = result.scalars().all()
    
    return [
        {
            "task_id": task.id,
            "status": task.status,
            "progress_message": task.progress_message,
            "progress": task.progress,
            "progress": task.progress,
            "job_title": task.job_title,
            "company_name": task.company_name,
            "created_at": task.created_at.isoformat(),
            "result_job_id": task.result_job_id,
            "error_message": task.error_message,
            "total_duration": (task.updated_at - task.created_at).total_seconds() if task.status in ['complete', 'failed'] and task.updated_at and task.created_at else None
        }
        for task in tasks
    ]


@router.get("/{task_id}", response_model=AnalyzeStatusResponse)
async def get_task_status(
    task_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the current status of an analysis task."""
    result = await db.execute(
        select(AnalysisTask).where(
            AnalysisTask.id == task_id,
            AnalysisTask.user_id == user.id
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return AnalyzeStatusResponse(
        task_id=task.id,
        status=task.status,
        job_title=task.job_title,
        progress_message=task.progress_message,
        progress=task.progress,
        result=task.result_data,
        error_message=task.error_message
    )

@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an analysis task."""
    result = await db.execute(
        select(AnalysisTask).where(
            AnalysisTask.id == task_id,
            AnalysisTask.user_id == user.id
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await db.delete(task)
    await db.commit()
    
    
    return {"message": "Task deleted"}


@router.delete("/tasks")
async def clear_all_tasks(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete all analysis tasks for the current user."""
    result = await db.execute(
        select(AnalysisTask).where(AnalysisTask.user_id == user.id)
    )
    tasks = result.scalars().all()
    
    for task in tasks:
        await db.delete(task)
    
    await db.commit()
    
    return {"message": f"Cleared {len(tasks)} tasks"}


# Cleanup old tasks (can be called via cron or startup)
async def cleanup_old_tasks():
    """Remove tasks older than TASK_RETENTION_DAYS."""
    cutoff = datetime.utcnow() - timedelta(days=TASK_RETENTION_DAYS)
    async with async_session() as db:
        result = await db.execute(
            select(AnalysisTask).where(AnalysisTask.created_at < cutoff)
        )
        old_tasks = result.scalars().all()
        for task in old_tasks:
            await db.delete(task)
        await db.commit()
        if old_tasks:
            print(f"🧹 Cleaned up {len(old_tasks)} old analysis tasks")
