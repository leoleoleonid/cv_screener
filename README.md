# AI CV Screener

Minimal instructions to run the project.

## Prerequisites

- Docker Engine + Docker Compose
- Google Gemini API key stored in `backend/.env` (see `backend/.env.example` for required vars)

## Development

Bring up the full stack (API + Celery worker + Redis + Postgres + frontend) with:

```bash
docker compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Redis: 6379 (Celery broker)
- Postgres: 5432 (Celery result backend)

## Production‑style stack

```bash
docker compose -f docker-compose.prod.yml up --build
```

Same services as above; frontend is built with the production Dockerfile and served on port 3000.

## Useful API endpoints

- `POST /cv/generate` – queues a new CV generation task
- `POST /cv/generate-mock` – queues a mock CV generation task
- `GET /cv` – list available PDF names
- `POST /rag/ingest` – queues FAISS rebuild
- `POST /chat` – ask questions backed by RAG
- `GET /tasks/{task_id}` – poll task status/result
