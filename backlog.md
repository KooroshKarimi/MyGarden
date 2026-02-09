# Security Backlog

## 1. Automated TLS Certificate Management
**Description:** Implement automated TLS certificate issuance and renewal using `acme.sh` with DNS-01 challenge via IONOS API to ensure secure HTTPS communication without manual intervention.
**Acceptance Criteria:**
- `acme.sh` container is deployed and configured with IONOS API credentials.
- A valid Let's Encrypt wildcard certificate (or specific domains) is obtained for `karimi.me`.
- The certificate is automatically deployed to the Synology DSM Reverse Proxy.
- The renewal process is automated and verified (e.g., via a dry-run).

## 2. Centralized Authentication & Authorization (Authelia)
**Description:** Set up Authelia as the central authentication service to protect private and group-specific routes, ensuring that only authorized users can access sensitive content.
**Acceptance Criteria:**
- Authelia container is running and accessible internally.
- Nginx Gateway is configured to use `auth_request` for protected paths (`/private/`, `/g/*`, `/reader/`).
- Users are redirected to the Authelia login page when accessing protected resources.
- After successful login, users are redirected back to the requested resource.
- Access is denied for unauthenticated users on protected paths.

## 3. Strict Content Separation to Prevent Leaks
**Description:** Configure the static site generator and build process to strictly separate public, group, and private content into different output directories. This prevents private content from ever being present in the public web root.
**Acceptance Criteria:**
- The build script generates distinct output directories: `out/public`, `out/groups/<group>`, and `out/private`.
- A verification step in the build pipeline checks that `out/public` contains zero private or group-restricted files.
- Nginx is configured to serve strictly from the appropriate directory based on the request path and authentication status.

## 4. Rate Limiting & Security Headers
**Description:** Harden the Nginx Gateway configuration by implementing rate limiting for sensitive endpoints and adding standard security headers to protect against common web attacks.
**Acceptance Criteria:**
- Rate limiting is configured and active for login endpoints (`/auth/`) and comment submissions to prevent brute-force and spam.
- Security headers are present in all responses:
  - `Content-Security-Policy` (CSP)
  - `Strict-Transport-Security` (HSTS)
  - `X-Content-Type-Options`
  - `X-Frame-Options`
  - `Referrer-Policy`
- The configuration is validated using a tool like Mozilla Observatory or Qualys SSL Labs (aiming for A/A+ rating).
