from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List, Dict
import json

from promethium.core.logging import logger

router = APIRouter(prefix="/ws", tags=["websockets"])

class ConnectionManager:
    def __init__(self):
        # job_id -> list of websockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, job_id: str):
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = []
        self.active_connections[job_id].append(websocket)
        logger.debug(f"Client connected to job {job_id}")

    def disconnect(self, websocket: WebSocket, job_id: str):
        if job_id in self.active_connections:
            if websocket in self.active_connections[job_id]:
                self.active_connections[job_id].remove(websocket)
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]
        logger.debug(f"Client disconnected from job {job_id}")

    async def broadcast_to_job(self, job_id: str, message: dict):
        if job_id in self.active_connections:
            for connection in self.active_connections[job_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning(f"Failed to send message to client: {e}")

manager = ConnectionManager()

@router.websocket("/jobs/{job_id}")
async def websocket_job_progress(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time job progress updates.
    """
    await manager.connect(websocket, job_id)
    try:
        while True:
            # We keep the connection open.
            # Clients might send heartbeats or commands, but mostly they listen.
            data = await websocket.receive_text()
            # echo or handle commands
            # await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, job_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, job_id)

# Helper function to be called by Celery workers or other parts of the app
# Note: This won't work directly if Celery runs in a separate process/container efficiently
# without a shared backend (like Redis PubSub).
# For production, we'd use Redis PubSub to broadcast from Worker -> API -> WebSockets.
# This simple implementation assumes API can push updates (e.g. if job is running async in API).
# Since we use Celery, the worker needs to publish to Redis, and the API needs to subscribe.
# That is a bit more complex. For now, we will leave this structure.
