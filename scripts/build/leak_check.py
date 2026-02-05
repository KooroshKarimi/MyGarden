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


def is_public_allowed(meta: dict) -> bool:
    visibility = str(meta.get('visibility', 'private')).lower()
    status = str(meta.get('status', 'seedling')).lower()
    return visibility == 'public' and status in {'plant', 'tree'}


def remove_empty_parents(path: Path, stop: Path) -> None:
    cur = path.parent
    while cur != stop and cur.exists():
        try:
            cur.rmdir()
        except OSError:
            break
        cur = cur.parent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True)
    ap.add_argument('--public', required=True)
    ap.add_argument('--fix', action='store_true', help='delete leaked/orphaned files and empty dirs')
    args = ap.parse_args()

    src = Path(args.source)
    pub = Path(args.public)

    # Expected page files that are allowed in public output.
    allowed: set[Path] = set()
    disallowed: set[Path] = set()

    for md in src.rglob('*.md'):
        rel = md.relative_to(src)

        # Section/home index pages are generated from _index.md and handled by Hugo.
        # We don't classify those as leaks here.
        if md.name == '_index.md':
            continue

        meta = parse_frontmatter(md)
        section = rel.parent.as_posix()
        slug = slug_from_file(md)
        html = pub / section / slug / 'index.html'
        if is_public_allowed(meta):
            allowed.add(html)
        else:
            disallowed.add(html)

    leaks = []

    # Direct policy leak: known non-public page exists in public output.
    for html in sorted(disallowed):
        if html.exists():
            leaks.append(html)

    # Orphan leak: generated leaf page exists, but no longer allowed by current source.
    for html in pub.rglob('index.html'):
        if html == pub / 'index.html':
            continue
        if html in allowed:
            continue
        # If it maps to a disallowed entry, already handled above.
        if html in disallowed:
            continue
        leaks.append(html)

    if leaks:
        if args.fix:
            for f in leaks:
                if f.exists():
                    f.unlink()
                    remove_empty_parents(f, pub)
            print('Leak check fixed leaked/orphaned pages in out/public:')
            for x in leaks:
                print(f' - removed {x}')
            print('Leak check passed after auto-fix.')
            return 0

        print('Leak check failed. Non-public or orphaned pages found in out/public:')
        for x in leaks:
            print(f' - {x}')
        print('Hint: run scripts/checks/leak-check.sh (default auto-fix) or LEAK_CHECK_STRICT=1 for strict mode.')
        return 1

    print('Leak check passed: no non-public pages found in out/public.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
