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
