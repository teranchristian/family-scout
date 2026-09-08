#!/usr/bin/env python3
"""Deterministic state and constraint helpers for the Family Scout skill."""

import argparse
from contextlib import contextmanager
from copy import deepcopy
from datetime import date, datetime, time, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
from urllib.parse import urlparse
import uuid
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


SCHEMA_VERSION = 1
ID_NAMESPACE = uuid.UUID("c9f11925-ceb0-4b59-bdf8-0af87fe2f98b")
LEGACY_BLANK_HASHES = {
    "profile.yaml": "6e7fa4deeda376c5e2d76d1dc9262dcab93bf27b660bfb10dcac8a3c579a8244",
    "sources.yaml": "c2ddac927b4058d5eee47e5c94bd2ce671676ed4146bf1caf08ba410f7e8a218",
}
DEFAULT_PROFILE = {
    "schema_version": 1,
    "home": {"label": None, "latitude": None, "longitude": None, "timezone": None},
    "default_radius_km": 15,
    "group_members": [],
    "preferences": [],
    "constraints": [],
    "provenance": [],
    "travel": None,
}
DEFAULT_SOURCES = {"schema_version": 1, "sources": []}
STATE_FILES = ("profile.yaml", "sources.yaml", "shortlists.jsonl", "feedback.jsonl")
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{2,95}$")
FEEDBACK_STATES = {
    "liked", "disliked", "saved", "interested", "visited", "bored",
    "too_crowded", "too_expensive", "too_much_walking", "note", "retracted",
}


class ScoutError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise ScoutError(message)


def parse_json(text, label):
    def reject_duplicate(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"{label} contains duplicate key {key!r}")
            result[key] = value
        return result

    try:
        return json.loads(text, object_pairs_hook=reject_duplicate,
                          parse_constant=lambda value: (_ for _ in ()).throw(
                              ScoutError(f"{label} contains invalid number {value}")))
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ScoutError(f"{label} is malformed JSON; existing data was preserved") from exc


def emit(value):
    print(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False))


def now_utc():
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso_now():
    return now_utc().isoformat().replace("+00:00", "Z")


def valid_id(value, label="id"):
    require(isinstance(value, str) and ID_PATTERN.fullmatch(value),
            f"{label} must use 3-96 lowercase letters, digits, dots, dashes or underscores")
    return value


def stable_id(prefix, value):
    return f"{prefix}-{uuid.uuid5(ID_NAMESPACE, prefix + '|' + value).hex[:20]}"


def valid_url(value, label="URL"):
    require(isinstance(value, str), f"{label} must be a string")
    parsed = urlparse(value)
    require(parsed.scheme in ("http", "https") and bool(parsed.netloc),
            f"{label} must be an http(s) URL")
    return value


def valid_number(value, label, minimum=None, maximum=None):
    require(isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value), f"{label} must be a finite number")
    if minimum is not None:
        require(value >= minimum, f"{label} must be at least {minimum}")
    if maximum is not None:
        require(value <= maximum, f"{label} must be at most {maximum}")
    return float(value)


def valid_timestamp(value, label, allow_date=False):
    require(isinstance(value, str) and value, f"{label} must be an ISO date/time")
    try:
        if allow_date and len(value) == 10:
            date.fromisoformat(value)
            return value
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ScoutError(f"{label} must be an ISO date/time") from exc
    require(parsed.tzinfo is not None, f"{label} must include a timezone offset")
    return value


def valid_location(value, label, require_expiry=False):
    require(isinstance(value, dict), f"{label} must be an object")
    for key in ("label", "timezone"):
        require(value.get(key) is None
                or (isinstance(value.get(key), str) and bool(value[key].strip())),
                f"{label}.{key} must be text or null")
    latitude = value.get("latitude")
    longitude = value.get("longitude")
    require((latitude is None) == (longitude is None),
            f"{label} latitude and longitude must both be set or both be null")
    if latitude is not None:
        valid_number(latitude, f"{label}.latitude", -90, 90)
        valid_number(longitude, f"{label}.longitude", -180, 180)
    if value.get("timezone"):
        try:
            ZoneInfo(value["timezone"])
        except ZoneInfoNotFoundError as exc:
            raise ScoutError(f"{label}.timezone is not a known IANA timezone") from exc
    if require_expiry:
        valid_timestamp(value.get("expires_at"), f"{label}.expires_at")
        require(value.get("label") is not None or latitude is not None,
                f"{label} must include a label or coordinates")


def validate_profile(profile):
    require(isinstance(profile, dict), "profile.yaml must contain an object")
    require(profile.get("schema_version") == SCHEMA_VERSION,
            "profile.yaml has an unsupported schema_version")
    valid_location(profile.get("home"), "home")
    valid_number(profile.get("default_radius_km"), "default_radius_km", 0.01)
    members = profile.get("group_members")
    require(isinstance(members, list), "group_members must be a list")
    member_ids = set()
    for index, member in enumerate(members):
        require(isinstance(member, dict), f"group_members[{index}] must be an object")
        member_id = valid_id(member.get("id"), f"group_members[{index}].id")
        require(member_id not in member_ids, f"duplicate group member id: {member_id}")
        member_ids.add(member_id)
        if "age" in member and member["age"] is not None:
            valid_number(member["age"], f"group_members[{index}].age", 0, 130)
        if "age_band" in member and member["age_band"] is not None:
            require(isinstance(member["age_band"], str) and member["age_band"].strip(),
                    f"group_members[{index}].age_band must be non-empty text")
    for key in ("preferences", "constraints", "provenance"):
        require(isinstance(profile.get(key), list), f"{key} must be a list")
    if profile.get("travel") is not None:
        valid_location(profile["travel"], "travel", require_expiry=True)
    return profile


