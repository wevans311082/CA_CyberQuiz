# Security audit

Date: 2026-08-31  
Scope: OWASP Top 10 review, server-side request forgery, upload handling, authentication/session settings, access-control boundaries, and SQL injection paths.

## Implemented hardening

- Server-side URL imports validate scheme, reject embedded credentials, restrict approved hosts where applicable, resolve DNS, reject loopback/private/link-local/reserved addresses, disable redirects, apply timeouts, and enforce response-size limits.
- Multipart and raw uploads are bounded and now persist their actual byte size. Deleted storage records are no longer downloadable through the public storage endpoints.
- HTTPS deployments set secure session/auth cookies and emit baseline browser security headers. Set `ENVIRONMENT=production` so the application refuses default secret keys at startup.
- Quiz PINs, controller codes, and hashcash salts use the `secrets` module instead of the non-cryptographic PRNG.
- Scenario reference documents are checked against the authenticated owner before being attached to a scenario.

## Findings and verification

- Static SQL review found ORM/parameterised database access; no request-controlled SQL string construction was found. The sitemap queries are fixed application constants. A live SQL injection test still requires a disposable Postgres-backed environment.
- Bandit found no high- or medium-confidence findings in application code. Remaining low-confidence results are mainly test assertions, avatar presentation randomness, and literal configuration strings.
- `npm audit --omit=dev` reports no production frontend vulnerabilities.
- Python dependency scanning of the shared development environment reports vulnerabilities in packages outside this repository's runtime set. The lockfile also contains older pinned dependencies and should be refreshed in a controlled dependency-upgrade change rather than auto-fixing the whole environment.
- Full authenticated multi-user DAST remains a release gate: exercise owner versus participant, private reference documents, file downloads, websocket events, uploads, and scenario/version endpoints must be tested against disposable Postgres and Redis services.

## Remaining high-priority work

1. Replace bare public storage UUID URLs for private exercise documents with short-lived, exercise-scoped signed URLs or an authenticated download endpoint. This is needed to close the residual IDOR/private-document exposure while preserving public quiz media.
2. Add a CSP after auditing the editor's intentionally rendered HTML and third-party assets; then reduce or narrowly isolate the remaining `{@html}` sinks.
3. Refresh and pin Python dependencies from a clean lock-generation environment, with application tests and a vulnerability review before deployment.

This document records the code-level review; it is not a substitute for a penetration test against an isolated deployment.
