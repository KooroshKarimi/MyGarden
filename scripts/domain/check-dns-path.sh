#!/usr/bin/env bash
set -euo pipefail

DOMAIN=${1:-karimi.me}
ALT_HOST=${2:-synology.${DOMAIN}}

echo "== DNS records for ${DOMAIN} =="
if command -v dig >/dev/null 2>&1; then
  echo "A records:"; dig +short A "${DOMAIN}" || true
  echo "AAAA records:"; dig +short AAAA "${DOMAIN}" || true
elif command -v nslookup >/dev/null 2>&1; then
  echo "A records:"; nslookup -type=A "${DOMAIN}" 2>/dev/null | awk '/^Address: /{print $2}' || true
  echo "AAAA records:"; nslookup -type=AAAA "${DOMAIN}" 2>/dev/null | awk '/^Address: /{print $2}' || true
else
  echo "Neither dig nor nslookup is available."
fi

echo
if command -v dig >/dev/null 2>&1; then
  echo "== Optional subdomain CNAME check (${ALT_HOST}) =="
  dig +short CNAME "${ALT_HOST}" || true
elif command -v nslookup >/dev/null 2>&1; then
  echo "== Optional subdomain CNAME check (${ALT_HOST}) =="
  nslookup -type=CNAME "${ALT_HOST}" 2>/dev/null | awk '/canonical name =/{print $NF}' || true
fi

echo
if command -v curl >/dev/null 2>&1; then
  echo "== HTTPS check over IPv4 =="
  curl -4 -I "https://${DOMAIN}/" || true
  echo
  echo "== HTTPS check over IPv6 =="
  curl -6 -I "https://${DOMAIN}/" || true
else
  echo "curl not found, skipping HTTPS checks"
fi

echo
cat <<'HINT'
Hinweis:
- Für die Hauptdomain `karimi.me` zählen die Apex-Records (`A`/`AAAA` bei `@`).
  Ein zusätzlicher `CNAME` wie `synology.karimi.me -> koorosh.synology.me`
  beeinflusst den Zugriff auf `https://karimi.me` nicht.
- Wenn IPv4 funktioniert, aber IPv6 fehlschlägt und ein AAAA-Record existiert,
  dann zeigt AAAA wahrscheinlich auf eine nicht korrekt konfigurierte IPv6-Zieladresse.
- In dem Fall: AAAA bei IONOS entfernen ODER IPv6 auf Router/DSM korrekt freischalten.
HINT
