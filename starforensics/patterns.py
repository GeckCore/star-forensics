"""
Forensic pattern detectors for fake-star analysis.

Each detector is a function that receives the list of StargazerProfile objects
and the RepoInfo, and returns a PatternResult describing what it found.
"""

from __future__ import annotations

import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .analyzer import RepoInfo, StargazerProfile


SEVERITY_LOW = "low"
SEVERITY_MEDIUM = "medium"
SEVERITY_HIGH = "high"
SEVERITY_CRITICAL = "critical"


@dataclass
class PatternResult:
    id: str
    name: str
    description: str
    severity: str  # low | medium | high | critical
    flagged: bool
    score_impact: float  # negative = penalize, 0 = neutral
    evidence: dict = field(default_factory=dict)
    detail: str = ""

    @property
    def emoji(self) -> str:
        if not self.flagged:
            return "✅"
        return {
            SEVERITY_LOW: "⚠️",
            SEVERITY_MEDIUM: "🟠",
            SEVERITY_HIGH: "🔴",
            SEVERITY_CRITICAL: "💀",
        }.get(self.severity, "⚠️")


# ---------------------------------------------------------------------------
# Individual detectors
# ---------------------------------------------------------------------------


def detect_empty_accounts(
    stargazers: list[StargazerProfile], repo: RepoInfo
) -> PatternResult:
    """Accounts with zero repos, followers, following, bio, or location."""
    empty = [s for s in stargazers if s.is_empty_account]
    ratio = len(empty) / max(len(stargazers), 1)

    flagged = ratio > 0.15
    severity = SEVERITY_LOW
    if ratio > 0.50:
        severity = SEVERITY_CRITICAL
    elif ratio > 0.35:
        severity = SEVERITY_HIGH
    elif ratio > 0.25:
        severity = SEVERITY_MEDIUM

    return PatternResult(
        id="empty_accounts",
        name="Ghost Accounts",
        description="Stargazers with no repos, followers, following, bio, or location",
        severity=severity,
        flagged=flagged,
        score_impact=-(ratio * 40) if flagged else 0,
        evidence={
            "count": len(empty),
            "ratio": round(ratio * 100, 1),
            "examples": [s.login for s in empty[:5]],
        },
        detail=f"{len(empty)} accounts ({ratio*100:.1f}%) show zero activity markers",
    )


def detect_account_age_clustering(
    stargazers: list[StargazerProfile], repo: RepoInfo
) -> PatternResult:
    """Many stargazers created on the same day or within a narrow window."""
    created_dates = [s.created_at.date() for s in stargazers]
    date_counts = Counter(created_dates)

    # Find dates with suspiciously many new accounts
    threshold = max(3, len(stargazers) * 0.05)
    suspicious_dates = {d: c for d, c in date_counts.items() if c >= threshold}
    clustered_count = sum(suspicious_dates.values())
    ratio = clustered_count / max(len(stargazers), 1)

    flagged = ratio > 0.10
    severity = SEVERITY_LOW
    if ratio > 0.50:
        severity = SEVERITY_CRITICAL
    elif ratio > 0.30:
        severity = SEVERITY_HIGH
    elif ratio > 0.20:
        severity = SEVERITY_MEDIUM

    top_dates = sorted(suspicious_dates.items(), key=lambda x: -x[1])[:3]

    return PatternResult(
        id="account_age_clustering",
        name="Account Creation Clustering",
        description="Large groups of accounts created on the same days",
        severity=severity,
        flagged=flagged,
        score_impact=-(ratio * 35) if flagged else 0,
        evidence={
            "clustered_accounts": clustered_count,
            "suspicious_dates": [
                {"date": str(d), "accounts": c} for d, c in top_dates
            ],
            "ratio": round(ratio * 100, 1),
        },
        detail=(
            f"{clustered_count} accounts ({ratio*100:.1f}%) were created on {len(suspicious_dates)} "
            f"suspicious date(s). Top: {top_dates[0][0]} had {top_dates[0][1]} account(s)."
            if top_dates
            else "No clustering detected."
        ),
    )


