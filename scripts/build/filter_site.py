#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import re
import shutil
import sys


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding='utf-8').replace('\r\n', '\n').replace('\r', '\n')
    if not text.startswith('---\n'):
        return {}

    # Accept YAML frontmatter with platform-dependent newlines and optional
    # whitespace around the closing delimiter.
    m = re.match(r'^---\n(.*?)\n---\s*(?:\n|$)', text, re.DOTALL)
    if not m:
        return {}

    fm = m.group(1).splitlines()
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


def clean_destination(dst: Path) -> tuple[bool, str]:
    """Clean the content directory inside dst (leave resources cache intact)."""
    content_dir = dst / 'content'
    if not content_dir.exists():
        dst.mkdir(parents=True, exist_ok=True)
        return True, ''

    try:
        shutil.rmtree(content_dir, ignore_errors=True)
        if content_dir.exists():
            raise PermissionError(f"could not fully remove {content_dir}")
        return True, ''
    except PermissionError:
        msg = (
            f"cannot clean destination '{dst}/content' (permission denied). "
            "This often happens after running the build once with sudo. "
            "Fix ownership (e.g. `sudo chown -R $USER:$USER .build out`) "
            "or run this command with sudo."
        )
        return False, msg



def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True)
    ap.add_argument('--dest', required=True)
    ap.add_argument('--audience', choices=['public', 'group', 'private'], required=True)
    ap.add_argument('--group', default='')
    args = ap.parse_args()

    src = Path(args.source)
    dst = Path(args.dest)
    ok, err = clean_destination(dst)
    if not ok:
        print(f"[FAIL] {err}", file=sys.stderr)
        return 1
    dst.mkdir(parents=True, exist_ok=True)

    for item in src.iterdir():
        if item.name in ('content', 'resources'):
            continue
        target = dst / item.name
        if item.is_dir():
            if target.exists():
                shutil.rmtree(target, ignore_errors=True)
            shutil.copytree(item, target, copy_function=shutil.copy)
        else:
            shutil.copy(item, target)

    content_root = src / 'content'
    (dst / 'content').mkdir(parents=True, exist_ok=True)

    include_regular: set[Path] = set()
    include_regular_meta: dict[Path, dict] = {}
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
            include_regular_meta[rel] = meta

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
        shutil.copy(content_root / rel, out)

        # Page bundle support: if this is an index.md (leaf bundle),
        # copy all non-MD sibling resources (images, etc.)
        if rel.name == 'index.md':
            bundle_dir = (content_root / rel).parent
            for res in bundle_dir.iterdir():
                if res.is_file() and res.suffix.lower() != '.md':
                    shutil.copy(res, out.parent / res.name)

    # Synthesize missing section _index.md files for included pages.
    # This keeps pretty section URLs (e.g. /politik/) resolvable even if an
    # upstream content source forgot to include visibility/status on _index.md.
    included_sections: set[Path] = set()
    for rel in include_regular:
        meta = include_regular_meta.get(rel, {})
        page_type = str(meta.get('type', '')).strip().lower()

        parent = rel.parent
        while parent != Path('.'):
            # Avoid synthesizing index pages for pure timeline-entry containers
            # like /politik/timeline/ when no source _index.md exists.
            if not (parent == rel.parent and page_type == 'timeline-entry'):
                included_sections.add(parent)
            parent = parent.parent

    # Collect leaf bundle dirs (have index.md) to avoid synthesizing _index.md there
    leaf_bundle_dirs: set[Path] = set()
    for rel in include_regular:
        if rel.name == 'index.md':
            leaf_bundle_dirs.add(rel.parent)

    for section in sorted(included_sections):
        # Don't create _index.md in leaf bundle directories
        if section in leaf_bundle_dirs:
            continue
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
