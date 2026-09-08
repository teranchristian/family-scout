#!/usr/bin/env python3
"""Copy the Family Scout skill into an existing Hermes home."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile


REPO = Path(__file__).resolve().parent.parent
SKILL_SOURCE = REPO / "hermes-skill"
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


def source_files():
    files = {"SKILL.md": SKILL_SOURCE / "SKILL.md"}
    references = SKILL_SOURCE / "references"
    if references.is_dir():
        for path in sorted(references.rglob("*.md")):
            require(path.is_file() and not path.is_symlink(),
                    "Skill references must be regular files inside the repository.")
            files[str(path.relative_to(SKILL_SOURCE))] = path
    require(files["SKILL.md"].is_file() and not files["SKILL.md"].is_symlink(),
            "Repository SKILL.md is missing or is not a regular file.")
    return files


def owned_files(record):
    if record["schema_version"] == 1:
        return {"SKILL.md": record["skill_sha256"]}
    return record["skill_files"]


def safe_relative_path(value):
    path = Path(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts


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
    schema = record.get("schema_version") if isinstance(record, dict) else None
    common = (isinstance(record, dict)
              and record.get("project") == "family-scout"
              and schema in (1, 2)
              and isinstance(record.get("source_dir"), str)
              and isinstance(record.get("data_dir"), str)
              and Path(record["source_dir"]).is_absolute()
              and Path(record["data_dir"]).is_absolute())
    versioned = ((schema == 1 and isinstance(record.get("skill_sha256"), str))
                 or (schema == 2 and isinstance(record.get("skill_files"), dict)
                     and bool(record["skill_files"])
                     and all(safe_relative_path(path) and isinstance(value, str)
                             for path, value in record["skill_files"].items())))
    require(common and versioned,
            "Unrecognized installation record; leave it intact.")
    available_sources = {}
    if (SKILL_SOURCE / "SKILL.md").is_file():
        try:
            available_sources = source_files()
        except SetupError:
            # Recorded hashes are sufficient to protect uninstall when the
            # checkout is incomplete. A later install will report the source error.
            available_sources = {}
    for relative, recorded_hash in owned_files(record).items():
        installed = target / relative
        require(all(not parent.is_symlink() for parent in installed.parents
                    if inside(parent, target) and parent != target),
                "An installed skill subdirectory is a symlink; leave it intact.")
        if not installed.exists():
            require(not installed.is_symlink(),
                    "An installed Family Scout path is a broken symlink; leave it intact.")
            # An interrupted install/uninstall may leave the ownership marker
            # after one of its files. The record still safely identifies the
            # remaining paths; install can restore and uninstall can finish.
            continue
        require(installed.is_file() and not installed.is_symlink(),
                "An installed Family Scout file is not regular; leave it intact.")
        current = digest(installed.read_bytes())
        accepted = {recorded_hash}
        if relative in available_sources:
            accepted.add(digest(available_sources[relative].read_bytes()))
        require(current in accepted,
                "An installed Family Scout file has local edits: " + relative +
                ". Review it, copy intended non-private changes into hermes-skill, "
                "then rerun. Nothing was overwritten or removed.")
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


def preflight_destinations(target, sources, previous):
    for relative, source in sources.items():
        destination = target / relative
        if relative not in previous:
            recoverable = (destination.is_file() and not destination.is_symlink()
                           and digest(destination.read_bytes()) == digest(source.read_bytes()))
            require((not destination.exists() and not destination.is_symlink()) or recoverable,
                    "A new skill path is already occupied; leave it intact: " + relative)
        parent = destination.parent
        while parent != target:
            require(not parent.is_symlink() and (not parent.exists() or parent.is_dir()),
                    "A skill subdirectory path is unsafe; leave it intact: " + relative)
            parent = parent.parent


def remove_empty_parents(target, relative_paths):
    parents = {parent for relative in relative_paths
               for parent in (target / relative).parents if parent != target}
    for parent in sorted(parents, key=lambda value: len(value.parts), reverse=True):
        if inside(parent, target):
            try:
                parent.rmdir()
            except OSError:
                pass


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
    sources = source_files()
    previous = owned_files(record) if record else {}
    preflight_destinations(target, sources, previous)
    prepare_state(data)
    target.mkdir(parents=True, exist_ok=True)
    for relative, source in sources.items():
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        atomic_write(destination, source.read_bytes())
    stale = set(previous) - set(sources)
    for relative in stale:
        path = target / relative
        if path.exists():
            path.unlink()
    remove_empty_parents(target, stale)
    hashes = {relative: digest(source.read_bytes())
              for relative, source in sources.items()}
    record = {
        "project": "family-scout",
        "schema_version": 2,
        "source_dir": str(REPO),
        "data_dir": str(data),
        "skill_sha256": hashes["SKILL.md"],
        "skill_files": hashes,
    }
    atomic_write(target / "installation.json",
                 (json.dumps(record, indent=2) + "\n").encode())
    print("OK: Local installation and state-access checks passed.")
    print("Hermes home: " + str(hermes_home))
    print("Installed skill (copy): " + str(target))
    print("Private data: " + str(data))
    print("Repository source: " + str(REPO))
    print("PROFILE: Review profile.yaml privately; new profiles are blank.")
    print("NEXT: In a fresh Hermes conversation, run one Phase 1 recommendation "
          "cycle and record live source, forecast and persistence outcomes.")


def uninstall(target, record):
    if record is None:
        print("OK: Family Scout is not installed at this Hermes home. State was untouched.")
        return
    paths = list(owned_files(record))
    for relative in paths:
        path = target / relative
        if path.exists():
            path.unlink()
    (target / "installation.json").unlink()
    remove_empty_parents(target, paths)
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
