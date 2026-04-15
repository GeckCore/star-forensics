# 🕵️ star-forensics

<div align="center">

**Detect fake GitHub stars with forensic analysis.**

[![PyPI](https://img.shields.io/pypi/v/star-forensics?color=blue&style=flat-square)](https://pypi.org/project/star-forensics/)
[![Python](https://img.shields.io/pypi/pyversions/star-forensics?style=flat-square)](https://pypi.org/project/star-forensics/)
[![CI](https://img.shields.io/github/actions/workflow/status/star-forensics/star-forensics/ci.yml?style=flat-square)](https://github.com/star-forensics/star-forensics/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)
[![Stars](https://img.shields.io/github/stars/star-forensics/star-forensics?style=flat-square&color=yellow)](https://github.com/star-forensics/star-forensics/stargazers)

*Buying GitHub stars is more common than you think.*

[**Quick Start**](#-quick-start) · [**How It Works**](#-how-it-works) · [**Patterns**](#-detection-patterns) · [**FAQ**](#-faq) · [**Contributing**](#-contributing)

</div>

---

## The Problem

GitHub stars are a proxy for trust. Developers use them to evaluate libraries, companies use them in pitches, hiring managers Google repos before interviews.

And a growing industry sells them.

Services like `buygithubstars.com` (yes, really) offer 1,000 stars for $50–$150. The accounts are either purchased, farmed, or created in bulk. The patterns are detectable — if you know what to look for.

**star-forensics** knows what to look for.

---

## ⚡ Quick Start

```bash
# Install
pip install star-forensics

# Analyze any repo
star-forensics analyze owner/repo

# With a GitHub token (recommended — 5000 req/hr vs 60)
GITHUB_TOKEN=ghp_xxx star-forensics analyze owner/repo

# Export as JSON or HTML
star-forensics analyze owner/repo --output html --out-file report.html

# Analyze more stargazers (default: 1000)
star-forensics analyze owner/repo --max-stars 3000
```

> **No installation?** Run it directly:
> ```bash
> pipx run star-forensics analyze owner/repo
> ```

---

## 🖥 Example Output

```
  ╭──────────────────────────────────────────────────────╮
  │  🔬 Trust Score: someorg/trending-repo               │
  │                                                      │
  │   23/100   Grade: F                                  │
  │   Manipulated                                        │
  │   Confidence: HIGH                                   │
  │                                                      │
  │   Overwhelming evidence of star manipulation.        │
  │   This repo almost certainly purchased stars.        │
  ╰──────────────────────────────────────────────────────╯

  🔍 Forensic Pattern Results
  ┌────────────────────────────┬────────────┬─────────────────────────────────────────────────┐
  │ Pattern                    │ Severity   │ Finding                                         │
  ├────────────────────────────┼────────────┼─────────────────────────────────────────────────┤
  │ 💀 Ghost Accounts          │ CRITICAL   │ 612 accounts (61.2%) show zero activity markers │
  │ 💀 Account Creation Clust… │ CRITICAL   │ 480 accounts clustered on 3 suspicious dates    │
  │ 🔴 Star Velocity Spikes    │ HIGH       │ Peak: 847 stars in one hour vs avg 4.2/hr       │
  │ 🔴 Freshly Minted Accounts │ HIGH       │ 234 accounts starred within 30 days of creation │
  │ 🟠 Bot-like Usernames      │ MEDIUM     │ 89 accounts (8.9%) match bot-farm patterns      │
  │ ✅ Star/Fork Disproportion  │ CLEAN      │ Star-to-fork ratio is 12:1 (within normal range)│
  └────────────────────────────┴────────────┴─────────────────────────────────────────────────┘
```

---

## 🔬 How It Works

star-forensics fetches stargazer data from the GitHub API and runs a battery of forensic detectors. Each detector produces a severity rating and a score impact. The final **Trust Score** (0–100) is computed from the combined evidence.

```
Fetch stargazers → Run detectors → Compute Trust Score → Report
```

The tool samples up to N stargazers (configurable) and applies statistical analysis — it doesn't need to check every star to find patterns.

**No data is stored. No accounts are tracked. Everything runs locally.**

---

## 🧪 Detection Patterns

| Pattern | What it detects | Severity |
|---|---|---|
| **Ghost Accounts** | Accounts with 0 repos, 0 followers, 0 following, no bio, no location | Critical |
| **Account Creation Clustering** | Large groups of accounts created on the same days | Critical |
| **Star Velocity Spikes** | Statistically abnormal bursts of stars (e.g. 500 stars in 1 hour) | High |
| **Freshly Minted Accounts** | Accounts that starred within 30 days of being created | High |
| **Socially Isolated Accounts** | Accounts with zero followers AND zero following | Medium |
| **Bot-like Usernames** | Usernames matching bot-farm patterns (e.g. `user12345678`) | Medium |
| **Repoless Stargazers** | Accounts with zero public repositories | Low |
| **Star/Fork Disproportion** | Abnormally high star-to-fork ratio vs. organic repos | Low |

Each pattern is independent and can be individually weighted. Contributions of new detectors are very welcome.

---

## 📊 Trust Score

| Score | Grade | Verdict |
|---|---|---|
| 80–100 | A | ✅ Trusted |
| 60–79 | B | ⚠️ Suspicious |
| 35–59 | C/D | 🔴 Likely Fake |
| 0–34 | F | 💀 Manipulated |

The score is **not a verdict** — it's a signal. A low score should prompt further investigation, not an immediate accusation. Natural repos can have some ghost accounts. The score reflects the *statistical likelihood* of manipulation.

---

## 🔑 GitHub Token

Without a token you get **60 API requests/hour**. With a token: **5,000/hour**.

```bash
# Create a token at: https://github.com/settings/tokens
# Only needs "public_repo" read access (no write permissions needed)
export GITHUB_TOKEN=ghp_your_token_here

# Or pass it directly
star-forensics analyze owner/repo --token ghp_your_token_here
```

---

## 📤 Output Formats

```bash
# Rich terminal output (default)
star-forensics analyze owner/repo

# JSON (machine-readable, great for CI)
star-forensics analyze owner/repo --output json

# Self-contained HTML report (share with your team)
star-forensics analyze owner/repo --output html --out-file report.html

# Save terminal output to file
star-forensics analyze owner/repo --out-file report.txt
```

---

## 🐍 Python API

```python
from starforensics.analyzer import analyze_repo

result = analyze_repo(
    owner="some-org",
    name="some-repo",
    token="ghp_...",    # optional
    max_stars=2000,
)

print(f"Trust Score: {result.trust_score.score}/100")
print(f"Verdict: {result.trust_score.verdict}")

for pattern in result.patterns:
    if pattern.flagged:
        print(f"  ⚠ {pattern.name}: {pattern.detail}")
```

---

## ⚠️ Limitations & Ethics

**This tool is for investigative and educational purposes.**

- A low score is a **signal**, not proof. Some patterns occur naturally.
- GitHub accounts can be old and inactive for legitimate reasons.
- Viral spikes (HN front page, Reddit, ProductHunt) can look like artificial bursts.
- The tool **does not identify specific fake accounts** — only statistical patterns.
- We recommend comparing results against the repo's history (launch date, press coverage).

**Do not use this tool to harass maintainers or make public accusations without thorough investigation.**

---

## ❓ FAQ

**Why would anyone buy GitHub stars?**
Social proof. Stars influence trending algorithms, appear in Google searches, affect hiring decisions, and increase VC interest. The incentives are real.

**Which repos have you found suspicious?**
We don't maintain a public list — that's not the goal. The goal is to give everyone a tool to investigate for themselves.

**Can I trust your own star count?**
Yes. You can run `star-forensics analyze star-forensics/star-forensics` anytime to verify. We welcome transparency.

**Does GitHub do anything about this?**
GitHub removes accounts that violate their ToS, but bulk-star services adapt faster than enforcement can react.

**How is this different from [other tools]?**
Most existing tools just check star velocity. star-forensics combines 8+ independent signals into a composite score with confidence levels and detailed evidence output.

**Will this tool be used to unfairly target legitimate repos?**
We've added significant guardrails in the scoring system to reduce false positives. But we can always improve — open an issue if you think a legitimate repo is being unfairly scored.

---

## 🤝 Contributing

Contributions are very welcome! Here's what we need most:

- **New detection patterns** — New ideas for signals? Open an issue or PR.
- **Improved scoring weights** — The current weights are heuristic. Help us calibrate them.
- **Test cases** — Known fake-star repos (historical) make great test fixtures.
- **False positive reports** — If a legitimate repo scores poorly, tell us why.

```bash
git clone https://github.com/star-forensics/star-forensics
cd star-forensics
pip install -e ".[dev]"
pytest tests/ -v
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

---

## 📖 Background Reading

- [Buying GitHub Stars](https://dagster.io/blog/fake-stars) — Dagster's investigation
- [The Star Inflation Problem](https://arxiv.org/abs/2412.13459) — Academic paper on GitHub star manipulation
- [Detecting Fake GitHub Stars at Scale](https://blog.gitguardian.com/github-stars/) — GitGuardian research

---

## 📄 License

MIT. See [LICENSE](LICENSE).

---

<div align="center">

Made with 🔬 by the open source community

*If this helped you, consider starring the repo — we'll know if you don't mean it.* 😏

</div>
