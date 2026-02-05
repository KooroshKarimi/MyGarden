#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

python3 scripts/build/leak_check.py --source site/content --public out/public
