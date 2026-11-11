# Family Scout contributor instructions

## Scope

Family Scout is a small Git-managed Hermes skill. Keep one straightforward workflow: load private family context, search local and nearby events with **the same discovery instructions**, check **daily weather**, then respond with age-specific recommendations. Avoid reintroducing complicated dated-vs-undated routing, renderer requirements, quota enforcement or numerical scoring. Do not add databases, providers, background jobs, scraper frameworks, booking integrations, new memory systems or dependencies without a demonstrated need.

The installed runtime skill has **exactly three Markdown files**: `SKILL.md`, `references/profile.md`, `references/research.md`. Older Python helpers and private state files stay intact; modifying/removing Python functionality is a separate deliberate change.

## Git ownership and privacy

Hermes runtime is a **consumer**, not a maintainer. Never auto-edit the repo, source directory, installed skill, setup or tests via `skill_manage`, background learning, curator or subagents. Report a proposed Git change for reviewed development work. `./install.sh` owns the installed files, checks their hashes, removes safely identified stale owned files and attempts `hermes curator lock family-scout`. Never edit global Hermes config just to run this skill.

The real user's home address, exact private coordinates, names, birthdates and preferences must not be committed as examples or sent to web searches/subagents. Use only synthetic fixtures in tests. The private `data_dir` remains outside Git. Preserve malformed state byte-for-byte; never repair, truncate, migrate or replace it without explicit consent. Use `discovery_context.py` to avoid reading history before fresh discovery. Birthdate-derived ages on the **activity date** override saved static ages.

## Behavior to preserve

- An explicit date, location, group, radius or budget overrides saved defaults. "My kids" focuses on the profile's children's age and *what each can actually do*.
- Two identical local-event discovery roles work on different public geographic areas. A third role researches weather by day **only**. When private `sources.yml` has URLs for the requested suburb, an optional fourth role researches those public calendars. Launch all applicable roles in one delegation batch; otherwise perform direct searches, not serial subagents.
- Search general council calendars, library programs, community events and interesting paid activities without a default free-only, budget or booking exclusion. Only enforce price/booking constraints explicitly requested by the user. Check every requested date equally, not just weekends.
- Verify current official sources for date/time, venue, actual activity, child fit, price, mandatory booking and closure. Snippets and navigation maps are not proof. Link targets must be relevant and working. Don't invent dates, prices, map coordinates, forecast, availability or numerical scores.
- Preserve a useful venue when a promoted feature is unavailable but another worthwhile activity is confirmed. Unknown hard constraints are **Needs checking**, not confirmed matches.
- Fresh discovery comes before history. Optional location sources are extra leads, not a substitute for discovery. Saving, finalizers, renderers and source files from the old ten-file workflow are not prerequisites for a good recommendation.
- Rank local-first and output up to five worthwhile activities **per requested day** (no global top-five cap), plus a clearly marked **Needs checking** group for promising unverified leads. Highlight a best pick and indoor weather backup per day when useful; never fabricate options to fill a day.

## Verification

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts tests
git diff --check
```

Test install, repeat install, upgrade/removal of old owned references, local edit refusal, uninstall and preservation of private data. A real Hermes smoke test is still required to verify live delegation and page reading.
