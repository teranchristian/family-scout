#!/usr/bin/env python3
"""Preflight, save and render one complete Family Scout recommendation payload.

Broad recommendation runs should call this once after research. The command
validates discovery/enrichment coverage, proves the shortlist and render payload
work together in a temporary copy of state, then performs the real save+render.
It never emits a partial/freehand briefing.
"""

import argparse
from datetime import date
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urlparse


JAPANESE_SCRIPT = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
DATED_FINDING_KINDS = {
    "scheduled_activity", "sub_facility", "venue_availability", "hours_exception"
}
DATED_FINDING_STATUSES = {"available", "unavailable"}


FINALIZE_TEMPLATE = {
    "discovery": {
        "fresh_discovery_completed": True,
        "candidates_considered": 4,
        "fresh_candidates_considered": 4,
        "cache_candidates_considered": 0,
        "activity_classes_searched": [
            "events", "play", "learning", "experiences"
        ],
        "exact_date_event_searched": True,
        "exact_date_event_source_urls": ["https://example.org/calendar"],
    },
    "shortlist": {
        "operation_id": "op-replace-me",
        "created_at": "2030-04-06T09:00:00Z",
        "conversation_ref": None,
        "effort_mode": "normal",
        "request": {
            "origin_ref": "explicit",
            "place_label": "Example City",
            "date_start": "2030-04-07",
            "date_end": "2030-04-07",
            "timezone": "Etc/UTC",
            "radius_km": 10,
            "attending_member_ids": [],
        },
        "weather": {"status": "unknown", "reason": "not available"},
        "options": [{
            "title": "Example Activity",
            "venue": "Example Venue",
            "discovery_origin": "fresh",
            "date_start": "2030-04-07T10:00:00+00:00",
            "date_end": "2030-04-07T11:00:00+00:00",
            "checked_at": "2030-04-06T09:00:00Z",
            "source_urls": ["https://example.org/venue"],
            "link_checks": [{
                "url": "https://example.org/venue",
                "purposes": ["facts"],
                "result": "content_verified",
                "checked_at": "2030-04-06T09:00:00Z",
            }],
            "distance_km": 1.2,
            "cost": {"status": "known", "amount": 0,
                     "currency": "XXX", "basis": "attending group"},
            "indoor_status": "indoor",
            "booking": {"required": False, "availability": "not_applicable"},
            "why": "Concise evidence-based reason.",
            "constraint_results": [{
                "requirement": "radius", "status": "confirmed_match",
                "reason": "inside inclusive boundary",
            }, {
                "requirement": "date", "status": "confirmed_match",
                "reason": "usable interval overlaps",
            }],
            "features": ["hands-on"],
            "place": {
                "name": "Example Venue",
                "area": "Example City",
                "categories": ["hands-on"],
                "official_url": "https://example.org/venue",
                "address": "1 Public Road, Example City",
                "latitude": 1.25,
                "longitude": 2.5,
            },
        }],
        "needs_checking": [],
        "consulted_sources": [{
            "url": "https://example.org/venue", "status": "read",
        }, {
            "url": "https://example.org/calendar", "status": "read",
        }],
        "tool_usage": {
            "search_queries": 2, "source_fetches": 3,
            "forecast_lookups": 0, "geocode_lookups": 1,
        },
    },
    "render": {"cards": [{
        "number": 1,
        "body": "Concise hours, cost, booking, address and ranking context.",
        "activities": [{
            "name": "Example activity",
            "kind": "everyday_facility",
            "availability": "available",
            "detail": "A concrete activity supported by the current source.",
            "source_url": "https://example.org/venue",
        }],
        "family_fit": [{
            "member_id": "member-example",
            "label": "Example child",
            "fit": "good",
            "activity_names": ["Example activity"],
            "limitations": [],
        }],
    }]},
}


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


def valid_url(value, label):
    require(isinstance(value, str) and value.strip(), f"{label} must be a URL")
    parsed = urlparse(value)
    require(parsed.scheme in ("http", "https") and bool(parsed.netloc),
            f"{label} must be an http(s) URL")
    return value


def non_empty_text(value, label):
    require(isinstance(value, str) and value.strip(), f"{label} must be non-empty text")
    return value.strip()


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
    """Keep local-language text in the saved option title only."""
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
                if key.endswith("_url") or key == "url":
                    continue
                walk(item, f"{path}.{key}")

    walk(render, "render")


def consulted_read_urls(shortlist):
    consulted = shortlist.get("consulted_sources")
    require(isinstance(consulted, list), "shortlist.consulted_sources must be a list")
    urls = set()
    for index, item in enumerate(consulted):
        require(isinstance(item, dict),
                f"shortlist.consulted_sources[{index}] must be an object")
        url = valid_url(item.get("url"), f"shortlist.consulted_sources[{index}].url")
        status = item.get("status")
        require(isinstance(status, str) and status,
                f"shortlist.consulted_sources[{index}].status must be non-empty")
        if status == "read":
            urls.add(url)
    return urls


