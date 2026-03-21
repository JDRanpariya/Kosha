# backend/api/main.py

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import digest, sources, feedback, ingest, search
from backend.api.routes import youtube_oauth
from backend.api.schemas import StatusResponse
from backend.core.config import settings
from backend.core.logging import setup_logging, set_correlation_id, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(level="INFO")
    logger.info("Kosha API starting up")
    yield
    logger.info("Kosha API shutting down")


app = FastAPI(
    title="Kosha API",
    description="Personal AI-powered content aggregator",
    version="0.1.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    cid = request.headers.get("X-Correlation-ID")
    set_correlation_id(cid)
    response = await call_next(request)
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sources.router,       prefix="/api/sources",  tags=["sources"])
app.include_router(ingest.router,        prefix="/api/ingest",   tags=["ingest"])
app.include_router(search.router,        prefix="/api/search",   tags=["search"])
app.include_router(digest.router,        prefix="/api/digest",   tags=["digest"])
app.include_router(feedback.router,      prefix="/api/feedback", tags=["feedback"])
app.include_router(youtube_oauth.router, prefix="/api/youtube/oauth", tags=["youtube"])


@app.get("/health", response_model=StatusResponse)
def health_check() -> StatusResponse:
    return StatusResponse(status="healthy")
