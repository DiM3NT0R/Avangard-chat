from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings
from app.model.user import User
from app.model.chat_room import ChatRoom
from app.model.message import Message


async def init_db():
    client = AsyncIOMotorClient(settings.mongodb_url)
    await init_beanie(
        database=client[settings.db_name],
        document_models=[User, Message, ChatRoom]
    )

    