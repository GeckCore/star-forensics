"""
Trust score engine. Aggregates pattern results into a single [0-100] score
with a verdict label and confidence indicator.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .analyzer import RepoInfo, StargazerProfile
    from .patterns import PatternResult


VERDICT_TRUSTED = "Trusted"
VERDICT_SUSPICIOUS = "Suspicious"
VERDICT_LIKELY_FAKE = "Likely Fake"
VERDICT_MANIPULATED = "Manipulated"


@dataclass
class TrustScore:
    score: int           # 0-100
    verdict: str
    confidence: str      # low | medium | high
    summary: str
    flagged_count: int
    critical_count: int

    @property
    def color(self) -> str:
        """ANSI-friendly color name for rich."""
        if self.score >= 80:
            return "green"
        if self.score >= 60:
            return "yellow"
        if self.score >= 40:
            return "orange3"
        return "red"

    @property
    def grade(self) -> str:
        if self.score >= 80:
            return "A"
        if self.score >= 65:
            return "B"
        if self.score >= 50:
            return "C"
        if self.score >= 35:
            return "D"
        return "F"


def compute_trust_score(
    patterns: list[PatternResult],
    stargazers: list[StargazerProfile],
    repo: RepoInfo,
) -> TrustScore:
    base = 100.0
    flagged = [p for p in patterns if p.flagged]
    critical = [p for p in flagged if p.severity == "critical"]

    for pattern in patterns:
        base += pattern.score_impact  # score_impact is already negative

    score = max(0, min(100, int(round(base))))

    # Verdict
    if score >= 80:
        verdict = VERDICT_TRUSTED
        summary = "This repository shows organic star patterns. No significant manipulation signals detected."
    elif score >= 60:
        verdict = VERDICT_SUSPICIOUS
        summary = "Some suspicious patterns detected. The repo may have purchased a portion of its stars."
    elif score >= 35:
        verdict = VERDICT_LIKELY_FAKE
        summary = "Multiple strong signals of star manipulation. A significant share of stars appear purchased."
    else:
        verdict = VERDICT_MANIPULATED
        summary = "Overwhelming evidence of star manipulation. This repo almost certainly purchased stars."

    # Confidence: depends on sample size
    sample_ratio = len(stargazers) / max(repo.stars, 1)
    if sample_ratio >= 0.5 or len(stargazers) >= 500:
        confidence = "high"
    elif sample_ratio >= 0.2 or len(stargazers) >= 100:
        confidence = "medium"
    else:
        confidence = "low"

    return TrustScore(
        score=score,
        verdict=verdict,
        confidence=confidence,
        summary=summary,
        flagged_count=len(flagged),
        critical_count=len(critical),
    )
