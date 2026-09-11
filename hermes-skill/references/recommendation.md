# Fast two-stage recommendation workflow

This is the complete runtime contract for normal Family Scout use. Do not open
any other reference, helper source, validator source or unowned file in the
installed skill directory—even after a tool failure or validation error. A
normal broad request starts with choices; it does not prematurely build a day
plan.

## 1. Interpret once and start the run

Read `installation.json`, then run `discovery_context.py` once. Copy its exact
`run_started_at` into the finalization payload. Resolve the public search anchor,
absolute date/window, timezone, attending ages, radius and hard cost/indoor
requirements. Do not send names, private coordinates or the full profile to web
tools.

Weather helps describe and compare the menu. It must not narrow discovery unless
indoor or outdoor is an explicit hard requirement.

## 2. Broad request: show an initial menu

For “what can we do?”, “find activities” and any other broad request without
selected venues, return an **initial menu**, not an itinerary and not a list of
only two or three winners. Aim for **6–8 plausible options** spanning at least
four genuinely different experience classes. If fewer plausible options exist,
show fewer and say so; never invent or duplicate choices. The validated menu
requires at least four distinct options. If even four cannot be supported, report
the discovery shortfall without pretending that a three-option plan is a menu.

Use at most **three search queries** total:

1. one broad, local-language family activity sweep;
2. one broad general attractions/experiences sweep that is not restricted to
   child-focused wording; and
3. for a dated request, one exact-date events/calendar sweep.

These are total searches, not “discovery searches.” Do not add separate weather,
booking or geocoding searches. Use a forecast tool for weather and directly read
already-known official, calendar or booking URLs.

Use generic classes such as events, play/community spaces, learning/culture,
animals/nature, commercial attractions, hands-on experiences and outdoor
options. Standing searches must remain category-based and must not name a niche
activity or venue. When nearby municipalities could fall inside the requested
radius, the exact-date events/calendar sweep must include them in the same
query; the named place or station remains the anchor.

Before detailed reading, keep a working ledger of the exact plausible candidates
you intend to show. Each ledger entry needs its title, primary class,
`fresh`/`cache` origin and `shown` disposition. Do not stop after finding three
acceptable venues. Do not type a candidate count later: the finalizer derives it
from this ledger.

History and explicit feedback may adjust the final order only after the fresh
candidate ledger exists. They may not remove otherwise useful menu choices or
replace fresh discovery.

Search results and aggregators are leads. For every displayed candidate, read at
least one accountable page that establishes it as a real relevant possibility.
Do not claim exact-date opening, price, distance, eligibility, activity schedule
or booking availability unless that fact was actually checked. Put unresolved
facts in `needs_verification` instead.

After the fresh searches, always query for one recent cached lead:

```sh
python3 <source_dir>/scripts/family_scout.py --data-dir <data_dir> \
  place-cache-leads --area "<public area>" --limit 1
```

Set `cache_lookup_performed: true` after the command succeeds, even when it
returns no lead. The cache may contribute at most one displayed option and never proves current
facts. For a fresh candidate, one batch `place-cache-lookup` may supply stable
verification pointers. Do not open `places.jsonl` directly.

Do not geocode every initial option. When an accountable source provides the
exact address, include it in the stable `place` block. The helper automatically
creates the Google Maps search link locally, so this costs no external call and
does not use Maps as operating-status evidence.

Get the initial-menu payload without opening another reference:

```sh
python3 <source_dir>/scripts/finalize_briefing.py \
  --print-template --template-mode explore
```

Use `result_mode: "explore"`. Keep cards short: what it is, why it could suit the
family, useful facts already known, and what still needs verification. Finalize
once, paste `numbered_options_markdown` verbatim, and let the user reply with one
or more option numbers.

The saved option is the single source of truth for `known` and
`needs_verification`; do not repeat `needs_verification` in the render card.
Before finalizing, remove any item that the current run already established.
Correct the structured fields directly—never put drafting notes, self-corrections
or explanations about an outdated line/field into user-facing `body` or
`highlights`.

## 3. Selection: verify only what the user chose

When the user chooses one to three numbers, resolve them from the saved menu and
deeply verify only those choices. Do not restart broad discovery merely to replace
a selected option unless it clearly fails a hard requirement.

For each selected place:

- establish the exact current venue/branch and address from an official or
  accountable source;
- check requested-date opening, temporary closures and relevant programs;
- verify concrete activities, family eligibility, mandatory group cost and
  indoor/outdoor status;
- if booking is mandatory, confirm an actual requested-date slot and set
  `slot_verified: true`; a booking page or phone number alone is not availability;
- geocode the exact venue/address once when radius must be proven; never retry,
  substitute a nearby landmark or invent distance;
- include a notable unavailable optional feature only when the venue remains
  useful for another verified activity; state its next verified availability
  when known;
- record every factual/booking link that was read. A stable place address
  automatically produces its Google Maps link.

Unknown hard requirements belong under **Needs checking**. A confirmed option
must have at least one concrete activity available on the requested date.

Get the selected-option payload with:

```sh
python3 <source_dir>/scripts/finalize_briefing.py \
  --print-template --template-mode verified
```

Use `result_mode: "verified"`. Return at most the selected three options. Build
an itinerary only when the user asks for one or after their choices are known.

## 4. Honest budgets and failures

Normal effort allows at most **three searches and twelve external calls total**,
including search, page reads, forecast and geocoding. Failed calls count. A page
failure gets at most one alternate accountable source. A failed geocode gets no
retry.

Keep actual counts while working. Never reduce, reset, estimate downward or
rewrite telemetry to satisfy validation. The finalizer accepts truthful overages,
saves them as `budget_status: "exceeded"`, and prints a warning. When the budget
is exhausted, stop researching and label the remaining uncertainty.

If finalization fails, report its exact error. Do not open extra references,
inspect source code, alter the payload dishonestly or replace the validated output
with a freehand recommendation.

Do not display normal research telemetry unless the user asks for an audit. An
automatic budget-exceeded warning is always shown because it is material.
