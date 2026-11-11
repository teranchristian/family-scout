# Family Scout

A small Git-managed Hermes skill for discovering **fresh, age-appropriate activities** near the user, checking each day's weather, and returning source-linked recommendations. There is **one discovery workflow** for dates or general event ideas, not separate complex dated/undated research paths.

## How it works

1. Read the existing private profile using `scripts/discovery_context.py`: saved location, group members, age context, preferences, constraints and enabled sources. Explicit user instructions override defaults. "My kids" targets the children's ages on the activity dates.
2. Determine the anchor suburb and nearby allowed suburbs. No city or family members are hardcoded into the skill.
3. For a broad search, launch **three tasks in one parallel `delegate_task` batch** when supported: **local events**, **nearby events**, and **weather for each requested day**. The first two agents use the same research rules; only their assigned public search areas differ. If delegation is unavailable, search directly. A single named-venue check does not need subagents.
4. Combine discoveries, deduplicate, confirm the best matches against current official/organiser pages, and rank by child-by-child fit, local convenience, cost, specialness and weather.
5. Reply in a scannable Telegram format: date/time, venue/suburb, brief description, who can participate, family price (or unknown), direct event link, map when the address is evidenced, booking/caveats, daily weather and useful daily picks/backup.

A broad search aims for 10–15 **actual leads when available**, not a mandatory quota. Return a top five if there are five good options and optional extras. Fresh discovery precedes any previous recommendations; no venue cache is used.

**Optional suburb sources:** Edit the private `sources.yml` (not the older structured `sources.yaml`) to point Family Scout at locally curated public event calendars:

```yaml
exampletown:
  - https://events.example.org/calendar

other-suburb:
  - https://events.example.org/another-calendar
```

The key is the suburb name, matched case-insensitively to the first comma-separated part of the saved home/travel location or to an explicit requested suburb. Matching is exact: a city key is not automatically applied to neighbouring suburbs. If the requested suburb has URLs, an **optional fourth agent** checks them alongside the two discovery agents and weather. Without matching URLs, the usual three-agent workflow remains. The installer creates `sources.yml` if missing but never replaces existing content; legacy `sources.yaml` and its source commands are preserved, not silently migrated. This limited YAML syntax supports top-level suburb keys and indented HTTP(S) URL lists only.

The **three installed Markdown files** are:
- `hermes-skill/SKILL.md` — task routing and final response
- `hermes-skill/references/profile.md` — load saved context and age calculations
- `hermes-skill/references/research.md` — shared local/nearby event research and weather

The Python helpers remain intact. Older optional validators/finalizers and saved shortlist/feedback commands remain available for explicit operations, but **ordinary recommendations do not require them**. Existing private state is not migrated, rewritten or erased by this refactor.

## One source of truth: Git instructions, separate private data

| Layer | Purpose |
| --- | --- |
| `hermes-skill/` and `scripts/` in this repository | Reviewed instructions and Python code |
| `~/.hermes/skills/family-scout/` | Installer-owned read-only copy plus `installation.json` |
| `~/.local/share/family-scout/` (or configured `data_dir`) | Private profile, suburb URLs, legacy sources, shortlists and feedback |

Hermes must never edit the checkout or installed skill during an activity search. General memory/autonomous skill management must not overwrite the reviewed workflow; use a **proposed Git change** instead. Private data changes use only explicit user-approved helper commands. Never commit personal profile data or send a full profile, birthdate or private home coordinates to search agents.

The installer's `installation.json` contains `source_dir`, `data_dir` and file hashes. These protect local installed edits. **On an upgrade from the old ten-file skill, `./install.sh` removes the old installer-owned reference files** after checking hashes, then records the new three-file set. Unowned files or locally modified owned files are never silently overwritten or deleted. The private data directory is untouched.

## Install or update on the Hermes host

Requires an existing Hermes installation, Bash, and Python 3.9+ (standard library only):

```sh
cd ~/repos/family-scout
./install.sh
```

Use `./install.sh --hermes-home /absolute/hermes/profile` for a non-default profile. An optional `--data-dir /absolute/private/dir` is supported on the initial install. Repeated installs retain the recorded data location.

The installer attempts to run `hermes curator lock family-scout` for the chosen Hermes profile. It reports `LOCKED` or `LOCK NOT APPLIED` without failing installation when the CLI cannot lock; this is an **agent-policy guard**, not an OS sandbox. Check with:

```sh
hermes curator status
```

Safe update sequence: review and merge Git changes, `git pull`, run `./install.sh`, then start a **fresh Hermes conversation**. If you see **local edits** on installed files, inspect and reconcile them deliberately; the installer refuses to overwrite. Removal with `./uninstall.sh` leaves the repository and private data intact.

## Test

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts tests
```

After installing on Hermes, test both a weekday and a weekend search and compare local/nearby discoveries, working source URLs, exact dates and age fit. Repository unit tests cannot prove live weather, browser or delegation behavior.
