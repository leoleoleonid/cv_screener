# AI CV Screener

Minimal instructions to run the project.

## Prerequisites

- Docker Engine + Docker Compose
- Google Gemini API key stored in `backend/.env` (see `backend/.env.example` for required vars)

## Development

```bash
docker compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:3000

The dev stack uses `network_mode: host`, so this command works best on Linux. On macOS/Windows use the production compose file below.

## Production‑style stack

```bash
docker compose -f docker-compose.prod.yml up --build
```

- Backend exposed on http://localhost:8000
- Frontend exposed on http://localhost:3000 (served via Nginx)

## Useful API endpoints

- `POST /cv/generate` – generate a new CV via Gemini
- `POST /cv/generate-mock` – quick mock CV
- `GET /cv` – list available PDF names
- `POST /rag/ingest` – rebuild FAISS index
- `POST /chat` – ask questions backed by RAG
