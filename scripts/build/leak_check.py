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


def expected_public_pages(src: Path, pub: Path) -> tuple[set[Path], set[Path]]:
    """Return (allowed, disallowed) html leaf paths derived from content files."""
    allowed: set[Path] = set()
    disallowed: set[Path] = set()

    for md in src.rglob('*.md'):
        rel = md.relative_to(src)
        meta = parse_frontmatter(md)

        if md.name == '_index.md':
            # Hugo section/home index mapping
            if rel.parent == Path('.'):
                html = pub / 'index.html'
            else:
                html = pub / rel.parent.as_posix() / 'index.html'
        elif md.name == 'index.md':
            # Hugo leaf page bundle: dir/index.md -> dir/index.html
            html = pub / rel.parent.as_posix() / 'index.html'
        else:
            html = pub / rel.parent.as_posix() / md.stem / 'index.html'

        if is_public_allowed(meta):
            allowed.add(html)
        else:
            disallowed.add(html)

    return allowed, disallowed


def looks_content_derived(pub: Path, html: Path, src: Path) -> bool:
    """True if the output path corresponds to a possible content file path."""
    rel = html.relative_to(pub)
    parts = rel.parts
    if len(parts) == 1 and parts[0] == 'index.html':
        return True

    if len(parts) >= 2 and parts[-1] == 'index.html':
        # section index: /section/index.html -> content/section/_index.md
        if len(parts) == 2:
            return (src / parts[0] / '_index.md').exists()

        # regular leaf page path: /section/slug/index.html
        # Treat as content-derived unless it's a known taxonomy leaf path.
        if len(parts) >= 3:
            if parts[0] in {'tags', 'categories'}:
                return False
            return True

        # fallback exact source match if present
        section = Path(*parts[:-2])
        slug = parts[-2]
        if (src / section / f'{slug}.md').exists():
            return True

    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True)
    ap.add_argument('--public', required=True)
    ap.add_argument('--fix', action='store_true', help='delete leaked/orphaned files and empty dirs')
    args = ap.parse_args()

    src = Path(args.source)
    pub = Path(args.public)

    allowed, disallowed = expected_public_pages(src, pub)

    leaks: list[Path] = []

    # Direct policy leak: known non-public page exists in public output.
    for html in sorted(disallowed):
        if html.exists():
            leaks.append(html)

    # Orphan leak: content-derived page exists but no longer allowed by current source.
    for html in pub.rglob('index.html'):
        if html in allowed or html in disallowed:
            continue
        if not looks_content_derived(pub, html, src):
            # Ignore non-content generated pages (e.g. taxonomy/utility pages).
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
