# Avangard Chat Backend

[![CI](https://github.com/DiM3NT0R/Avangard-chat/actions/workflows/ci.yml/badge.svg)](https://github.com/DiM3NT0R/Avangard-chat/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-proprietary-red)](https://github.com/DiM3NT0R/Avangard-chat/blob/main/LICENSE)
[![Coverage](https://codecov.io/gh/DiM3NT0R/Avangard-chat/graph/badge.svg)](https://codecov.io/gh/DiM3NT0R/Avangard-chat)

Бэкенд чат-приложения на FastAPI:
- JWT-аутентификация и refresh-сессии
- групповые чаты и личные сообщения
- realtime-обмен сообщениями через ws
- зашифрованное хранение сообщений
- полнотекстовый поиск (Typesense)
- счётчики непрочитанных

## Что реализовано сейчас

- Auth
  - регистрация, логин, refresh, logout
  - access token в JSON, refresh token в HttpOnly cookie
  - TTL по умолчанию: access 15 минут, refresh 30 дней
- Rooms
  - групповые комнаты и лс
  - управление участниками групп
  - список комнат
- Messages
  - отправка, редактирование, удаление, отметка прочитанного
  - история и поиск
  - счётчики непрочитанных и read-state по комнате
- WebSocket
  - realtime-сообщения, presence, typing, delivery-state события
  - идемпотентность отправки сообщений

## Шифрование и хранение сообщений

- Текст сообщений хранится в MongoDB в зашифрованном виде.
- Алгоритм: `AES-256-GCM`.
- Для каждого сообщения используется отдельный случайный nonce.
- Контекст привязывает шифртекст к `room_id` и `sender_id`.
- Хранятся поля: ciphertext, nonce, key id, aad.
- Удалённые сообщения soft-delete (`is_deleted=true`) и в API отдаются как `[deleted]`.

## Фоновые воркеры

Запускаются автоматически при старте приложения:

- Cleanup worker
  - обрабатывает асинхронные cleanup задачи с retry/backoff и dead-letter
  - очищает документы typesense и кэш после удаления сообщений/комнат
- Unread reconciliation worker
  - периодически пересчитывает unread-счётчики и исправляет дрейф

## Стэк

- FastAPI + Pydantic v2
- MongoDB + Beanie + Motor
- DragonflyDB (Redis protocol): rate limit, auth/session state, кэш, websocket presence/typing/pubsub
- Typesense: полнотекстовый поиск
- uv + pytest + ruff

## Запуск

```bash
docker compose up -d --build
```

API `http://localhost:8000`.

Некоторые эндпоинты:
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
- Liveness: `http://localhost:8000/health/live`
- Readiness: `http://localhost:8000/health/ready`

## Линтер

```bash
uv run --group dev ruff check .
uv run --group dev ruff format --check .
uv run --group dev pytest tests/unit tests/api
```

## Что пока не реализовано

- api загрузки файлов / медиа-хранилище
- speech-to-text / text-to-speech
- AI-модерация, перевод, саммаризация
- фронт

## Лицензия

См. [LICENSE](LICENSE).