def validate_sources(document):
    require(isinstance(document, dict), "sources.yaml must contain an object")
    require(document.get("schema_version") == SCHEMA_VERSION,
            "sources.yaml has an unsupported schema_version")
    sources = document.get("sources")
    require(isinstance(sources, list), "sources must be a list")
    seen_ids, seen_urls = set(), set()
    for index, source in enumerate(sources):
        require(isinstance(source, dict), f"sources[{index}] must be an object")
        source_id = valid_id(source.get("id"), f"sources[{index}].id")
        url = valid_url(source.get("url"), f"sources[{index}].url")
        require(source_id not in seen_ids, f"duplicate source id: {source_id}")
        require(url not in seen_urls, f"duplicate source URL: {url}")
        seen_ids.add(source_id)
        seen_urls.add(url)
        require(isinstance(source.get("name"), str) and source["name"].strip(),
                f"sources[{index}].name must be non-empty text")
        require(isinstance(source.get("enabled"), bool),
                f"sources[{index}].enabled must be true or false")
        require(source.get("scope") is None or isinstance(source.get("scope"), dict),
                f"sources[{index}].scope must be an object or null")
        require(source.get("query_guidance") is None
                or isinstance(source.get("query_guidance"), str),
                f"sources[{index}].query_guidance must be text or null")
        valid_timestamp(source.get("added_at"), f"sources[{index}].added_at", allow_date=True)
    return document


def load_document(path, kind):
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ScoutError(f"cannot read {path.name}: {exc}") from exc
    try:
        parsed = parse_json(raw.decode("utf-8"), path.name)
    except ScoutError:
        legacy = LEGACY_BLANK_HASHES.get(path.name)
        if legacy and hashlib.sha256(raw).hexdigest() == legacy:
            parsed = deepcopy(DEFAULT_PROFILE if kind == "profile" else DEFAULT_SOURCES)
        else:
            raise ScoutError(
                f"{path.name} is not JSON-compatible YAML; existing bytes were preserved")
    return validate_profile(parsed) if kind == "profile" else validate_sources(parsed)


