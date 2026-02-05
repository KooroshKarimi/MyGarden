#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

if [[ "${LEAK_CHECK_STRICT:-0}" == "1" ]]; then
  python3 scripts/build/leak_check.py --source site/content --public out/public
else
  python3 scripts/build/leak_check.py --source site/content --public out/public --fix
fi
