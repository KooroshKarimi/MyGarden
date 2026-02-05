#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import re


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        return {}
    parts = text.split('\n---\n', 1)
    if len(parts) != 2:
        return {}
    fm = parts[0].splitlines()[1:]
    data = {}
    for raw in fm:
        line = raw.strip()
        if not line:
            continue
        m = re.match(r'^([A-Za-z0-9_-]+):\s*(.*)$', line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip().strip('"\'')
        data[key] = val
    return data


def slug_from_file(path: Path) -> str:
    return path.stem


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True)
    ap.add_argument('--public', required=True)
    args = ap.parse_args()

    src = Path(args.source)
    pub = Path(args.public)

    leaks = []
    for md in src.rglob('*.md'):
        if md.name == '_index.md':
            continue
        meta = parse_frontmatter(md)
        visibility = str(meta.get('visibility', 'private')).lower()
        if visibility == 'public':
            continue
        rel = md.relative_to(src)
        # expected public html path by section/slug
        section = rel.parent.as_posix()
        slug = slug_from_file(md)
        html = pub / section / slug / 'index.html'
        if html.exists():
            leaks.append(str(html))

    if leaks:
        print('Leak check failed. Non-public pages found in out/public:')
        for x in leaks:
            print(f' - {x}')
        return 1

    print('Leak check passed: no non-public pages found in out/public.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