def atomic_document(path, value):
    content = (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)
               + "\n").encode("utf-8")
    fd, temporary = tempfile.mkstemp(prefix=".family-scout-", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_records(path, kind):
    records = []
    primary_ids = set()
    operation_ids = set()
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ScoutError(f"cannot read {path.name}: {exc}") from exc
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        record = parse_json(line, f"{path.name} line {number}")
        require(isinstance(record, dict) and record.get("schema_version") == SCHEMA_VERSION,
                f"{path.name} line {number} has an unsupported record")
        key = "search_id" if kind == "shortlist" else "event_id"
        primary_id = valid_id(record.get(key), f"{path.name} line {number} {key}")
        operation_id = valid_id(record.get("operation_id"),
                                f"{path.name} line {number} operation_id")
        require(primary_id not in primary_ids,
                f"{path.name} line {number} repeats {key}")
        require(operation_id not in operation_ids,
                f"{path.name} line {number} repeats operation_id")
        primary_ids.add(primary_id)
        operation_ids.add(operation_id)
        if kind == "shortlist":
            valid_timestamp(record.get("created_at"),
                            f"{path.name} line {number} created_at")
            require(isinstance(record.get("request"), dict),
                    f"{path.name} line {number} request is missing")
            options = record.get("options")
            require(isinstance(options, list),
                    f"{path.name} line {number} options must be a list")
            option_numbers = set()
            for option in options:
                require(isinstance(option, dict)
                        and isinstance(option.get("number"), int)
                        and not isinstance(option.get("number"), bool)
                        and option["number"] >= 1,
                        f"{path.name} line {number} has an invalid option number")
                require(option["number"] not in option_numbers,
                        f"{path.name} line {number} has duplicate option numbers")
                option_numbers.add(option["number"])
                valid_id(option.get("activity_id"),
                         f"{path.name} line {number} activity_id")
                valid_id(option.get("session_id"),
                         f"{path.name} line {number} session_id")
        else:
            for record_key in ("search_id", "activity_id", "session_id"):
                valid_id(record.get(record_key),
                         f"{path.name} line {number} {record_key}")
            require(isinstance(record.get("option_number"), int)
                    and not isinstance(record.get("option_number"), bool)
                    and record["option_number"] >= 1,
                    f"{path.name} line {number} option_number is invalid")
            require(record.get("state") in FEEDBACK_STATES,
                    f"{path.name} line {number} state is invalid")
            features = record.get("features")
            require(isinstance(features, list)
                    and all(isinstance(item, dict)
                            and isinstance(item.get("feature"), str)
                            and bool(item["feature"].strip()) for item in features),
                    f"{path.name} line {number} features are invalid")
            member_ids = record.get("member_ids")
            require(isinstance(member_ids, list)
                    and all(isinstance(item, str) and ID_PATTERN.fullmatch(item)
                            for item in member_ids),
                    f"{path.name} line {number} member_ids are invalid")
            require(isinstance(record.get("original"), str)
                    and bool(record["original"].strip()),
                    f"{path.name} line {number} original wording is missing")
            valid_timestamp(record.get("created_at"),
                            f"{path.name} line {number} created_at")
            if record.get("supersedes_event_id") is not None:
                valid_id(record["supersedes_event_id"],
                         f"{path.name} line {number} supersedes_event_id")
        records.append(record)
    if kind == "feedback":
        links = {}
        for record in records:
            supersedes = record.get("supersedes_event_id")
            require(supersedes is None or supersedes in primary_ids,
                    f"{path.name} references unknown superseded feedback")
            links[record["event_id"]] = supersedes
        for event_id in links:
            visited = set()
            current = event_id
            while current is not None:
                require(current not in visited,
                        f"{path.name} contains a feedback supersession cycle")
                visited.add(current)
                current = links[current]
    return records


def append_record(path, value):
    line = (json.dumps(value, separators=(",", ":"), ensure_ascii=False,
                       allow_nan=False) + "\n").encode("utf-8")
    descriptor = os.open(path, os.O_WRONLY | os.O_APPEND)
    try:
        os.write(descriptor, line)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


@contextmanager
def state_lock(data_dir):
    require(data_dir.is_dir(), "private data directory does not exist; run install.sh first")
    for name in STATE_FILES:
        path = data_dir / name
        require(path.is_file() and not path.is_symlink(),
                f"{name} is missing or is not a regular file")
    lock_path = data_dir / ".family-scout.lock"
    require(not lock_path.is_symlink(),
            ".family-scout.lock is a symlink; existing state was preserved")
    descriptor = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def read_payload(path):
    if path == "-":
        return parse_json(sys.stdin.read(), "stdin payload")
    try:
        return parse_json(Path(path).read_text(encoding="utf-8"), path)
    except OSError as exc:
        raise ScoutError(f"cannot read input payload: {exc}") from exc


def deep_merge(original, changes):
    result = deepcopy(original)
    for key, value in changes.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def profile_blank(profile):
    comparable = deepcopy(profile)
    comparable["provenance"] = []
    return comparable == DEFAULT_PROFILE


def active_location(profile, at, force_home=False):
    if not force_home and profile.get("travel"):
        expiry = datetime.fromisoformat(profile["travel"]["expires_at"].replace("Z", "+00:00"))
        if at <= expiry:
            return {"origin_ref": "travel", "location": profile["travel"]}
    home = profile["home"]
    if home.get("label") or home.get("latitude") is not None:
        return {"origin_ref": "home", "location": home}
    return {"origin_ref": "unknown", "location": None}


def effective_feedback(records):
    superseded = {record.get("supersedes_event_id") for record in records
                  if record.get("supersedes_event_id")}
    return [record for record in records
            if record["event_id"] not in superseded and record.get("state") != "retracted"]


def parse_at(value):
    if value is None:
        return now_utc()
    valid_timestamp(value, "--at")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def command_status(data_dir):
    with state_lock(data_dir):
        profile = load_document(data_dir / "profile.yaml", "profile")
        sources = load_document(data_dir / "sources.yaml", "sources")
        shortlists = load_records(data_dir / "shortlists.jsonl", "shortlist")
        feedback = load_records(data_dir / "feedback.jsonl", "feedback")
    emit({
        "ok": True,
        "profile": {
            "blank": profile_blank(profile),
            "home_configured": profile["home"].get("latitude") is not None,
            "travel_configured": profile.get("travel") is not None,
            "group_member_count": len(profile["group_members"]),
        },
        "sources": {"total": len(sources["sources"]),
                    "enabled": sum(1 for item in sources["sources"] if item["enabled"])},
        "history": {"shortlists": len(shortlists), "feedback_events": len(feedback)},
    })


def command_context(data_dir, args):
    at = parse_at(args.at)
    with state_lock(data_dir):
        profile = load_document(data_dir / "profile.yaml", "profile")
        sources = load_document(data_dir / "sources.yaml", "sources")
        shortlists = load_records(data_dir / "shortlists.jsonl", "shortlist")
        feedback = load_records(data_dir / "feedback.jsonl", "feedback")
    emit({
        "ok": True,
        "at": at.isoformat(),
        "resolved_location": active_location(profile, at, args.location == "home"),
        "profile": profile,
        "enabled_sources": [item for item in sources["sources"] if item["enabled"]],
        "recent_shortlists": shortlists[-args.history_limit:],
        "effective_feedback": effective_feedback(feedback)[-args.history_limit:],
    })


def command_profile_update(data_dir, args):
    payload = read_payload(args.input)
    require(isinstance(payload, dict), "profile update payload must be an object")
    operation_id = valid_id(payload.get("operation_id"), "operation_id")
    changes = payload.get("changes")
    require(isinstance(changes, dict) and changes, "changes must be a non-empty object")
    allowed = set(DEFAULT_PROFILE) - {"schema_version", "provenance"}
    require(set(changes) <= allowed, "changes contains unsupported profile fields")
    reviewed_at = payload.get("reviewed_at", iso_now())
    valid_timestamp(reviewed_at, "reviewed_at", allow_date=True)
    source = payload.get("source", "explicit_user")
    require(isinstance(source, str) and source.strip(), "source must be non-empty text")
    with state_lock(data_dir):
        path = data_dir / "profile.yaml"
        profile = load_document(path, "profile")
        if any(item.get("operation_id") == operation_id for item in profile["provenance"]
               if isinstance(item, dict)):
            emit({"ok": True, "duplicate": True, "operation_id": operation_id})
            return
        updated = deep_merge(profile, changes)
        updated["provenance"].append({
            "operation_id": operation_id,
            "fields": sorted(changes),
            "source": source,
            "reviewed_at": reviewed_at,
        })
        validate_profile(updated)
        atomic_document(path, updated)
    emit({"ok": True, "duplicate": False, "operation_id": operation_id,
          "updated_fields": sorted(changes)})


def normalized_source(payload):
    source = deepcopy(payload)
    require(isinstance(source, dict), "source must be an object")
    require(isinstance(source.get("name"), str) and source["name"].strip(),
            "source.name must be non-empty text")
    url = valid_url(source.get("url"), "source.url")
    source.setdefault("id", stable_id("source", url.lower()))
    valid_id(source["id"], "source.id")
    source.setdefault("enabled", True)
    source.setdefault("scope", None)
    source.setdefault("added_at", date.today().isoformat())
    source.setdefault("query_guidance", None)
    validate_sources({"schema_version": 1, "sources": [source]})
    return source


def command_source_add(data_dir, args):
    payload = read_payload(args.input)
    require(isinstance(payload, dict), "source add payload must be an object")
    operation_id = valid_id(payload.get("operation_id"), "operation_id")
    source = normalized_source(payload.get("source"))
    source["last_operation_id"] = operation_id
    with state_lock(data_dir):
        path = data_dir / "sources.yaml"
        document = load_document(path, "sources")
        existing = next((item for item in document["sources"]
                         if item["id"] == source["id"] or item["url"] == source["url"]), None)
        if existing:
            require(existing["id"] == source["id"] and existing["url"] == source["url"],
                    "source id or URL conflicts with an existing source")
            emit({"ok": True, "duplicate": True, "source": existing})
            return
        document["sources"].append(source)
        validate_sources(document)
        atomic_document(path, document)
    emit({"ok": True, "duplicate": False, "source": source})


def command_source_set(data_dir, args):
    operation_id = valid_id(args.operation_id, "operation_id")
    valid_id(args.id, "source id")
    with state_lock(data_dir):
        path = data_dir / "sources.yaml"
        document = load_document(path, "sources")
        source = next((item for item in document["sources"] if item["id"] == args.id), None)
        require(source is not None, "source id was not found")
        duplicate = source.get("last_operation_id") == operation_id
        if not duplicate:
            source["enabled"] = args.enabled
            source["updated_at"] = iso_now()
            source["last_operation_id"] = operation_id
            validate_sources(document)
            atomic_document(path, document)
    emit({"ok": True, "duplicate": duplicate, "source_id": args.id,
          "enabled": args.enabled})


def command_source_remove(data_dir, args):
    valid_id(args.operation_id, "operation_id")
    valid_id(args.id, "source id")
    with state_lock(data_dir):
        path = data_dir / "sources.yaml"
        document = load_document(path, "sources")
        remaining = [item for item in document["sources"] if item["id"] != args.id]
        removed = len(remaining) != len(document["sources"])
        if removed:
            document["sources"] = remaining
            atomic_document(path, document)
    emit({"ok": True, "source_id": args.id, "removed": removed})


def haversine_km(origin_lat, origin_lon, venue_lat, venue_lon):
    values = (
        valid_number(origin_lat, "origin latitude", -90, 90),
        valid_number(origin_lon, "origin longitude", -180, 180),
        valid_number(venue_lat, "venue latitude", -90, 90),
        valid_number(venue_lon, "venue longitude", -180, 180),
    )
    lat1, lon1, lat2, lon2 = map(math.radians, values)
    delta_lat, delta_lon = lat2 - lat1, lon2 - lon1
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    a = min(1.0, max(0.0, a))
    return 6371.0088 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def command_distance(args):
    distance = haversine_km(args.origin_lat, args.origin_lon,
                            args.venue_lat, args.venue_lon)
    emit({"ok": True, "distance_km": round(distance, 3),
          "label": "straight-line distance"})


def interval(value_start, value_end, timezone_name, label):
    require(value_start is not None, f"{label}.start is required")
    try:
        zone = ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, TypeError) as exc:
        raise ScoutError(f"{label} timezone is invalid") from exc

    def parse(value, is_end):
        require(isinstance(value, str), f"{label} values must be ISO dates/times")
        try:
            if len(value) == 10:
                parsed_date = date.fromisoformat(value)
                return datetime.combine(parsed_date, time.max if is_end else time.min, zone)
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ScoutError(f"{label} values must be ISO dates/times") from exc
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=zone)
        return parsed

    start = parse(value_start, False)
    end = parse(value_end if value_end is not None else value_start, True)
    require(end >= start, f"{label}.end must not precede start")
    return start.astimezone(timezone.utc), end.astimezone(timezone.utc)


