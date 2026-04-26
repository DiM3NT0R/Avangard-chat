from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class SummaryResponse(BaseModel):
    room_id: str
    summary: str
    messages_count: int
    was_capped: bool          # True — сообщений было больше лимита
    mode: str                 # "unread" | "range" | "unread+range" | "recent"
    generated_at: datetime