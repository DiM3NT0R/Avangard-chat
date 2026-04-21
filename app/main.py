from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.database import init_db
from app.router import auth, messages, rooms, users, ws


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
app.include_router(ws.router, prefix="/ws", tags=["WebSockets"])


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
