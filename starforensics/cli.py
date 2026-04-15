"""
CLI entry point for star-forensics.
Uses Rich for beautiful terminal output.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import click
from rich.columns import Columns
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich import box

from .analyzer import (
    RateLimitError,
    RepoNotFoundError,
    analyze_repo,
)
from .patterns import SEVERITY_CRITICAL, SEVERITY_HIGH, SEVERITY_MEDIUM

console = Console()


BANNER = r"""
  ███████╗████████╗ █████╗ ██████╗      ███████╗ ██████╗ ██████╗ ███████╗███╗   ██╗███████╗██╗ ██████╗███████╗
  ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗     ██╔════╝██╔═══██╗██╔══██╗██╔════╝████╗  ██║██╔════╝██║██╔════╝██╔════╝
  ███████╗   ██║   ███████║██████╔╝     █████╗  ██║   ██║██████╔╝█████╗  ██╔██╗ ██║███████╗██║██║     ███████╗
  ╚════██║   ██║   ██╔══██║██╔══██╗     ██╔══╝  ██║   ██║██╔══██╗██╔══╝  ██║╚██╗██║╚════██║██║██║     ╚════██║
  ███████║   ██║   ██║  ██║██║  ██║     ██║     ╚██████╔╝██║  ██║███████╗██║ ╚████║███████║██║╚██████╗███████║
  ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝     ╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝╚══════╝╚═╝ ╚═════╝╚══════╝
