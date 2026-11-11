# Family Scout

Family Scout is a Hermes skill for finding practical family outings from current
sources and remembering only explicit feedback.

**Current workflow:** Requests for any specific day or date range return a
source-linked shortlist directly. General undated searches use a two-stage
menu and verify selected choices. Both use fresh sources, not cached venues.

Repository: <https://github.com/teranchristian/family-scout>

## What Family Scout does

- Interprets today, tomorrow, weekdays, weekends and named dates in the
  activity location's timezone.
- Searches the live web, reads current source pages and obtains a dated forecast
  using the tools already available to Hermes.
- Uses fresh discovery for every new recommendation, without a venue cache.
- Lets a radius-aware broad search cover plausible adjacent areas inside the
  existing query budget without moving the named geographic anchor.
- Applies strict date, radius, group cost, indoor, age, closure and mandatory
  booking checks without silently treating unknown facts as matches.
- Checks exact venue/branch identity and resolves current closure or relocation
  signals before investing in detailed research or calling a venue open.
- Checks current official notices for requested-date closures, maintenance and
  unavailable promoted sub-facilities instead of relying on weekly hours alone.
- Opens and validates factual and booking links, omits broken or wrong-target
  URLs, and can generate a Google Maps search link locally from an exact address.
- For a normal broad search, first shows a varied menu aiming for 6–8 plausible
  possibilities; after the user chooses, deeply verifies at most three selected
  options and can turn them into a practical plan.
- Keeps the initial menu lightweight and explicit about facts still needing
  verification; selected options then receive concrete activity details,
  requested-date hours, age fit, family cost, booking status and factual/map links.
- For multi-day or weather-sensitive requests, recommends a plan for each day
  with a realistic backup.
- Saves undated initial menus and selected verified options for follow-ups
  without storing a separate venue database. Dated-event searches show the
  sourced shortlist immediately; saving is optional.
- Remembers explicit feedback across fresh conversations, including corrections
  and retractions, and can use it for “more like this”.
- Supports explicit home/travel context, profile corrections and custom source
  add, enable, disable and removal.

Hermes owns natural-language interpretation, live discovery, page reading,
evidence selection and qualitative ranking. A standard-library Python helper
owns validation, straight-line distance, stable references and safe persistence.
It is not a separate search application.

The project deliberately excludes databases, background scraping, provider
frameworks, routing, booking integrations, web UI, accounts, machine learning
and numerical match scores.

## Dated activities: one workflow for every day

"What's on Tuesday?", "activities tomorrow", "this weekend" and "14–15 November"
all use the same straightforward path:

1. Resolve the requested date(s), location, family ages and hard constraints.
2. Discover fresh local council, library and community events, plus worthwhile
   nearby activities. Look in adjacent areas within the requested scope.
3. Check current official dates/hours, child-by-child fit, costs, booking,
   closures and the weather where available.
4. Return a practical source-linked shortlist with Google Maps links for
   evidenced addresses. Let the family choose what to do.

There is **no weekend-only logic, mandatory three-subagent batch, fixed
10–15-lead target, JSON finalizer or required save step**. Do not invent
candidates to reach a quota. Saving is optional unless requested. A dated
search for one specific venue needs only that venue checked.

For open-ended **undated** discovery, keep the existing two-stage menu:
show 6–8 varied possibilities when available; verify the selected options.
This preserves saved menu numbers and explicit feedback without making every
dated request perform those extra steps.

The skill's `SKILL.md` entry point is intentionally small. Other detailed
reference files remain available for explicit deeper investigation, profile
work and the undated menu's validation.

## One source of truth: Git code, private state, locked skill

Family Scout is **Git-managed**, not an agent-maintained skill. Its three
distinct stores have different responsibilities:

| Layer | Owner | May Hermes modify it during a normal outing? |
| --- | --- | --- |
| `hermes-skill/`, `scripts/` and other repository files | Reviewed Git changes | **No** |
| `~/.hermes/skills/family-scout/` installed skill copy | `./install.sh` from Git | **No** |
| Private `<data_dir>/profile.yaml`, `feedback.jsonl`, `sources.yaml`, `shortlists.jsonl` | Family Scout helper commands | **Yes**, using documented safe commands and explicit feedback rules |

Hermes can learn general factual memories and can propose new procedures, but
**must never turn them into edits of Family Scout skill instructions**.
If its memory or a run suggests a better search process, report what happened
and propose a Git issue/PR. Don't silently store a competing Family Scout
workflow in Hermes memory. Family Scout's private state is authoritative for
its own saved preferences and feedback; an explicit current user request still
takes priority. There is no automatic memory-to-skill synchronization.

**`./install.sh` now attempts to lock Family Scout automatically**
*after* it copies the Git-owned skill. It calls
`hermes curator lock family-scout` through the installed Hermes CLI with
`HERMES_HOME` set to the exact profile targeted by the installer (including
`--hermes-home`). This is repeatable and does not enable autonomous curation
or hand ownership of the skill to Curator.

On success the installer prints `LOCKED`. If the Hermes CLI is missing or
too old to support locking, the installation still succeeds but prints
`LOCK NOT APPLIED` so there is no false claim of protection. Update Hermes
and rerun `./install.sh` to apply the lock; no separate command is needed.
To check status manually:

```sh
hermes curator status
```

