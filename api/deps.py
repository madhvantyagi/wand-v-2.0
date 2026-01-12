"""
FastAPI dependencies.

Supports both JWT authentication and legacy X-User-Id header.
"""

from typing import Optional
from fastapi import Depends, HTTPException, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

try:
    from .db import get_db, User
    from .auth import decode_token
except ImportError as e:
    # Check if it's a relative import error or a missing dependency
    if "attempted relative import" in str(e) or "No module named 'api'" not in str(e):
        # Likely missing dependency or legitimate error, re-raise if it's not just the relative import issue
        # Use a simple heuristic: if we are running as api.main, relative imports should work.
        # If they fail with "No module named 'jose'", that's a dependency issue we want to see.
        pass
        
    try:
        from db import get_db, User
        from auth import decode_token
    except ImportError:
        # Re-raise the original error if fallback also fails, to show the root cause
        raise e

# Bearer token scheme (optional - doesn't require auth)
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current user.
    
    Tries JWT token first, falls back to X-User-Id header for backward compatibility.
    """
    user_id = None
    
    # Try JWT token first
    if credentials:
        payload = decode_token(credentials.credentials)
        if payload:
            user_id = payload.get("sub")
    
    # Fallback to X-User-Id header
    if not user_id and x_user_id:
        user_id = x_user_id
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get user if authenticated, otherwise None."""
    try:
        return await get_current_user(credentials, x_user_id, db)
    except HTTPException:
        return None
