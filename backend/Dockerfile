FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

# Cache layer: deps only

COPY pyproject.toml ./
RUN uv pip install --system --no-cache -r pyproject.toml || true  

# Note: uv can read pyproject.toml deps directly

COPY . .
RUN uv pip install --system --no-cache --no-deps .

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
