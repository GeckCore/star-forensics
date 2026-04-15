# 🚀 Launch Strategy — star-forensics

## Why this will go viral

This tool hits every viral trigger:

1. **Controversy** — It exposes fraud. People love receipts.
2. **Utility** — Devs immediately want to check repos they've used or competed with.
3. **Shareable output** — A score like "23/100 — Manipulated" is made for screenshots.
4. **Self-referential** — The tool can analyze itself. Transparency builds trust.
5. **Media hook** — "We checked the top 100 starred repos on GitHub" writes itself.

---

## Pre-launch checklist

- [ ] Create GitHub org: `star-forensics`
- [ ] Repo name: `star-forensics/star-forensics` (clean, memorable)
- [ ] Publish to PyPI: `pip install star-forensics` must work on day 1
- [ ] Pin a "Good First Issues" set (3-5 small pattern ideas) for contributor momentum
- [ ] Add a demo GIF to the README (record with `asciinema` or `vhs`)
- [ ] Add a "Verified Clean" badge to your own repo's README on launch day
- [ ] Prepare 3 example analysis results to share (pick interesting repos, not to attack anyone)

---

## Launch sequence

### Day 0 (48h before)
- Soft-launch on Twitter/X: "Building something that detects fake GitHub stars. Preview: [screenshot]"
- Don't explain everything. Create curiosity.

### Day 1 — Main push
1. **Hacker News** — Post at 8am ET (peak engagement). Title options:
   - *"Show HN: star-forensics – detect fake GitHub stars with forensic analysis"*
   - *"I built a tool that detects fake GitHub stars"*
   - The "Show HN" prefix is crucial — it gets its own section
   
2. **Reddit r/programming** — Post at same time with a longer writeup. Title:
   - *"I built an open-source tool to detect fake GitHub stars. It analyzes 8 patterns: account clustering, velocity spikes, ghost accounts, and more."*

3. **Reddit r/netsec / r/opensourcesecurity** — Security angle post

4. **Twitter/X thread** — Screenshot format works best:
   - Tweet 1: The claim ("Buying GitHub stars is a real industry")
   - Tweet 2: How the tool works (diagram or gif)
   - Tweet 3: A dramatic example result (screenshot)
   - Tweet 4: Install command

### Day 2-7 — Sustain
- Respond to EVERY comment on HN and Reddit (it keeps threads active)
- Post follow-up findings: "We analyzed the top 50 trending repos and found..."
- Reach out to: InfoQ, TLDR newsletter, Changelog podcast, DevHunt

---

## Content that drives shares

### The "we analyzed X repos" angle
Write a companion blog post:
> *"We analyzed 1,000 trending GitHub repos. Here's what we found."*
This is pure link-bait in the best sense — concrete, data-driven, shareable.

### The "check your competitors" angle
This is what devs will actually use it for. 
Don't say this — let the community figure it out and post results themselves.

### The "check us" angle
Add to your own README: "Run `star-forensics analyze star-forensics/star-forensics` to verify our stars are real."
This is gold. It's transparent, confident, and shows you believe in the tool.

---

## Potential press targets

| Outlet | Contact angle |
|---|---|
| The Register | "Fake star farms are a real industry. Here's a tool to detect them." |
| Ars Technica | Security + open source angle |
| TechCrunch | "Startup metrics are being gamed" angle |
| Dev.to | Tutorial: "How fake stars work and how to detect them" |
| InfoQ | "New OSS tool applies forensic analysis to GitHub star manipulation" |

---

## Community features to add early (drives engagement)

1. **Public Hall of Shame / Hall of Fame** — a `results/` folder with community-submitted JSON reports
2. **GitHub Action** — `- uses: star-forensics/action@v1` that runs on schedule and comments on PRs
3. **Web UI** — Even a simple `star-forensics.dev` that lets people enter a repo name and see results
4. **Discord / discussions** — A place for people to post their findings

---

## What NOT to do

- Don't make a "list of fake repos" — that creates legal risk and controversy you don't want
- Don't publicly call out specific maintainers — let the tool speak for itself
- Don't over-claim — call it a "signal" not "proof"
- Don't ignore false positive reports — respond fast, fix fast

---

## GitHub repo optimizations

- **Topics**: `github`, `stars`, `fake-stars`, `security`, `analysis`, `forensics`, `cli`, `python`
- **Website field**: Link to PyPI or a landing page
- **Social preview image**: Dark background, "🕵️ star-forensics" + "Detect fake GitHub stars" (generate with Vercel's og-image or Satori)
- **Pinned issues**: 3-5 "good first issue" items ready for contributors

---

## Metrics to watch

- GitHub stars (ironic but important)
- PyPI downloads (shows real adoption)
- HN points and ranking
- Reddit karma and comment velocity
- Backlinks from other repos embedding the badge

---

## Long-term moat

Once the badge system catches on — repos embedding `[![star-forensics](badge-url)](...)` in their READMEs — every badge is a backlink and a discovery path. This is the real flywheel.

The GitHub Action is the ultimate moat: once CI pipelines run this tool, it becomes infrastructure.
