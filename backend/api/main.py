# backend/api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import digest, sources, feedback
from backend.core.config import settings

app = FastAPI(
    title="Kosha API",
    description="Personal AI-powered content aggregator",
    version="0.1.0"
)

# CORS for frontend

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes

app.include_router(digest.router, prefix="/api/digest", tags=["digest"])
app.include_router(sources.router, prefix="/api/sources", tags=["sources"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["feedback"])

@app.get("/health")
def health_check():
    return {"status": "healthy"}
