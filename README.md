# 🕵️ star-forensics

<div align="center">

**Detect fake GitHub stars with forensic analysis.**

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![CI](https://img.shields.io/github/actions/workflow/status/GeckCore/star-forensics/ci.yml?style=flat-square)](https://github.com/GeckCore/star-forensics/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)
[![Stars](https://img.shields.io/github/stars/GeckCore/star-forensics?style=flat-square&color=yellow)](https://github.com/GeckCore/star-forensics/stargazers)

*Buying GitHub stars is more common than you think.*

[**🚀 Complete beginner? Start here**](#-complete-installation-guide-no-experience-needed) · [**Quick Start**](#-quick-start) · [**How It Works**](#-how-it-works) · [**Patterns**](#-detection-patterns) · [**FAQ**](#-faq) · [**Contributing**](#-contributing)

</div>

---

## The Problem

GitHub stars are a proxy for trust. Developers use them to evaluate libraries, companies use them in pitches, hiring managers Google repos before interviews.

And a growing industry sells them.

Services like `buygithubstars.com` (yes, really) offer 1,000 stars for $50–$150. The accounts are either purchased, farmed, or created in bulk. The patterns are detectable — if you know what to look for.

**star-forensics** knows what to look for.

---

## 🚀 Complete Installation Guide (No Experience Needed)

> **Never used a terminal before? Never installed Python?** This section is for you. Follow every step and you'll be analyzing repos in under 5 minutes.

### Step 1 — Install Python

Python is the programming language this tool runs on. Think of it as the engine. You need to install it once, and it's free.

**On Windows:**
1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Click the big yellow **"Download Python"** button
3. Run the downloaded file
4. ⚠️ **CRITICAL:** On the first screen of the installer, check the box that says **"Add Python to PATH"** before clicking Install. If you miss this, nothing will work and you'll have to reinstall.

**On Mac:**
1. Open **Terminal** (press `Cmd + Space`, type `Terminal`, press Enter)
2. Paste this and press Enter:
   ```bash
   brew install python


If you get an error, first install Homebrew by going to [brew.sh](https://brew.sh) and following their one-line install command. Then try again.

**On Linux (Ubuntu/Debian):**

```bash
sudo apt install python3 python3-pip
```

**How to verify it worked:** Open a terminal and type:

```bash
python --version
```

You should see something like `Python 3.11.4`. Any version `3.9` or higher is fine.

-----

### Step 2 — Open a Terminal

A terminal is a text window where you type commands. It sounds scary but you'll only need to type two things total.

| System | How to open it |
|---|---|
| **Windows** | Press `Win + R`, type `cmd`, press Enter. Or search "Command Prompt" in the Start menu. |
| **Mac** | Press `Cmd + Space`, type `Terminal`, press Enter. |
| **Linux** | `Ctrl + Alt + T` on most distros. |

-----

### Step 3 — Download and Install

Currently, the tool must be installed directly from the source. In your terminal, run these commands in order:

```bash
git clone [https://github.com/GeckCore/star-forensics.git](https://github.com/GeckCore/star-forensics.git)
cd star-forensics
pip install .
```

*(Note: If you don't have `git` installed, you can download the repository as a ZIP file, extract it, open your terminal inside the extracted folder, and run `pip install .`)*

**If you get an error saying `pip` is not found**, try:

```bash
pip3 install .
```

-----

### Step 4 — Analyze your first repo

Now type this in your terminal:

```bash
star-forensics analyze owner/repo
```

Replace `owner/repo` with any GitHub repository. The format is always the two words at the end of a GitHub URL separated by a slash.

**Examples:**

```bash
star-forensics analyze microsoft/vscode
star-forensics analyze facebook/react
star-forensics analyze torvalds/linux
```

You'll see a score and detailed breakdown appear in your terminal.

-----

### Step 5 (Recommended) — Get a GitHub Token for Faster Analysis

Without a token, the tool is limited to analyzing about 60 accounts per hour by GitHub's rules. With a free token, that jumps to 5,000. For repos with thousands of stars, this makes a big difference in speed.

**How to get a free token (takes 2 minutes):**

1.  Go to [github.com/settings/tokens](https://github.com/settings/tokens) (you need a free GitHub account)
2.  Click **"Generate new token (classic)"**
3.  Give it any name, e.g. `star-forensics`
4.  You don't need to check any permission boxes — leave them all unchecked
5.  Scroll down and click **"Generate token"**
6.  Copy the long string that starts with `ghp_`

**Use the token:**

```bash
star-forensics analyze owner/repo --token ghp_paste_your_token_here
```

**Or set it once so you never have to type it again:**

Windows (Command Prompt):

```cmd
set GITHUB_TOKEN=ghp_paste_your_token_here
```

Mac/Linux (Terminal):

```bash
export GITHUB_TOKEN=ghp_paste_your_token_here
```

-----

### 🆘 Troubleshooting

| Error | Fix |
|---|---|
| `star-forensics is not recognized` | The Python Scripts folder is not in your system PATH. You can either add it to your Windows PATH variables, or run the tool using `python -m starforensics analyze owner/repo` instead. |
| `pip is not recognized` | Reinstall Python and check "Add to PATH" (Windows). On Mac/Linux, try `pip3` instead of `pip`. |
| `Directory '.' is not installable` | You are not in the correct folder. Make sure you use `cd star-forensics` to enter the folder containing the `pyproject.toml` file before running `pip install .`. |
| `Rate limit exceeded` | You've hit GitHub's hourly cap. Add a token following Step 5 above. |
| Tool runs but shows nothing | The repo might have 0 stars. Try with a popular repo first: `star-forensics analyze microsoft/vscode` |

-----

## ⚡ Quick Start

```bash
# Clone and Install
git clone [https://github.com/GeckCore/star-forensics.git](https://github.com/GeckCore/star-forensics.git)
cd star-forensics
pip install .

# Analyze any repo
star-forensics analyze owner/repo

# With a GitHub token (recommended — 5000 req/hr vs 60)
GITHUB_TOKEN=ghp_xxx star-forensics analyze owner/repo

# Export as JSON or HTML
star-forensics analyze owner/repo --output html --out-file report.html

# Analyze more stargazers (default: 1000)
star-forensics analyze owner/repo --max-stars 3000
```

-----

## 🖥 Example Output

```text
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

-----

## 🔬 How It Works

star-forensics fetches stargazer data from the GitHub API and runs a battery of forensic detectors. Each detector produces a severity rating and a score impact. The final **Trust Score** (0–100) is computed from the combined evidence.

```text
Fetch stargazers → Run detectors → Compute Trust Score → Report
```

The tool samples up to N stargazers (configurable) and applies statistical analysis — it doesn't need to check every star to find patterns.

**No data is stored. No accounts are tracked. Everything runs locally.**

-----

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

-----

## 📊 Trust Score

| Score | Grade | Verdict |
|---|---|---|
| 80–100 | A | ✅ Trusted |
| 60–79 | B | ⚠️ Suspicious |
| 35–59 | C/D | 🔴 Likely Fake |
| 0–34 | F | 💀 Manipulated |

The score is **not a verdict** — it's a signal. A low score should prompt further investigation, not an immediate accusation. Natural repos can have some ghost accounts. The score reflects the *statistical likelihood* of manipulation.

-----

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

-----

## ⚠️ Limitations & Ethics

**This tool is for investigative and educational purposes.**

  - A low score is a **signal**, not proof. Some patterns occur naturally.
  - GitHub accounts can be old and inactive for legitimate reasons.
  - Viral spikes (HN front page, Reddit, ProductHunt) can look like artificial bursts.
  - The tool **does not identify specific fake accounts** — only statistical patterns.
  - We recommend comparing results against the repo's history (launch date, press coverage).

**Do not use this tool to harass maintainers or make public accusations without thorough investigation.**

-----

## ❓ FAQ

**Why would anyone buy GitHub stars?**
Social proof. Stars influence trending algorithms, appear in Google searches, affect hiring decisions, and increase VC interest. The incentives are real.

**Which repos have you found suspicious?**
We don't maintain a public list — that's not the goal. The goal is to give everyone a tool to investigate for themselves.

**Can I trust your own star count?**
Yes. You can run `star-forensics analyze GeckCore/star-forensics` anytime to verify. We welcome transparency.

**Does GitHub do anything about this?**
GitHub removes accounts that violate their ToS, but bulk-star services adapt faster than enforcement can react.

**How is this different from [other tools]?**
Most existing tools just check star velocity. star-forensics combines 8+ independent signals into a composite score with confidence levels and detailed evidence output.

**Will this tool be used to unfairly target legitimate repos?**
We've added significant guardrails in the scoring system to reduce false positives. But we can always improve — open an issue if you think a legitimate repo is being unfairly scored.

-----

## 🤝 Contributing

Contributions are very welcome\! Here's what we need most:

  - **New detection patterns** — New ideas for signals? Open an issue or PR.
  - **Improved scoring weights** — The current weights are heuristic. Help us calibrate them.
  - **Test cases** — Known fake-star repos (historical) make great test fixtures.
  - **False positive reports** — If a legitimate repo scores poorly, tell us why.

<!-- end list -->

```bash
git clone [https://github.com/GeckCore/star-forensics](https://github.com/GeckCore/star-forensics)
cd star-forensics
pip install -e ".[dev]"
pytest tests/ -v
```

See `CONTRIBUTING.md` for the full guide.

-----

## 📖 Background Reading

  - [Buying GitHub Stars](https://dagster.io/blog/fake-stars) — Dagster's investigation
  - [The Star Inflation Problem](https://arxiv.org/abs/2412.13459) — Academic paper on GitHub star manipulation
  - [Detecting Fake GitHub Stars at Scale](https://blog.gitguardian.com/github-stars/) — GitGuardian research

-----

## 📄 License

MIT. See `LICENSE`.

-----

\<div align="center"\>

Made with 🔬 by the open source community

*If this helped you, consider starring the repo — we'll know if you don't mean it.* 😏

\</div\>

```
```
