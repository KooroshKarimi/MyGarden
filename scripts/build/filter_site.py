#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import re
import shutil


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        return {}
    parts = text.split('\n---\n', 1)
    if len(parts) != 2:
        return {}
    fm = parts[0].splitlines()[1:]
    data = {}
    current_list_key = None
    for raw in fm:
        line = raw.rstrip()
        if not line.strip() or line.strip().startswith('#'):
            continue
        m = re.match(r'^([A-Za-z0-9_-]+):\s*(.*)$', line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            current_list_key = None
            if val.startswith('[') and val.endswith(']'):
                inner = val[1:-1].strip()
                data[key] = [x.strip().strip('"\'') for x in inner.split(',') if x.strip()]
            elif val == '':
                data[key] = []
                current_list_key = key
            else:
                data[key] = val.strip('"\'')
            continue
        m = re.match(r'^\s*-\s*(.+)$', line)
        if m and current_list_key:
            data.setdefault(current_list_key, []).append(m.group(1).strip().strip('"\''))
    return data


def should_include(meta: dict, audience: str, group: str | None) -> bool:
    visibility = str(meta.get('visibility', 'private')).strip().lower()
    status = str(meta.get('status', 'seedling')).strip().lower()
    groups = meta.get('groups', [])
    if not isinstance(groups, list):
        groups = [str(groups)] if groups else []

    if audience == 'private':
        return True
    if audience == 'public':
        return visibility == 'public' and status in {'plant', 'tree'}
    # group audience
    if visibility == 'public':
        return True
    if visibility == 'group' and group:
        return group in [str(g) for g in groups]
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True)
    ap.add_argument('--dest', required=True)
    ap.add_argument('--audience', choices=['public', 'group', 'private'], required=True)
    ap.add_argument('--group', default='')
    args = ap.parse_args()

    src = Path(args.source)
    dst = Path(args.dest)
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True, exist_ok=True)

    for item in src.iterdir():
        if item.name == 'content':
            continue
        target = dst / item.name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)

    (dst / 'content').mkdir(parents=True, exist_ok=True)
    for md in (src / 'content').rglob('*.md'):
        rel = md.relative_to(src / 'content')
        meta = parse_frontmatter(md)
        if should_include(meta, args.audience, args.group or None):
            out = dst / 'content' / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(md, out)

    return 0

if __name__ == '__main__':
    raise SystemExit(main())
