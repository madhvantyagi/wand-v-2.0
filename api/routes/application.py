"""
Application tracking routes.
"""

import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from ..db import get_db, User, Job, Application
from ..schemas import ApplicationResponse, ApplicationUpdate
from ..deps import get_current_user

router = APIRouter()


@router.get("/jobs/{job_id}/application", response_model=ApplicationResponse | None)
async def get_application_status(
    job_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get application status for a job."""
    result = await db.execute(
        select(Application).where(
            Application.job_id == job_id,
            Application.user_id == user.id
        )
    )
    application = result.scalar_one_or_none()
    return application


@router.post("/jobs/{job_id}/application", response_model=ApplicationResponse)
async def create_or_update_application(
    job_id: str,
    data: ApplicationUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create or update application status for a job."""
    # Check if job exists
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.user_id == user.id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if application already exists
    result = await db.execute(
        select(Application).where(
            Application.job_id == job_id,
            Application.user_id == user.id
        )
    )
    application = result.scalar_one_or_none()
    
    if application:
        # Update existing
        application.status = data.status
        if data.notes is not None:
            application.notes = data.notes
        if data.status == "applied" and not application.applied_at:
            application.applied_at = datetime.utcnow()
    else:
        # Create new
        application = Application(
            user_id=user.id,
            job_id=job_id,
            status=data.status,
            notes=data.notes,
            applied_at=datetime.utcnow() if data.status == "applied" else None
        )
        db.add(application)
    
    await db.commit()
    await db.refresh(application)
    return application
