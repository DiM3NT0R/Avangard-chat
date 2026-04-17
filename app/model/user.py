from beanie import Document
from pydantic import EmailStr, ConfigDict, Field
from datetime import datetime, UTC
from typing import Optional


class User(Document):
    id: str = Field(alias="_id")
    username: str
    full_name: str
    email: EmailStr
    avatar_url: Optional[str] = None
    is_online: bool = False
    created_at: datetime = datetime.now(UTC)
    last_time_online: Optional[datetime] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def to_response(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "full_name": self.full_name,
            "email": self.email,
            "avatar_url": self.avatar_url,
            "is_online": self.is_online,
            "created_at": self.created_at,
        }

    class Settings:
        name = "users"
        indexes = ["username", "email", "full_name"]

