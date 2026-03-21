"""
GitHub connector — fetches:
  1. Latest releases from watched repos
  2. Trending repositories via the GitHub Search API

Rate limits:
  - Unauthenticated: 60 requests/hour
  - Authenticated:   5,000 requests/hour

  Set api_token to a personal access token (read:public_repo scope is sufficient).
"""

import logging
from datetime import datetime, timezone, timedelta

import httpx
from markdownify import markdownify as md

from connectors.base import BaseConnector, ConnectorConfig
from schemas.connector_output import ConnectorOutput

logger = logging.getLogger(__name__)

_API = "https://api.github.com"


class GitHubConfig(ConnectorConfig):
    api_token: str = ""
    repos: list[str] = []          # ["owner/repo", ...] for release tracking
    fetch_releases: bool = True    # pull latest releases for each repo
    fetch_trending: bool = True    # pull trending repos via Search API
    trending_language: str = ""   # "" = all languages
    trending_since: str = "daily" # daily | weekly | monthly
    max_results: int = 25          # max releases per repo AND max trending repos


class GitHubConnector(BaseConnector):
    """
    Fetches GitHub releases and trending repositories.

    Example configs
    ---------------
    Track specific repo releases + trending Python repos:
        {
            "api_token": "ghp_...",
            "repos": ["openai/whisper", "ollama/ollama"],
            "fetch_trending": true,
            "trending_language": "python",
            "trending_since": "weekly"
        }

    Only trending (no specific repos):
        {
            "fetch_releases": false,
            "fetch_trending": true,
            "trending_since": "daily",
            "max_results": 30
        }
    """

    ConfigModel = GitHubConfig
    source_type = "github"

    # ── private helpers ───────────────────────────────────────────────────────

    def _headers(self) -> dict:
        h = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "kosha-aggregator/1.0",
        }
        if self.config.api_token:
            h["Authorization"] = f"Bearer {self.config.api_token}"
        return h

    def _client(self) -> httpx.Client:
        return httpx.Client(headers=self._headers(), timeout=15)

    def _since_date(self) -> str:
        delta = {
            "daily": timedelta(days=1),
            "weekly": timedelta(weeks=1),
            "monthly": timedelta(days=30),
        }.get(self.config.trending_since, timedelta(days=1))
        return (datetime.now(timezone.utc) - delta).strftime("%Y-%m-%d")

    @staticmethod
    def _parse_github_datetime(raw: str | None) -> datetime | None:
        if not raw:
            return None
        try:
            return (
                datetime.fromisoformat(raw.replace("Z", "+00:00"))
                .astimezone(timezone.utc)
                .replace(tzinfo=None)
            )
        except ValueError:
            return None

    # ── fetchers ─────────────────────────────────────────────────────────────

    def _fetch_releases(self, client: httpx.Client) -> list[ConnectorOutput]:
        items: list[ConnectorOutput] = []

        for repo in self.config.repos:
            self.logger.info(f"Fetching releases for {repo}")
            try:
                resp = client.get(
                    f"{_API}/repos/{repo}/releases",
                    params={"per_page": self.config.max_results},
                )
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 404:
                    self.logger.warning(f"Repo not found: {repo}")
                else:
                    self.logger.error(f"Error fetching releases for {repo}: {exc}")
                continue
            except httpx.HTTPError as exc:
                self.logger.error(f"Error fetching releases for {repo}: {exc}")
                continue

            for release in resp.json():
                # Skip drafts and pre-releases unless you want them
                if release.get("draft"):
                    continue

                body_raw = (release.get("body") or "").strip()
                # Release notes are already Markdown from GitHub
                content = body_raw if body_raw else "(no release notes)"

                items.append(ConnectorOutput(
                    title=f"{repo} {release.get('tag_name', '')}".strip(),
                    url=release.get("html_url", f"https://github.com/{repo}/releases"),
                    author=release.get("author", {}).get("login"),
                    published_at=self._parse_github_datetime(release.get("published_at")),
                    content=content,
                    metadata={
                        "source_type": "social",
                        "platform": "github",
                        "content_type": "release",
                        "repo": repo,
                        "tag": release.get("tag_name"),
                        "release_name": release.get("name"),
                        "prerelease": release.get("prerelease", False),
                        "assets_count": len(release.get("assets", [])),
                    },
                ))

        self.logger.info(f"Fetched {len(items)} releases from {len(self.config.repos)} repos")
        return items

    def _fetch_trending(self, client: httpx.Client) -> list[ConnectorOutput]:
        since_date = self._since_date()
        query = f"created:>{since_date}"
        if self.config.trending_language:
            query += f" language:{self.config.trending_language}"

        self.logger.info(
            f"Fetching trending repos — language={self.config.trending_language or 'any'} "
            f"since={self.config.trending_since} (>{since_date})"
        )

        try:
            resp = client.get(
                f"{_API}/search/repositories",
                params={
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": self.config.max_results,
                },
            )
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            self.logger.error(f"Error fetching trending repos: {exc}")
            return []

        items: list[ConnectorOutput] = []

        for repo in resp.json().get("items", []):
            description = (repo.get("description") or "").strip()
            topics = repo.get("topics", [])
            language = repo.get("language") or "N/A"
            stars = repo.get("stargazers_count", 0)
            forks = repo.get("forks_count", 0)

            content_parts: list[str] = []
            if description:
                content_parts.append(description)
            if topics:
                content_parts.append(f"**Topics:** {', '.join(topics)}")
            content_parts.append(
                f"**Stars:** {stars:,} | **Forks:** {forks:,} | **Language:** {language}"
            )

            items.append(ConnectorOutput(
                title=repo.get("full_name", "Unknown Repo"),
                url=repo.get("html_url", ""),
                author=repo.get("owner", {}).get("login"),
                published_at=self._parse_github_datetime(repo.get("created_at")),
                content="\n\n".join(content_parts),
                metadata={
                    "source_type": "social",
                    "platform": "github",
                    "content_type": "trending_repo",
                    "stars": stars,
                    "forks": forks,
                    "language": language,
                    "topics": topics,
                    "open_issues": repo.get("open_issues_count", 0),
                    "watchers": repo.get("watchers_count", 0),
                    "trending_since": self.config.trending_since,
                    "homepage": repo.get("homepage"),
                },
            ))

        self.logger.info(f"Fetched {len(items)} trending repos")
        return items

    # ── main entry point ──────────────────────────────────────────────────────

    def fetch(self) -> list[ConnectorOutput]:
        items: list[ConnectorOutput] = []

        with self._client() as client:
            if self.config.fetch_releases and self.config.repos:
                items.extend(self._fetch_releases(client))
            if self.config.fetch_trending:
                items.extend(self._fetch_trending(client))

        self.logger.info(f"GitHub connector: {len(items)} total items")
        return items
