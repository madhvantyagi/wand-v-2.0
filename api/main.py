"""
Wand API - Job Intelligence & Profile Matching

FastAPI backend for the Wand application.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    # When running from parent directory: uvicorn api.main:app
    from .db import create_tables
    from .routes import profile, job, match, discrepancy, user, auth
except ImportError as e:
    # Print the error for debugging
    import traceback
    traceback.print_exc()
    print(f"⚠️ Import error (likely running from api dir or missing dependency): {e}")
    # When running from api directory: uvicorn main:app
    from db import create_tables
    from routes import profile, job, match, discrepancy, user, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: Create tables
    await create_tables()
    print("✅ Database tables created")
    yield
    # Shutdown
    print("👋 Shutting down")


app = FastAPI(
    title="Wand API",
    description="Job Intelligence & Profile Matching API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/user", tags=["Users"])
app.include_router(profile.router, prefix="/profile", tags=["Profile"])
app.include_router(job.router, prefix="/job", tags=["Job Intelligence"])
app.include_router(match.router, prefix="/match", tags=["Matching"])
app.include_router(discrepancy.router, prefix="/discrepancy", tags=["Discrepancy"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Wand API is running",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy"}