def requirement(name, status, reason, value=None):
    result = {"requirement": name, "status": status, "reason": reason}
    if value is not None:
        result["value"] = value
    return result


def validate_evaluation_request(request):
    require(isinstance(request, dict), "request must be an object")
    if request.get("radius_km") is not None:
        valid_number(request["radius_km"], "request.radius_km", 0)
    for key in ("free_only", "indoor_only"):
        if key in request:
            require(isinstance(request[key], bool), f"request.{key} must be true or false")
    if request.get("date_start") is not None:
        interval(request["date_start"], request.get("date_end"),
                 request.get("timezone"), "request date")
    if request.get("budget") is not None:
        budget = request["budget"]
        require(isinstance(budget, dict), "request.budget must be an object")
        valid_number(budget.get("amount"), "request budget amount", 0)
        for key in ("currency", "basis"):
            require(isinstance(budget.get(key), str) and budget[key].strip(),
                    f"request budget {key} must be non-empty text")
    attending = request.get("attending", [])
    require(isinstance(attending, list), "request.attending must be a list")
    for index, member in enumerate(attending):
        require(isinstance(member, dict), f"request.attending[{index}] must be an object")
        valid_id(member.get("id"), f"request.attending[{index}].id")
        if member.get("age") is not None:
            valid_number(member["age"], f"request.attending[{index}].age", 0, 130)
    return request


