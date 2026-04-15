"""
Core analysis engine for star-forensics.
Fetches stargazer data from GitHub API and runs all detection patterns.
"""

from __future__ import annotations

import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterator

import httpx

from .patterns import PatternResult, run_all_patterns
from .scorer import compute_trust_score, TrustScore


GITHUB_API = "https://api.github.com"
STARS_PER_PAGE = 100


@dataclass
class StargazerProfile:
    login: str
    created_at: datetime
    public_repos: int
    followers: int
    following: int
    starred_at: datetime
    bio: str | None
    location: str | None
    company: str | None
    twitter_username: str | None
    has_avatar: bool = True

    @property
    def account_age_days(self) -> int:
        return (datetime.now(timezone.utc) - self.created_at).days

    @property
    def is_empty_account(self) -> bool:
        return (
            self.public_repos == 0
            and self.followers == 0
            and self.following == 0
            and not self.bio
            and not self.location
        )


@dataclass
class RepoInfo:
    owner: str
    name: str
    stars: int
    created_at: datetime
    description: str | None
    language: str | None
    forks: int
    watchers: int


@dataclass
class AnalysisResult:
    repo: RepoInfo
    stargazers: list[StargazerProfile]
    patterns: list[PatternResult]
    trust_score: TrustScore
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    sample_size: int = 0
    total_stars: int = 0

    @property
    def is_full_sample(self) -> bool:
        return self.sample_size >= self.total_stars


class RateLimitError(Exception):
    def __init__(self, reset_at: datetime):
        self.reset_at = reset_at
        super().__init__(f"GitHub API rate limit exceeded. Resets at {reset_at}")


class RepoNotFoundError(Exception):
    pass


class GitHubClient:
    def __init__(self, token: str | None = None, timeout: int = 30):
        headers = {
            "Accept": "application/vnd.github.v3.star+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"

        self._client = httpx.Client(
            base_url=GITHUB_API,
            headers=headers,
            timeout=timeout,
            follow_redirects=True,
        )
        self._token = token

    def _check_rate_limit(self, response: httpx.Response) -> None:
        if response.status_code == 403:
            remaining = int(response.headers.get("x-ratelimit-remaining", 0))
            if remaining == 0:
                reset_ts = int(response.headers.get("x-ratelimit-reset", 0))
                reset_at = datetime.fromtimestamp(reset_ts, tz=timezone.utc)
                raise RateLimitError(reset_at)

    def get_repo(self, owner: str, name: str) -> RepoInfo:
        resp = self._client.get(f"/repos/{owner}/{name}")
        self._check_rate_limit(resp)
        if resp.status_code == 404:
            raise RepoNotFoundError(f"Repository {owner}/{name} not found")
        resp.raise_for_status()
        data = resp.json()
        return RepoInfo(
            owner=owner,
            name=name,
            stars=data["stargazers_count"],
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            description=data.get("description"),
            language=data.get("language"),
            forks=data["forks_count"],
            watchers=data["watchers_count"],
        )

    def iter_stargazers_pages(
        self, owner: str, name: str, max_pages: int | None = None
    ) -> Iterator[list[dict]]:
        page = 1
        while True:
            resp = self._client.get(
                f"/repos/{owner}/{name}/stargazers",
                params={"per_page": STARS_PER_PAGE, "page": page},
            )
            self._check_rate_limit(resp)
            resp.raise_for_status()
            data = resp.json()
            if not data:
                break
            yield data
            if len(data) < STARS_PER_PAGE:
                break
            if max_pages and page >= max_pages:
                break
            page += 1
            # Respect rate limits
            remaining = int(resp.headers.get("x-ratelimit-remaining", 60))
            if remaining < 5:
                reset_ts = int(resp.headers.get("x-ratelimit-reset", 0))
                wait = max(0, reset_ts - time.time()) + 1
                time.sleep(wait)

    def get_user_detail(self, login: str) -> dict:
        resp = self._client.get(f"/users/{login}")
        self._check_rate_limit(resp)
        if resp.status_code == 404:
            return {}
        resp.raise_for_status()
        return resp.json()

    def get_rate_limit(self) -> dict:
        resp = self._client.get("/rate_limit")
        resp.raise_for_status()
        return resp.json()

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def _parse_starred_at(raw: dict) -> datetime:
    ts = raw.get("starred_at", "")
    if ts:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return datetime.now(timezone.utc)


def _parse_created_at(ts_str: str) -> datetime:
    return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))


def analyze_repo(
    owner: str,
    name: str,
    token: str | None = None,
    max_stars: int = 3000,
    progress_callback=None,
) -> AnalysisResult:
    """
    Main entry point. Fetches up to `max_stars` stargazers and runs
    all forensic patterns against them.
    """
    with GitHubClient(token=token) as client:
        repo = client.get_repo(owner, name)
        total_stars = repo.stars
        max_pages = (min(max_stars, total_stars) + STARS_PER_PAGE - 1) // STARS_PER_PAGE

        stargazers: list[StargazerProfile] = []
        fetched = 0

        for page_data in client.iter_stargazers_pages(owner, name, max_pages=max_pages):
            batch: list[StargazerProfile] = []
            for raw in page_data:
                user = raw.get("user", raw)
                starred_at = _parse_starred_at(raw)
                login = user.get("login", "")

                # Fetch full user profile for richer signal
                detail = client.get_user_detail(login)
                if not detail:
                    continue

                created_at = _parse_created_at(
                    detail.get("created_at", "2008-04-10T00:00:00Z")
                )
                profile = StargazerProfile(
                    login=login,
                    created_at=created_at,
                    public_repos=detail.get("public_repos", 0),
                    followers=detail.get("followers", 0),
                    following=detail.get("following", 0),
                    starred_at=starred_at,
                    bio=detail.get("bio") or None,
                    location=detail.get("location") or None,
                    company=detail.get("company") or None,
                    twitter_username=detail.get("twitter_username") or None,
                    has_avatar=bool(detail.get("avatar_url")),
                )
                batch.append(profile)

            stargazers.extend(batch)
            fetched += len(batch)

            if progress_callback:
                progress_callback(fetched, min(max_stars, total_stars))

            if fetched >= max_stars:
                break

        patterns = run_all_patterns(stargazers, repo)
        trust_score = compute_trust_score(patterns, stargazers, repo)

        return AnalysisResult(
            repo=repo,
            stargazers=stargazers,
            patterns=patterns,
            trust_score=trust_score,
            sample_size=len(stargazers),
            total_stars=total_stars,
        )
