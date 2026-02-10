#!/usr/bin/env python3
"""Content API server for MyGarden admin editing (Flask version)."""
from __future__ import annotations

import json
import os
import re
import subprocess
import threading
from pathlib import Path

from flask import Flask, request, jsonify, send_file, render_template

app = Flask(__name__)

CONTENT_ROOT = Path("/workspace/site/content")
BUILD_SCRIPT = "/workspace/scripts/build-all.sh"
AVATAR_DIR = Path("/workspace/infra/avatars")
AVATAR_MAX_SIZE = 1 * 1024 * 1024  # 1 MB

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


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/content/_status", methods=["GET"])
def get_status():
    with _rebuild_lock:
        return jsonify({"rebuilding": _rebuilding})


@app.route("/api/content/_avatar", methods=["PUT"])
def upload_avatar():
    if request.content_type not in ("image/jpeg", "image/png"):
        return jsonify({"error": "only image/jpeg or image/png allowed"}), 400
    
    data = request.get_data()
    if not data or len(data) > AVATAR_MAX_SIZE:
        return jsonify({"error": "body required, max 1 MB"}), 400

    AVATAR_DIR.mkdir(parents=True, exist_ok=True)
    AVATAR_DIR.joinpath("admin.jpg").write_bytes(data)
    return jsonify({"ok": True})


@app.route("/api/content/<path:filepath>", methods=["GET"])
def get_content(filepath):
    full = _validate_path(filepath)
    if full is None:
        return jsonify({"error": "invalid path"}), 400
    if not full.is_file():
        return jsonify({"error": "file not found"}), 404

    text = full.read_text(encoding="utf-8")
    fm, body = _parse_frontmatter(text)
    return jsonify({"path": filepath, "frontmatter": fm, "body": body})


@app.route("/api/content/<path:filepath>", methods=["PUT"])
def update_content(filepath):
    full = _validate_path(filepath)
    if full is None:
        return jsonify({"error": "invalid path"}), 400
    if not full.is_file():
        return jsonify({"error": "file not found"}), 404

    try:
        data = request.get_json()
    except Exception:
        return jsonify({"error": "invalid JSON"}), 400

    if not data:
        return jsonify({"error": "invalid JSON"}), 400

    fm = data.get("frontmatter")
    body = data.get("body", "")
    if not isinstance(fm, dict):
        return jsonify({"error": "frontmatter must be an object"}), 400

    errors = _validate_frontmatter(fm)
    if errors:
        return jsonify({"error": "validation failed", "details": errors}), 422

    content = _serialize_frontmatter(fm, body)
    full.write_text(content, encoding="utf-8")
    _trigger_rebuild()
    return jsonify({"ok": True, "path": filepath})


@app.route("/api/content/<path:filepath>", methods=["DELETE"])
def delete_content(filepath):
    full = _validate_path(filepath)
    if full is None:
        return jsonify({"error": "invalid path"}), 400
    if not full.is_file():
        return jsonify({"error": "file not found"}), 404

    full.unlink()
    _trigger_rebuild()
    return jsonify({"ok": True, "deleted": filepath})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    print(f"[content-api] listening on :{port}")
    app.run(host="0.0.0.0", port=port)
