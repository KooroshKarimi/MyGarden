#!/usr/bin/env python3
"""Validate frontmatter of all content markdown files."""
from __future__ import annotations

import re
import sys
from pathlib import Path

VALID_TYPES = {"note", "trip", "timeline-entry", "dossier", "article"}
VALID_SEGMENTS = {"politik", "technik", "reisen"}
VALID_STATUSES = {"seedling", "plant", "tree"}
VALID_VISIBILITIES = {"public", "group", "private"}
REQUIRED_FIELDS = {"title", "type", "segment", "status", "visibility", "date"}


def parse_frontmatter(path: Path) -> dict:
    """Minimal YAML frontmatter parser (mirrors filter_site.py logic)."""
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    if not text.startswith("---\n"):
        return {}

    m = re.match(r"^---\n(.*?)\n---\s*(?:\n|$)", text, re.DOTALL)
    if not m:
        return {}

    data: dict = {}
    current_list_key: str | None = None
    for raw in m.group(1).splitlines():
        line = raw.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue
        kv = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if kv:
            key, val = kv.group(1), kv.group(2).strip()
            current_list_key = None
            if val.startswith("[") and val.endswith("]"):
                inner = val[1:-1].strip()
                data[key] = [x.strip().strip("\"'") for x in inner.split(",") if x.strip()]
            elif val == "":
                data[key] = []
                current_list_key = key
            else:
                data[key] = val.strip("\"'")
            continue
        lm = re.match(r"^\s*-\s*(.+)$", line)
        if lm and current_list_key:
            data.setdefault(current_list_key, []).append(lm.group(1).strip().strip("\"'"))
    return data


def lint_file(path: Path, content_root: Path) -> list[str]:
    errors: list[str] = []
    rel = path.relative_to(content_root)
    fm = parse_frontmatter(path)

    if not fm:
        errors.append(f"{rel}: no valid frontmatter found")
        return errors

    # Required fields
    for field in REQUIRED_FIELDS:
        if field not in fm:
            errors.append(f"{rel}: missing required field '{field}'")

    # Allowed values
    if "type" in fm and fm["type"] not in VALID_TYPES:
        errors.append(f"{rel}: invalid type '{fm['type']}' (allowed: {VALID_TYPES})")

    if "segment" in fm and fm["segment"] not in VALID_SEGMENTS:
        errors.append(f"{rel}: invalid segment '{fm['segment']}' (allowed: {VALID_SEGMENTS})")

    if "status" in fm and fm["status"] not in VALID_STATUSES:
        errors.append(f"{rel}: invalid status '{fm['status']}' (allowed: {VALID_STATUSES})")

    if "visibility" in fm and fm["visibility"] not in VALID_VISIBILITIES:
        errors.append(f"{rel}: invalid visibility '{fm['visibility']}' (allowed: {VALID_VISIBILITIES})")

    # group visibility requires groups field
    if fm.get("visibility") == "group":
        groups = fm.get("groups")
        if not groups or (isinstance(groups, list) and len(groups) == 0):
            errors.append(f"{rel}: visibility is 'group' but no groups specified")

    return errors


def main() -> int:
    content_root = Path("site/content")
    if not content_root.is_dir():
        print(f"[FAIL] content root not found: {content_root}", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    checked = 0

    for md in sorted(content_root.rglob("*.md")):
        if md.name == "_index.md":
            continue
        checked += 1
        all_errors.extend(lint_file(md, content_root))

    if all_errors:
        for e in all_errors:
            print(f"[FAIL] {e}", file=sys.stderr)
        print(f"\n{len(all_errors)} error(s) in {checked} file(s)", file=sys.stderr)
        return 1

    print(f"[OK] {checked} content file(s) passed frontmatter lint")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
