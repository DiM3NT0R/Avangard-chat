from datetime import datetime, UTC
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends

from app.model.chat_room import ChatRoom
from app.schema.chat_room import ChatRoomCreate, ChatRoomResponse
from app.schema.summary import SummaryResponse
from app.service.room_service import RoomService
from app.dependencies import verify_token
from app.service.summary_service import SummaryService

router = APIRouter()


@router.get("/room/{room_id}/summary", response_model=SummaryResponse)
async def get_room_summary(
    room_id: str,
    unread_only: bool = False,
    from_dt: Optional[datetime] = None,
    to_dt: Optional[datetime] = None,
    user: dict = Depends(verify_token),
):
    """
    Краткая выжимка сообщений. Режимы:
    - (по умолчанию)        — последние N сообщений
    - ?unread_only=true     — только непрочитанные текущим юзером
    - ?from_dt=&to_dt=      — за период (ISO 8601, напр. 2025-04-20T10:00:00Z)
    - комбинация: ?unread_only=true&from_dt=...&to_dt=...
    """
    room = await ChatRoom.get(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    summary, count, was_capped, mode = await SummaryService.summarize_room(
        room_id=room_id,
        user_id=user["sub"],
        from_dt=from_dt,
        to_dt=to_dt,
        unread_only=unread_only,
    )

    return SummaryResponse(
        room_id=room_id,
        summary=summary,
        messages_count=count,
        was_capped=was_capped,
        mode=mode,
        generated_at=datetime.now(UTC),
    )