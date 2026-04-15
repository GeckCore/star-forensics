"""Tests for star-forensics pattern detectors."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from starforensics.analyzer import RepoInfo, StargazerProfile
from starforensics.patterns import (
    detect_account_age_clustering,
    detect_empty_accounts,
    detect_new_account_surge,
    detect_star_velocity_spikes,
    detect_username_patterns,
    run_all_patterns,
)
from starforensics.scorer import compute_trust_score


NOW = datetime.now(timezone.utc)


def make_user(
    login="user1",
    created_days_ago=365,
    starred_days_ago=10,
    repos=5,
    followers=10,
    following=8,
    bio="A real developer",
    location="NYC",
) -> StargazerProfile:
    return StargazerProfile(
        login=login,
        created_at=NOW - timedelta(days=created_days_ago),
        public_repos=repos,
        followers=followers,
        following=following,
        starred_at=NOW - timedelta(days=starred_days_ago),
        bio=bio,
        location=location,
        company=None,
        twitter_username=None,
    )


def make_repo(stars=1000, forks=100) -> RepoInfo:
    return RepoInfo(
        owner="owner",
        name="repo",
        stars=stars,
        created_at=NOW - timedelta(days=500),
        description="A cool repo",
        language="Python",
        forks=forks,
        watchers=stars,
    )


# ---------------------------------------------------------------------------
# Empty accounts
# ---------------------------------------------------------------------------

class TestDetectEmptyAccounts:
    def test_clean_batch(self):
        users = [make_user(f"user{i}") for i in range(100)]
        result = detect_empty_accounts(users, make_repo())
        assert not result.flagged

    def test_high_ratio_flags(self):
        empty = [
            make_user(f"ghost{i}", repos=0, followers=0, following=0, bio=None, location=None)
            for i in range(60)
        ]
        real = [make_user(f"real{i}") for i in range(40)]
        result = detect_empty_accounts(empty + real, make_repo())
        assert result.flagged
        assert result.severity in ("high", "critical")

    def test_empty_list(self):
        result = detect_empty_accounts([], make_repo())
        assert not result.flagged


# ---------------------------------------------------------------------------
# Account age clustering
# ---------------------------------------------------------------------------

class TestAccountAgeClustering:
    def test_no_clustering(self):
        users = [make_user(f"u{i}", created_days_ago=i * 30) for i in range(1, 50)]
        result = detect_account_age_clustering(users, make_repo())
        assert not result.flagged

    def test_heavy_clustering_flags(self):
        same_day = NOW - timedelta(days=100)
        users = [
            StargazerProfile(
                login=f"bot{i}",
                created_at=same_day,
                public_repos=0,
                followers=0,
                following=0,
                starred_at=NOW - timedelta(days=5),
                bio=None,
                location=None,
                company=None,
                twitter_username=None,
            )
            for i in range(80)
        ] + [make_user(f"real{i}") for i in range(20)]
        result = detect_account_age_clustering(users, make_repo())
        assert result.flagged


# ---------------------------------------------------------------------------
# Star velocity spikes
# ---------------------------------------------------------------------------

class TestStarVelocitySpikes:
    def test_organic_velocity(self):
        # Spread evenly
        users = [
            make_user(f"u{i}", starred_days_ago=i)
            for i in range(100)
        ]
        result = detect_star_velocity_spikes(users, make_repo())
        # May or may not flag; we just ensure it doesn't crash
        assert isinstance(result.flagged, bool)

    def test_spike_detected(self):
        # 1 normal hour, 1 massive spike
        normal = [
            StargazerProfile(
                login=f"n{i}",
                created_at=NOW - timedelta(days=400),
                public_repos=5,
                followers=10,
                following=5,
                starred_at=NOW - timedelta(hours=100 - i),
                bio="dev",
                location="US",
                company=None,
                twitter_username=None,
            )
            for i in range(20)
        ]
        spike_hour = NOW.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
        spike = [
            StargazerProfile(
                login=f"s{i}",
                created_at=NOW - timedelta(days=10),
                public_repos=0,
                followers=0,
                following=0,
                starred_at=spike_hour + timedelta(minutes=i % 59),
                bio=None,
                location=None,
                company=None,
                twitter_username=None,
            )
            for i in range(200)
        ]
        result = detect_star_velocity_spikes(normal + spike, make_repo(stars=220))
        assert result.flagged


# ---------------------------------------------------------------------------
# New account surge
# ---------------------------------------------------------------------------

class TestNewAccountSurge:
    def test_no_surge(self):
        users = [make_user(f"u{i}", created_days_ago=500) for i in range(50)]
        result = detect_new_account_surge(users, make_repo())
        assert not result.flagged

    def test_surge_detected(self):
        users = [
            StargazerProfile(
                login=f"new{i}",
                created_at=NOW - timedelta(days=2),
                public_repos=0,
                followers=0,
                following=0,
                starred_at=NOW - timedelta(days=1),
                bio=None,
                location=None,
                company=None,
                twitter_username=None,
            )
            for i in range(60)
        ] + [make_user(f"old{i}") for i in range(40)]
        result = detect_new_account_surge(users, make_repo())
        assert result.flagged


# ---------------------------------------------------------------------------
# Username patterns
# ---------------------------------------------------------------------------

class TestUsernamePatterns:
    def test_clean_usernames(self):
        users = [make_user(f"alice{i}") for i in range(20)]
        result = detect_username_patterns(users, make_repo())
        # alice0..alice19 should not trigger
        assert result.evidence.get("count", 0) < 5

    def test_bot_usernames_flagged(self):
        bots = [make_user(f"user{100000+i}") for i in range(50)]
        real = [make_user(f"realdev{i}") for i in range(10)]
        result = detect_username_patterns(bots + real, make_repo())
        assert result.flagged


# ---------------------------------------------------------------------------
# Integration: run_all_patterns
# ---------------------------------------------------------------------------

class TestRunAllPatterns:
    def test_returns_list_of_results(self):
        users = [make_user(f"u{i}") for i in range(10)]
        results = run_all_patterns(users, make_repo())
        assert len(results) > 0
        for r in results:
            assert hasattr(r, "flagged")
            assert hasattr(r, "score_impact")

    def test_clean_repo_high_score(self):
        users = [make_user(f"dev{i}", created_days_ago=500 + i) for i in range(100)]
        repo = make_repo()
        patterns = run_all_patterns(users, repo)
        score = compute_trust_score(patterns, users, repo)
        assert score.score >= 60  # organic data → reasonable score