"""

SEVERITY_STYLE = {
    "low": "yellow",
    "medium": "orange3",
    "high": "red",
    "critical": "bold red",
}


def _parse_repo(repo: str) -> tuple[str, str]:
    """Parse 'owner/repo' or full GitHub URL."""
    repo = repo.rstrip("/")
    if "github.com" in repo:
        parts = repo.split("github.com/")[-1].split("/")
    else:
        parts = repo.split("/")
    if len(parts) < 2:
        console.print("[red]❌ Invalid repo format. Use owner/repo or a GitHub URL.[/red]")
        sys.exit(1)
    return parts[0], parts[1]


@click.group()
@click.version_option(package_name="star-forensics")
def cli():
    """
    🕵️  star-forensics — Detect fake GitHub stars with forensic analysis.

    Analyze star patterns, identify suspicious accounts, and generate
    a public trust score for any repository.
    """


@cli.command()
@click.argument("repo")
@click.option(
    "--token", "-t",
    envvar="GITHUB_TOKEN",
    default=None,
    help="GitHub personal access token (or set GITHUB_TOKEN env var). Unauthenticated: 60 req/hr.",
)
@click.option(
    "--max-stars", "-n",
    default=1000,
    show_default=True,
    help="Maximum number of stargazers to analyze.",
)
@click.option(
    "--output", "-o",
    type=click.Choice(["text", "json", "html"]),
    default="text",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--out-file", "-f",
    type=click.Path(),
    default=None,
    help="Write output to file instead of stdout.",
)
@click.option("--no-banner", is_flag=True, help="Skip the ASCII banner.")
def analyze(repo: str, token: str | None, max_stars: int, output: str, out_file: str | None, no_banner: bool):
    """
    Analyze a repository for fake stars.

    REPO can be 'owner/repo' or a full GitHub URL.

    \b
    Examples:
      star-forensics analyze torvalds/linux
      star-forensics analyze https://github.com/someorg/somerepo --max-stars 2000
      star-forensics analyze owner/repo --output json --out-file report.json
    """
    owner, name = _parse_repo(repo)

    if output == "text" and not no_banner:
        console.print(f"[bold cyan]{BANNER}[/bold cyan]")
        console.print(Rule("[dim]Forensic Star Analysis[/dim]"))

    if output == "text":
        console.print(
            f"\n[bold]🔍 Analyzing[/bold] [cyan]{owner}/{name}[/cyan] "
            f"[dim](up to {max_stars:,} stargazers)[/dim]\n"
        )
        if not token:
            console.print(
                "[yellow]⚠[/yellow]  No GitHub token found. "
                "Rate limit: 60 requests/hour. "
                "Set [bold]GITHUB_TOKEN[/bold] for 5,000/hour.\n"
            )

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    )

    task_id = None
    result = None

    def on_progress(done: int, total: int):
        nonlocal task_id
        if task_id is None:
            task_id = progress.add_task("Fetching stargazers…", total=total)
        progress.update(task_id, completed=done)

    try:
        if output == "text":
            with progress:
                result = analyze_repo(
                    owner, name,
                    token=token,
                    max_stars=max_stars,
                    progress_callback=on_progress,
                )
        else:
            result = analyze_repo(
                owner, name,
                token=token,
                max_stars=max_stars,
            )

    except RepoNotFoundError:
        console.print(f"[red]❌ Repository [bold]{owner}/{name}[/bold] not found.[/red]")
        sys.exit(1)
    except RateLimitError as e:
        console.print(
            f"[red]❌ GitHub API rate limit hit.[/red] "
            f"Resets at [bold]{e.reset_at.strftime('%H:%M:%S UTC')}[/bold].\n"
            f"[dim]Tip: Set GITHUB_TOKEN to increase limit to 5,000 req/hour.[/dim]"
        )
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠  Interrupted by user.[/yellow]")
        sys.exit(0)

    # ---- Output ----
    if output == "json":
        _output_json(result, out_file)
    elif output == "html":
        _output_html(result, out_file)
    else:
        _output_rich(result, out_file)


def _output_rich(result, out_file):
    from io import StringIO
    from .patterns import SEVERITY_CRITICAL, SEVERITY_HIGH, SEVERITY_MEDIUM

    buf = None
    if out_file:
        buf = StringIO()
        c = Console(file=buf, highlight=False)
    else:
        c = console

    ts = result.trust_score
    repo = result.repo

    # ---- Score panel ----
    score_text = Text()
    score_text.append(f"\n  {ts.score}/100 ", style=f"bold {ts.color} on black")
    score_text.append(f"  Grade: {ts.grade}\n", style=f"bold {ts.color}")
    score_text.append(f"  {ts.verdict}\n", style=f"bold white")
    score_text.append(f"  Confidence: {ts.confidence.upper()}\n\n", style="dim")
    score_text.append(f"  {ts.summary}\n", style="white")

    c.print()
    c.print(Panel(score_text, title=f"[bold]🔬 Trust Score: {owner_name(result)}", border_style=ts.color, expand=False))

    # ---- Repo info ----
    info_table = Table(box=None, padding=(0, 2), show_header=False)
    info_table.add_column(style="dim")
    info_table.add_column()
    info_table.add_row("Repository", f"[bold cyan]{repo.owner}/{repo.name}[/bold cyan]")
    info_table.add_row("Stars", f"[bold]{repo.stars:,}[/bold]")
    info_table.add_row("Forks", f"{repo.forks:,}")
    info_table.add_row("Sample analyzed", f"{result.sample_size:,} stargazers ({result.sample_size/max(repo.stars,1)*100:.1f}%)")
    if repo.language:
        info_table.add_row("Language", repo.language)
    if repo.description:
        desc = repo.description[:72] + "…" if len(repo.description or "") > 72 else repo.description
        info_table.add_row("Description", desc or "")

    c.print()
    c.print(Panel(info_table, title="📦 Repository Info", border_style="blue"))

    # ---- Patterns table ----
    c.print()
    ptable = Table(
        title="🔍 Forensic Pattern Results",
        box=box.ROUNDED,
        border_style="dim",
        show_lines=True,
        expand=True,
    )
    ptable.add_column("", width=3)
    ptable.add_column("Pattern", style="bold", min_width=24)
    ptable.add_column("Severity", justify="center", width=10)
    ptable.add_column("Finding", min_width=36)

    for p in result.patterns:
        sev_color = SEVERITY_STYLE.get(p.severity, "white") if p.flagged else "dim"
        ptable.add_row(
            p.emoji,
            p.name,
            f"[{sev_color}]{p.severity.upper()}[/{sev_color}]" if p.flagged else "[dim]CLEAN[/dim]",
            p.detail,
        )

    c.print(ptable)

    # ---- Evidence details for flagged patterns ----
    flagged = [p for p in result.patterns if p.flagged]
    if flagged:
        c.print()
        c.print(Rule("[bold red]⚠  Flagged Patterns — Evidence[/bold red]"))
        for p in flagged:
            ev_lines = []
            for k, v in p.evidence.items():
                if isinstance(v, list) and v and isinstance(v[0], dict):
                    ev_lines.append(f"  [dim]{k}:[/dim]")
                    for item in v[:5]:
                        ev_lines.append(f"    • {item}")
                elif isinstance(v, list):
                    ev_lines.append(f"  [dim]{k}:[/dim] {', '.join(str(x) for x in v[:5])}")
                else:
                    ev_lines.append(f"  [dim]{k}:[/dim] {v}")
            body = "\n".join(ev_lines) if ev_lines else "  No additional evidence."
            c.print(Panel(body, title=f"{p.emoji} {p.name}", border_style=SEVERITY_STYLE.get(p.severity, "yellow"), expand=False))

    # ---- Footer ----
    c.print()
    c.print(Rule("[dim]star-forensics • github.com/star-forensics/star-forensics[/dim]"))
    c.print(f"[dim]Analyzed at {result.analyzed_at.strftime('%Y-%m-%d %H:%M:%S UTC')}[/dim]\n")

    if out_file and buf:
        Path(out_file).write_text(buf.getvalue())
        console.print(f"[green]✅ Report saved to [bold]{out_file}[/bold][/green]")


def owner_name(result):
    return f"{result.repo.owner}/{result.repo.name}"


def _output_json(result, out_file):
    from .patterns import PatternResult
    ts = result.trust_score
    data = {
        "repo": {
            "owner": result.repo.owner,
            "name": result.repo.name,
            "stars": result.repo.stars,
            "forks": result.repo.forks,
            "language": result.repo.language,
            "description": result.repo.description,
        },
        "analysis": {
            "sample_size": result.sample_size,
            "total_stars": result.total_stars,
            "analyzed_at": result.analyzed_at.isoformat(),
        },
        "trust_score": {
            "score": ts.score,
            "grade": ts.grade,
            "verdict": ts.verdict,
            "confidence": ts.confidence,
            "summary": ts.summary,
        },
        "patterns": [
            {
                "id": p.id,
                "name": p.name,
                "flagged": p.flagged,
                "severity": p.severity if p.flagged else "clean",
                "score_impact": p.score_impact,
                "detail": p.detail,
                "evidence": p.evidence,
            }
            for p in result.patterns
        ],
    }
    out = json.dumps(data, indent=2, default=str)
    if out_file:
        Path(out_file).write_text(out)
        console.print(f"[green]✅ JSON report saved to [bold]{out_file}[/bold][/green]")
    else:
        print(out)


def _output_html(result, out_file):
    from .report import render_html
    html = render_html(result)
    target = out_file or f"{result.repo.owner}_{result.repo.name}_forensics.html"
    Path(target).write_text(html)
    console.print(f"[green]✅ HTML report saved to [bold]{target}[/bold][/green]")


@cli.command()
@click.argument("repo")
@click.option("--token", "-t", envvar="GITHUB_TOKEN", default=None, help="GitHub token.")
@click.option("--max-stars", "-n", default=500, show_default=True)
@click.option("--svg", "fmt", flag_value="svg", help="Output SVG file.")
@click.option("--markdown", "fmt", flag_value="markdown", default=True, help="Output Markdown snippet (default).")
@click.option("--out-file", "-f", type=click.Path(), default=None)
def badge(repo: str, token: str | None, max_stars: int, fmt: str, out_file: str | None):
    """
    Generate an embeddable trust-score badge for a repository.

    \b
    Example:
      star-forensics badge owner/repo
      # → [![star-forensics score](...)](...)
    """
    from .badge import generate_badge_svg, generate_badge_markdown

    owner, name = _parse_repo(repo)
    console.print(f"\n[bold]🏷  Generating badge for[/bold] [cyan]{owner}/{name}[/cyan]...\n")

    result = analyze_repo(owner, name, token=token, max_stars=max_stars)
    ts = result.trust_score

    if fmt == "svg":
        svg = generate_badge_svg(ts.score, ts.grade, ts.verdict, owner, name)
        target = out_file or f"{owner}_{name}_badge.svg"
        from pathlib import Path
        Path(target).write_text(svg)
        console.print(f"[green]✅ SVG badge saved to [bold]{target}[/bold][/green]")
    else:
        md = generate_badge_markdown(ts.score, ts.grade, ts.verdict, owner, name, out_file)
        console.print("[bold]Paste this into your README:[/bold]\n")
        console.print(f"[cyan]{md}[/cyan]\n")
        if out_file:
            console.print(f"[green]✅ Also saved to [bold]{out_file}[/bold][/green]")


@cli.command()
@click.option("--token", "-t", envvar="GITHUB_TOKEN", default=None, help="GitHub token.")
def limits(token: str | None):
    """Show current GitHub API rate limit status."""
    from .analyzer import GitHubClient
    with GitHubClient(token=token) as client:
        data = client.get_rate_limit()
    core = data["resources"]["core"]
    used = core["limit"] - core["remaining"]
    reset = datetime.fromtimestamp(core["reset"], tz=timezone.utc)
    table = Table(box=box.SIMPLE, title="GitHub API Rate Limits")
    table.add_column("Resource")
    table.add_column("Used", justify="right")
    table.add_column("Remaining", justify="right")
    table.add_column("Resets at")
    table.add_row("core", str(used), str(core["remaining"]), reset.strftime("%H:%M:%S UTC"))
    console.print(table)


def main():
    cli()


if __name__ == "__main__":
    main()
