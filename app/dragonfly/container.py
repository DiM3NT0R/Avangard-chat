from functools import lru_cache

from app.core.config import settings
from app.dragonfly.adapter import DragonflyAdapter
from app.dragonfly.service import DragonflyService


@lru_cache
def get_dragonfly_adapter_singleton() -> DragonflyAdapter:
    return DragonflyAdapter(
        url=settings.dragonfly.url,
        connect_timeout_seconds=settings.dragonfly.timeout.connect_seconds,
        socket_timeout_seconds=settings.dragonfly.timeout.socket_seconds,
    )


@lru_cache
def get_dragonfly_service_singleton() -> DragonflyService:
    return DragonflyService(
        adapter=get_dragonfly_adapter_singleton(),
        settings=settings,
    )
