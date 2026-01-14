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
    from .routes import profile, job, match, discrepancy, user, auth, application, analyze
except ImportError as e:
    # Print the error for debugging
    import traceback
    traceback.print_exc()
    print(f"⚠️ Import error (likely running from api dir or missing dependency): {e}")
    # When running from api directory: uvicorn main:app
    from db import create_tables
    from routes import profile, job, match, discrepancy, user, auth, application, analyze


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
app.include_router(application.router, prefix="/application", tags=["Applications"])
app.include_router(analyze.router, prefix="/analyze", tags=["Unified Analysis"])


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


# ============================================================================
# WebSocket for Real-time Analysis Updates
# ============================================================================

from fastapi import WebSocket, WebSocketDisconnect

try:
    from .websocket import manager
    from .auth import decode_token
except ImportError:
    from websocket import manager
    from auth import decode_token


@app.websocket("/ws/analyze/{token}")
async def websocket_analyze(websocket: WebSocket, token: str):
    """
    WebSocket endpoint for real-time analysis status updates.
    
    Client connects with JWT token in path.
    Receives status updates during background analysis.
    """
    # Validate token and get user_id
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=4001, reason="Invalid token")
            return
    except Exception:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    # Connect and manage lifecycle
    await manager.connect(websocket, user_id)
    
    try:
        # Keep connection alive, receive ping/pong
        while True:
            data = await websocket.receive_text()
            # Echo back pings or handle client messages
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception:
        manager.disconnect(websocket, user_id)