def evaluate_candidate(request, candidate):
    require(isinstance(candidate, dict), "each candidate must be an object")
    title = candidate.get("title")
    require(isinstance(title, str) and title.strip(), "candidate.title is required")
    checks = []
    closure = candidate.get("closure_status")
    require(closure in (None, "open", "closed", "cancelled", "unknown"),
            "candidate.closure_status is invalid")
    if closure in ("closed", "cancelled"):
        checks.append(requirement("closure", "confirmed_failure", f"reported {closure}"))

    radius = request.get("radius_km")
    distance = None
    if radius is not None:
        valid_number(radius, "request.radius_km", 0)
        origin, venue = request.get("origin"), candidate.get("coordinates")
        if not isinstance(origin, dict) or not isinstance(venue, dict):
            checks.append(requirement("radius", "unverified", "coordinates are missing or ambiguous"))
        else:
            distance = haversine_km(origin.get("latitude"), origin.get("longitude"),
                                    venue.get("latitude"), venue.get("longitude"))
            status = "confirmed_match" if distance <= radius else "confirmed_failure"
            checks.append(requirement("radius", status,
                                      "inside inclusive boundary" if status == "confirmed_match"
                                      else "outside boundary", round(distance, 3)))

    if request.get("date_start") is not None:
        timezone_name = request.get("timezone")
        requested = interval(request["date_start"], request.get("date_end"),
                             timezone_name, "request date")
        if candidate.get("date_start") is None:
            checks.append(requirement("date", "unverified", "usable date/time is missing"))
        else:
            candidate_range = interval(candidate["date_start"], candidate.get("date_end"),
                                       timezone_name, "candidate date")
            overlaps = candidate_range[1] >= requested[0] and candidate_range[0] <= requested[1]
            checks.append(requirement("date", "confirmed_match" if overlaps else "confirmed_failure",
                                      "usable interval overlaps" if overlaps else "outside requested interval"))

    cost = candidate.get("cost")
    if request.get("free_only") or request.get("budget") is not None:
        if not isinstance(cost, dict) or cost.get("status") != "known":
            checks.append(requirement("cost", "unverified", "mandatory group cost is unknown"))
        else:
            amount = valid_number(cost.get("amount"), "candidate cost amount", 0)
            currency = cost.get("currency")
            basis = cost.get("basis")
            require(isinstance(currency, str) and currency, "known candidate cost needs currency")
            require(isinstance(basis, str) and basis, "known candidate cost needs basis")
            if request.get("free_only"):
                checks.append(requirement("free_only",
                                          "confirmed_match" if amount == 0 else "confirmed_failure",
                                          "mandatory group cost is zero" if amount == 0
                                          else "mandatory group cost is not zero"))
            if request.get("budget") is not None:
                budget = request["budget"]
                require(isinstance(budget, dict), "request.budget must be an object")
                limit = valid_number(budget.get("amount"), "request budget amount", 0)
                compatible = currency == budget.get("currency") and basis == budget.get("basis")
                if not compatible:
                    checks.append(requirement("budget", "unverified",
                                              "currency or cost basis does not match"))
                else:
                    checks.append(requirement("budget",
                                              "confirmed_match" if amount <= limit else "confirmed_failure",
                                              "within budget" if amount <= limit else "over budget"))

    if request.get("indoor_only"):
        indoor = candidate.get("indoor_status")
        if indoor == "indoor":
            checks.append(requirement("indoor_only", "confirmed_match", "confirmed indoor"))
        elif indoor in ("outdoor", "mixed"):
            checks.append(requirement("indoor_only", "confirmed_failure", f"reported {indoor}"))
        else:
            checks.append(requirement("indoor_only", "unverified", "indoor status is unknown"))

    attending = request.get("attending", [])
    if attending:
        eligibility = candidate.get("eligibility")
        if not isinstance(eligibility, dict) or eligibility.get("status") != "verified":
            checks.append(requirement("eligibility", "unverified",
                                      "participation eligibility is not verified"))
        else:
            minimum, maximum = eligibility.get("min_age"), eligibility.get("max_age")
            if minimum is not None:
                valid_number(minimum, "eligibility.min_age", 0)
            if maximum is not None:
                valid_number(maximum, "eligibility.max_age", 0)
            require(minimum is None or maximum is None or maximum >= minimum,
                    "eligibility.max_age must not be less than min_age")
            age_unknown = any(member.get("age") is None and (minimum is not None or maximum is not None)
                              for member in attending)
            excluded = [member.get("id") for member in attending
                        if member.get("age") is not None
                        and ((minimum is not None and member["age"] < minimum)
                             or (maximum is not None and member["age"] > maximum))]
            if excluded:
                checks.append(requirement("eligibility", "confirmed_failure",
                                          "one or more attending members are outside the verified age range",
                                          excluded))
            elif age_unknown:
                checks.append(requirement("eligibility", "unverified",
                                          "an exact age is needed for the verified cutoff"))
            else:
                checks.append(requirement("eligibility", "confirmed_match",
                                          "all attending members meet verified eligibility"))

    booking = candidate.get("booking")
    if booking is not None:
        require(isinstance(booking, dict)
                and isinstance(booking.get("required"), bool),
                "candidate.booking must state whether booking is required")
        require(booking.get("availability") in
                ("available", "unavailable", "unknown", "not_applicable"),
                "candidate.booking availability is invalid")
    if isinstance(booking, dict) and booking.get("required"):
        availability = booking.get("availability")
        if availability == "available":
            checks.append(requirement("booking", "confirmed_match", "required booking is available"))
        elif availability == "unavailable":
            checks.append(requirement("booking", "confirmed_failure", "required booking is unavailable"))
        else:
            checks.append(requirement("booking", "unverified", "required booking availability is unknown"))

    statuses = {item["status"] for item in checks}
    overall = ("confirmed_failure" if "confirmed_failure" in statuses
               else "unverified" if "unverified" in statuses else "confirmed_match")
    return {"title": title, "classification": overall,
            "straight_line_distance_km": round(distance, 3) if distance is not None else None,
            "requirements": checks}


def command_evaluate(args):
    payload = read_payload(args.input)
    require(isinstance(payload, dict), "evaluation payload must be an object")
    request = payload.get("request")
    candidates = payload.get("candidates")
    validate_evaluation_request(request)
    require(isinstance(candidates, list), "candidates must be a list")
    emit({"ok": True, "results": [evaluate_candidate(request, item) for item in candidates]})