def detect_star_velocity_spikes(
    stargazers: list[StargazerProfile], repo: RepoInfo
) -> PatternResult:
    """Sudden bursts: e.g. 500 stars in one hour."""
    if not stargazers:
        return PatternResult(
            id="star_velocity_spikes",
            name="Star Velocity Spikes",
            description="Sudden unnatural bursts in star acquisition",
            severity=SEVERITY_LOW,
            flagged=False,
            score_impact=0,
            detail="Insufficient data.",
        )

    # Group stars by hour
    hourly: dict[datetime, int] = defaultdict(int)
    for s in stargazers:
        hour = s.starred_at.replace(minute=0, second=0, microsecond=0)
        hourly[hour] += 1

    if len(hourly) < 2:
        return PatternResult(
            id="star_velocity_spikes",
            name="Star Velocity Spikes",
            description="Sudden unnatural bursts in star acquisition",
            severity=SEVERITY_LOW,
            flagged=False,
            score_impact=0,
            detail="Not enough time range to analyze velocity.",
        )

    counts = list(hourly.values())
    mean = statistics.mean(counts)
    stdev = statistics.stdev(counts) if len(counts) > 1 else 0

    # Spikes = hours that are > mean + 3*stdev, and have at least 10 stars
    spike_threshold = max(mean + 3 * stdev, 10)
    spikes = {t: c for t, c in hourly.items() if c >= spike_threshold}

    flagged = bool(spikes)
    max_spike = max(spikes.values()) if spikes else 0
    ratio = max_spike / max(len(stargazers), 1)

    severity = SEVERITY_LOW
    if ratio > 0.40:
        severity = SEVERITY_CRITICAL
    elif ratio > 0.25:
        severity = SEVERITY_HIGH
    elif ratio > 0.15:
        severity = SEVERITY_MEDIUM

    top_spikes = sorted(spikes.items(), key=lambda x: -x[1])[:3]

    return PatternResult(
        id="star_velocity_spikes",
        name="Star Velocity Spikes",
        description="Sudden unnatural bursts in star acquisition",
        severity=severity,
        flagged=flagged,
        score_impact=-(ratio * 30) if flagged else 0,
        evidence={
            "spike_hours": [
                {"timestamp": t.isoformat(), "stars": c} for t, c in top_spikes
            ],
            "hourly_mean": round(mean, 2),
            "spike_threshold": round(spike_threshold, 1),
        },
        detail=(
            f"Detected {len(spikes)} spike hour(s). Peak: {max_spike} stars in one hour "
            f"vs. average of {mean:.1f} stars/hour."
            if flagged
            else f"Velocity looks organic. Average {mean:.1f} stars/hour."
        ),
    )


def detect_low_follower_accounts(
    stargazers: list[StargazerProfile], repo: RepoInfo
) -> PatternResult:
    """Most real developers have at least a few followers."""
    no_followers = [s for s in stargazers if s.followers == 0 and s.following == 0]
    ratio = len(no_followers) / max(len(stargazers), 1)

    flagged = ratio > 0.30
    severity = SEVERITY_LOW
    if ratio > 0.70:
        severity = SEVERITY_CRITICAL
    elif ratio > 0.55:
        severity = SEVERITY_HIGH
    elif ratio > 0.40:
        severity = SEVERITY_MEDIUM

    return PatternResult(
        id="low_follower_accounts",
        name="Socially Isolated Accounts",
        description="Accounts with zero followers AND zero following — rare for real developers",
        severity=severity,
        flagged=flagged,
        score_impact=-(ratio * 20) if flagged else 0,
        evidence={
            "count": len(no_followers),
            "ratio": round(ratio * 100, 1),
        },
        detail=f"{len(no_followers)} accounts ({ratio*100:.1f}%) have 0 followers and 0 following",
    )


def detect_new_account_surge(
    stargazers: list[StargazerProfile], repo: RepoInfo
) -> PatternResult:
    """Accounts younger than 30 days at the time they starred the repo."""
    young = []
    for s in stargazers:
        age_at_star = (s.starred_at - s.created_at).days
        if age_at_star <= 30:
            young.append(s)

    ratio = len(young) / max(len(stargazers), 1)
    flagged = ratio > 0.10

    severity = SEVERITY_LOW
    if ratio > 0.50:
        severity = SEVERITY_CRITICAL
    elif ratio > 0.30:
        severity = SEVERITY_HIGH
    elif ratio > 0.20:
        severity = SEVERITY_MEDIUM

    return PatternResult(
        id="new_account_surge",
        name="Freshly Minted Accounts",
        description="Accounts that starred the repo within 30 days of being created",
        severity=severity,
        flagged=flagged,
        score_impact=-(ratio * 25) if flagged else 0,
        evidence={
            "count": len(young),
            "ratio": round(ratio * 100, 1),
            "examples": [s.login for s in young[:5]],
        },
        detail=f"{len(young)} accounts ({ratio*100:.1f}%) starred within 30 days of account creation",
    )


