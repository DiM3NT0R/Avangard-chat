from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError

from app.model.user import User
from app.security import decode_access_token
from app.service.auth_service import AuthService
from app.service.message_service import MessageService
from app.service.room_service import RoomService

bearer_scheme = HTTPBearer(auto_error=False)


def get_bearer_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> str:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Missing bearer token")
    return credentials.credentials


async def verify_token(token: str = Depends(get_bearer_token)) -> dict:
    try:
        payload = decode_access_token(token)
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await User.find_one(User.id == payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload


def get_room_service() -> RoomService:
    return RoomService()


def get_message_service(
    room_service: RoomService = Depends(get_room_service),
) -> MessageService:
    return MessageService(room_service=room_service)


def get_auth_service() -> AuthService:
    return AuthService()
