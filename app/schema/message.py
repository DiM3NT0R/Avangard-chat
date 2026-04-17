from typing import List

from pydantic import BaseModel
from datetime import datetime


class MessageCreate(BaseModel):
    room_id: str
    text: str


class MessageUpdate(BaseModel):
    text: str


class MessageResponse(BaseModel):
    id: str
    room_id: str
    sender_id: str
    text: str
    is_edited: bool
    is_deleted: bool
    read_by: List[str]
    created_at: datetime