The lock is a **Hermes agent-policy guard**, not an operating-system sandbox,
and does not block your own `git pull` + `./install.sh` updates. It
protects only the installed skill, not arbitrary copies of the repository.
Do not disable all Hermes memory or self-improvement; Family Scout's own
private state and feedback remain writable through the safe helper commands.
The installer does not change `config.yaml` or global Hermes settings.

Safe update workflow: make and test a Git change, review/merge the PR,
`git pull` on the Hermes host, run `./install.sh`, and start a fresh Hermes
conversation. If installation reports **local edits**, inspect and reconcile
them deliberately rather than overwriting or resetting private state. The
installer already checks recorded hashes and refuses to silently overwrite
modified installed skill files.

## Install or update

Use an existing Hermes installation, Bash and Python 3.9 or newer. The setup
helper installs no dependencies and does not change system Python, Hermes
configuration or running services.

From this checkout on the Hermes host:

```sh
./install.sh
```

The preferred checkout location is `$HOME/repos/family-scout`; other persistent
locations work. Do not remove the checkout while the skill is installed because
the installed skill invokes the helper through the recorded repository path.

The installer uses `--hermes-home`, then `HERMES_HOME`, then `~/.hermes`. If the
default Hermes home indicates a named active profile, setup stops rather than
guessing. For an explicitly selected profile, using an invented example name:

```sh
./install.sh --hermes-home "$HOME/.hermes/profiles/demo-profile"
```

An optional `--data-dir /absolute/private/directory` changes the state location.
It must be outside the checkout and separate from the installed skill directory.
While installed, a repeat install without `--data-dir` reuses the recorded data
directory. Profiles share the default state directory; choose separate data
directories when they must not share context.

Installation leaves existing private data untouched. New data directories use
mode `0700`, and new state files use `0600`; existing permissions are unchanged.

## Age accuracy and privacy

An individual `group_members` entry in the private profile may include
`date_of_birth: "YYYY-MM-DD"`. At runtime, the deterministic helper derives
the child's age **on the activity date**, including birthdays between now
and the planned outing. A saved static age remains a backward-compatible
fallback until a birthdate is explicitly supplied and approved. The
`ages-on --date YYYY-MM-DD` command returns only derived ages and member IDs,
not birthdates; the profile itself stays private. No personal birthdates are
seeded in example files or committed to Git.

## Private state

| Location | Purpose |
| --- | --- |
| `hermes-skill/SKILL.md` | Thin task router and shared boundaries |
| `hermes-skill/references/` | Fast recommendation workflow plus detailed discovery, briefing, runtime, memory and helper contracts |
| `scripts/family_scout.py` | Deterministic validation and persistence helper |
| `<hermes-home>/skills/family-scout/` | Installed copy of the skill instruction tree |
| `<hermes-home>/skills/family-scout/installation.json` | Owned-file hashes plus repository and private-state paths |
| `~/.local/share/family-scout/profile.yaml` | Private origin, group, preferences, constraints and travel context |
| `~/.local/share/family-scout/sources.yaml` | Private custom source list |
| `~/.local/share/family-scout/shortlists.jsonl` | Append-only exact shortlist history |
| `~/.local/share/family-scout/feedback.jsonl` | Append-only explicit feedback and corrections |

The `.yaml` documents use indented JSON, which is valid YAML. Use the
documented helper commands for updates; avoid hand-editing a different YAML
style. Private data stays outside the repository.

The templates contain no people, precise locations or credentials. Never commit
private runtime state. The helper's `status` command is redacted; its `context`
command intentionally returns private context to Hermes and must not be copied
into web queries, logs or public reports.

## Smoke test after an update

After `git pull` and `./install.sh`, start a fresh Hermes conversation
and check both active workflows:

- **Dated activities:** Ask for free or low-cost activities on a weekday, then repeat for a weekend.
  Expect nearby suburbs, fresh small council/community events, checked links,
  practical weather advice and age-specific suitability. A useful sourced
  answer must not depend on saving or running the old finalizer.
- **Undated outings:** Ask for general activities nearby. Expect a varied
  initial menu and deeper checks for selected options, with honest uncertainty.

Test at a second public location and check that user-provided radius and
location constraints override the saved home location. Report failures with
source evidence and reproduce them before changing the workflow. The
historical verification log is retained in Git history, not required at
runtime.

## Helper and development checks

Hermes should follow the documented interface in
`hermes-skill/references/cli.md`. For a redacted manual check:

```sh
python3 scripts/family_scout.py --data-dir /absolute/private/directory status
```

Run the deterministic repository checks with:

```sh
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/setup.py scripts/family_scout.py scripts/discovery_context.py scripts/finalize_briefing.py scripts/render_briefing.py tests/*.py
```

The GitHub Actions workflow runs the Python tests and compilation checks.

## Updates and removal

Review repository changes, then rerun `./install.sh` to refresh the installed
copy. The installer owns only the files listed in `installation.json`. If any
installed owned file has local edits, update and uninstall both stop before
overwriting or removing it. Reconcile intended non-private behavior into the
repository first.

To remove the integration while preserving the checkout and all private state:

```sh
./uninstall.sh
```

Pass the same `--hermes-home` option for a named or custom profile. Repeated
uninstall is harmless. There is intentionally no purge command.

Hermes references: [skill discovery and management](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)
and [profiles and configuration](https://hermes-agent.nousresearch.com/docs/reference/faq).
