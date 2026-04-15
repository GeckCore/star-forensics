"""
Badge generator — creates embeddable SVG trust score badges.
Run a repo analysis once, then generate a badge URL or SVG to embed in your README.

This is the network-effect feature: every repo that embeds a badge links back to star-forensics.
"""

from __future__ import annotations

import math
from pathlib import Path


SCORE_COLORS = {
    (80, 101): ("#166534", "#22c55e"),   # green
    (60, 80):  ("#78350f", "#f59e0b"),   # yellow
    (35, 60):  ("#7c2d12", "#f97316"),   # orange
    (0, 35):   ("#7f1d1d", "#ef4444"),   # red
}

GRADE_COLORS = {
    "A": "#22c55e",
    "B": "#84cc16",
    "C": "#f59e0b",
    "D": "#f97316",
    "F": "#ef4444",
}


def _score_color(score: int) -> tuple[str, str]:
    for (lo, hi), colors in SCORE_COLORS.items():
        if lo <= score < hi:
            return colors
    return ("#7f1d1d", "#ef4444")


def generate_badge_svg(
    score: int,
    grade: str,
    verdict: str,
    owner: str,
    name: str,
) -> str:
    """Generate a self-contained SVG badge."""
    bg_dark, fg = _score_color(score)
    label = "star-forensics"
    value = f"{score}/100 · {grade}"

    label_w = len(label) * 6.5 + 16
    value_w = len(value) * 7 + 20
    total_w = int(label_w + value_w)
    height = 22

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="{height}" role="img" aria-label="{label}: {value}">
  <title>{label}: {value}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="{total_w}" height="{height}" rx="4" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="{int(label_w)}" height="{height}" fill="#1f2937"/>
    <rect x="{int(label_w)}" width="{int(value_w)}" height="{height}" fill="{bg_dark}"/>
    <rect width="{total_w}" height="{height}" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="{int(label_w/2 + 1)}" y="15" fill="#000" fill-opacity=".3" lengthAdjust="spacing">{label}</text>
    <text x="{int(label_w/2)}" y="14" lengthAdjust="spacing">{label}</text>
    <text x="{int(label_w + value_w/2 + 1)}" y="15" fill="#000" fill-opacity=".3" font-weight="bold" lengthAdjust="spacing">{value}</text>
    <text x="{int(label_w + value_w/2)}" y="14" fill="{fg}" font-weight="bold" lengthAdjust="spacing">{value}</text>
  </g>
</svg>"""


def generate_badge_markdown(
    score: int,
    grade: str,
    verdict: str,
    owner: str,
    name: str,
    out_file: str | None = None,
) -> str:
    """Return the Markdown snippet to embed the badge in a README."""
    repo_slug = f"{owner}/{name}"
    # In a real deployment this would be an API endpoint
    # For now, we generate a shields.io static badge URL
    color_map = {
        "A": "22c55e", "B": "84cc16", "C": "f59e0b", "D": "f97316", "F": "ef4444",
    }
    color = color_map.get(grade, "888888")
    label = "star-forensics"
    message = f"{score}%2F100+{grade}"
    shields_url = f"https://img.shields.io/badge/{label}-{message}-{color}?style=flat-square&logo=github"
    repo_url = f"https://github.com/star-forensics/star-forensics"

    md = f"[![star-forensics score]({shields_url})]({repo_url})"
    if out_file:
        Path(out_file).write_text(md)
    return md
