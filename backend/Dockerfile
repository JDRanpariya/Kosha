FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install deps only (no source needed)

COPY pyproject.toml ./
RUN pip install --no-cache-dir "fastapi>=0.111" "uvicorn[standard]>=0.30" \
    "sqlalchemy>=2.0" "psycopg2-binary>=2.9" "pgvector>=0.3" \
    "alembic>=1.13" "pydantic>=2.7" "pydantic-settings>=2.3" \
    "feedparser>=6.0" "markdownify>=0.13" "httpx>=0.27" \
    "spotipy>=2.23" "google-api-python-client>=2.130" \
    "google-auth-oauthlib>=1.2" "celery[redis]>=5.4" "redis>=5.0"

# Copy source and install package (fast — deps already cached)

COPY . .
RUN pip install --no-cache-dir --no-deps .

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
