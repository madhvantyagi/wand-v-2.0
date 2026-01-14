"""
WebSocket Connection Manager for real-time analysis updates.

Manages user-specific WebSocket connections and broadcasts status updates.
"""

from typing import Dict, List
from fastapi import WebSocket
import json


class ConnectionManager:
    """
    Manages WebSocket connections per user.
    
    Allows broadcasting status updates to specific users during background analysis.
    """
    
    def __init__(self):
        # Map of user_id -> list of active WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept a new WebSocket connection for a user."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        print(f"🔌 WebSocket connected for user {user_id[:8]}... (total: {len(self.active_connections[user_id])})")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection for a user."""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        print(f"🔌 WebSocket disconnected for user {user_id[:8]}...")
    
    async def send_to_user(self, user_id: str, message: dict):
        """Send a message to all connections for a specific user."""
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)
            
            # Clean up disconnected sockets
            for conn in disconnected:
                self.disconnect(conn, user_id)
    
    async def broadcast_status(
        self,
        user_id: str,
        task_id: str,
        status: str,
        message: str,
        progress: int = 0,
        job_id: str = None,
        match_score: int = None,
        error: str = None,
        total_duration: float = None,
        job_title: str = None
    ):
        """
        Broadcast a status update to all user's connections.
        
        Args:
            user_id: Target user
            task_id: Analysis task ID
            status: Current status (pending, parsing, intel, analyzing, optimizing, complete, failed)
            message: Human-readable progress message
            progress: 0-100 progress percentage
            job_id: Result job ID (on completion)
            match_score: Match score (on completion)
            error: Error message (on failure)
            total_duration: Time taken in seconds (on completion/failure)
            job_title: Job title (if available)
        """
        payload = {
            "type": "status_update" if status != "complete" and status != "failed" else status,
            "task_id": task_id,
            "status": status,
            "message": message,
            "progress": progress
        }
        
        if job_id:
            payload["job_id"] = job_id
        if match_score is not None:
            payload["match_score"] = match_score
        if error:
            payload["error"] = error
        if total_duration is not None:
            payload["total_duration"] = total_duration
        if job_title:
            payload["job_title"] = job_title
        
        await self.send_to_user(user_id, payload)


# Global connection manager instance
manager = ConnectionManager()
