import logging
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.core.auth import decode_token
from app.database import SessionLocal
from app.models import User
from app.services.websocket_manager import manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
):
    """
    WebSocket endpoint for live updates.
    Token should be passed as query parameter: ?token=...
    """
    # Authenticate via token
    if not token:
        await websocket.close(code=1008, reason="Authentication required")
        return

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=1008, reason="Invalid token")
            return

        # Verify user exists and is active
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == int(user_id)).first()
            if not user or not user.is_active:
                await websocket.close(code=1008, reason="User not found or inactive")
                return
        finally:
            db.close()

        # Connect
        await manager.connect(websocket)
        logger.info(f"WebSocket authenticated for user {user_id}")

        try:
            # Keep connection alive and handle incoming messages
            while True:
                # Wait for any message (client can send ping/pong)
                data = await websocket.receive_text()
                # Echo back or handle client messages if needed
                # For now, just keep connection alive
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            logger.info(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close(code=1011, reason="Internal error")
        except Exception:
            pass
        manager.disconnect(websocket)
