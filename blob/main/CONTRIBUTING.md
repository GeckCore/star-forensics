# Contributing to star-forensics

Thank you for your interest in contributing! This project thrives on community input — detection patterns, scoring improvements, bug reports, and test cases all make a huge difference.

## Getting Started

```bash
git clone https://github.com/star-forensics/star-forensics
cd star-forensics
pip install -e ".[dev]"
```

## Adding a New Detection Pattern

1. Open `starforensics/patterns.py`
2. Create a new function following the `detect_*` signature:
   ```python
   def detect_my_pattern(
       stargazers: list[StargazerProfile],
       repo: RepoInfo,
   ) -> PatternResult:
       ...
   ```
3. Add it to `_DETECTORS` at the bottom of the file
4. Write tests in `tests/test_patterns.py`
5. Open a PR with a clear description of what the pattern detects and why it's a signal

## Reporting False Positives

If a legitimate repo scores poorly, please open an issue with:
- The repo URL
- The score and which patterns fired
- Any context that explains why the patterns don't apply (e.g., "this repo went viral on HN")

## Code Style

We use `ruff` for linting. Run `ruff check .` before committing.

## Testing

```bash
pytest tests/ -v --cov=starforensics
```

Tests run against offline fixtures — no GitHub API calls required.

## Principles

- **Don't expose individual accounts** — report aggregate statistics only
- **Prefer precision over recall** — false negatives are better than false positives
- **Document your reasoning** — pattern PRs should explain the theory behind the signal
