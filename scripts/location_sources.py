#!/usr/bin/env python3
"""Read public event-calendar URLs grouped by suburb, using only the standard library."""

from pathlib import Path
from urllib.parse import urlparse


def location_key(label):
    """Match 'Exampletown, NSW' to the YAML key 'exampletown'."""
    if not isinstance(label, str):
        return None
    key = " ".join(label.split(",", 1)[0].split()).casefold()
    return key or None


def read_location_sources(path):
    """Read the deliberately small YAML subset: suburb: / two-space - URL lines."""
    path = Path(path)
    if not path.exists() and not path.is_symlink():
        return {}
    if path.is_symlink() or not path.is_file():
        raise ValueError("sources.yml must be a regular file, not a symlink")
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"cannot read sources.yml: {exc}") from exc

    groups = {}
    current = None
    for number, raw in enumerate(lines, 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw == raw.lstrip() and raw.endswith(":"):
            label = raw[:-1].strip()
            if not label or any(char in label for char in "#[]{}"):
                raise ValueError(f"sources.yml line {number}: invalid suburb key")
            current = location_key(label)
            if current in groups:
                raise ValueError(f"sources.yml line {number}: duplicate suburb {label!r}")
            groups[current] = []
        elif raw.startswith("  - "):
            if current is None:
                raise ValueError(f"sources.yml line {number}: URL has no suburb key")
            url = raw[4:].strip()
            parsed = urlparse(url)
            if (parsed.scheme not in ("http", "https") or not parsed.hostname
                    or parsed.username is not None or parsed.password is not None):
                raise ValueError(f"sources.yml line {number}: expected a public http(s) URL")
            if url in groups[current]:
                raise ValueError(f"sources.yml line {number}: duplicate URL")
            groups[current].append(url)
        else:
            raise ValueError(
                f"sources.yml line {number}: use 'suburb:' and '  - https://...' only"
            )
    return groups


def matching_location_sources(path, label):
    suburb = location_key(label)
    groups = read_location_sources(path)
    return {"suburb": suburb, "urls": groups.get(suburb, []) if suburb else []}
