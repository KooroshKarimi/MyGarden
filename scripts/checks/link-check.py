#!/usr/bin/env python3
"""Check for broken internal links in the public HTML output."""
from __future__ import annotations

import re
import sys
from pathlib import Path

HREF_RE = re.compile(r'href="(/[^"]*)"')


def main() -> int:
    out_dir = Path("out/public")
    if not out_dir.is_dir():
        print(f"[FAIL] output directory not found: {out_dir}", file=sys.stderr)
        return 1

    html_files = sorted(out_dir.rglob("*.html"))
    if not html_files:
        print(f"[FAIL] no HTML files found in {out_dir}", file=sys.stderr)
        return 1

    broken: list[str] = []
    checked = 0

    for html_path in html_files:
        text = html_path.read_text(encoding="utf-8", errors="replace")
        rel_source = html_path.relative_to(out_dir)

        for match in HREF_RE.finditer(text):
            href = match.group(1)
            checked += 1

            # Strip fragment
            href_clean = href.split("#")[0]
            if not href_clean or href_clean == "/":
                continue

            # Resolve to filesystem path
            target = out_dir / href_clean.lstrip("/")

            if target.is_file():
                continue
            if target.is_dir() and (target / "index.html").is_file():
                continue
            # Try with trailing slash removed
            if href_clean.endswith("/"):
                stripped = out_dir / href_clean.rstrip("/").lstrip("/")
                if stripped.is_file():
                    continue
                if stripped.is_dir() and (stripped / "index.html").is_file():
                    continue

            broken.append(f"{rel_source}: broken link {href}")

    if broken:
        for b in broken:
            print(f"[FAIL] {b}", file=sys.stderr)
        print(f"\n{len(broken)} broken link(s) in {len(html_files)} file(s)", file=sys.stderr)
        return 1

    print(f"[OK] {checked} internal link(s) checked in {len(html_files)} file(s), no broken links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
