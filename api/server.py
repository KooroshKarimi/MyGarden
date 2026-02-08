#!/usr/bin/env python3
"""Content API server for MyGarden admin editing."""
from __future__ import annotations

import json
import os
import re
import subprocess
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

CONTENT_ROOT = Path("/workspace/site/content")
BUILD_SCRIPT = "/workspace/scripts/build-all.sh"

VALID_TYPES = {"note", "trip", "timeline-entry", "dossier", "article"}
VALID_SEGMENTS = {"politik", "technik", "reisen"}
VALID_STATUSES = {"seedling", "plant", "tree"}
VALID_VISIBILITIES = {"public", "group", "private"}
REQUIRED_FIELDS = {"title", "type", "segment", "status", "visibility", "date"}

_rebuild_lock = threading.Lock()
_rebuilding = False


def _trigger_rebuild():
    """Run build-all.sh asynchronously."""
    global _rebuilding

    def _run():
        global _rebuilding
        try:
            result = subprocess.run(
                ["bash", BUILD_SCRIPT],
                cwd="/workspace",
                capture_output=True,
                text=True,
                timeout=600,
            )
            if result.returncode != 0:
                print(f"[content-api] rebuild FAILED (rc={result.returncode})")
                print(f"[content-api] stderr: {result.stderr[-500:]}")
            else:
                print("[content-api] rebuild OK")
        except Exception as e:
            print(f"[content-api] rebuild error: {e}")
        finally:
            with _rebuild_lock:
                _rebuilding = False

    with _rebuild_lock:
        if _rebuilding:
            return
        _rebuilding = True
    threading.Thread(target=_run, daemon=True).start()


def _validate_path(rel_path: str) -> Path | None:
    """Validate and resolve a content path. Returns None if invalid."""
    if not rel_path or ".." in rel_path:
        return None
    if not rel_path.endswith(".md"):
        return None
    # Only allow simple path characters
    if not re.match(r'^[a-zA-Z0-9/_-]+\.md$', rel_path):
        return None
    full = (CONTENT_ROOT / rel_path).resolve()
    if not str(full).startswith(str(CONTENT_ROOT.resolve())):
        return None
    return full


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse frontmatter and body from markdown text."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if not text.startswith("---\n"):
        return {}, text

    m = re.match(r"^---\n(.*?)\n---\s*(?:\n|$)", text, re.DOTALL)
    if not m:
        return {}, text

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
    body = text[m.end():]
    return data, body


def _serialize_frontmatter(fm: dict, body: str) -> str:
    """Serialize frontmatter dict + body back to markdown."""
    lines = ["---"]
    # Write fields in a stable order
    ordered_keys = ["title", "type", "segment", "status", "visibility", "groups",
                    "date", "event_date", "dossier", "dossier_key", "tags"]
    written = set()
    for key in ordered_keys:
        if key in fm:
            _write_fm_field(lines, key, fm[key])
            written.add(key)
    for key in sorted(fm.keys()):
        if key not in written:
            _write_fm_field(lines, key, fm[key])
    lines.append("---")
    return "\n".join(lines) + "\n" + body


def _write_fm_field(lines: list[str], key: str, val):
    if isinstance(val, list):
        if len(val) == 0:
            lines.append(f"{key}: []")
        else:
            lines.append(f"{key}:")
            for item in val:
                lines.append(f"  - {item}")
    else:
        # Quote title to be safe
        if key == "title":
            lines.append(f'{key}: "{val}"')
        else:
            lines.append(f"{key}: {val}")


def _validate_frontmatter(fm: dict) -> list[str]:
    """Validate frontmatter fields. Returns list of errors."""
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in fm:
            errors.append(f"missing required field '{field}'")
    if "type" in fm and fm["type"] not in VALID_TYPES:
        errors.append(f"invalid type '{fm['type']}'")
    if "segment" in fm and fm["segment"] not in VALID_SEGMENTS:
        errors.append(f"invalid segment '{fm['segment']}'")
    if "status" in fm and fm["status"] not in VALID_STATUSES:
        errors.append(f"invalid status '{fm['status']}'")
    if "visibility" in fm and fm["visibility"] not in VALID_VISIBILITIES:
        errors.append(f"invalid visibility '{fm['visibility']}'")
    if fm.get("visibility") == "group":
        groups = fm.get("groups")
        if not groups or (isinstance(groups, list) and len(groups) == 0):
            errors.append("visibility is 'group' but no groups specified")
    return errors


class ContentHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length)

    def _get_content_path(self) -> str | None:
        prefix = "/api/content/"
        if self.path.startswith(prefix):
            return self.path[len(prefix):]
        return None

    def do_GET(self):
        rel = self._get_content_path()
        if rel is None:
            self._send_json(404, {"error": "not found"})
            return

        # Status endpoint
        if rel == "_status":
            with _rebuild_lock:
                self._send_json(200, {"rebuilding": _rebuilding})
            return

        full = _validate_path(rel)
        if full is None:
            self._send_json(400, {"error": "invalid path"})
            return
        if not full.is_file():
            self._send_json(404, {"error": "file not found"})
            return

        text = full.read_text(encoding="utf-8")
        fm, body = _parse_frontmatter(text)
        self._send_json(200, {"path": rel, "frontmatter": fm, "body": body})

    def do_PUT(self):
        rel = self._get_content_path()
        if rel is None:
            self._send_json(404, {"error": "not found"})
            return

        full = _validate_path(rel)
        if full is None:
            self._send_json(400, {"error": "invalid path"})
            return
        if not full.is_file():
            self._send_json(404, {"error": "file not found"})
            return

        try:
            data = json.loads(self._read_body())
        except (json.JSONDecodeError, ValueError):
            self._send_json(400, {"error": "invalid JSON"})
            return

        fm = data.get("frontmatter")
        body = data.get("body", "")
        if not isinstance(fm, dict):
            self._send_json(400, {"error": "frontmatter must be an object"})
            return

        errors = _validate_frontmatter(fm)
        if errors:
            self._send_json(422, {"error": "validation failed", "details": errors})
            return

        content = _serialize_frontmatter(fm, body)
        full.write_text(content, encoding="utf-8")
        _trigger_rebuild()
        self._send_json(200, {"ok": True, "path": rel})

    def do_DELETE(self):
        rel = self._get_content_path()
        if rel is None:
            self._send_json(404, {"error": "not found"})
            return

        full = _validate_path(rel)
        if full is None:
            self._send_json(400, {"error": "invalid path"})
            return
        if not full.is_file():
            self._send_json(404, {"error": "file not found"})
            return

        full.unlink()
        _trigger_rebuild()
        self._send_json(200, {"ok": True, "deleted": rel})

    def log_message(self, format, *args):
        print(f"[content-api] {args[0]}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    server = HTTPServer(("0.0.0.0", port), ContentHandler)
    print(f"[content-api] listening on :{port}")
    server.serve_forever()
