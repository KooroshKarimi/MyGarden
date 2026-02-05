#!/usr/bin/env bash
set -euo pipefail

DOMAIN=${1:-karimi.me}
EXPECT_IPV4_ONLY=${EXPECT_IPV4_ONLY:-false}

servers=("1.1.1.1" "8.8.8.8" "9.9.9.9")

lookup() {
  local type=$1
  local server=$2
  if command -v dig >/dev/null 2>&1; then
    dig +short "${type}" "${DOMAIN}" @"${server}" | sed '/^$/d' || true
  elif command -v nslookup >/dev/null 2>&1; then
    nslookup -type="${type}" "${DOMAIN}" "${server}" 2>/dev/null | awk '/^Address: /{print $2}' || true
  else
    echo "DNS lookup tool missing (need dig or nslookup)" >&2
    return 1
  fi
}

all_ok=true

echo "== DNS propagation for ${DOMAIN} =="
for s in "${servers[@]}"; do
  a=$(lookup A "$s" | tr '\n' ' ' | xargs || true)
  aaaa=$(lookup AAAA "$s" | tr '\n' ' ' | xargs || true)
  echo "${s} -> A: ${a:-<none>} | AAAA: ${aaaa:-<none>}"

  if [[ "${EXPECT_IPV4_ONLY}" == "true" ]] && [[ -n "${aaaa}" ]]; then
    all_ok=false
  fi
done

echo
if [[ "${EXPECT_IPV4_ONLY}" == "true" ]]; then
  if [[ "${all_ok}" == "true" ]]; then
    echo "[OK] No AAAA seen on checked public resolvers."
  else
    echo "[WARN] AAAA still visible on at least one public resolver; browser may still try IPv6 until TTL expires." >&2
    echo "Tip: test with IPv4-forced client first, then retry after DNS TTL propagation." >&2
    exit 2
  fi
fi
