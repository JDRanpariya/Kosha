# Backend

The backend is the central hub of Kosha. It orchestrates ingestion, stores and serves data, handles business logic (digests, reading queues, categories), exposes APIs to the frontend and Obsidian plugin, and eventually integrates ML models and RLHF pipelines.

- We choose to go with FastAPI
- We choose to follow this best practices for FastAPI by [Zhanymanov](https://github.com/zhanymkanov/fastapi-best-practices?tab=readme-ov-file#project-structure)

## Structure

backend/
  api/          # FastAPI routes (digest, sources, feedback)
  core/         # Config + secrets loading
  db/           # SQLAlchemy models, migrations (Alembic)
  services/     # Business logic (ingestion pipeline)
  scripts/      # One-off scripts: init_db, run_ingestion

