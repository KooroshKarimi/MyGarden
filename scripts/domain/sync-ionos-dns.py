#!/usr/bin/env python3
"""Synchronize karimi.me apex A/AAAA records in IONOS DNS via API.

Usage:
  ./scripts/domain/sync-ionos-dns.py
  DOMAIN=karimi.me TARGET_HOSTNAME=koorosh.synology.me ./scripts/domain/sync-ionos-dns.py
"""

from __future__ import annotations

import json
import os
import socket
import sys
import urllib.error
import urllib.request
from pathlib import Path


def load_dotenv(path: str = ".env") -> None:
    p = Path(path)
    if not p.exists():
        return
    for raw in p.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        print(f"ERROR: {name} is required (set in .env).", file=sys.stderr)
        sys.exit(1)
    return value


def api_request(method: str, path: str, api_key: str, payload: dict | list | None = None) -> tuple[int, object]:
    base = os.getenv("IONOS_DNS_API_BASE", "https://api.hosting.ionos.com/dns/v1").rstrip("/")
    url = f"{base}{path}"
    body = None
    headers = {
        "X-API-KEY": api_key,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url=url, method=method.upper(), data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="ignore")
        data = None
        try:
            data = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            data = {"raw": raw}
        return e.code, data




def is_record_not_found_error(data: object) -> bool:
    if isinstance(data, list):
        return any(isinstance(item, dict) and item.get("code") == "RECORD_NOT_FOUND" for item in data)
    if isinstance(data, dict):
        return data.get("code") == "RECORD_NOT_FOUND"
    return False

def resolve_records(target_hostname: str) -> tuple[list[str], list[str]]:
    infos = socket.getaddrinfo(target_hostname, None)
    a = sorted({item[4][0] for item in infos if item[0] == socket.AF_INET})
    aaaa = sorted({item[4][0] for item in infos if item[0] == socket.AF_INET6})
    return a, aaaa


def find_zone_id(zones: list[dict], domain: str) -> str:
    for zone in zones:
        if zone.get("name", "").rstrip(".") == domain.rstrip("."):
            return zone["id"]
    print(f"ERROR: zone for domain {domain} not found in IONOS DNS API.", file=sys.stderr)
    sys.exit(1)


def upsert_records(zone_id: str, existing_records: list[dict], record_type: str, desired_values: list[str], api_key: str, domain: str) -> None:
    matching = [
        r
        for r in existing_records
        if r.get("type") == record_type and r.get("name", "").rstrip(".") in {domain.rstrip("."), "@"}
    ]

    existing_by_value = {r.get("content"): r for r in matching}

    for value in desired_values:
        if value in existing_by_value:
            continue
        payload = {
            "name": domain,
            "type": record_type,
            "content": value,
            "ttl": 3600,
            "prio": 0,
            "disabled": False,
        }
        code, data = api_request("POST", f"/zones/{zone_id}/records", api_key, payload)
        if code >= 400:
            code, data = api_request("POST", f"/zones/{zone_id}/records", api_key, [payload])
        if code >= 400:
            print(f"ERROR: failed to create {record_type} record {value}: {data}", file=sys.stderr)
            sys.exit(1)
        print(f"Created {record_type} {domain} -> {value}")

    desired_set = set(desired_values)
    for record in matching:
        if record.get("content") in desired_set:
            continue
        record_id = record.get("id")
        if not record_id:
            continue
        code, data = api_request("DELETE", f"/zones/{zone_id}/records/{record_id}", api_key)
        if code >= 400:
            if is_record_not_found_error(data):
                print(
                    f"Skipping stale {record_type} {domain} -> {record.get('content')} (already removed).",
                    file=sys.stderr,
                )
                continue
            print(f"ERROR: failed to delete stale {record_type} record {record.get('content')}: {data}", file=sys.stderr)
            sys.exit(1)
        print(f"Deleted stale {record_type} {domain} -> {record.get('content')}")


def main() -> None:
    load_dotenv()

    domain = os.getenv("DOMAIN", "karimi.me").strip()
    target_hostname = os.getenv("TARGET_HOSTNAME", "koorosh.synology.me").strip()
    ionos_prefix = require_env("IONOS_PREFIX")
    ionos_secret = require_env("IONOS_SECRET")

    api_key = f"{ionos_prefix}.{ionos_secret}"

    a_records, aaaa_records = resolve_records(target_hostname)
    if not a_records and not aaaa_records:
        print(f"ERROR: could not resolve A/AAAA for {target_hostname}.", file=sys.stderr)
        sys.exit(1)

    print(f"Resolved {target_hostname} -> A={a_records} AAAA={aaaa_records}")

    status, zones_data = api_request("GET", "/zones", api_key)
    if status >= 400:
        print(f"ERROR: failed to list zones: {zones_data}", file=sys.stderr)
        sys.exit(1)

    zones = zones_data if isinstance(zones_data, list) else zones_data.get("zones", [])
    zone_id = find_zone_id(zones, domain)

    status, zone_data = api_request("GET", f"/zones/{zone_id}", api_key)
    if status >= 400:
        print(f"ERROR: failed to fetch zone {zone_id}: {zone_data}", file=sys.stderr)
        sys.exit(1)

    records = zone_data.get("records", []) if isinstance(zone_data, dict) else []

    upsert_records(zone_id, records, "A", a_records, api_key, domain)
    upsert_records(zone_id, records, "AAAA", aaaa_records, api_key, domain)

    print("IONOS DNS sync completed.")


if __name__ == "__main__":
    main()
