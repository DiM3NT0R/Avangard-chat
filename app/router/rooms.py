from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import verify_token
from app.schema.chat_room import (
    ChatRoomCreate,
    ChatRoomResponse,
    serialize_chat_room_response,
)
from app.service.room_service import RoomService

router = APIRouter()


@router.post("", response_model=ChatRoomResponse)
async def create_room(data: ChatRoomCreate, user: dict = Depends(verify_token)):
    result = await RoomService.create(data=data, creator_id=user["sub"])
    return serialize_chat_room_response(result)


@router.get("/{room_id}", response_model=ChatRoomResponse)
async def get_room(room_id: str, user: dict = Depends(verify_token)):
    room = await RoomService.get_for_user(room_id, user["sub"])
    return serialize_chat_room_response(room)


@router.get("/user/{user_id}", response_model=list[ChatRoomResponse])
async def get_rooms_by_user_id(user_id: str, user: dict = Depends(verify_token)):
    if user_id != user["sub"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to view these rooms",
        )
    result = await RoomService.list_all_by_user(user_id)
    return [serialize_chat_room_response(room) for room in result]


@router.delete("/{room_id}")
async def delete_room(room_id: str, user: dict = Depends(verify_token)):
    await RoomService.delete_room(room_id, user["sub"])
    return {"ok": True}
