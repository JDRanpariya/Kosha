# backend/api/routes/youtube_oauth.py

import json
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db, ensure_user_exists
from backend.core.config import settings
from backend.core.logging import get_logger
from backend.db.models import Source

logger = get_logger(__name__)

router = APIRouter()

_SCOPES = "https://www.googleapis.com/auth/youtube.readonly"
_GOOGLE_AUTH_URL  = "https://accounts.google.com/o/oauth2/v2/auth"
_GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


def _redirect_uri(request: Request) -> str:
    """
    Build the redirect URI from the actual incoming request so it works
    in dev (http://localhost:8000) and prod (https://your-domain.com)
    without any manual configuration.
    """
    return str(request.base_url).rstrip("/") + "/api/youtube/oauth/callback"


@router.get("/start")
def youtube_oauth_start(request: Request):
    """Redirect browser to Google's OAuth consent screen."""
    client_id = settings.YOUTUBE_CLIENT_ID
    if not client_id:
        raise HTTPException(
            status_code=503,
            detail="YouTube OAuth not configured — add youtube_client_id secret",
        )

    params = {
        "client_id": client_id,
        "redirect_uri": _redirect_uri(request),
        "response_type": "code",
        "scope": _SCOPES,
        "access_type": "offline",
        "prompt": "consent",
    }
    url = f"{_GOOGLE_AUTH_URL}?{urlencode(params)}"
    logger.info(f"Starting YouTube OAuth flow, redirect_uri={_redirect_uri(request)}")
    return RedirectResponse(url)


@router.get("/callback")
def youtube_oauth_callback(
    request: Request,
    code: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(ensure_user_exists),
):
    """Exchange auth code for tokens, persist as a source, redirect to frontend."""
    client_id     = settings.YOUTUBE_CLIENT_ID
    client_secret = settings.YOUTUBE_CLIENT_SECRET
    redirect_uri  = _redirect_uri(request)

    logger.info(f"OAuth callback received, exchanging code, redirect_uri={redirect_uri}")

    try:
        resp = httpx.post(
            _GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
            timeout=15,
        )
        resp.raise_for_status()
        token_data = resp.json()
    except httpx.HTTPError as exc:
        logger.error(f"Token exchange failed: {exc}")
        raise HTTPException(status_code=502, detail="Token exchange failed")

    access_token  = token_data.get("access_token", "")
    refresh_token = token_data.get("refresh_token", "")

    if not access_token:
        raise HTTPException(status_code=502, detail="No access token returned")

    existing = (
        db.query(Source)
        .filter(Source.user_id == user_id, Source.type == "youtube_subscriptions")
        .first()
    )

    if existing:
        existing.config_json = {
            **existing.config_json,
            "access_token": access_token,
            "refresh_token": refresh_token or existing.config_json.get("refresh_token", ""),
            "client_id": client_id,
            "client_secret": client_secret,
        }
        db.commit()
        logger.info(f"Updated YouTube Subscriptions tokens for user {user_id}")
    else:
        source = Source(
            user_id=user_id,
            name="YouTube Subscriptions",
            type="youtube_subscriptions",
            enabled=True,
            config_json={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "client_id": client_id,
                "client_secret": client_secret,
            },
        )
        db.add(source)
        db.commit()
        logger.info(f"Created YouTube Subscriptions source for user {user_id}")

    return RedirectResponse("/sources?youtube_connected=1")
