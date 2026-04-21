from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.model.chat_room import ChatRoom
from app.model.message import Message
from app.model.user import User


async def init_db() -> None:
    client = AsyncIOMotorClient(settings.database.mongodb_url)
    await init_beanie(
        database=client[settings.database.db_name],
        document_models=[User, Message, ChatRoom],
    )
