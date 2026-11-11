# Fast two-stage recommendation workflow

This is the complete runtime contract for **undated/general** Family Scout
recommendations. Do not open any other reference, helper source, validator
source or unowned file—even after tool failure—except that a **dated
event/weekend search** also reads `dated-events.md` and follows its explicit
one-pass verified-shortlist route. General broad requests start with choices,
not a premature day plan.

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
activity or venue. Adjacent areas may appear inside the same queries when they
could fit the requested radius; the named place or station remains the anchor.

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

## 4. Optional one-call parallel delegation

Undated, general Family Scout recommendations **do not need subagents**.
Use this optional pattern when the user explicitly requests multiple research
agents, when a thorough regional comparison warrants them, **or for a broad
dated event/weekend search as described in `dated-events.md`**. This changes
orchestration, not the budgets or finalization rules for the selected route.
Do not delegate a trivial question or a single page read.

When delegation is useful:

1. Split independent discovery across **(a) the named local area first,
   (b) adjacent areas inside the requested scope, and (c) standout wider-area
   options/indoor backups**. Respect any tighter user geographic priority.
   Do not let the wider-area worker crowd out good local events.
2. Call `delegate_task` **exactly once with all three tasks in its `tasks`
   array**. Do not submit three separate `delegate_task` calls: those can run
   sequentially and caused a slow previous trial.
3. Build each `goal` and `context` as a short, self-contained **single-line
   string**; avoid embedded newlines and unnecessary quotation marks. Aim for
   roughly 1.5 KB or less per task and under 8 KB for the complete payload.
   Check that the JSON parses before dispatching. Pass the public area,
   absolute dates/timezone, attending **age bands**, relevant constraints and
   individual search/page-read limits to **each** child. Children have no
   parent conversation history. Never pass names, home coordinates, full
   profile, API keys or private state.
4. Give each agent a share of the **existing total** search and external-call
   allowance, reserving capacity for parent-side verification and weather.
   Aggregate **actual** usage, including failures and retries, across children
   and parent. Three children do **not** create three fresh budgets. If usage
   is missing, report that gap; never assume the run was under budget.
5. Ask children to return one compact JSON result: a small set of candidate
   titles, exact dates/areas, experience classes, direct source URLs, what is
   known vs unverified, concise reasons and actual tool counts. Do not return
   verbose transcripts or repeat JSON. Search snippets alone are not proof;
   the parent still checks current source pages and the saved-link contract
   before displaying any claims or URLs.

One valid **illustrative JSON payload** (placeholders must be replaced by
resolved request/profile values before dispatch). The examples allocate three
searches and six page reads across all agents, leaving capacity for parent work:

<!-- begin single-batch-example -->
```json
{
  "tasks": [
    {
      "goal": "Find dated family activities in the named local area",
      "context": "Resolved public anchor: <area from request or profile>; dates: <resolved date window and timezone>; ages: <resolved age bands>; priority: local councils and libraries; budget: 1 search and up to 2 page reads; return compact JSON candidates with official URLs, verification and actual tool counts."
    },
    {
      "goal": "Find dated family activities in nearby areas",
      "context": "Resolved public anchor: <area from request or profile>; adjacent areas: <nearby places inside scope>; dates: <resolved date window and timezone>; ages: <resolved age bands>; priority: neighbouring councils and community venues; budget: 1 search and up to 2 page reads; return compact JSON candidates with official URLs, verification and actual tool counts."
    },
    {
      "goal": "Find unusual wider-area options and weather-safe backups",
      "context": "Resolved public anchor: <area from request or profile>; dates: <resolved date window and timezone>; ages: <resolved age bands>; priority: exceptional wider events and weather backups; budget: 1 search and up to 2 page reads; return compact JSON candidates with official URLs, verification and actual tool counts."
    }
  ]
}
```
<!-- end single-batch-example -->

If the batched call is rejected for a parsing error, shorten the contexts,
validate the whole `tasks` object and **retry the batch once**. If it still
fails, report the delegation failure and perform only bounded direct research
with the **remaining shared budget**. **Never recover by launching the three
subagents separately.** Do not claim that the agents ran in parallel without
evidence from the actual invocation. For gateway delivery, do not repeatedly
poll the background handle.

Use the evidence, cache and finalization rules for the **selected** workflow:
the undated two-stage flow or the dated-events one-pass flow. Do not modify
Hermes configuration or installed files to enable this pattern.

## 5. Honest budgets and failures

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
