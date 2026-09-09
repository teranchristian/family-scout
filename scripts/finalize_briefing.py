#!/usr/bin/env python3
"""Preflight, save and render one complete Family Scout recommendation payload.

Broad recommendation runs should call this once after research. The command
validates discovery/enrichment coverage, proves the shortlist and render payload
work together in a temporary copy of state, then performs the real save+render.
It never emits a partial/freehand briefing.
"""

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


JAPANESE_SCRIPT = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


class FinalizeError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise FinalizeError(message)


def read_json(path):
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    try:
        value = json.loads(text)
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise FinalizeError("finalize payload is malformed JSON") from exc
    require(isinstance(value, dict), "finalize payload must be an object")
    return value


def run_json(command):
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    stream = completed.stdout if completed.returncode == 0 else completed.stderr
    try:
        payload = json.loads(stream)
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise FinalizeError("Family Scout helper returned malformed JSON") from exc
    if completed.returncode != 0:
        raise FinalizeError(payload.get("error") or "Family Scout helper failed")
    require(isinstance(payload, dict) and payload.get("ok") is True,
            "Family Scout helper did not report success")
    return payload


def validate_output_language(render):
    """Keep local-language text in the saved option title only.

    The deterministic renderer gets option titles from the saved shortlist, so
    every free-text string supplied through the render payload is user-facing
    descriptive content and must be English. This catches the Japanese-script
    leakage seen in live trials without rejecting a Japanese venue title.
    """
    require(isinstance(render, dict), "finalize payload needs render")

    def walk(value, path):
        if isinstance(value, str):
            require(JAPANESE_SCRIPT.search(value) is None,
                    f"render content must be English; only option titles may use "
                    f"local-language text ({path})")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, f"{path}[{index}]")
        elif isinstance(value, dict):
            for key, item in value.items():
                # URLs are evidence identifiers rather than prose and may be
                # percent-encoded or otherwise contain non-English path text.
                if key.endswith("_url") or key == "url":
                    continue
                walk(item, f"{path}.{key}")

    walk(render, "render")


def validate_discovery(payload, shortlist):
    discovery = payload.get("discovery")
    require(isinstance(discovery, dict),
            "broad recommendation requires discovery coverage")
    require(discovery.get("fresh_discovery_completed") is True,
            "fresh discovery must complete before finalization")

    candidates = discovery.get("candidates_considered")
    require(isinstance(candidates, int) and not isinstance(candidates, bool)
            and candidates >= 0,
            "discovery.candidates_considered must be a non-negative integer")

    classes = discovery.get("activity_classes_searched")
    require(isinstance(classes, list)
            and all(isinstance(item, str) and item.strip() for item in classes),
            "discovery.activity_classes_searched must contain non-empty names")
    normalized_classes = [item.strip() for item in classes]
    require(len(normalized_classes) == len(set(normalized_classes)),
            "discovery.activity_classes_searched must be unique")
    require(len(normalized_classes) >= 4,
            "broad recommendations must deliberately search at least four activity classes")

    options = shortlist.get("options")
    require(isinstance(options, list) and options,
            "shortlist.options must contain at least one finalist")
    require(candidates >= len(options),
            "candidates_considered cannot be smaller than the final shortlist")

    needs_checking = shortlist.get("needs_checking", [])
    require(isinstance(needs_checking, list),
            "shortlist.needs_checking must be a list")
    require(candidates >= len(options) + len(needs_checking),
            "fresh candidate count cannot be smaller than confirmed plus needs-checking results")

    request = shortlist.get("request")
    require(isinstance(request, dict), "shortlist.request must be an object")
    exact_date = discovery.get("exact_date_event_searched")
    require(isinstance(exact_date, bool),
            "discovery.exact_date_event_searched must be boolean")
    if request.get("date_start"):
        require(exact_date,
                "dated recommendations require an exact-date event search")

    enriched = discovery.get("finalist_numbers_date_enriched")
    require(isinstance(enriched, list)
            and all(isinstance(item, int) and not isinstance(item, bool) and item >= 1
                    for item in enriched),
            "discovery.finalist_numbers_date_enriched must contain option numbers")
    require(len(enriched) == len(set(enriched)),
            "finalist_numbers_date_enriched must be unique")
    expected = set(range(1, len(options) + 1))
    require(set(enriched) == expected,
            "every finalist must receive exact-date enrichment before finalization")

    not_shortlisted = candidates - len(options) - len(needs_checking)
    return {
        "fresh_candidates": candidates,
        "activity_classes_checked": len(normalized_classes),
        "finalists_deeply_verified": len(options),
        "confirmed_recommendations": len(options),
        "needs_checking": len(needs_checking),
        "not_shortlisted": not_shortlisted,
        "exact_date_event_searched": exact_date,
    }


def research_summary(coverage):
    return (
        "Research: "
        f"{coverage['fresh_candidates']} fresh candidates across "
        f"{coverage['activity_classes_checked']} categories · "
        f"{coverage['finalists_deeply_verified']} finalists deeply verified · "
        f"{coverage['confirmed_recommendations']} confirmed · "
        f"{coverage['needs_checking']} needs checking · "
        f"{coverage['not_shortlisted']} not shortlisted"
    )


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")


def execute(source_dir, data_dir, shortlist_path, render_path):
    helper = source_dir / "scripts" / "family_scout.py"
    renderer = source_dir / "scripts" / "render_briefing.py"
    saved = run_json([
        sys.executable, str(helper), "--data-dir", str(data_dir),
        "shortlist-save", "--input", str(shortlist_path),
    ])
    search_id = saved.get("search_id")
    require(isinstance(search_id, str) and search_id,
            "shortlist-save did not return a search_id")
    rendered = run_json([
        sys.executable, str(renderer), "--data-dir", str(data_dir),
        "--search-id", search_id, "--input", str(render_path),
    ])
    return saved, rendered


def finalize(args):
    payload = read_json(args.input)
    shortlist = payload.get("shortlist")
    render = payload.get("render")
    require(isinstance(shortlist, dict), "finalize payload needs shortlist")
    require(isinstance(render, dict), "finalize payload needs render")
    validate_output_language(render)
    coverage = validate_discovery(payload, shortlist)

    source_dir = Path(args.source_dir).expanduser().resolve()
    data_dir = Path(args.data_dir).expanduser().resolve()
    require((source_dir / "scripts" / "family_scout.py").is_file(),
            "source_dir does not contain Family Scout")
    require(data_dir.is_dir(), "data_dir does not exist")

    with tempfile.TemporaryDirectory(prefix="family-scout-finalize-") as temporary:
        root = Path(temporary)
        sandbox_data = root / "state"
        shutil.copytree(data_dir, sandbox_data)
        shortlist_path = root / "shortlist.json"
        render_path = root / "render.json"
        write_json(shortlist_path, shortlist)
        write_json(render_path, render)

        # Preflight both deterministic phases against disposable state. A bad
        # render therefore cannot leave a real shortlist behind.
        execute(source_dir, sandbox_data, shortlist_path, render_path)

        saved, rendered = execute(source_dir, data_dir, shortlist_path, render_path)

    output = {
        "ok": True,
        "search_id": saved["search_id"],
        "duplicate": bool(saved.get("duplicate", False)),
        "research_coverage": coverage,
        "research_summary_markdown": research_summary(coverage),
        "numbered_options_markdown": rendered["numbered_options_markdown"],
        "links_by_option": rendered.get("links_by_option", []),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--input", default="-", help="Complete JSON payload or - for stdin")
    args = parser.parse_args()
    try:
        finalize(args)
        return 0
    except (FinalizeError, OSError, UnicodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False),
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
