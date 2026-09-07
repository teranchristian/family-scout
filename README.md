# Family Scout

Family Scout is a planned Hermes skill for finding practical family outings
using current sources and explicit feedback. **This repository implements Phase
0 only:** installation, private state and instructions for setup verification.
It does not yet generate recommendations or process feedback.

Repository: <https://github.com/teranchristian/family-scout>

## Prerequisites and installation

Use an existing Hermes installation, Bash and Python 3.9 or newer. The setup
helper uses only the Python standard library. It installs no dependencies and
does not change system Python, Hermes configuration or running services.

From this checkout on the Hermes host:

```sh
./install.sh
```

The preferred checkout location is `$HOME/repos/family-scout`; other locations
work. The installer uses `--hermes-home`, then `HERMES_HOME`, then `~/.hermes`.
If the default Hermes home indicates a named active profile, setup stops and
requires its explicit directory rather than assuming the default profile.
Confirm the actual profile on your host before installing. A directory existing
does not, by itself, prove that Hermes is installed or can load the skill.

For an explicitly selected profile (the name below is invented):

```sh
./install.sh --hermes-home "$HOME/.hermes/profiles/demo-profile"
```

An optional `--data-dir /absolute/private/directory` changes the state location.
It must be outside the checkout and separate from the installed skill directory.
Use the same options after uninstalling to reuse custom state. While installed,
a repeat install without `--data-dir` reuses the recorded directory. Profiles
share the default state directory; choose separate data directories if needed.

The installer prints the selected paths and reports local setup checks separately
from unverified live capabilities. Existing private files are never overwritten,
even if malformed. Only missing state files are initialized. New data directories
are created with mode `0700`, and new state files with mode `0600`; existing
permissions are left unchanged.

## Files and ownership

| Location | Purpose |
| --- | --- |
| `hermes-skill/SKILL.md` in this checkout | Canonical skill instructions, tracked in Git |
| `<hermes-home>/skills/family-scout/SKILL.md` | Installed copy loaded by Hermes |
| `<hermes-home>/skills/family-scout/installation.json` | Local ownership, source path, state path and installed checksum |
| `~/.local/share/family-scout/profile.yaml` | Private origin, group and preferences; initially blank |
| `~/.local/share/family-scout/sources.yaml` | Private source list; initially empty |
| `~/.local/share/family-scout/shortlists.jsonl` | Private shortlist history; initially empty |
| `~/.local/share/family-scout/feedback.jsonl` | Private explicit feedback history; initially empty |

The installed skill is a **copy**, refreshed explicitly by `install.sh`. This
uses Hermes' documented skill directory and avoids assuming a particular host
version discovers directory symlinks. A fresh conversation must still verify
discovery. The installer refuses an existing skill without its ownership record.

The `examples/` templates intentionally contain no people, precise locations or
credentials. Edit the private installed profile when ready; never put personal
details into the templates or skill instructions. A blank origin remains unknown.
An empty source list is valid. Phase 0 checks file access without validating or
implementing the future recommendation data model.

The initial YAML files have `schema_version: 1`. Home includes a label,
latitude, longitude and timezone; the default radius is 15 km. Group identifiers,
age information, preferences, constraints and field provenance belong in private
state. Any future travel context needs an explicit expiry. Future JSONL records
will carry their own schema version and stable IDs; no records are created by
Phase 0.

## Updates and removal

Review repository changes, then run `./install.sh` again to refresh the skill.
The installer leaves uncommitted repository edits intact. If Hermes edited the
installed `SKILL.md`, both update and uninstall stop before overwriting it.
Review the difference, remove any personal material from the proposed behavior
change, reconcile the intended instructions into `hermes-skill/SKILL.md`, and
commit them. Rerun setup only after preserving the installed changes you need.

To remove the integration:

```sh
./uninstall.sh
```

Pass the same `--hermes-home` option when using a named or custom profile. This
removes only the owned skill and installation record. It preserves the checkout,
all private state and any unrelated files. If unrelated files remain in the
skill directory, resolve that directory collision before a later reinstall.
Repeated uninstall is harmless. Reinstall with the same options to reuse state.
There is no purge option in Phase 0.

## Phase 0 verification

Repository and temporary-directory checks are recorded in `VERIFICATION.md`.
They do not establish live host readiness. On the actual Hermes host:

1. Install, run the same install again, and confirm the printed profile and data
   paths are the intended ones. Review the private profile without copying its
   contents into Git or public reports.
2. Start a fresh Hermes conversation and ask: **“Load Family Scout and verify
   Phase 0 setup. Use an arbitrary public location, with no personal details.”**
3. Record skill loading and private profile reading separately. A blank profile
   can pass file access while home/group configuration remains pending.
4. Record a real public search, a successfully read result page, and a dated
   forecast or an explicit unavailable result. Include check date and public
   source URLs. Existing Hermes tools must do the work; no automatic replacement
   services are installed.
5. Verify normal uninstall and reinstall against synthetic state, preserving
   every state file. Record any remaining host or tool blocker before Phase 1.

Missing search or source reading blocks Phase 1 live integration. Forecast
unavailability is an acceptable recorded outcome. A missing private home origin
can remain pending while a public origin is used for setup checks. **Phase 0 is
not complete until the required actual-host checks have recorded outcomes.**

Phase 1 is the thin recommendation probe and real search cycle. After its
side-by-side trial, Phase 1.5 reviews setup friction before deciding whether a
doctor command, purge workflow or broader installer automation is warranted.
Deferred work is not an automatic backlog commitment.

Hermes references: [skill discovery and management](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)
and [profiles and configuration](https://hermes-agent.nousresearch.com/docs/reference/faq).
