from fastapi import APIRouter, Depends, WebSocket

from app.dependencies import get_message_service, get_room_service
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
):
    await handle_room_chat(
        websocket=websocket,
        room_id=room_id,
        room_service=room_service,
        message_service=message_service,
    )