def verified_fact_urls(option, option_number):
    source_urls = option.get("source_urls")
    checks = option.get("link_checks")
    require(isinstance(source_urls, list) and source_urls,
            f"option {option_number} must have source_urls")
    require(isinstance(checks, list) and checks,
            f"option {option_number} must have link_checks")

    verified = set()
    for index, check in enumerate(checks):
        require(isinstance(check, dict),
                f"option {option_number} link_checks[{index}] must be an object")
        url = valid_url(check.get("url"),
                        f"option {option_number} link_checks[{index}].url")
        purposes = check.get("purposes")
        if (check.get("result") == "content_verified"
                and isinstance(purposes, list) and "facts" in purposes):
            verified.add(url)

    for index, url in enumerate(source_urls):
        valid_url(url, f"option {option_number} source_urls[{index}]")
    return set(source_urls), verified


def render_activity_matches(render, option_number, name, source_url, availability,
                            required_kind=None):
    cards = render.get("cards") if isinstance(render, dict) else None
    if not isinstance(cards, list):
        return False
    for card in cards:
        if not isinstance(card, dict) or card.get("number") != option_number:
            continue
        activities = card.get("activities")
        if not isinstance(activities, list):
            return False
        for activity in activities:
            if not isinstance(activity, dict):
                continue
            if (activity.get("name") == name
                    and activity.get("source_url") == source_url
                    and activity.get("availability") == availability
                    and (required_kind is None or activity.get("kind") == required_kind)):
                return True
    return False


def validate_requested_date(value, request, label):
    non_empty_text(value, label)
    try:
        finding_date = date.fromisoformat(value)
        start = date.fromisoformat(request["date_start"])
        end = date.fromisoformat(request.get("date_end") or request["date_start"])
    except (KeyError, TypeError, ValueError) as exc:
        raise FinalizeError(f"{label} and request dates must be ISO dates") from exc
    require(start <= finding_date <= end,
            f"{label} must fall within the requested date range")


def validate_exact_date_event_findings(discovery, read_urls, event_urls, options,
                                       render, request, dated_request):
    findings = discovery.get("exact_date_event_findings", [])
    require(isinstance(findings, list),
            "discovery.exact_date_event_findings must be a list")
    for index, finding in enumerate(findings):
        require(isinstance(finding, dict),
                f"discovery.exact_date_event_findings[{index}] must be an object")
        name = non_empty_text(finding.get("name"),
                              f"exact_date_event_findings[{index}].name")
        source_url = valid_url(finding.get("source_url"),
                               f"exact_date_event_findings[{index}].source_url")
        require(source_url in event_urls,
                "each exact-date event finding must cite an exact-date event source")
        require(source_url in read_urls,
                "each exact-date event finding source must be consulted with status read")
        if dated_request:
            validate_requested_date(finding.get("date"), request,
                                    f"exact_date_event_findings[{index}].date")
        if finding.get("time") is not None:
            non_empty_text(finding["time"], f"exact_date_event_findings[{index}].time")
        if finding.get("detail") is not None:
            non_empty_text(finding["detail"], f"exact_date_event_findings[{index}].detail")

        number = finding.get("option_number")
        if number is not None:
            require(isinstance(number, int) and not isinstance(number, bool)
                    and 1 <= number <= len(options),
                    f"exact_date_event_findings[{index}].option_number is invalid")
            require(render_activity_matches(render, number, name, source_url,
                                            "available", "scheduled_activity"),
                    f"exact-date event '{name}' for option {number} must appear as an "
                    "available scheduled_activity in rendered activities")
    return len(findings)


def validate_dated_findings(item, number, evidence_urls, read_urls, render,
                            dated_request):
    findings = item.get("dated_findings", [])
    require(isinstance(findings, list),
            f"option {number} dated_findings must be a list")
    if dated_request:
        require(findings,
                f"option {number} date enrichment requires concrete dated_findings")

    for index, finding in enumerate(findings):
        require(isinstance(finding, dict),
                f"option {number} dated_findings[{index}] must be an object")
        kind = finding.get("kind")
        require(kind in DATED_FINDING_KINDS,
                f"option {number} dated_findings[{index}].kind is invalid")
        status = finding.get("status")
        require(status in DATED_FINDING_STATUSES,
                f"option {number} dated_findings[{index}].status is invalid")
        name = non_empty_text(finding.get("name"),
                              f"option {number} dated_findings[{index}].name")
        non_empty_text(finding.get("detail"),
                       f"option {number} dated_findings[{index}].detail")
        source_url = valid_url(finding.get("source_url"),
                               f"option {number} dated_findings[{index}].source_url")
        require(source_url in evidence_urls,
                f"option {number} dated finding must cite one of its date-enrichment sources")
        require(source_url in read_urls,
                f"option {number} dated finding source must be consulted with status read")
        if kind in ("scheduled_activity", "sub_facility"):
            require(render_activity_matches(render, number, name, source_url, status,
                                            kind),
                    f"option {number} dated {kind} '{name}' must appear in rendered activities")
    return len(findings)


