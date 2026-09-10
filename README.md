# Family Scout

Family Scout is a Hermes skill for finding practical family outings from current
sources and remembering only explicit feedback.

**Current status: Phase 1 is built; real-use trial pending.** The deterministic
helper, persistence flow and skill contract are implemented and tested. The
project is not yet validated: that requires 3–5 real searches in Hermes,
including later feedback use and a side-by-side comparison with ordinary Hermes.

Repository: <https://github.com/teranchristian/family-scout>

## What Phase 1 does

- Interprets today, tomorrow, weekend and named-date requests in the activity
  location's timezone.
- Searches the live web, reads current source pages and obtains a dated forecast
  using the tools already available to Hermes.
- Reuses stable official/calendar/address/coordinate pointers only after a place
  independently appears in fresh discovery; cached pointers never prove current
  status.
- Lets a radius-aware broad search cover plausible adjacent areas inside the
  existing query budget without moving the named geographic anchor.
- Applies strict date, radius, group cost, indoor, age, closure and mandatory
  booking checks without silently treating unknown facts as matches.
- Checks exact venue/branch identity and resolves current closure or relocation
  signals before investing in detailed research or calling a venue open.
- Checks current official notices for requested-date closures, maintenance and
  unavailable promoted sub-facilities instead of relying on weekly hours alone.
- Opens and validates every factual, booking and navigation link that will be
  shown to the user, omitting broken, soft-404 and wrong-target URLs.
- For broad searches, targets four or five decision-ready ranked options, fewer
  when evidence is weak, and at most two clearly labelled **Needs checking**
  leads.
- Gives each option concrete activity details, requested-date hours, age fit,
  family cost, booking status, weather fit and direct factual/map links.
- For multi-day or weather-sensitive requests, recommends a plan for each day
  with a realistic backup.
- Saves the exact displayed options with stable activity/session identities.
- Remembers explicit feedback across fresh conversations, including corrections
  and retractions, and can use it for “more like this”.
- Supports explicit home/travel context, profile corrections and custom source
  add, enable, disable and removal.

Hermes owns natural-language interpretation, live discovery, page reading,
evidence selection and qualitative ranking. A standard-library Python helper
owns validation, straight-line distance, stable references and safe persistence.
It is not a separate search application.

Phase 1 deliberately excludes databases, background scraping, provider
frameworks, routing, booking integrations, web UI, accounts, machine learning
and numerical match scores.

The installed skill uses progressive disclosure so its entry point stays small:
`SKILL.md` routes recommendation work to separate discovery and briefing
references, discovery loads focused runtime-tool and venue-status notes, and
feedback/profile work uses a memory reference. Hermes loads only the modules
required for the current task instead of one increasingly large instruction
file.

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

Running `install.sh` over a Phase 0 installation safely upgrades the ownership
record and copies the Phase 1 reference files. Existing private files are never
overwritten, parsed or repaired by the installer. New data directories use mode
`0700`, and new state files use `0600`; existing permissions are unchanged.

## Private state

| Location | Purpose |
| --- | --- |
| `hermes-skill/SKILL.md` | Thin task router and shared boundaries |
| `hermes-skill/references/` | Focused discovery, briefing, runtime, memory and helper contracts |
| `scripts/family_scout.py` | Deterministic validation and persistence helper |
| `<hermes-home>/skills/family-scout/` | Installed copy of the skill instruction tree |
| `<hermes-home>/skills/family-scout/installation.json` | Owned-file hashes plus repository and private-state paths |
| `~/.local/share/family-scout/profile.yaml` | Private origin, group, preferences, constraints and travel context |
| `~/.local/share/family-scout/sources.yaml` | Private custom source list |
| `~/.local/share/family-scout/shortlists.jsonl` | Append-only exact shortlist history |
| `~/.local/share/family-scout/feedback.jsonl` | Append-only explicit feedback and corrections |
| `~/.local/share/family-scout/places.jsonl` | Mutable stable-place verification pointers; never current opening/event truth |

The `.yaml` documents use indented JSON, which is valid YAML and can be handled
without an added YAML package. Exact blank files created by Phase 0 are accepted
and migrated on their first helper write. A nonblank file manually converted to
another YAML style is preserved but rejected with an explanatory error; convert
it to JSON-compatible YAML deliberately rather than allowing an automatic rewrite.

The templates contain no people, precise locations or credentials. Never commit
private runtime state. The helper's `status` command is redacted; its `context`
command intentionally returns private context to Hermes and must not be copied
into web queries, logs or public reports.

## Try Phase 1 in Hermes

After updating the installed copy, start a fresh Hermes conversation. For a
privacy-safe smoke cycle, choose an arbitrary public test origin and replace the
bracketed values below:

> Load Family Scout. Using [public test location] as an explicit origin, find
> free activities on [absolute future date] within [radius] km. Do not use or
> save any private profile details. Show your interpreted place, date, attending
> group and cost basis before searching.

Check that Hermes:

1. Reads live pages rather than relying only on snippets.
2. Searches multiple relevant source classes in the local language when useful.
3. Uses the right dated forecast or explicitly reports it unavailable.
4. Rejects or labels unknown hard facts instead of assuming they pass.
5. Gives decision-ready option details with direct factual and map links that
   were opened or reachability-checked during the current search.
6. Makes its ranking agree with the weather and attending ages.
7. Saves the exact shortlist before presenting it.

Then refer to an option by number and give explicit feedback. In a new
conversation, ask for another search and confirm Hermes loads that feedback only
as a preference signal—not as permission to weaken current constraints. Also run
one search at a second explicit public location.

For at least two searches, ask ordinary Hermes the same question without Family
Scout. Compare evidence correctness, practical usefulness, latency and whether
the persistent context materially improves the later result. Record failures as
well as wins in `VERIFICATION.md` or the project plan.

Phase 1 becomes **validated** only after:

- 3–5 real Family Scout searches;
- explicit feedback followed by a later fresh-conversation recommendation;
- one second-location practical search; and
- at least two side-by-side comparisons with ordinary Hermes.

Until all four are observed, keep the label **built; trial pending**. The reader
path used during Phase 0 (`curl` through `r.jina.ai`) is an explicit reliability
risk to observe during this trial, not a reason to pre-build a provider system.

## Helper and development checks

Hermes should follow the documented interface in
`hermes-skill/references/cli.md`. For a redacted manual check:

```sh
python3 scripts/family_scout.py --data-dir /absolute/private/directory status
```

Run the deterministic repository checks with:

```sh
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/setup.py scripts/family_scout.py tests/test_phase1.py tests/test_place_cache.py
python3 /root/.codex/skills/.system/skill-creator/scripts/quick_validate.py hermes-skill
```

See `VERIFICATION.md` for recorded outcomes and the remaining live trial.

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
uninstall is harmless. There is intentionally no purge command; reconsider that
only in Phase 1.5 if the trial reveals real setup or removal friction.

Hermes references: [skill discovery and management](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)
and [profiles and configuration](https://hermes-agent.nousresearch.com/docs/reference/faq).
