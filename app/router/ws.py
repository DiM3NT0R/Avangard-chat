from fastapi import APIRouter, Depends, WebSocket

from app.dependencies import (
    get_dragonfly_service,
    get_message_service,
    get_rate_limit_service,
    get_room_service,
)
from app.dragonfly.service import DragonflyService
from app.rate_limit import RateLimitService
from app.service.message_service import MessageService
from app.service.room_service import RoomService
from app.ws.chat_handler import handle_room_chat

router = APIRouter()


@router.websocket("/{room_id}")
async def chat(
    websocket: WebSocket,
    room_id: str,
    room_service: RoomService = Depends(get_room_service),
    message_service: MessageService = Depends(get_message_service),
    rate_limit_service: RateLimitService = Depends(get_rate_limit_service),
    dragonfly: DragonflyService = Depends(get_dragonfly_service),
):
    await handle_room_chat(
        websocket=websocket,
        room_id=room_id,
        room_service=room_service,
        message_service=message_service,
        rate_limit_service=rate_limit_service,
        dragonfly=dragonfly,
    )
