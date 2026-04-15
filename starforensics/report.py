"""
Generates a self-contained HTML forensics report.
No external dependencies required in the output file.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .analyzer import AnalysisResult


SEVERITY_COLOR = {
    "low": "#f59e0b",
    "medium": "#f97316",
    "high": "#ef4444",
    "critical": "#dc2626",
    "clean": "#22c55e",
}

VERDICT_COLOR = {
    "Trusted": "#22c55e",
    "Suspicious": "#f59e0b",
    "Likely Fake": "#ef4444",
    "Manipulated": "#dc2626",
}


def render_html(result: AnalysisResult) -> str:
    ts = result.trust_score
    repo = result.repo
    score_color = VERDICT_COLOR.get(ts.verdict, "#888")

    patterns_html = ""
    for p in result.patterns:
        sev = p.severity if p.flagged else "clean"
        color = SEVERITY_COLOR.get(sev, "#888")
        icon = p.emoji
        evidence_rows = ""
        for k, v in p.evidence.items():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                val = "<br>".join(str(x) for x in v[:5])
            elif isinstance(v, list):
                val = ", ".join(str(x) for x in v[:5])
            else:
                val = str(v)
            evidence_rows += f"<tr><td class='ev-key'>{k}</td><td>{val}</td></tr>"

        evidence_table = (
            f"<table class='evidence'>{evidence_rows}</table>" if evidence_rows else ""
        )

        patterns_html += f"""
        <div class="pattern {'flagged' if p.flagged else 'clean'}">
          <div class="pattern-header">
            <span class="pattern-icon">{icon}</span>
            <span class="pattern-name">{p.name}</span>
            <span class="badge" style="background:{color}">{sev.upper()}</span>
          </div>
          <p class="pattern-detail">{p.detail}</p>
          {evidence_table}
        </div>
        """

    flagged_count = sum(1 for p in result.patterns if p.flagged)

    sample_pct = result.sample_size / max(repo.stars, 1) * 100

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>⭐ Star Forensics — {repo.owner}/{repo.name}</title>
<style>
  :root {{
    --bg: #0d1117;
    --surface: #161b22;
    --border: #30363d;
    --text: #e6edf3;
    --muted: #7d8590;
    --accent: #58a6ff;
    --score: {score_color};
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif; line-height: 1.6; padding: 2rem; }}
  .container {{ max-width: 900px; margin: 0 auto; }}
  header {{ text-align: center; padding: 2rem 0; border-bottom: 1px solid var(--border); margin-bottom: 2rem; }}
  header h1 {{ font-size: 1.5rem; color: var(--muted); font-weight: 400; }}
  header h2 {{ font-size: 2.2rem; color: var(--accent); font-weight: 700; margin: 0.5rem 0; }}
  .score-card {{ background: var(--surface); border: 2px solid var(--score); border-radius: 12px; padding: 2rem; text-align: center; margin-bottom: 2rem; }}
  .score-number {{ font-size: 5rem; font-weight: 900; color: var(--score); line-height: 1; }}
  .score-label {{ font-size: 1.6rem; font-weight: 700; color: var(--score); margin: 0.5rem 0; }}
  .score-confidence {{ color: var(--muted); font-size: 0.9rem; margin-bottom: 1rem; }}
  .score-summary {{ color: var(--text); max-width: 600px; margin: 0 auto; }}
  .meta {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .meta-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 1rem; }}
  .meta-card .label {{ color: var(--muted); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; }}
  .meta-card .value {{ font-size: 1.3rem; font-weight: 700; color: var(--text); margin-top: 0.25rem; }}
  h3 {{ font-size: 1.1rem; color: var(--muted); margin-bottom: 1rem; text-transform: uppercase; letter-spacing: 0.05em; }}
  .pattern {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 1.25rem; margin-bottom: 1rem; }}
  .pattern.flagged {{ border-left: 4px solid var(--score); }}
  .pattern-header {{ display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem; }}
  .pattern-icon {{ font-size: 1.4rem; }}
  .pattern-name {{ font-weight: 600; font-size: 1rem; flex: 1; }}
  .badge {{ padding: 0.2rem 0.6rem; border-radius: 999px; font-size: 0.75rem; font-weight: 700; color: white; }}
  .pattern-detail {{ color: var(--muted); font-size: 0.9rem; margin-bottom: 0.75rem; }}
  .evidence {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
  .evidence td {{ padding: 0.25rem 0.5rem; border: 1px solid var(--border); }}
  .ev-key {{ color: var(--muted); width: 30%; font-weight: 500; }}
  footer {{ text-align: center; color: var(--muted); font-size: 0.85rem; padding: 2rem 0; border-top: 1px solid var(--border); margin-top: 2rem; }}
  a {{ color: var(--accent); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>🕵️ star-forensics</h1>
    <h2>{repo.owner}/{repo.name}</h2>
    <p style="color:var(--muted)">Forensic star analysis report</p>
  </header>

  <div class="score-card">
    <div class="score-number">{ts.score}</div>
    <div style="color:var(--muted); font-size:0.9rem">/ 100 — Grade: <strong style="color:var(--score)">{ts.grade}</strong></div>
    <div class="score-label">{ts.verdict}</div>
    <div class="score-confidence">Confidence: {ts.confidence.upper()} &nbsp;|&nbsp; {flagged_count} pattern(s) flagged</div>
    <div class="score-summary">{ts.summary}</div>
  </div>

  <div class="meta">
    <div class="meta-card"><div class="label">Total Stars</div><div class="value">{repo.stars:,}</div></div>
    <div class="meta-card"><div class="label">Forks</div><div class="value">{repo.forks:,}</div></div>
    <div class="meta-card"><div class="label">Sample Analyzed</div><div class="value">{result.sample_size:,} <span style="font-size:0.8rem;color:var(--muted)">({sample_pct:.1f}%)</span></div></div>
    <div class="meta-card"><div class="label">Language</div><div class="value">{repo.language or '—'}</div></div>
  </div>

  <h3>Forensic Patterns</h3>
  {patterns_html}

  <footer>
    Generated by <a href="https://github.com/star-forensics/star-forensics">star-forensics</a>
    on {result.analyzed_at.strftime('%Y-%m-%d %H:%M UTC')} &nbsp;|&nbsp;
    <a href="https://github.com/{repo.owner}/{repo.name}">View on GitHub</a>
  </footer>
</div>
</body>
</html>"""