def sanitize_request(request):
    require(isinstance(request, dict), "request must be an object")
    forbidden = {"latitude", "longitude", "coordinates", "address"}

    def walk(value):
        if isinstance(value, dict):
            for key, nested in value.items():
                normalized = str(key).lower().replace("-", "_")
                require(not any(normalized == item or normalized.endswith("_" + item)
                                for item in forbidden),
                        "saved request must use an origin reference, not coordinates or an address")
                walk(nested)
        elif isinstance(value, list):
            for nested in value:
                walk(nested)

    walk(request)
    for key in ("origin_ref", "place_label", "date_start", "date_end", "timezone"):
        require(isinstance(request.get(key), str) and request[key],
                f"request.{key} is required")
    valid_number(request.get("radius_km"), "request.radius_km", 0)
    require(request["origin_ref"] in ("home", "travel", "explicit"),
            "request.origin_ref must be home, travel or explicit")
    try:
        ZoneInfo(request["timezone"])
    except ZoneInfoNotFoundError as exc:
        raise ScoutError("request.timezone is not a known IANA timezone") from exc
    interval(request["date_start"], request["date_end"], request["timezone"],
             "request date")
    require(isinstance(request.get("attending_member_ids"), list)
            and all(isinstance(value, str) and ID_PATTERN.fullmatch(value)
                    for value in request["attending_member_ids"]),
            "request.attending_member_ids must be a list")
    for key in ("free_only", "indoor_only"):
        if key in request:
            require(isinstance(request[key], bool), f"request.{key} must be true or false")
    if request.get("budget") is not None:
        budget = request["budget"]
        require(isinstance(budget, dict), "request.budget must be an object")
        valid_number(budget.get("amount"), "request.budget.amount", 0)
        for key in ("currency", "basis"):
            require(isinstance(budget.get(key), str) and budget[key].strip(),
                    f"request.budget.{key} must be non-empty text")
    return deepcopy(request)


def normalize_option(option, number, timezone_name, request):
    require(isinstance(option, dict), "each option must be an object")
    result = deepcopy(option)
    for key in ("title", "venue", "date_start", "checked_at"):
        require(isinstance(result.get(key), str) and result[key], f"option.{key} is required")
    valid_timestamp(result["date_start"], "option.date_start", allow_date=True)
    if result.get("date_end") is not None:
        valid_timestamp(result["date_end"], "option.date_end", allow_date=True)
    interval(result["date_start"], result.get("date_end"), timezone_name,
             "option date")
    valid_timestamp(result["checked_at"], "option.checked_at")
    require(result.get("status", "confirmed_match") == "confirmed_match",
            "displayed options must be confirmed matches")
    urls = result.get("source_urls")
    require(isinstance(urls, list) and urls, "option.source_urls must not be empty")
    for url in urls:
        valid_url(url, "option source URL")
    if result.get("distance_km") is not None:
        valid_number(result["distance_km"], "option.distance_km", 0)
    cost = result.get("cost")
    require(isinstance(cost, dict) and cost.get("status") in ("known", "unknown"),
            "option.cost must state known or unknown")
    if cost["status"] == "known":
        valid_number(cost.get("amount"), "option.cost.amount", 0)
        require(isinstance(cost.get("currency"), str) and cost["currency"],
                "known option cost needs currency")
        require(isinstance(cost.get("basis"), str) and cost["basis"],
                "known option cost needs basis")
    require(result.get("indoor_status") in ("indoor", "outdoor", "mixed", "unknown"),
            "option.indoor_status is invalid")
    booking = result.get("booking")
    require(isinstance(booking, dict) and isinstance(booking.get("required"), bool),
            "option.booking must state whether booking is required")
    require(booking.get("availability") in
            ("available", "unavailable", "unknown", "not_applicable"),
            "option.booking availability is invalid")
    require(not booking["required"] or booking["availability"] == "available",
            "an option requiring booking must have verified availability")
    require(isinstance(result.get("why"), str) and result["why"].strip(),
            "option.why is required")
    constraint_results = result.get("constraint_results")
    require(isinstance(constraint_results, list),
            "option.constraint_results must be copied from evaluate")
    classified = {}
    for item in constraint_results:
        require(isinstance(item, dict)
                and isinstance(item.get("requirement"), str)
                and item["requirement"].strip()
                and item.get("status") in
                ("confirmed_match", "confirmed_failure", "unverified")
                and isinstance(item.get("reason"), str)
                and item["reason"].strip(),
                "option.constraint_results contains an invalid classification")
        name = item["requirement"]
        require(name not in classified,
                "option.constraint_results repeats a requirement")
        classified[name] = item["status"]
    require(all(status == "confirmed_match" for status in classified.values()),
            "displayed options cannot contain failed or unverified hard requirements")
    expected = set()
    if request.get("radius_km") is not None:
        expected.add("radius")
    if request.get("date_start") is not None:
        expected.add("date")
    if request.get("free_only"):
        expected.add("free_only")
    if request.get("budget") is not None:
        expected.add("budget")
    if request.get("indoor_only"):
        expected.add("indoor_only")
    if request.get("attending_member_ids"):
        expected.add("eligibility")
    if booking["required"]:
        expected.add("booking")
    require(expected <= set(classified),
            "option.constraint_results is missing an applicable hard requirement")
    if request.get("radius_km") is not None:
        require(result.get("distance_km") is not None
                and result["distance_km"] <= request["radius_km"],
                "displayed option does not satisfy the requested radius")
    requested_range = interval(request["date_start"], request["date_end"],
                               timezone_name, "request date")
    option_range = interval(result["date_start"], result.get("date_end"),
                            timezone_name, "option date")
    require(option_range[1] >= requested_range[0]
            and option_range[0] <= requested_range[1],
            "displayed option does not overlap the requested date")
    if request.get("free_only"):
        require(cost["status"] == "known" and cost.get("amount") == 0,
                "displayed option does not satisfy free-only")
    if request.get("budget") is not None:
        budget = request["budget"]
        require(cost["status"] == "known"
                and cost.get("currency") == budget["currency"]
                and cost.get("basis") == budget["basis"]
                and cost.get("amount") <= budget["amount"],
                "displayed option does not satisfy the requested budget")
    if request.get("indoor_only"):
        require(result["indoor_status"] == "indoor",
                "displayed option does not satisfy indoor-only")
    require(isinstance(result.get("features", []), list)
            and all(isinstance(value, str) for value in result.get("features", [])),
            "option.features must be a list of text values")
    identity = result.get("identity_key") or (result["title"].strip().lower()
                                               + "|" + result["venue"].strip().lower())
    require(isinstance(identity, str) and identity.strip(),
            "option.identity_key must be non-empty text")
    activity_id = result.get("activity_id") or stable_id("activity", identity)
    valid_id(activity_id, "option.activity_id")
    session_identity = activity_id + "|" + result["date_start"] + "|" + str(result.get("date_end"))
    session_id = result.get("session_id") or stable_id("session", session_identity)
    valid_id(session_id, "option.session_id")
    result.update({"number": number, "activity_id": activity_id,
                   "session_id": session_id, "status": "confirmed_match"})
    return result


