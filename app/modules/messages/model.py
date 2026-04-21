from datetime import UTC, datetime
from typing import List, Optional

from beanie import Document, Link
from pydantic import Field
from pymongo import DESCENDING, IndexModel

from app.modules.rooms.model import ChatRoom
from app.modules.users.model import User


class Message(Document):
    room: Link[ChatRoom]
    sender: Link[User]
    text_ciphertext: str
    text_nonce: str
    text_key_id: str
    text_aad: str
    is_edited: bool = False
    edited_at: Optional[datetime] = None
    is_deleted: bool = False
    read_by: List[Link[User]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "messages"
        indexes = [
            IndexModel([("room", 1), ("created_at", DESCENDING), ("_id", DESCENDING)]),
            IndexModel([("room", 1), ("is_deleted", 1), ("created_at", DESCENDING)]),
            IndexModel([("room", 1), ("read_by", 1), ("created_at", DESCENDING)]),
        ]
