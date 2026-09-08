#!/usr/bin/env python3
"""Render Family Scout numbered option cards from a validated saved shortlist."""

import argparse
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse


ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{2,95}$")
URL_PATTERN = re.compile(r"https?://", re.IGNORECASE)
LINK_PURPOSES = {"facts", "booking", "map", "other"}
LINK_RESULTS = {"content_verified", "reachable"}


class RenderError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise RenderError(message)


def valid_id(value, label):
    require(isinstance(value, str) and ID_PATTERN.fullmatch(value),
            f"{label} must use 3-96 lowercase letters, digits, dots, dashes or underscores")
    return value


def valid_url(value, label):
    require(isinstance(value, str), f"{label} must be a string")
    parsed = urlparse(value)
    require(parsed.scheme in ("http", "https") and bool(parsed.netloc),
            f"{label} must be an http(s) URL")
    return value


def load_shortlist(path, search_id):
    require(path.is_file(), "shortlists.jsonl was not found")
    matches = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RenderError(f"shortlists.jsonl line {number} is malformed JSON") from exc
        require(isinstance(record, dict), f"shortlists.jsonl line {number} is not an object")
        if record.get("search_id") == search_id:
            matches.append(record)
    require(len(matches) == 1, "search_id must resolve to exactly one saved shortlist")
    return matches[0]


def verified_links(option):
    source_urls = option.get("source_urls")
    checks = option.get("link_checks")
    require(isinstance(source_urls, list) and source_urls,
            "saved option has no source_urls")
    require(isinstance(checks, list) and checks,
            "saved option has no link_checks")

    by_url = {}
    ordered = []
    for index, check in enumerate(checks):
        require(isinstance(check, dict), f"link_checks[{index}] must be an object")
        url = valid_url(check.get("url"), f"link_checks[{index}].url")
        require(url not in by_url, "saved option repeats a link_check URL")
        purposes = check.get("purposes")
        result = check.get("result")
        require(isinstance(purposes, list) and purposes
                and all(isinstance(value, str) and value in LINK_PURPOSES for value in purposes)
                and len(purposes) == len(set(purposes)),
                f"link_checks[{index}].purposes is invalid")
        require(result in LINK_RESULTS, f"link_checks[{index}].result is invalid")
        require(result == "content_verified" or set(purposes) <= {"map"},
                "reachable is allowed only for map links")
        by_url[url] = check
        ordered.append(check)

    for url in source_urls:
        valid_url(url, "source URL")
        check = by_url.get(url)
        require(check is not None and "facts" in check["purposes"]
                and check["result"] == "content_verified",
                "every saved source URL must have a content-verified facts link check")
    return ordered


def purpose_label(purposes):
    labels = []
    for purpose in purposes:
        labels.append({
            "facts": "Verified information",
            "booking": "Booking",
            "map": "Map",
            "other": "More information",
        }[purpose])
    return " / ".join(labels)


def render(shortlist, payload):
    options = shortlist.get("options")
    require(isinstance(options, list) and options, "saved shortlist has no options")
    saved = {}
    for option in options:
        require(isinstance(option, dict), "saved option must be an object")
        number = option.get("number")
        require(isinstance(number, int) and not isinstance(number, bool) and number >= 1,
                "saved option number is invalid")
        require(number not in saved, "saved shortlist repeats an option number")
        require(isinstance(option.get("title"), str) and option["title"].strip(),
                "saved option title is missing")
        saved[number] = option

    require(isinstance(payload, dict), "render payload must be an object")
    cards = payload.get("cards")
    require(isinstance(cards, list), "render payload cards must be a list")
    bodies = {}
    for card in cards:
        require(isinstance(card, dict), "each render card must be an object")
        number = card.get("number")
        body = card.get("body")
        require(isinstance(number, int) and not isinstance(number, bool) and number >= 1,
                "render card number is invalid")
        require(number not in bodies, "render payload repeats an option number")
        require(isinstance(body, str) and body.strip(), "render card body must be non-empty text")
        require(URL_PATTERN.search(body) is None,
                "render card body must not contain URLs; verified links are appended automatically")
        bodies[number] = body.strip()

    require(set(bodies) == set(saved),
            "render payload must contain exactly one card body for every saved option")

    blocks = []
    links_by_option = []
    for number in sorted(saved):
        option = saved[number]
        checks = verified_links(option)
        lines = [f"**{number}. {option['title'].strip()}**", bodies[number], "", "🔗 Verified links:"]
        rendered_links = []
        for check in checks:
            label = purpose_label(check["purposes"])
            url = check["url"]
            lines.append(f"- {label}: {url}")
            rendered_links.append({"url": url, "purposes": check["purposes"]})
        blocks.append("\n".join(lines))
        links_by_option.append({"number": number, "links": rendered_links})

    return {
        "ok": True,
        "search_id": shortlist["search_id"],
        "option_count": len(saved),
        "numbered_options_markdown": "\n\n".join(blocks),
        "links_by_option": links_by_option,
    }


def read_payload(path):
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise RenderError("render payload is malformed JSON") from exc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--search-id", required=True)
    parser.add_argument("--input", default="-", help="JSON file or - for stdin")
    args = parser.parse_args()
    try:
        search_id = valid_id(args.search_id, "search_id")
        data_dir = Path(args.data_dir).expanduser().resolve()
        shortlist = load_shortlist(data_dir / "shortlists.jsonl", search_id)
        output = render(shortlist, read_payload(args.input))
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0
    except (RenderError, OSError, UnicodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