def command_shortlist_save(data_dir, args):
    payload = read_payload(args.input)
    require(isinstance(payload, dict), "shortlist payload must be an object")
    operation_id = valid_id(payload.get("operation_id"), "operation_id")
    saved_request = sanitize_request(payload.get("request"))
    options_input = payload.get("options")
    require(isinstance(options_input, list) and len(options_input) <= 5,
            "options must be a list with at most five entries")
    options = [normalize_option(option, index, saved_request["timezone"], saved_request)
               for index, option in enumerate(options_input, 1)]
    session_ids = [item["session_id"] for item in options]
    require(len(session_ids) == len(set(session_ids)),
            "duplicate activity session; combine its source evidence before saving")
    needs_checking = payload.get("needs_checking", [])
    require(isinstance(needs_checking, list) and len(needs_checking) <= 2,
            "needs_checking must have at most two leads")
    for lead in needs_checking:
        require(isinstance(lead, dict) and isinstance(lead.get("missing"), list)
                and bool(lead["missing"]),
                "each needs_checking lead must state missing requirements")
        for url in lead.get("source_urls", []):
            valid_url(url, "needs_checking source URL")
    tool_usage = payload.get("tool_usage", {})
    require(isinstance(tool_usage, dict), "tool_usage must be an object")
    limits = {"search_queries": 6, "source_fetches": 12, "forecast_lookups": 1}
    effort_mode = payload.get("effort_mode", "normal")
    require(effort_mode in ("normal", "deep"), "effort_mode must be normal or deep")
    for key, limit in limits.items():
        value = tool_usage.get(key, 0)
        require(isinstance(value, int) and not isinstance(value, bool) and value >= 0,
                f"{key} must be a non-negative integer")
        if effort_mode == "normal":
            require(isinstance(value, int) and not isinstance(value, bool)
                    and 0 <= value <= limit,
                    f"normal request {key} must be between 0 and {limit}")
    weather = payload.get("weather")
    require(isinstance(weather, dict) and weather.get("status") in ("known", "unknown"),
            "weather must state known or unknown")
    if weather["status"] == "known":
        valid_url(weather.get("source_url"), "weather.source_url")
        valid_timestamp(weather.get("checked_at"), "weather.checked_at")
    else:
        require(isinstance(weather.get("reason"), str) and weather["reason"].strip(),
                "unknown weather must include a reason")
        if weather.get("source_url") is not None:
            valid_url(weather["source_url"], "weather.source_url")
    consulted_sources = payload.get("consulted_sources", [])
    require(isinstance(consulted_sources, list), "consulted_sources must be a list")
    for source in consulted_sources:
        require(isinstance(source, dict), "each consulted source must be an object")
        valid_url(source.get("url"), "consulted source URL")
        require(source.get("status") in ("read", "failed", "skipped"),
                "consulted source status is invalid")
    record = {
        "schema_version": 1,
        "search_id": stable_id("search", operation_id),
        "operation_id": operation_id,
        "created_at": payload.get("created_at", iso_now()),
        "conversation_ref": payload.get("conversation_ref"),
        "effort_mode": effort_mode,
        "request": saved_request,
        "weather": deepcopy(weather),
        "options": options,
        "needs_checking": deepcopy(needs_checking),
        "consulted_sources": deepcopy(consulted_sources),
        "tool_usage": deepcopy(tool_usage),
    }
    valid_timestamp(record["created_at"], "created_at")
    require(record["conversation_ref"] is None or isinstance(record["conversation_ref"], str),
            "conversation_ref must be text or null")
    with state_lock(data_dir):
        path = data_dir / "shortlists.jsonl"
        records = load_records(path, "shortlist")
        existing = next((item for item in records if item["operation_id"] == operation_id), None)
        if existing:
            emit({"ok": True, "duplicate": True, "search_id": existing["search_id"]})
            return
        append_record(path, record)
    emit({"ok": True, "duplicate": False, "search_id": record["search_id"],
          "option_count": len(options)})


def select_shortlist(records, search_id=None, conversation_ref=None):
    if search_id:
        matches = [item for item in records if item["search_id"] == search_id]
    elif conversation_ref:
        matches = [item for item in records if item.get("conversation_ref") == conversation_ref]
    else:
        matches = records
    require(matches, "no matching saved shortlist was found")
    require(search_id or len(matches) == 1,
            "shortlist reference is ambiguous; ask which search/activity was intended")
    return matches[-1]


def resolve_option(records, number, search_id=None, conversation_ref=None):
    shortlist = select_shortlist(records, search_id, conversation_ref)
    option = next((item for item in shortlist["options"] if item["number"] == number), None)
    require(option is not None, "option number was not present in the selected shortlist")
    return shortlist, option


def command_resolve_option(data_dir, args):
    with state_lock(data_dir):
        records = load_records(data_dir / "shortlists.jsonl", "shortlist")
    shortlist, option = resolve_option(records, args.number, args.search_id,
                                       args.conversation_ref)
    emit({"ok": True, "search_id": shortlist["search_id"],
          "created_at": shortlist["created_at"], "option": option})


