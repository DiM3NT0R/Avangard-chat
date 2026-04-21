from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.utils import get_openapi
from pydantic import ValidationError

from app.database import init_db
from app.dependencies import verify_token
from app.router import auth, messages, rooms, users
from app.schema.message import MessageCreate
from app.service.message_service import MessageService
from app.service.room_service import RoomService
from app.ws.manager import manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Avangard API",
    lifespan=lifespan,
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/user", tags=["Users"])
app.include_router(rooms.router, prefix="/room", tags=["Rooms"])
app.include_router(messages.router, prefix="/message", tags=["Messages"])


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title="Avangard API", version="0.0.1", routes=app.routes)
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.websocket("/ws/{room_id}")
async def chat(websocket: WebSocket, room_id: str, token: str):
    try:
        payload = await verify_token(token)
        await RoomService.get_for_user(room_id, payload["sub"])
    except HTTPException:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_json()
            try:
                message_input = MessageCreate(
                    room_id=room_id,
                    text=data["text"],
                )
            except (KeyError, TypeError, ValidationError):
                await websocket.send_json(
                    {"type": "error", "detail": "Invalid message payload"}
                )
                continue

            try:
                message = await MessageService.send(
                    data=message_input,
                    sender_id=payload["sub"],
                )
            except HTTPException as exc:
                await websocket.send_json({"type": "error", "detail": exc.detail})
                if exc.status_code in {401, 403}:
                    await websocket.close(code=1008)
                    break
                continue

            message_payload = await message.to_response()
            await manager.broadcast(
                room_id,
                jsonable_encoder({"type": "message", "message": message_payload}),
            )
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, room_id)
