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
ACTIVITY_KINDS = {
    "everyday_facility", "scheduled_activity", "sub_facility", "interaction", "other"
}
ACTIVITY_AVAILABILITY = {"available", "unavailable", "unknown"}
FIT_LEVELS = {"strong", "good", "limited", "guardian"}


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


def non_empty_text(value, label):
    require(isinstance(value, str) and value.strip(), f"{label} must be non-empty text")
    return value.strip()


def text_list(value, label, allow_empty=True):
    require(isinstance(value, list), f"{label} must be a list")
    require(allow_empty or value, f"{label} must not be empty")
    require(all(isinstance(item, str) and item.strip() for item in value),
            f"{label} must contain non-empty text")
    return [item.strip() for item in value]


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


def normalize_activities(card, facts_urls):
    raw = card.get("activities")
    require(isinstance(raw, list) and raw,
            "each render card must include at least one evidenced activity")
    seen = set()
    activities = []
    for index, item in enumerate(raw):
        require(isinstance(item, dict), f"activities[{index}] must be an object")
        name = non_empty_text(item.get("name"), f"activities[{index}].name")
        require(name not in seen, "activities must use unique names within a card")
        seen.add(name)
        kind = item.get("kind")
        availability = item.get("availability")
        require(kind in ACTIVITY_KINDS, f"activities[{index}].kind is invalid")
        require(availability in ACTIVITY_AVAILABILITY,
                f"activities[{index}].availability is invalid")
        detail = non_empty_text(item.get("detail"), f"activities[{index}].detail")
        source_url = valid_url(item.get("source_url"), f"activities[{index}].source_url")
        require(source_url in facts_urls,
                "every activity must cite a content-verified factual link saved for that option")
        activities.append({
            "name": name,
            "kind": kind,
            "availability": availability,
            "detail": detail,
            "source_url": source_url,
        })
    require(any(item["availability"] == "available" for item in activities),
            "a confirmed option must contain at least one activity available on the requested date")
    return activities


def normalize_family_fit(card, expected_member_ids, activities):
    raw = card.get("family_fit")
    require(isinstance(raw, list) and raw,
            "each render card must include family_fit")
    available_names = {
        item["name"] for item in activities if item["availability"] == "available"
    }
    fits = []
    seen = set()
    for index, item in enumerate(raw):
        require(isinstance(item, dict), f"family_fit[{index}] must be an object")
        member_id = valid_id(item.get("member_id"), f"family_fit[{index}].member_id")
        require(member_id not in seen, "family_fit repeats a member_id")
        seen.add(member_id)
        label = non_empty_text(item.get("label"), f"family_fit[{index}].label")
        fit = item.get("fit")
        require(fit in FIT_LEVELS, f"family_fit[{index}].fit is invalid")
        activity_names = text_list(
            item.get("activity_names"), f"family_fit[{index}].activity_names",
            allow_empty=(fit == "guardian")
        )
        require(all(name in available_names for name in activity_names),
                "family_fit may reference only activities available on the requested date")
        require(fit == "guardian" or activity_names,
                "a participating family member must have at least one available activity")
        limitations = text_list(
            item.get("limitations", []), f"family_fit[{index}].limitations"
        )
        fits.append({
            "member_id": member_id,
            "label": label,
            "fit": fit,
            "activity_names": activity_names,
            "limitations": limitations,
        })

    if expected_member_ids:
        require(seen == expected_member_ids,
                "family_fit must contain exactly one entry for every attending member")
    require(any(item["fit"] != "guardian" for item in fits),
            "family_fit must include at least one participating family member")
    return fits


def activity_status_label(value):
    return {
        "available": "Available on the requested date",
        "unavailable": "Unavailable on the requested date",
        "unknown": "Availability not established",
    }[value]


def fit_label(value):
    return {
        "strong": "strong fit",
        "good": "good fit",
        "limited": "limited fit",
        "guardian": "guardian/accompanying role",
    }[value]


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

    request = shortlist.get("request", {})
    raw_member_ids = request.get("attending_member_ids", []) if isinstance(request, dict) else []
    require(isinstance(raw_member_ids, list)
            and all(isinstance(value, str) and ID_PATTERN.fullmatch(value)
                    for value in raw_member_ids),
            "saved attending_member_ids are invalid")
    expected_member_ids = set(raw_member_ids)

    require(isinstance(payload, dict), "render payload must be an object")
    cards = payload.get("cards")
    require(isinstance(cards, list), "render payload cards must be a list")
    normalized_cards = {}
    for card in cards:
        require(isinstance(card, dict), "each render card must be an object")
        number = card.get("number")
        body = card.get("body")
        require(isinstance(number, int) and not isinstance(number, bool) and number >= 1,
                "render card number is invalid")
        require(number not in normalized_cards, "render payload repeats an option number")
        require(number in saved, "render payload contains an option that was not saved")
        require(isinstance(body, str) and body.strip(), "render card body must be non-empty text")
        require(URL_PATTERN.search(body) is None,
                "render card body must not contain URLs; verified links are appended automatically")

        checks = verified_links(saved[number])
        facts_urls = {
            check["url"] for check in checks
            if "facts" in check["purposes"] and check["result"] == "content_verified"
        }
        activities = normalize_activities(card, facts_urls)
        family_fit = normalize_family_fit(card, expected_member_ids, activities)
        normalized_cards[number] = {
            "body": body.strip(),
            "activities": activities,
            "family_fit": family_fit,
            "checks": checks,
        }

    require(set(normalized_cards) == set(saved),
            "render payload must contain exactly one card for every saved option")

    blocks = []
    links_by_option = []
    for number in sorted(saved):
        option = saved[number]
        card = normalized_cards[number]
        lines = [f"**{number}. {option['title'].strip()}**", card["body"], "",
                 "**What you can actually do**"]
        for activity in card["activities"]:
            lines.append(
                f"- **{activity['name']}** — {activity_status_label(activity['availability'])}. "
                f"{activity['detail']}"
            )

        lines.extend(["", "**Fit for each attending family member**"])
        for fit in card["family_fit"]:
            if fit["fit"] == "guardian":
                continue
            activities_text = ", ".join(fit["activity_names"])
            limitation_text = (
                " Limitations: " + "; ".join(fit["limitations"]) + "."
                if fit["limitations"] else ""
            )
            lines.append(
                f"- **{fit['label']}** — {fit_label(fit['fit'])}; "
                f"can do: {activities_text}.{limitation_text}"
            )

        lines.extend(["", "🔗 Verified links:"])
        rendered_links = []
        for check in card["checks"]:
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
