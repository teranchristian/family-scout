#!/usr/bin/env python3
"""Read Family Scout context for fresh discovery without loading history."""

import argparse
from pathlib import Path
import os
import sys

import family_scout as scout


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", help="Family Scout private state directory")
    parser.add_argument("--at", help="Timezone-aware ISO instant; defaults to now")
    parser.add_argument("--location", choices=("auto", "home"), default="auto")
    return parser


def main():
    args = build_parser().parse_args()
    selected = args.data_dir or os.environ.get("FAMILY_SCOUT_DATA_DIR")
    data_dir = Path(selected).expanduser().resolve() if selected else (
        Path.home() / ".local" / "share" / "family-scout").resolve()
    try:
        at = scout.parse_at(args.at)
        with scout.state_lock(data_dir):
            profile = scout.load_document(data_dir / "profile.yaml", "profile")
            sources = scout.load_document(data_dir / "sources.yaml", "sources")
        scout.emit({
            "ok": True,
            "scope": "discovery",
            "history_loaded": False,
            "at": at.isoformat(),
            "resolved_location": scout.active_location(
                profile, at, args.location == "home"
            ),
            "profile": profile,
            "enabled_sources": [
                item for item in sources["sources"] if item["enabled"]
            ],
        })
        return 0
    except (scout.ScoutError, OSError, UnicodeError) as exc:
        print(
            scout.json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())
