from fastapi import APIRouter, Depends, HTTPException

from app.modules.system.dependencies import get_dragonfly_service, verify_token
from app.modules.users.model import User
from app.modules.users.schemas import UserResponse, serialize_user_response
from app.platform.backends.dragonfly.service import DragonflyService
from app.platform.http.errors import error_responses

router = APIRouter()


async def _serialize_user_with_presence(
    user: User,
    dragonfly: DragonflyService,
) -> UserResponse:
    is_online, last_time_online = await dragonfly.get_user_presence(user.id)
    return serialize_user_response(user).model_copy(
        update={
            "is_online": is_online,
            "last_time_online": last_time_online or user.last_time_online,
        }
    )


@router.get(
    "/me",
    response_model=UserResponse,
    responses=error_responses(401, 404),
)
async def get_me(
    user: dict = Depends(verify_token),
    dragonfly: DragonflyService = Depends(get_dragonfly_service),
):
    result = await User.find_one(User.id == user["sub"])
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return await _serialize_user_with_presence(result, dragonfly)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    responses=error_responses(401, 404),
)
async def get_user(
    user_id: str,
    current_user: dict = Depends(verify_token),
    dragonfly: DragonflyService = Depends(get_dragonfly_service),
):
    del current_user
    result = await User.find_one(User.id == user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return await _serialize_user_with_presence(result, dragonfly)
