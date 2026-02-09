# Security Auditor Memory -- MyGarden

## Last Audit: 2026-02-09

See [audit-findings.md](audit-findings.md) for detailed findings.

## Attack Surface Inventory
- **Public**: nginx static files at `/`, section routes, `/comments/` (remark42), `/api/avatar/`, `/healthz`
- **Authenticated (any user)**: `/private/`, `/g/friends/`, `/g/family/`, `/comments-private/`, `/reader/`
- **Admin only**: `/api/content/`, `/api/admin-check`
- **Internal only**: `/internal/authelia/authz`

## Critical Vulnerabilities Found
1. `.env` file world-readable (777) with all production secrets (DSM password, IONOS API, Authelia secrets)
2. Docker socket mounted in content-api container = root-equivalent host access
3. Shared test password hash on friends_user/family_user (salt: "ThisIsASeedForTesting")

## Key Access Control Gaps
- `/private/`, `/comments-private/`, `/reader/` have no `subject` restriction in Authelia -- any authenticated user can access
- No CSRF protection on content API (no SameSite cookie, no token, no Origin check)
- `X-Authenticated-User` header leaked to browser in responses

## Content Filtering Notes
- `filter_site.py` public audience does NOT check `status` field -- seedlings with visibility:public leak to public build
- Leak check runs in auto-fix mode by default, masking filter bugs
- `leak_check.py` uses different frontmatter parser than `filter_site.py` (split-based vs regex) -- potential inconsistency

## Security Headers
- CSP allows `script-src 'unsafe-inline'` -- defeats XSS protection
- No HSTS header
- No Permissions-Policy header
- No `server_tokens off`

## Docker/Infra Notes
- content-api has docker.sock + full project mount read-write
- Authelia secrets have weak fallback defaults in docker-compose.yml
- REMARK42_PRIVATE_SECRET missing from production .env (falls back to placeholder)
- users_database.yml committed to git history
