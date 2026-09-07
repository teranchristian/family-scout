#!/usr/bin/env python3
"""Copy the setup skill into an existing Hermes home; preserve private state."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile


REPO = Path(__file__).resolve().parent.parent
SOURCE = REPO / "hermes-skill" / "SKILL.md"
STATE_FILES = {
    "profile.yaml": "profile.example.yaml",
    "sources.yaml": "sources.example.yaml",
    "shortlists.jsonl": None,
    "feedback.jsonl": None,
}


class SetupError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise SetupError(message)


def digest(content):
    return hashlib.sha256(content).hexdigest()


def inside(path, parent):
    return path == parent or parent in path.parents


def resolve_home(explicit):
    selected = explicit or os.environ.get("HERMES_HOME")
    if selected:
        return Path(selected).expanduser().resolve()
    base = Path.home() / ".hermes"
    marker = base / "active_profile"
    if marker.exists():
        active = marker.read_text().strip()
        require(active in ("", "default"),
                "A named Hermes profile is active. Pass its actual home with "
                "--hermes-home or HERMES_HOME; no profile was guessed.")
    return base.resolve()


def read_installation(target):
    require(not target.is_symlink(), "The skill directory is a symlink; leave it intact.")
    if not target.exists():
        return None
    marker = target / "installation.json"
    require(target.is_dir() and marker.is_file() and not marker.is_symlink(),
            "Existing skill has no Family Scout ownership record; leave it intact.")
    try:
        record = json.loads(marker.read_text())
    except (ValueError, UnicodeError) as exc:
        raise SetupError("Installation record is unreadable; leave it intact.") from exc
    require(isinstance(record, dict) and record.get("project") == "family-scout"
            and record.get("schema_version") == 1
            and isinstance(record.get("skill_sha256"), str)
            and isinstance(record.get("source_dir"), str)
            and isinstance(record.get("data_dir"), str)
            and Path(record["source_dir"]).is_absolute()
            and Path(record["data_dir"]).is_absolute(),
            "Unrecognized installation record; leave it intact.")
    skill = target / "SKILL.md"
    require(skill.is_file() and not skill.is_symlink(),
            "Installed SKILL.md is missing or is not a regular file; leave it intact.")
    current = digest(skill.read_bytes())
    accepted = {record["skill_sha256"]}
    if SOURCE.is_file():
        accepted.add(digest(SOURCE.read_bytes()))
    require(current in accepted,
            "Installed SKILL.md has local edits. Review them, copy the intended "
            "non-private changes into hermes-skill/SKILL.md, then rerun. "
            "Nothing was overwritten or removed.")
    return record


def atomic_write(path, content):
    # Same-directory replacement avoids a partially written installed file.
    fd, temporary = tempfile.mkstemp(prefix=".family-scout-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def prepare_state(data):
    data.mkdir(parents=True, exist_ok=True, mode=0o700)
    require(data.is_dir() and os.access(data, os.R_OK | os.W_OK | os.X_OK),
            "Private data directory must be readable and writable.")
    # Check every existing file before creating any missing ones. Do not parse,
    # repair, truncate, or replace existing state, including malformed content.
    for name in STATE_FILES:
        path = data / name
        require(not path.is_symlink(), "A private state file is a symlink; leave it intact.")
        require(not path.exists() or (path.is_file() and os.access(path, os.R_OK | os.W_OK)),
                "Existing private state must be regular, readable, writable files.")
    for name, template in STATE_FILES.items():
        content = (REPO / "examples" / template).read_bytes() if template else b""
        try:
            fd = os.open(data / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            continue
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)


def install(args, hermes_home, target, record):
    chosen_data = (args.data_dir or (record and record["data_dir"])
                   or str(Path.home() / ".local" / "share" / "family-scout"))
    data = Path(chosen_data).expanduser().resolve()
    require(not inside(data, REPO), "Private data must be outside the repository.")
    resolved_target = target.resolve()
    require(not inside(data, resolved_target) and not inside(resolved_target, data),
            "Private data and the installed skill must be separate directories.")
    require(not record or data == Path(record["data_dir"]).resolve(),
            "This installation already uses another data directory. Uninstall "
            "first to change it; state migration is not automatic.")
    content = SOURCE.read_bytes()
    prepare_state(data)
    target.mkdir(parents=True, exist_ok=True)
    atomic_write(target / "SKILL.md", content)
    record = {
        "project": "family-scout",
        "schema_version": 1,
        "source_dir": str(REPO),
        "data_dir": str(data),
        "skill_sha256": digest(content),
    }
    atomic_write(target / "installation.json",
                 (json.dumps(record, indent=2) + "\n").encode())
    print("OK: Local installation and state-access checks passed.")
    print("Hermes home: " + str(hermes_home))
    print("Installed skill (copy): " + str(target))
    print("Private data: " + str(data))
    print("Repository source: " + str(REPO))
    print("SETUP PENDING: Review profile.yaml privately; new profiles are blank.")
    print("UNVERIFIED: Fresh Hermes loading, profile reading, live search, "
          "source reading and dated forecast handling still need host checks.")


def uninstall(target, record):
    if record is None:
        print("OK: Family Scout is not installed at this Hermes home. State was untouched.")
        return
    (target / "SKILL.md").unlink()
    (target / "installation.json").unlink()
    if not any(target.iterdir()):
        target.rmdir()
    else:
        print("NOTE: Unrelated files remain in the skill directory; they were preserved.")
    print("OK: Removed owned integration files. Repository and private state were preserved.")
    print("Preserved private data: " + record["data_dir"])
    print("Reinstall with the same Hermes home and data-directory options to reuse it.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("install", "uninstall"))
    parser.add_argument("--hermes-home", help="Existing active Hermes home directory")
    parser.add_argument("--data-dir", help="Private state directory (install only)")
    args = parser.parse_args()
    try:
        require(sys.version_info >= (3, 9), "UNAVAILABLE: Python 3.9 or newer is required.")
        require(args.action == "install" or args.data_dir is None,
                "Uninstall takes --hermes-home only; it always preserves private data.")
        hermes_home = resolve_home(args.hermes_home)
        require(hermes_home.is_dir(),
                "SETUP PENDING: Hermes home does not exist. Set up Hermes first "
                "or pass its actual home with --hermes-home.")
        target = hermes_home / "skills" / "family-scout"
        require(not inside(target.resolve(), REPO),
                "The installed skill must be outside the repository.")
        record = read_installation(target)
        if args.action == "install":
            install(args, hermes_home, target, record)
        else:
            uninstall(target, record)
        return 0
    except (SetupError, OSError, UnicodeError) as exc:
        print("SETUP BLOCKED: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
