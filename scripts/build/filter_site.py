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

    content_root = src / 'content'
    (dst / 'content').mkdir(parents=True, exist_ok=True)

    include_regular: set[Path] = set()
    index_files: list[Path] = []

    # First pass: decide on regular content pages.
    for md in content_root.rglob('*.md'):
        rel = md.relative_to(content_root)
        if md.name == '_index.md':
            index_files.append(rel)
            continue
        meta = parse_frontmatter(md)
        if should_include(meta, args.audience, args.group or None):
            include_regular.add(rel)

    # Include section/home indexes when needed so pretty section URLs work.
    include_indexes: set[Path] = set()
    for rel in index_files:
        meta = parse_frontmatter(content_root / rel)
        if should_include(meta, args.audience, args.group or None):
            include_indexes.add(rel)
            continue

        # Structural fallback: keep _index for sections that contain included children.
        if rel.name == '_index.md':
            section = rel.parent
            has_child = any(str(child).startswith(str(section) + '/') for child in include_regular)
            if has_child:
                include_indexes.add(rel)

    for rel in sorted(include_regular | include_indexes):
        out = dst / 'content' / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(content_root / rel, out)

    # Synthesize missing section _index.md files for included pages.
    # This keeps pretty section URLs (e.g. /politik/) resolvable even if an
    # upstream content source forgot to include visibility/status on _index.md.
    included_sections: set[Path] = set()
    for rel in include_regular:
        parent = rel.parent
        while parent != Path('.'):
            included_sections.add(parent)
            parent = parent.parent

    for section in sorted(included_sections):
        idx_rel = section / '_index.md'
        idx_dst = dst / 'content' / idx_rel
        if idx_dst.exists():
            continue
        idx_src = content_root / idx_rel
        idx_dst.parent.mkdir(parents=True, exist_ok=True)
        if idx_src.exists():
            shutil.copy2(idx_src, idx_dst)
        else:
            idx_dst.write_text(
                "\n".join([
                    "---",
                    f'title: "{section.name.title()}"',
                    "status: tree",
                    "visibility: public",
                    "---",
                    "",
                ]),
                encoding='utf-8',
            )

    return 0

if __name__ == '__main__':
    raise SystemExit(main())
