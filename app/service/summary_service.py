from datetime import datetime, UTC
from typing import Optional

from bson import ObjectId
from openai import AsyncOpenAI

from app.config import settings
from app.model.chat_room import ChatRoom
from app.model.message import Message

_client = AsyncOpenAI(
    api_key=settings.groq_api_key,
    base_url="https://api.groq.com/openai/v1",
)

SYSTEM_PROMPT = (
    "You are a concise chat summarizer. "
    "Given a list of chat messages with timestamps, produce a brief summary "
    "(3-5 sentences) highlighting the key topics and decisions. "
    "Reply in the same language as the messages."
)

# Жёсткий потолок — даже если диапазон огромный
HARD_CAP = 100


class SummaryService:

    @staticmethod
    def _build_conditions(
        room,
        user_id: str,
        from_dt: Optional[datetime],
        to_dt: Optional[datetime],
        unread_only: bool,
    ) -> list:
        conditions: list = [
            Message.room.id == room.id,
            Message.is_deleted == False,
        ]

        if from_dt:
            conditions.append(Message.created_at >= from_dt)
        if to_dt:
            conditions.append(Message.created_at <= to_dt)

        if unread_only:
            # User.id — строка (Keycloak sub), не ObjectId.
            # Ищем документы, где user_id НЕ встречается в массиве ссылок read_by.
            # $not + $elemMatch корректно обрабатывает и пустой массив.
            conditions.append(
                {"read_by": {"$not": {"$elemMatch": {"$id": user_id}}}}
            )

        return conditions

    @staticmethod
    def _detect_mode(
        unread_only: bool,
        from_dt: Optional[datetime],
        to_dt: Optional[datetime],
    ) -> str:
        has_range = bool(from_dt or to_dt)
        if unread_only and has_range:
            return "unread+range"
        if unread_only:
            return "unread"
        if has_range:
            return "range"
        return "recent"

    @staticmethod
    async def summarize_room(
        room_id: str,
        user_id: str,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
        unread_only: bool = False,
    ) -> tuple[str, int, bool, str]:
        """Returns (summary, count, was_capped, mode)"""

        room = await ChatRoom.get(room_id)
        if not room:
            return "Room not found.", 0, False, "none"

        conditions = SummaryService._build_conditions(
            room, user_id, from_dt, to_dt, unread_only
        )

        mode = SummaryService._detect_mode(unread_only, from_dt, to_dt)

        # Для режима "recent" — берём последние N, иначе всё + HARD_CAP
        if mode == "recent":
            messages = (
                await Message.find(*conditions)
                .sort(-Message.created_at)
                .limit(settings.summary_max_messages)
                .to_list()
            )
            messages.reverse()
            was_capped = False  # В режиме "recent" cap — это норма, не флаг
        else:
            # Для диапазонных режимов: считаем сколько есть, потом берём HARD_CAP
            total_count = await Message.find(*conditions).count()
            messages = (
                await Message.find(*conditions)
                .sort(+Message.created_at)
                .limit(HARD_CAP)
                .to_list()
            )
            was_capped = total_count > HARD_CAP

        if not messages:
            label = "unread messages" if unread_only else "messages"
            return f"No {label} found for the given criteria.", 0, False, mode

        # --- Сборка текста с жёстким обрезанием ---
        lines = []
        for msg in messages:
            await msg.fetch_link(Message.sender)
            sender = getattr(msg.sender, "username", "?")
            ts = msg.created_at.strftime("%d.%m %H:%M")
            # Обрезаем длинные сообщения
            text = msg.text[: settings.summary_max_chars_per_message]
            if len(msg.text) > settings.summary_max_chars_per_message:
                text += "…"
            lines.append(f"[{ts}] {sender}: {text}")

        chat_text = "\n".join(lines)

        response = await _client.chat.completions.create(
            model=settings.summary_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Chat messages:\n\n{chat_text}"},
            ],
            max_tokens=300,
            temperature=0.3,
        )

        summary = response.choices[0].message.content.strip()
        return summary, len(messages), was_capped, mode