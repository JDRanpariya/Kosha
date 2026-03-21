# Kosha 🪴

A fully open-source, self-hosted personal content aggregator. Kosha pulls from RSS feeds, arXiv, Spotify podcasts, and YouTube channels, stores everything in a searchable Postgres + pgvector database, and serves it through a clean REST API.

---

## Prerequisites

| Tool | Minimum Version | Install |
|---|---|---|
| Python | 3.11 | [python.org](https://python.org) |
| uv | latest | `pip install uv` or [docs.astral.sh/uv](https://docs.astral.sh/uv) |
| Docker + Compose | 24 / v2 | [docs.docker.com](https://docs.docker.com) |
| PostgreSQL *(local dev only)* | 15 with pgvector | see below |

> **Tip** — easiest path for local dev: skip installing Postgres locally and use the Docker Compose recipe in the next section to spin up only the infrastructure services (Postgres, Redis, MinIO) while running the Python code directly on your machine.

---

## Local Development (no Docker)

### 1. Clone and enter the repo

```bash
git clone https://github.com/your-org/kosha.git
cd kosha
```

### 2. Create a virtual environment and install dependencies

```bash
uv venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# Core dependencies
uv pip install -e .

# Optional: ML extras (sentence-transformers, torch) for embeddings
uv pip install -e ".[ml]"

# Dev tools (pytest, ruff, mypy)
uv pip install -e ".[dev]"
```

### 3. Install and configure PostgreSQL with pgvector

**macOS (Homebrew):**

```bash
brew install postgresql@18
brew install pgvector
echo 'export PATH="/opt/homebrew/opt/postgresql@18/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
pg_ctl -D $(brew --prefix)/var/postgresql@18 -l $(brew --prefix)/var/postgresql@18/server.log start
```

**Ubuntu/Debian:**

```bash
sudo apt install postgresql postgresql-contrib

# pgvector — build from source or use the apt repo:
# https://github.com/pgvector/pgvector#installation
```

**Create the database:**

```bash
psql postgres -c "ALTER USER kosha SUPERUSER;"
psql postgres <<SQL
  CREATE USER kosha WITH PASSWORD 'localpassword';
  CREATE DATABASE kosha_db OWNER kosha;
  GRANT ALL PRIVILEGES ON DATABASE kosha_db TO kosha;
SQL
```

**Enable the extension** (Alembic does this automatically on migrate, but you can do it manually if needed):

```bash
psql postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 4. Create secrets files

The app reads secrets from `infra/secrets/<name>.txt`. Create the directory (it is already git-ignored):

```bash
# Mandatory
echo "localpassword"       > infra/secrets/db_password.txt

# Optional — only needed if you use those connectors
echo "your_minio_user"     > infra/secrets/minio_root_user.txt
echo "your_minio_pass"     > infra/secrets/minio_root_password.txt
echo "your_spotify_id"     > infra/secrets/spotify_client_id.txt
echo "your_spotify_secret" > infra/secrets/spotify_client_secret.txt
echo "your_yt_api_key"     > infra/secrets/youtube_api_key.txt
```

### 5. Create a `.env` file for non-secret config

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

> `.env` is git-ignored. Values here override the defaults in `backend/core/config.py`.

### 6. Run database migrations

```bash
alembic upgrade head
```

### 7. Start the API server

```bash
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

Visit [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive Swagger UI.

### 8. Seed some sources *(optional)*

```bash
python tests/backend/seed_data.py
```

### 9. Run a manual ingestion cycle

```bash
python -m backend.scripts.run_ingestion
```

---

## Local Development (Docker for services only)

This is the recommended workflow. Docker runs Postgres, Redis, and MinIO; your Python code runs natively for fast iteration.

### 1. Start only the infrastructure services

```bash
# First, make sure secret files exist (see step 4 above)
docker compose up postgres redis minio -d
```

### 2. Point your `.env` at the Docker services

```bash
cat > .env <<EOF
DB_HOST=localhost          # Docker publishes port 5432 to localhost
DB_PORT=5432
DB_USER=kosha
DB_NAME=kosha_db

REDIS_HOST=localhost
REDIS_PORT=6379
EOF
```

### 3. Follow steps 2, 4, 6–9 from the previous section

Everything else is identical — you just don't need a local Postgres install.

---

## Full Docker Deployment

### 1. Populate all secret files

```
infra/secrets/
├── db_password.txt
├── minio_root_user.txt
├── minio_root_password.txt
├── spotify_client_id.txt       # leave empty string if unused
├── spotify_client_secret.txt
└── youtube_api_key.txt
```

```bash
# Quick scaffold — replace values before running in production
echo "changeme_strong_password" > infra/secrets/db_password.txt
echo "minioadmin"               > infra/secrets/minio_root_user.txt
echo "changeme_minio_pass"      > infra/secrets/minio_root_password.txt
echo ""                         > infra/secrets/spotify_client_id.txt
echo ""                         > infra/secrets/spotify_client_secret.txt
echo ""                         > infra/secrets/youtube_api_key.txt
```

### 2. Build and start all services

```bash
docker compose up --build -d
```

### 3. Run migrations inside the container

```bash
docker compose exec backend alembic upgrade head
```

### 4. Verify everything is running

```bash
docker compose ps
curl http://localhost:8000/health   # → {"status":"healthy"}
```

### 5. View logs

```bash
docker compose logs -f backend
docker compose logs -f postgres
```

### 6. Tear down

```bash
docker compose down      # keep volumes
docker compose down -v   # also delete all data volumes
```

---

## Secrets Reference

| File | Purpose | Required |
|---|---|---|
| `db_password.txt` | Postgres password | ✅ Always |
| `minio_root_user.txt` | MinIO admin user | Only if using MinIO |
| `minio_root_password.txt` | MinIO admin password | Only if using MinIO |
| `spotify_client_id.txt` | Spotify API client ID | Only for Spotify connector |
| `spotify_client_secret.txt` | Spotify API secret | Only for Spotify connector |
| `youtube_api_key.txt` | YouTube Data API v3 key | Only for YouTube connector |

**Secret resolution order** (highest priority first):

1. `/run/secrets/<name>` — Docker secrets (production)
2. `infra/secrets/<name>.txt` — local file (development)
3. Empty string default (connector will be skipped or raise a config error)

---

## Database Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Roll back one step
alembic downgrade -1

# Auto-generate a migration after changing models.py
alembic revision --autogenerate -m "describe your change"

# Show current revision
alembic current

# Show full migration history
alembic history
```

> ⚠️ The pgvector extension must exist in the database before running migrations. The `env.py` migration runner creates it automatically via `CREATE EXTENSION IF NOT EXISTS vector`.

---

## Running Ingestion

**Manual one-shot run:**

```bash
# Natively
python -m backend.scripts.run_ingestion

# Inside Docker
docker compose exec backend python -m backend.scripts.run_ingestion
```

**Scheduled (Celery — coming soon)**

Celery worker and beat scheduler will be added as separate Compose services. For now, use a cron job to call the manual script:

```bash
# /etc/cron.d/kosha  — run ingestion every 6 hours
0 */6 * * * cd /path/to/kosha && .venv/bin/python -m backend.scripts.run_ingestion
```

---

## API Reference

The full interactive docs are at [http://localhost:8000/docs](http://localhost:8000/docs).

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/api/digest/daily` | Items from the last 24 hours |
| `GET` | `/api/digest/item/{id}` | Full item with parsed content |
| `GET` | `/api/sources/` | List all configured sources |
| `POST` | `/api/feedback/` | Submit feedback (stub) |

---

## Adding a New Source

### 1. Write the connector

Create `connectors/<category>/<type>.py` following the `BaseConnector` interface:

```python
from connectors.base import BaseConnector, ConnectorConfig
from schemas.connector_output import ConnectorOutput

class MyConfig(ConnectorConfig):
    some_field: str

class MyConnector(BaseConnector):
    ConfigModel = MyConfig

    def fetch(self) -> list[ConnectorOutput]:
        # ... call an API, parse a feed, etc.
        return [ConnectorOutput(...)]
```

### 2. Register it

Add an entry to `connectors/registry.py`:

```python
from connectors.<category>.<type> import MyConnector

CONNECTOR_REGISTRY["<category>"] = {
    "<type>": {
        "class": MyConnector,
        "display_name": "Human Readable Name",
        "required_fields": ["some_field"],
    },
}
```

### 3. Map the category in the ingestion script

If you introduced a new category string, add it to `CATEGORY_MAP` in `backend/scripts/run_ingestion.py`:

```python
CATEGORY_MAP = {
    ...
    "<type>": "<category>",
}
```

### 4. Add a row to the sources table

```python
# In a seed script or via psql
Source(
    name="My New Source",
    type="<type>",
    enabled=True,
    config_json={"some_field": "value"},
)
```

---

## Project Structure

```
kosha/
├── backend/
│   ├── api/
│   │   ├── main.py              # FastAPI app, middleware, router mounts
│   │   └── routes/
│   │       ├── digest.py        # /api/digest endpoints
│   │       ├── sources.py       # /api/sources endpoints
│   │       └── feedback.py      # /api/feedback endpoints
│   ├── core/
│   │   └── config.py            # Settings (secrets + env vars)
│   ├── db/
│   │   ├── database.py          # SQLAlchemy engine + session factory
│   │   ├── models.py            # ORM models (User, Source, Item, …)
│   │   └── migrations/          # Alembic migration scripts
│   └── services/
│       └── ingestion.py         # Core fetch → store pipeline
├── connectors/
│   ├── base.py                  # BaseConnector + ConnectorConfig
│   ├── registry.py              # Maps category/type → connector class
│   ├── newsletters/rss.py
│   ├── papers/arxiv.py
│   ├── podcasts/spotify.py
│   └── youtube/youtube.py
├── schemas/
│   └── connector_output.py      # Shared Pydantic output schema
├── infra/
│   └── secrets/                 # *.txt files (git-ignored)
├── tests/
├── compose.yml
├── alembic.ini
└── pyproject.toml
```

---
