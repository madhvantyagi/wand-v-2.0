"""
Discrepancy routes.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import asyncio

from ..db import get_db, User, Profile, DiscrepancyReport
from ..schemas import (
    DiscrepancyRequest, DiscrepancyResponse, 
    DiscrepancyHistoryItem, DiscrepancyReportResponse
)
from ..deps import get_current_user
from engine.discrepancy import compare_profile_sources, format_for_table

router = APIRouter()


@router.post("/compare", response_model=DiscrepancyReportResponse)
async def compare_profiles(
    request: DiscrepancyRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Compare profile sources to find discrepancies.
    
    Needs at least 2 profiles (resume, linkedin, portfolio).
    Returns UI-friendly table data and saves to history.
    """
    if len(request.profile_ids) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 profiles to compare")
    
    # Fetch profiles
    profiles = {}
    for pid in request.profile_ids:
        result = await db.execute(
            select(Profile).where(Profile.id == pid, Profile.user_id == user.id)
        )
        profile = result.scalar_one_or_none()
        
        if profile:
            profiles[profile.source_type] = profile.parsed_data
    
    if len(profiles) < 2:
        raise HTTPException(status_code=404, detail="Not enough valid profiles found")
    
    # Compare profiles - run in thread pool
    try:
        result = await asyncio.to_thread(
            compare_profile_sources,
            resume=profiles.get('resume'),
            linkedin=profiles.get('linkedin'),
            portfolio=profiles.get('portfolio')
        )
        
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        
        # Format for table
        table_data = format_for_table(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")
    
    # Build report data
    report_data = {
        "consistency_score": result.get('consistency_score', 100),
        "discrepancies": result.get('discrepancies', []),
        "skill_comparison": result.get('skill_comparison', []),
        "missing_in_resume": result.get('missing_in_resume', []),
        "missing_online": result.get('missing_online', []),
        "recommendations": result.get('recommendations', []),
        "table_data": table_data
    }
    
    # Save to database
    report = DiscrepancyReport(
        user_id=user.id,
        profile_ids=request.profile_ids,
        consistency_score=result.get('consistency_score', 100),
        report_data=report_data
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    
    return report


@router.get("/history", response_model=List[DiscrepancyHistoryItem])
async def get_discrepancy_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of all discrepancy analysis reports for the current user."""
    result = await db.execute(
        select(DiscrepancyReport)
        .where(DiscrepancyReport.user_id == user.id)
        .order_by(DiscrepancyReport.created_at.desc())
    )
    reports = result.scalars().all()
    return reports


@router.get("/{report_id}", response_model=DiscrepancyReportResponse)
async def get_discrepancy_report(
    report_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific discrepancy report by ID."""
    result = await db.execute(
        select(DiscrepancyReport).where(
            DiscrepancyReport.id == report_id,
            DiscrepancyReport.user_id == user.id
        )
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report
