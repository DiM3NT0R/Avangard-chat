from datetime import UTC, datetime
from typing import List, Optional

from beanie import Document, Link
from pydantic import Field

from app.model.user import User


class ChatRoom(Document):
    name: Optional[str] = None
    is_group: bool = False
    members: List[Link[User]] = []
    created_by: Link[User]
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "chat_rooms"
