"""
Profile routes - CRUD for Resume (PDF), LinkedIn (PDF), and Portfolio (HTML)
"""

import os
import tempfile
import asyncio
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ..db import get_db, User, Profile
from ..schemas import ProfileResponse
from ..deps import get_current_user
from profile_extractor.extractor import parse_profile
import json

router = APIRouter()


# ============================================================================
# RESUME ENDPOINTS (PDF)
# ============================================================================

@router.post("/resume", response_model=ProfileResponse)
async def upload_resume(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload and parse a resume (PDF only)."""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Resume must be a PDF file")
    
    return await _parse_and_save(file, 'resume', 'pdf', user, db)


@router.get("/resume", response_model=ProfileResponse)
async def get_resume(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the user's resume."""
    return await _get_profile_by_type('resume', user, db)


@router.delete("/resume")
async def delete_resume(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete the user's resume."""
    return await _delete_profile_by_type('resume', user, db)


# ============================================================================
# LINKEDIN ENDPOINTS (PDF)
# ============================================================================

@router.post("/linkedin", response_model=ProfileResponse)
async def upload_linkedin(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload and parse a LinkedIn profile export (PDF only)."""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="LinkedIn profile must be a PDF file")
    
    return await _parse_and_save(file, 'linkedin', 'pdf', user, db)


@router.get("/linkedin", response_model=ProfileResponse)
async def get_linkedin(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the user's LinkedIn profile."""
    return await _get_profile_by_type('linkedin', user, db)


@router.delete("/linkedin")
async def delete_linkedin(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete the user's LinkedIn profile."""
    return await _delete_profile_by_type('linkedin', user, db)


# ============================================================================
# PORTFOLIO ENDPOINTS (HTML)
# ============================================================================

@router.post("/portfolio", response_model=ProfileResponse)
async def upload_portfolio(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload and parse a portfolio website (HTML only)."""
    if not file.filename.lower().endswith(('.html', '.htm')):
        raise HTTPException(status_code=400, detail="Portfolio must be an HTML file")
    
    return await _parse_and_save(file, 'portfolio', 'html', user, db)


@router.get("/portfolio", response_model=ProfileResponse)
async def get_portfolio(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the user's portfolio."""
    return await _get_profile_by_type('portfolio', user, db)


@router.delete("/portfolio")
async def delete_portfolio(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete the user's portfolio."""
    return await _delete_profile_by_type('portfolio', user, db)


# ============================================================================
# GENERAL ENDPOINTS
# ============================================================================

@router.get("/", response_model=List[ProfileResponse])
async def get_all_profiles(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all profiles for the current user."""
    result = await db.execute(
        select(Profile).where(Profile.user_id == user.id).order_by(Profile.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile_by_id(
    profile_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific profile by ID."""
    result = await db.execute(
        select(Profile).where(Profile.id == profile_id, Profile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile


@router.get("/{profile_id}/file")
async def get_profile_file(
    profile_id: str,
    token: str = None,  # Allow token via query param for iframe/embed
    db: AsyncSession = Depends(get_db)
):
    """Get the raw file content for a profile (for preview)."""
    from fastapi.responses import Response
    from ..auth import decode_token
    
    # Authenticate via token query param
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    result = await db.execute(
        select(Profile).where(Profile.id == profile_id, Profile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    if not profile.file_content:
        raise HTTPException(status_code=404, detail="No file content available")
    
    # Determine content type based on source_type
    if profile.source_type == 'portfolio':
        content_type = 'text/html'
    else:
        content_type = 'application/pdf'
    
    return Response(
        content=profile.file_content,
        media_type=content_type,
        headers={
            'Content-Disposition': f'inline; filename="{profile.file_name}"'
        }
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def _parse_and_save(
    file: UploadFile,
    source_type: str,
    file_type: str,
    user: User,
    db: AsyncSession
) -> Profile:
    """Parse file and save to database (replaces existing if present)."""
    
    # Delete existing profile of this type
    result = await db.execute(
        select(Profile).where(Profile.user_id == user.id, Profile.source_type == source_type)
    )
    existing = result.scalar_one_or_none()
    if existing:
        await db.delete(existing)
    
    # Read file content
    content = await file.read()
    
    # Save file temporarily and parse - run in thread pool
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_type}') as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        parsed_result = await asyncio.to_thread(parse_profile, tmp_path, file_type)
        parsed_data = json.loads(parsed_result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse file: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
    
    # Save new profile with file content
    profile = Profile(
        user_id=user.id,
        source_type=source_type,
        file_name=file.filename,
        file_content=content,  # Store raw file bytes
        parsed_data=parsed_data
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    
    return profile


async def _get_profile_by_type(source_type: str, user: User, db: AsyncSession) -> Profile:
    """Get profile by source type."""
    result = await db.execute(
        select(Profile).where(Profile.user_id == user.id, Profile.source_type == source_type)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail=f"{source_type.capitalize()} not found")
    
    return profile


async def _delete_profile_by_type(source_type: str, user: User, db: AsyncSession):
    """Delete profile by source type."""
    result = await db.execute(
        select(Profile).where(Profile.user_id == user.id, Profile.source_type == source_type)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail=f"{source_type.capitalize()} not found")
    
    await db.delete(profile)
    await db.commit()
    
    return {"message": f"{source_type.capitalize()} deleted"}
