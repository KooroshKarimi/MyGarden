#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

echo "[filter-site] Python compile"
python3 -m py_compile scripts/build/filter_site.py scripts/build/leak_check.py

echo "[filter-site] permission-handling self-check"
python3 <<'PY'
from pathlib import Path
import scripts.build.filter_site as fs

p = Path('.tmp-filter-site-check')
p.mkdir(exist_ok=True)
orig_rmtree = fs.shutil.rmtree

try:
    def boom(_):
        raise PermissionError('denied')

    fs.shutil.rmtree = boom
    ok, err = fs.clean_destination(p)
    assert ok is False
    assert 'permission denied' in err
finally:
    fs.shutil.rmtree = orig_rmtree
    p.rmdir()
PY

echo "[filter-site] checks passed"
