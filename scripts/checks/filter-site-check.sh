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

echo "[filter-site] functional public-tree self-check"
python3 scripts/build/filter_site.py --source site --dest .build/filter-site-check --audience public

python3 <<'PY'
from pathlib import Path

root = Path('.build/filter-site-check/content')
required = [
    root / '_index.md',
    root / 'politik' / '_index.md',
    root / 'technik' / '_index.md',
    root / 'reisen' / '_index.md',
    root / 'politik' / 'dossier-iran.md',
]

for f in required:
    assert f.exists(), f"missing expected file: {f}"

assert not (root / 'politik' / 'timeline' / '_index.md').exists(), \
    'unexpected synthesized timeline _index.md'
PY

rm -rf .build/filter-site-check

echo "[filter-site] checks passed"
