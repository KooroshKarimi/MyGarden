#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

echo "[filter-site] Python compile"
python3 -m py_compile scripts/build/filter_site.py scripts/build/leak_check.py

echo "[filter-site] permission-handling self-check"
python3 -c 'from pathlib import Path; import scripts.build.filter_site as fs; p=Path(".tmp-filter-site-check"); p.mkdir(exist_ok=True); orig=fs.shutil.rmtree; \
setattr(fs.shutil,"rmtree",lambda _: (_ for _ in ()).throw(PermissionError("denied"))); ok, err=fs.clean_destination(p); setattr(fs.shutil,"rmtree",orig); p.rmdir(); assert (ok is False) and ("permission denied" in err), "clean_destination permission check failed"'

echo "[filter-site] checks passed"
