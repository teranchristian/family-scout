#!/usr/bin/env python3
"""Read recommendation context without exposing prior history or cached places."""

import argparse
import json
import os
from pathlib import Path
import sys

import family_scout as scout
from location_sources import matching_location_sources


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", help="Family Scout private state directory")
    parser.add_argument("--at", help="Timezone-aware ISO instant; defaults to now")
    parser.add_argument("--location", choices=("auto", "home"), default="auto")
    parser.add_argument("--source-location", help="Explicit requested suburb for saved URL matching")
    return parser


def main():
    args = build_parser().parse_args()
    run_started_at = scout.iso_now()
    selected = args.data_dir or os.environ.get("FAMILY_SCOUT_DATA_DIR")
    data_dir = Path(selected).expanduser().resolve() if selected else (
        Path.home() / ".local" / "share" / "family-scout").resolve()
    try:
        at = scout.parse_at(args.at)
        with scout.state_lock(data_dir):
            profile = scout.load_document(data_dir / "profile.yaml", "profile")
            sources = scout.load_document(data_dir / "sources.yaml", "sources")
        resolved_location = scout.active_location(profile, at, args.location == "home")
        local_date = scout.age_reference_date(at, resolved_location)
        source_label = args.source_location or (resolved_location.get("location") or {}).get("label")
        location_sources = matching_location_sources(data_dir / "sources.yml", source_label)
        scout.emit({
            "ok": True,
            "scope": "discovery",
            "run_started_at": run_started_at,
            "at": at.isoformat(),
            "resolved_location": resolved_location,
            "age_as_of": local_date.isoformat(),
            "effective_member_ages": scout.member_ages_on(profile, local_date),
            "profile": profile,
            "enabled_sources": [item for item in sources["sources"] if item["enabled"]],
            "location_sources": location_sources,
        })
        return 0
    except (scout.ScoutError, OSError, UnicodeError, ValueError) as exc:
        print(
            json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())
