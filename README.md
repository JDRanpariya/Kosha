# [Kosha](https://jdranpariya.github.io/projects/kosha/) 🪷

A fully open-source, self-hosted personal content aggregator. Kosha pulls from RSS feeds, arXiv, Hacker News, Reddit, YouTube channels, and email newsletters — stores everything in a searchable Postgres + pgvector database, and serves it through a clean REST API with a warm, reading-focused frontend.

---

## Prerequisites

| Tool | Minimum Version | Install |
|---|---|---|
| Python | 3.11 | [python.org](https://python.org) |
| uv | latest | `pip install uv` or [docs.astral.sh/uv](https://docs.astral.sh/uv) |
| Docker + Compose | 24 / v2 | [docs.docker.com](https://docs.docker.com) |
| Node / Bun *(frontend only)* | Bun 1.1+ | [bun.sh](https://bun.sh) |

---

## Local Development (Docker for services, code runs natively)

This is the recommended workflow. Docker runs Postgres and Redis; your Python and frontend code run natively for fast iteration.

### 1. Clone and enter the repo

```bash
git clone https://github.com/your-org/kosha.git
cd kosha
```

### 2. Create a virtual environment and install dependencies

```bash
uv venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

### Core dependencies

uv pip install -e .

### Dev tools (pytest, ruff)

uv pip install -e ".[dev]"
```

### 3. Create secrets files

The app reads secrets from `infra/secrets/<name>.txt`. The directory is git-ignored.

```bash
mkdir -p infra/secrets

### Required

echo "localpassword"        > infra/secrets/db_password.txt

### Optional — leave empty if you don't use the connector

echo ""                     > infra/secrets/youtube_api_key.txt
echo ""                     > infra/secrets/email_username.txt
echo ""                     > infra/secrets/email_password.txt
```

### 4. Create a `.env` file

```bash
cat > .env <<EOF
DB_HOST=localhost
DB_PORT=5432
DB_USER=kosha
DB_NAME=kosha_db
REDIS_HOST=localhost
REDIS_PORT=6379
EOF
```

### 5. Start infrastructure services

```bash
docker compose up postgres redis -d
```

### 6. Run database migrations

```bash
alembic upgrade head
```

### 7. Start the backend

```bash
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

Visit [http://localhost:8000/docs](http://localhost:8000/docs) for the Swagger UI.

### 8. Start the frontend

```bash
cd frontend
bun install
bun run dev
```

Visit [http://localhost:5173](http://localhost:5173). The Vite dev server proxies `/api` requests to the backend.

### 9. Add sources and trigger ingestion

Use the Sources page in the UI, or seed manually:

```bash
python -m backend.scripts.run_ingestion
```

---

## Full Docker Deployment

### 1. Populate secret files

```bash
echo "changeme_strong_password" > infra/secrets/db_password.txt
echo ""                         > infra/secrets/youtube_api_key.txt
echo ""                         > infra/secrets/email_username.txt
echo ""                         > infra/secrets/email_password.txt
```

### 2. Build and start all services

```bash
docker compose up --build -d
```

### 3. Run migrations

```bash
docker compose exec backend alembic upgrade head
```

### 4. Verify

```bash
docker compose ps
curl http://localhost:8000/health   # → {"status":"healthy"}
```

### 5. Tear down

```bash
docker compose down      # keep volumes
docker compose down -v   # delete all data
```

---

## Secrets Reference

| File | Purpose | Required |
|---|---|---|
| `db_password.txt` | Postgres password | ✅ Always |
| `youtube_api_key.txt` | YouTube Data API v3 key | Only for YouTube connector |
| `email_username.txt` | IMAP email address | Only for Email connector |
| `email_password.txt` | IMAP app password | Only for Email connector |

**Resolution order** (highest priority first):

1. `/run/secrets/<name>` — Docker secrets (production)
2. `infra/secrets/<name>.txt` — local file (development)
3. Empty string default — connector will be skipped

---

## Supported Connectors

| Type | Category | Auth Required | Example Config |
|---|---|---|---|
| `rss` | Newsletters | None | `{"feed_url": "https://example.com/feed"}` |
| `substack` | Newsletters | None | `{"publication_url": "https://stratechery.substack.com"}` |
| `email_imap` | Newsletters | IMAP credentials | `{"imap_host": "imap.gmail.com", "sender_filter": "@substack.com"}` |
| `arxiv` | Papers | None | `{"categories": ["cs.AI", "stat.ML"]}` |
| `hackernews` | Social | None | `{"tags": "front_page", "min_points": 100}` |
| `reddit` | Social | None | `{"subreddits": ["MachineLearning", "LocalLLaMA"]}` |
| `youtube` | Videos | API key | `{"channels": ["UCBcRF18a7Qf58cCRy5xuWwQ"]}` |

---

## Ingestion

There is no background scheduler built in. Content is fetched on demand.

**From the UI:**
Click the ⟳ button in the header, or use per-source "Fetch now" on the Sources page.

**From the API:**

```bash

### All enabled sources

curl -X POST http://localhost:8000/api/ingest/trigger-all

### Single source

curl -X POST http://localhost:8000/api/ingest/trigger/1
```

**CLI:**

```bash
python -m backend.scripts.run_ingestion
```

**Scheduled (cron):**

```bash

### crontab -e

0 */6 * * * curl -s -X POST http://localhost:8000/api/ingest/trigger-all
```

---

## Database Migrations

```bash
alembic upgrade head                              # apply all
alembic downgrade -1                              # roll back one
alembic revision --autogenerate -m "description"  # generate from model changes
alembic current                                   # show current revision
alembic history                                   # full history
```

> The pgvector extension is created automatically by the migration runner.

---

## API Reference

Full interactive docs at [http://localhost:8000/docs](http://localhost:8000/docs).

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/api/digest/daily` | Items from the last 24 h (excludes dismissed) |
| `GET` | `/api/digest/item/{id}` | Full item with parsed content |
| `GET` | `/api/search/?q=...` | Semantic search via pgvector |
| `GET` | `/api/sources/` | List configured sources |
| `POST` | `/api/sources/` | Create a source |
| `PATCH` | `/api/sources/{id}` | Update a source |
| `DELETE` | `/api/sources/{id}` | Delete a source |
| `POST` | `/api/feedback/` | Save / dismiss / unsave an item |
| `GET` | `/api/feedback/saved` | Reading list |
| `POST` | `/api/ingest/trigger-all` | Fetch all enabled sources |
| `POST` | `/api/ingest/trigger/{id}` | Fetch a single source |

---

## Adding a New Connector

### 1. Write the connector

Create `connectors/<category>/<type>.py`:

```python
from connectors.base import BaseConnector, ConnectorConfig
from schemas.connector_output import ConnectorOutput

class MyConfig(ConnectorConfig):
    some_field: str

class MyConnector(BaseConnector):
    ConfigModel = MyConfig
    source_type = "my_type"

    def fetch(self) -> list[ConnectorOutput]:
        # call an API, parse a feed, etc.
        return [ConnectorOutput(title=..., url=..., content=...)]
```

### 2. Register it in `connectors/registry.py`

```python
from connectors.<category>.<type> import MyConnector

CONNECTOR_REGISTRY["<category>"]["<type>"] = {
    "class": MyConnector,
    "display_name": "My Source",
    "required_fields": ["some_field"],
}
```

### 3. Map the category in `backend/api/routes/ingest.py`

```python
CATEGORY_MAP["<type>"] = "<category>"
```

### 4. Add the type to `SourceType` in `backend/api/schemas.py`

```python
SourceType = Literal[..., "<type>"]
```

### 5. Create a source via the API or UI

```bash
curl -X POST http://localhost:8000/api/sources/ \
  -H "Content-Type: application/json" \
  -d '{"name": "My Source", "type": "<type>", "config_json": {"some_field": "value"}}'
```

---

## Project Structure

```
kosha/
├── backend/
│   ├── api/
│   │   ├── main.py            # FastAPI app, middleware, router mounts
│   │   ├── schemas.py         # All Pydantic request/response models
│   │   ├── dependencies.py    # get_db, ensure_user_exists
│   │   └── routes/
│   │       ├── digest.py      # /api/digest/*
│   │       ├── sources.py     # /api/sources/*
│   │       ├── feedback.py    # /api/feedback/*
│   │       ├── ingest.py      # /api/ingest/*
│   │       └── search.py      # /api/search/*
│   ├── core/
│   │   ├── config.py          # Settings (secrets + env vars)
│   │   ├── constants.py       # Magic numbers, model names
│   │   └── logging.py         # Structured logging + correlation IDs
│   ├── db/
│   │   ├── database.py        # SQLAlchemy engine + session
│   │   ├── models.py          # ORM models (User, Source, Item, …)
│   │   └── migrations/        # Alembic scripts
│   └── services/
│       ├── embedding.py       # Singleton SentenceTransformer wrapper
│       ├── ingestion.py       # Fetch → deduplicate → store → embed
│       └── items.py           # Query helpers for items
├── connectors/
│   ├── base.py                # BaseConnector + ConnectorConfig
│   ├── registry.py            # Maps type → connector class
│   ├── subscriptions/
│   │   ├── rss.py
│   │   ├── substack.py
│   │   ├── email_imap.py
│   │   ├── arxiv.py
│   │   └── youtube.py
│   └── discovery/
│       ├── hackernews.py
│       └── reddit.py
├── frontend/
│   ├── src/
│   │   ├── pages/             # DigestPage, SourcesPage, etc.
│   │   ├── components/        # ItemCard, ItemDetail, Layout, Sidebar
│   │   ├── hooks/             # useItems, useSources, useSearch
│   │   ├── lib/               # api.ts, utils.ts
│   │   ├── stores/            # Zustand UI state
│   │   └── types/             # TypeScript interfaces
│   ├── package.json
│   └── vite.config.ts
├── schemas/
│   └── connector_output.py    # Shared output schema for connectors
├── infra/
│   └── secrets/               # *.txt credential files (git-ignored)
├── tests/
├── compose.yml                # Postgres + Redis + backend + frontend
├── alembic.ini
└── pyproject.toml
```

---

## Architecture

```
┌─────────────┐     ┌───────────────────┐     ┌──────────────┐
│  Frontend    │────▶│  FastAPI Backend   │────▶│  PostgreSQL  │
│  (Vite+React)│     │                   │     │  + pgvector  │
└─────────────┘     │  /api/digest      │     └──────────────┘
                    │  /api/sources     │            │
                    │  /api/search      │     ┌──────────────┐
                    │  /api/feedback    │     │    Redis      │
                    │  /api/ingest ─────│────▶│  (cache)     │
                    └────────┬──────────┘     └──────────────┘
                             │
                    ┌────────▼──────────┐
                    │   Connectors      │
                    │  RSS · arXiv · HN │
                    │  Reddit · YouTube │
                    │  Email · Substack │
                    └───────────────────┘
```

**Data flow:** Trigger ingestion → Connectors fetch content → Deduplicate by URL hash → Store items + content → Generate embeddings → Available in digest/search.

---