def command_feedback_add(data_dir, args):
    payload = read_payload(args.input)
    require(isinstance(payload, dict), "feedback payload must be an object")
    operation_id = valid_id(payload.get("operation_id"), "operation_id")
    state = payload.get("state")
    require(state in FEEDBACK_STATES, "unsupported feedback state")
    original = payload.get("original")
    require(isinstance(original, str) and original.strip(), "original feedback wording is required")
    with state_lock(data_dir):
        shortlist_records = load_records(data_dir / "shortlists.jsonl", "shortlist")
        feedback_path = data_dir / "feedback.jsonl"
        feedback_records = load_records(feedback_path, "feedback")
        existing = next((item for item in feedback_records
                         if item["operation_id"] == operation_id), None)
        if existing:
            emit({"ok": True, "duplicate": True, "event_id": existing["event_id"]})
            return
        supersedes = payload.get("supersedes_event_id")
        previous = None
        if supersedes:
            valid_id(supersedes, "supersedes_event_id")
            previous = next((item for item in feedback_records
                             if item["event_id"] == supersedes), None)
            require(previous is not None, "superseded feedback event was not found")
        require(state != "retracted" or previous is not None,
                "retracted feedback must supersede an existing event")
        search_id = previous["search_id"] if previous else payload.get("search_id")
        option_number = (previous["option_number"] if previous is not None
                         else payload.get("option_number"))
        require(isinstance(option_number, int) and not isinstance(option_number, bool),
                "option_number is required")
        require(option_number >= 1, "option_number must be at least 1")
        shortlist, option = resolve_option(shortlist_records, option_number, search_id)
        features = payload.get("features", [])
        require(isinstance(features, list)
                and all(isinstance(item, dict) and isinstance(item.get("feature"), str)
                        and bool(item["feature"].strip())
                        for item in features),
                "features must be objects with a feature value")
        member_ids = payload.get("member_ids", [])
        require(isinstance(member_ids, list)
                and all(isinstance(item, str) and ID_PATTERN.fullmatch(item)
                        for item in member_ids),
                "member_ids must be a list of identifiers")
        record = {
            "schema_version": 1,
            "event_id": stable_id("feedback", operation_id),
            "operation_id": operation_id,
            "created_at": payload.get("created_at", iso_now()),
            "search_id": shortlist["search_id"],
            "option_number": option_number,
            "activity_id": option["activity_id"],
            "session_id": option["session_id"],
            "state": state,
            "features": deepcopy(features),
            "member_ids": member_ids,
            "context": deepcopy(payload.get("context")),
            "original": original,
            "supersedes_event_id": supersedes,
        }
        valid_timestamp(record["created_at"], "created_at")
        append_record(feedback_path, record)
    emit({"ok": True, "duplicate": False, "event_id": record["event_id"],
          "activity_id": record["activity_id"]})


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", help="Family Scout private state directory")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status", help="Validate state and report a redacted summary")

    context_parser = commands.add_parser("context", help="Read current private context and history")
    context_parser.add_argument("--at", help="Timezone-aware ISO instant; defaults to now")
    context_parser.add_argument("--location", choices=("auto", "home"), default="auto")
    context_parser.add_argument("--history-limit", type=int, default=10)

    profile_parser = commands.add_parser("profile-update", help="Atomically merge an explicit profile update")
    profile_parser.add_argument("--input", default="-", help="JSON file or - for stdin")

    source_add = commands.add_parser("source-add", help="Add an enabled source")
    source_add.add_argument("--input", default="-", help="JSON file or - for stdin")
    for name, enabled in (("source-enable", True), ("source-disable", False)):
        source_set = commands.add_parser(name, help=name.replace("-", " "))
        source_set.add_argument("--id", required=True)
        source_set.add_argument("--operation-id", required=True)
        source_set.set_defaults(enabled=enabled)
    source_remove = commands.add_parser("source-remove", help="Remove a source")
    source_remove.add_argument("--id", required=True)
    source_remove.add_argument("--operation-id", required=True)

    distance = commands.add_parser("distance", help="Calculate evidenced straight-line distance")
    distance.add_argument("--origin-lat", required=True, type=float)
    distance.add_argument("--origin-lon", required=True, type=float)
    distance.add_argument("--venue-lat", required=True, type=float)
    distance.add_argument("--venue-lon", required=True, type=float)

    evaluate = commands.add_parser("evaluate", help="Classify structured hard requirements")
    evaluate.add_argument("--input", default="-", help="JSON file or - for stdin")

    shortlist = commands.add_parser("shortlist-save", help="Persist the exact displayed shortlist")
    shortlist.add_argument("--input", default="-", help="JSON file or - for stdin")
    resolve = commands.add_parser("resolve-option", help="Resolve a displayed option number")
    resolve.add_argument("--number", required=True, type=int)
    resolve.add_argument("--search-id")
    resolve.add_argument("--conversation-ref")
    feedback = commands.add_parser("feedback-add", help="Append explicit feedback or a correction")
    feedback.add_argument("--input", default="-", help="JSON file or - for stdin")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    selected = args.data_dir or os.environ.get("FAMILY_SCOUT_DATA_DIR")
    data_dir = Path(selected).expanduser().resolve() if selected else (
        Path.home() / ".local" / "share" / "family-scout").resolve()
    try:
        if args.command == "status":
            command_status(data_dir)
        elif args.command == "context":
            require(1 <= args.history_limit <= 100, "history-limit must be between 1 and 100")
            command_context(data_dir, args)
        elif args.command == "profile-update":
            command_profile_update(data_dir, args)
        elif args.command == "source-add":
            command_source_add(data_dir, args)
        elif args.command in ("source-enable", "source-disable"):
            command_source_set(data_dir, args)
        elif args.command == "source-remove":
            command_source_remove(data_dir, args)
        elif args.command == "distance":
            command_distance(args)
        elif args.command == "evaluate":
            command_evaluate(args)
        elif args.command == "shortlist-save":
            command_shortlist_save(data_dir, args)
        elif args.command == "resolve-option":
            command_resolve_option(data_dir, args)
        elif args.command == "feedback-add":
            command_feedback_add(data_dir, args)
        return 0
    except (ScoutError, OSError, UnicodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