def detect_username_patterns(
    stargazers: list[StargazerProfile], repo: RepoInfo
) -> PatternResult:
    """
    Bot farms often use generated usernames with trailing numbers,
    e.g. user12345678, dev98765, github_user_001.
    """
    import re

    numeric_suffix_pattern = re.compile(r"[a-z_\-]{3,}\d{4,}$", re.IGNORECASE)
    uuid_like_pattern = re.compile(
        r"^[a-f0-9]{8}-?[a-f0-9]{4}", re.IGNORECASE
    )

    suspicious = [
        s
        for s in stargazers
        if numeric_suffix_pattern.match(s.login) or uuid_like_pattern.match(s.login)
    ]
    ratio = len(suspicious) / max(len(stargazers), 1)
    flagged = ratio > 0.08

    severity = SEVERITY_LOW
    if ratio > 0.40:
        severity = SEVERITY_HIGH
    elif ratio > 0.25:
        severity = SEVERITY_MEDIUM

    return PatternResult(
        id="username_patterns",
        name="Bot-like Usernames",
        description="Usernames matching bot-farm patterns (e.g. user123456, dev98765)",
        severity=severity,
        flagged=flagged,
        score_impact=-(ratio * 15) if flagged else 0,
        evidence={
            "count": len(suspicious),
            "ratio": round(ratio * 100, 1),
            "examples": [s.login for s in suspicious[:8]],
        },
        detail=f"{len(suspicious)} accounts ({ratio*100:.1f}%) have bot-farm username patterns",
    )


def detect_no_repos_accounts(
    stargazers: list[StargazerProfile], repo: RepoInfo
) -> PatternResult:
    """Developers almost always have at least one public repo."""
    no_repos = [s for s in stargazers if s.public_repos == 0]
    ratio = len(no_repos) / max(len(stargazers), 1)
    flagged = ratio > 0.25

    severity = SEVERITY_LOW
    if ratio > 0.60:
        severity = SEVERITY_HIGH
    elif ratio > 0.45:
        severity = SEVERITY_MEDIUM

    return PatternResult(
        id="no_repos_accounts",
        name="Repoless Stargazers",
        description="Accounts with zero public repositories — unusual for GitHub users who star dev tools",
        severity=severity,
        flagged=flagged,
        score_impact=-(ratio * 10) if flagged else 0,
        evidence={
            "count": len(no_repos),
            "ratio": round(ratio * 100, 1),
        },
        detail=f"{len(no_repos)} stargazers ({ratio*100:.1f}%) have no public repositories",
    )


def detect_star_to_repo_ratio(
    stargazers: list[StargazerProfile], repo: RepoInfo
) -> PatternResult:
    """
    Repos that buy stars often have an oddly high star count compared
    to forks, watchers, or contributors.
    """
    star_to_fork_ratio = repo.stars / max(repo.forks, 1)

    # For most healthy repos star:fork ratio is under 50:1
    # Extremely high ratio can be a signal (though not conclusive alone)
    flagged = star_to_fork_ratio > 100 and repo.stars > 500
    severity = SEVERITY_LOW
    if star_to_fork_ratio > 500 and repo.stars > 1000:
        severity = SEVERITY_MEDIUM

    return PatternResult(
        id="star_fork_ratio",
        name="Star/Fork Disproportion",
        description="Unusually high star-to-fork ratio compared to typical organic repos",
        severity=severity,
        flagged=flagged,
        score_impact=-5 if flagged else 0,
        evidence={
            "stars": repo.stars,
            "forks": repo.forks,
            "ratio": round(star_to_fork_ratio, 1),
        },
        detail=(
            f"Star-to-fork ratio is {star_to_fork_ratio:.0f}:1 "
            f"({'suspicious' if flagged else 'within normal range'})"
        ),
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_DETECTORS = [
    detect_empty_accounts,
    detect_account_age_clustering,
    detect_star_velocity_spikes,
    detect_low_follower_accounts,
    detect_new_account_surge,
    detect_username_patterns,
    detect_no_repos_accounts,
    detect_star_to_repo_ratio,
]


def run_all_patterns(
    stargazers: list[StargazerProfile], repo: RepoInfo
) -> list[PatternResult]:
    results = []
    for detector in _DETECTORS:
        try:
            result = detector(stargazers, repo)
            results.append(result)
        except Exception as exc:  # noqa: BLE001
            results.append(
                PatternResult(
                    id=detector.__name__,
                    name=detector.__name__,
                    description="Detector encountered an error",
                    severity=SEVERITY_LOW,
                    flagged=False,
                    score_impact=0,
                    detail=f"Error: {exc}",
                )
            )
    return results
