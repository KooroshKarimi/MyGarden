# Security Audit Findings -- 2026-02-09

## Finding Index
| ID | Severity | Title | File |
|----|----------|-------|------|
| C1 | CRITICAL | .env world-readable with production secrets | .env |
| C2 | CRITICAL | Docker socket in content-api | docker-compose.yml:27 |
| C3 | CRITICAL | Shared test password hash | users_database.yml:5,13 |
| H1 | HIGH | No CSRF protection on API | api/server.py |
| H2 | HIGH | No CORS headers on API | default.conf:79-91 |
| H3 | HIGH | /private/ open to all authenticated users | configuration.yml:33-36 |
| H4 | HIGH | /comments-private/ open to all | configuration.yml:39-40 |
| H5 | HIGH | /reader/ open to all (supposed to be owner only) | configuration.yml:43-44 |
| H6 | HIGH | X-Authenticated-User header exposed | default.conf:207,222,236 |
| M1 | MEDIUM | Leak check auto-fix masks bugs | leak-check.sh:9 |
| M2 | MEDIUM | CSP unsafe-inline for scripts | security-headers.inc:3 |
| M3 | MEDIUM | Default fallback secrets | docker-compose.yml:48-50 |
| M4 | MEDIUM | img-src allows any https | security-headers.inc:3 |
| M5 | MEDIUM | No rate limit on content API | default.conf:79-91 |
| M6 | MEDIUM | Avatar upload no content validation | server.py:258-270 |
| M7 | MEDIUM | Public filter ignores status field | filter_site.py:57 |

## Remediation Priority
1. chmod 600 .env + rotate ALL secrets
2. Add subject restrictions to /private, /reader, /comments-private in Authelia
3. Remove docker.sock from content-api
4. Add SameSite=Lax to Authelia session + Origin validation in API
5. Fix filter_site.py to check status for public builds