def validate_date_evidence(discovery, shortlist, options, render, request, dated_request):
    read_urls = consulted_read_urls(shortlist)

    event_searched = discovery.get("exact_date_event_searched")
    require(isinstance(event_searched, bool),
            "discovery.exact_date_event_searched must be boolean")

    event_urls = discovery.get("exact_date_event_source_urls", [])
    require(isinstance(event_urls, list)
            and all(isinstance(item, str) and item.strip() for item in event_urls),
            "discovery.exact_date_event_source_urls must be a list of URLs")
    require(len(event_urls) == len(set(event_urls)),
            "discovery.exact_date_event_source_urls must be unique")
    for index, url in enumerate(event_urls):
        valid_url(url, f"discovery.exact_date_event_source_urls[{index}]")
        require(url in read_urls,
                "every exact-date event source must appear in consulted_sources with status read")

    if dated_request:
        require(event_searched,
                "dated recommendations require an exact-date event search")
        require(event_urls,
                "dated recommendations require at least one exact-date event/calendar source URL")

    event_findings = validate_exact_date_event_findings(
        discovery, read_urls, set(event_urls), options, render, request, dated_request
    )

    enrichment = discovery.get("finalist_date_enrichment")
    if enrichment is None:
        total_sources = 0
        total_findings = 0
        cards = render.get("cards") if isinstance(render, dict) else None
        require(isinstance(cards, list), "render.cards must be a list")
        cards_by_number = {
            card.get("number"): card for card in cards if isinstance(card, dict)
        }
        for number, option in enumerate(options, 1):
            option_urls, fact_urls = verified_fact_urls(option, number)
            current_urls = option_urls & fact_urls & read_urls
            require(current_urls,
                    f"option {number} needs a current read, content-verified factual source")
            card = cards_by_number.get(number)
            require(isinstance(card, dict), f"render card {number} is missing")
            activities = card.get("activities")
            require(isinstance(activities, list) and activities,
                    f"option {number} needs at least one evidenced activity")
            require(any(isinstance(item, dict)
                        and item.get("availability") == "available"
                        and item.get("source_url") in current_urls
                        for item in activities),
                    f"option {number} needs an available activity backed by current evidence")
            total_sources += len(current_urls)
            total_findings += len(activities)
        return {
            "exact_date_event_searched": event_searched,
            "exact_date_event_sources_checked": len(event_urls),
            "exact_date_event_findings_captured": event_findings,
            "finalist_date_evidence_sources": total_sources,
            "finalist_dated_findings": total_findings,
        }

    require(isinstance(enrichment, list),
            "discovery.finalist_date_enrichment must be a list")
    require(len(enrichment) == len(options),
            "every finalist must have one date-enrichment evidence record")

    expected_numbers = set(range(1, len(options) + 1))
    seen_numbers = set()
    total_sources = 0
    total_findings = 0

    for index, item in enumerate(enrichment):
        require(isinstance(item, dict),
                f"discovery.finalist_date_enrichment[{index}] must be an object")
        number = item.get("option_number")
        require(isinstance(number, int) and not isinstance(number, bool)
                and number in expected_numbers,
                f"discovery.finalist_date_enrichment[{index}].option_number is invalid")
        require(number not in seen_numbers,
                "discovery.finalist_date_enrichment repeats an option number")
        seen_numbers.add(number)

        evidence_urls = item.get("source_urls")
        require(isinstance(evidence_urls, list) and evidence_urls
                and all(isinstance(url, str) and url.strip() for url in evidence_urls),
                f"option {number} date enrichment requires at least one source URL")
        require(len(evidence_urls) == len(set(evidence_urls)),
                f"option {number} date-enrichment source URLs must be unique")

        option_source_urls, fact_urls = verified_fact_urls(options[number - 1], number)
        for source_index, url in enumerate(evidence_urls):
            valid_url(url, f"option {number} date enrichment source_urls[{source_index}]")
            require(url in option_source_urls,
                    f"option {number} date-enrichment URL must be saved in that option's source_urls")
            require(url in fact_urls,
                    f"option {number} date-enrichment URL must have a content-verified facts link check")
            require(url in read_urls,
                    f"option {number} date-enrichment URL must appear in consulted_sources with status read")
        total_sources += len(evidence_urls)
        total_findings += validate_dated_findings(
            item, number, set(evidence_urls), read_urls, render, dated_request
        )

    require(seen_numbers == expected_numbers,
            "every finalist must receive evidence-backed exact-date enrichment")

    return {
        "exact_date_event_searched": event_searched,
        "exact_date_event_sources_checked": len(event_urls),
        "exact_date_event_findings_captured": event_findings,
        "finalist_date_evidence_sources": total_sources,
        "finalist_dated_findings": total_findings,
    }


