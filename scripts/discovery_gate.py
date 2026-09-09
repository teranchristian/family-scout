#!/usr/bin/env python3
"""Discovery-phase context and shortlist coverage gates for Family Scout.

This helper keeps fresh discovery isolated from prior shortlist history, then
validates that a broad recommendation recorded enough evidence to show discovery
and exact-date enrichment actually happened before the normal shortlist helper
persists the result.
"""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys


REQUIRED_TELEMETRY = {
    "candidates_considered": int,
    "candidates_new": int,
    "candidates_from_history": int,
    "activity_classes_searched": list,
    "exact_date_event_searched": bool,
    "finalists_date_enriched": bool,
}


class GateError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise GateError(message)


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as exc:
        raise GateError(f"cannot read valid JSON from {path}") from exc


def run_helper(source_dir, data_dir, *args):
    command = [sys.executable, str(Path(source_dir) / "scripts" / "family_scout.py"),
               "--data-dir", str(data_dir), *args]
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise GateError(completed.stderr.strip() or "family_scout.py failed")
    try:
        return json.loads(completed.stdout)
    except ValueError as exc:
        raise GateError("family_scout.py returned malformed JSON") from exc


def discovery_context(args):
    full = run_helper(args.source_dir, args.data_dir, "context", "--at", args.at,
                      "--history-limit", "1")
    # Fresh discovery intentionally cannot see prior shortlist candidates or
    # effective feedback. Explicit profile preferences remain available because
    # they define the family/request context, not candidate history.
    result = {
        "ok": True,
        "scope": "discovery",
        "at": full["at"],
        "resolved_location": full["resolved_location"],
        "profile": full["profile"],
        "enabled_sources": full["enabled_sources"],
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


def validate_telemetry(payload):
    telemetry = payload.get("discovery_telemetry")
    require(isinstance(telemetry, dict),
            "broad recommendation requires discovery_telemetry")
    for key, expected_type in REQUIRED_TELEMETRY.items():
        value = telemetry.get(key)
        require(isinstance(value, expected_type) and not
                (expected_type is int and isinstance(value, bool)),
                f"discovery_telemetry.{key} has the wrong type")
    for key in ("candidates_considered", "candidates_new", "candidates_from_history"):
        require(telemetry[key] >= 0, f"discovery_telemetry.{key} must be non-negative")
    classes = telemetry["activity_classes_searched"]
    require(classes and all(isinstance(item, str) and item.strip() for item in classes),
            "activity_classes_searched must contain non-empty names")
    require(len(set(classes)) == len(classes), "activity_classes_searched must be unique")
    require(telemetry["candidates_new"] + telemetry["candidates_from_history"]
            <= telemetry["candidates_considered"],
            "candidate telemetry is internally inconsistent")
    require(telemetry["finalists_date_enriched"],
            "finalists must receive exact-date enrichment before saving")
    request = payload.get("request", {})
    dated = bool(request.get("date_start"))
    if dated:
        require(telemetry["exact_date_event_searched"],
                "dated broad recommendations require exact-date event discovery")
    # Broad searches should prove meaningful category coverage. This gate does
    # not require that new candidates were found.
    require(len(classes) >= 5,
            "broad recommendation must deliberately search at least five activity classes")
    require(telemetry["candidates_considered"] >= len(payload.get("options", [])),
            "candidates_considered cannot be smaller than the final shortlist")
    return telemetry


def save(args):
    payload = read_json(args.input)
    validate_telemetry(payload)
    # family_scout.py deliberately remains backward compatible; this gate owns
    # the new broad-recommendation contract and passes only the supported fields
    # to the existing persistence helper.
    forwarded = dict(payload)
    telemetry = forwarded.pop("discovery_telemetry")
    tmp = Path(args.input).with_suffix(Path(args.input).suffix + ".forward.json")
    try:
        tmp.write_text(json.dumps(forwarded, ensure_ascii=False), encoding="utf-8")
        result = run_helper(args.source_dir, args.data_dir, "shortlist-save", "--input", str(tmp))
    finally:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass
    result["discovery_telemetry"] = telemetry
    print(json.dumps(result, indent=2, ensure_ascii=False))


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--data-dir", required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    context = commands.add_parser("context")
    context.add_argument("--at", default=datetime.now(timezone.utc).replace(microsecond=0).isoformat())
    save_parser = commands.add_parser("shortlist-save")
    save_parser.add_argument("--input", required=True)
    return parser


def main():
    args = build_parser().parse_args()
    try:
        if args.command == "context":
            discovery_context(args)
        else:
            save(args)
        return 0
    except GateError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
