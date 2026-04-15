# Security Policy

## Our commitment

star-forensics is a **read-only** analysis tool. It:

- Never writes data to GitHub
- Never stores stargazer data beyond the current analysis session
- Never makes API calls that require write permissions
- Only requires `public_repo` read access (or no token at all for public repos)

## Responsible disclosure

If you discover a security vulnerability in this tool (e.g. a way to inject malicious data into analysis output, or a privacy concern with how we handle API responses), please report it privately:

**Email:** security@star-forensics.dev *(placeholder — update before launch)*

Please **do not** open a public GitHub issue for security vulnerabilities.

## Scope

The following are **in scope**:
- Code execution vulnerabilities (e.g. injecting commands via repo names)
- Privacy issues with how API data is handled or logged
- Token leakage or credential exposure

The following are **out of scope**:
- GitHub's own API security (report to GitHub directly)
- Disagreements with scoring methodology (open a regular issue)

## Token handling

star-forensics accepts a GitHub token via `--token` or `GITHUB_TOKEN` environment variable. The token is:
- Only used for GitHub API authentication
- Never logged or written to disk
- Never sent to any third-party service