def validate_discovery(payload, shortlist, render):
    discovery = payload.get("discovery")
    require(isinstance(discovery, dict),
            "broad recommendation requires discovery coverage")
    require(discovery.get("fresh_discovery_completed") is True,
            "fresh discovery must complete before finalization")

    candidates = discovery.get("candidates_considered")
    require(isinstance(candidates, int) and not isinstance(candidates, bool)
            and candidates >= 0,
            "discovery.candidates_considered must be a non-negative integer")
    fresh_candidates = discovery.get("fresh_candidates_considered", candidates)
    cache_candidates = discovery.get("cache_candidates_considered", 0)
    for value, label in (
        (fresh_candidates, "fresh_candidates_considered"),
        (cache_candidates, "cache_candidates_considered"),
    ):
        require(isinstance(value, int) and not isinstance(value, bool) and value >= 0,
                f"discovery.{label} must be a non-negative integer")
    if ("fresh_candidates_considered" in discovery
            or "cache_candidates_considered" in discovery):
        require(candidates == fresh_candidates + cache_candidates,
                "candidates_considered must equal fresh plus cache candidates")

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
    cache_finalists = sum(
        1 for option in options
        if isinstance(option, dict) and option.get("discovery_origin", "fresh") == "cache"
    )
    fresh_finalists = len(options) - cache_finalists
    effort_mode = shortlist.get("effort_mode", "normal")
    if effort_mode == "normal":
        require(len(options) <= 3,
                "normal effort allows at most three confirmed recommendations")
        require(cache_finalists <= 1,
                "normal effort allows at most one cache-seeded finalist")
        require(fresh_finalists >= min(2, len(options)),
                "normal effort requires fresh discovery for at least two finalists")

    needs_checking = shortlist.get("needs_checking", [])
    require(isinstance(needs_checking, list),
            "shortlist.needs_checking must be a list")
    require(candidates >= len(options) + len(needs_checking),
            "fresh candidate count cannot be smaller than confirmed plus needs-checking results")

    request = shortlist.get("request")
    require(isinstance(request, dict), "shortlist.request must be an object")
    dated_request = bool(request.get("date_start"))
    date_evidence = validate_date_evidence(
        discovery, shortlist, options, render, request, dated_request
    )

    not_shortlisted = candidates - len(options) - len(needs_checking)
    return {
        "candidates_considered": candidates,
        "fresh_candidates": fresh_candidates,
        "cache_candidates": cache_candidates,
        "fresh_finalists": fresh_finalists,
        "cache_finalists": cache_finalists,
        "activity_classes_checked": len(normalized_classes),
        "finalists_deeply_verified": len(options),
        "confirmed_recommendations": len(options),
        "needs_checking": len(needs_checking),
        "not_shortlisted": not_shortlisted,
        **date_evidence,
    }


def research_summary(coverage):
    return (
        "Research: "
        f"{coverage['fresh_candidates']} fresh + "
        f"{coverage['cache_candidates']} cached lead(s) across "
        f"{coverage['activity_classes_checked']} categories · "
        f"{coverage['finalists_deeply_verified']} finalists deeply verified · "
        f"{coverage['confirmed_recommendations']} confirmed · "
        f"{coverage['needs_checking']} needs checking · "
        f"{coverage['not_shortlisted']} not shortlisted · "
        f"{coverage['exact_date_event_sources_checked']} exact-date event/calendar source(s) checked · "
        f"{coverage['exact_date_event_findings_captured']} exact-date event finding(s) captured"
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
    coverage = validate_discovery(payload, shortlist, render)

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
        "place_cache": saved.get("place_cache", {}),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir")
    parser.add_argument("--data-dir")
    parser.add_argument("--input", default="-", help="Complete JSON payload or - for stdin")
    parser.add_argument("--print-template", action="store_true",
                        help="Print the compact normal-effort payload template")
    args = parser.parse_args()
    try:
        if args.print_template:
            print(json.dumps(FINALIZE_TEMPLATE, ensure_ascii=False, indent=2))
            return 0
        require(args.source_dir, "--source-dir is required")
        require(args.data_dir, "--data-dir is required")
        finalize(args)
        return 0
    except (FinalizeError, OSError, UnicodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False),
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
