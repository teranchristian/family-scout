# Dated family events: one-pass, local-first research

Use this route only when the request is to **find events or activities on an
explicit date, on a named day, this/next weekend, or another bounded date
window**, and the family wants practical suggestions now. Keep the general
`recommendation.md` two-stage menu for open-ended or undated "things to do"
requests and selection/follow-up workflows.

## 1. Resolve context dynamically

- Resolve `this weekend`, `next weekend`, `Saturday`, etc. into **absolute
  dates in the requested activity location's IANA timezone** at run time.
  "This weekend" on a weekend means the remaining usable portion.
- Prefer the user's **explicit location and radius**. Otherwise use the
  applicable saved **home/travel** profile from `discovery_context.py`; never
  assume a particular country, city, suburb, fixed weekday, or date. If no
  usable activity area can be established, request that missing fact.
- Resolve attending ages, free-only/budget constraints, travel limits and
  weather/indoor constraints from the request and available family context.
  When a member has a saved `date_of_birth`, use the **local `ages-on` helper
  for the actual event date** before age eligibility checks and before
  dispatching subagents; do not rely on an old numerical age. Recalculate
  for each day if the date window crosses a birthday. If no birthdate is
  saved, the numeric age remains a fallback and should be treated as
  potentially stale. Pass derived age bands, not names, birthdates or
  private coordinates, in public web/delegation queries. Do not disclose
  the full private profile or home address.
- Read `installation.json` and run `discovery_context.py` once; retain the
  exact `run_started_at` for finalization. Use actual current local date,
  not dates in examples, previous events or earlier sessions.

## 2. Geographic priorities and source coverage

Build three relative priority areas for **this request**, not a permanent
list of suburbs:

1. **Priority 1 — closest to the resolved anchor:** the named locality,
   nearby suburbs and its local council/library branches, within the
   requested radius.
2. **Priority 2 — neighbouring areas:** other local councils, libraries,
   community venues and family events in the requested region/radius.
3. **Priority 3 — wider standout experiences:** only unusual activities
   that justify longer travel and still satisfy the user's scope.

For a travel request, build these areas around the travel destination, not
the home profile. Never silently expand a hard radius. Search the official
**general events calendars AND library/event-program calendars** where
available, including small free community, seasonal and one-off activities.
Use reliable current booking/event organisers as supplements. A popular
museum or generic attraction should not automatically outrank a similarly
good local one-off event. Cover the date window **day by day**, not just the
first day. Prefer active participation by each attending child; being
allowed in a venue is not enough.

## 3. Efficient research using one parallel delegation

For a broad weekend/event search that benefits from independent regional
coverage, launch **one** `delegate_task` call with a `tasks` array containing
three children, not three sequential calls:

- **Local specialist:** Priority 1 — official council events, library
  programs, neighbourhood and community listings.
- **Neighbouring-area specialist:** Priority 2 — adjoining councils,
  libraries, galleries and special family activities.
- **Wider-area specialist:** Priority 3 — genuinely exceptional events,
  indoor backups and forecast leads.

Pass the **resolved public area, exact dates/timezone, age bands, relevant
constraints and individual work limits to every task**. Children do not
inherit parent context. Each `goal`/`context` must be concise, single-line
strings; keep each context <= ~1.5 KB and the whole JSON payload < 8 KB.
Use the exact one-call pattern and parse-failure retry rules in
`recommendation.md`. After one malformed batch, rebuild shorter and retry
the full batch once; **never serialize the three tasks as a fallback**.

Research is **bounded across the parent and all children together**:
`effort_mode: "deep"` permits **at most six searches and twenty-four
external calls total**, including page fetches, weather and geocoding.
Give agents explicit portions of this shared budget and reserve calls for
the parent's final verification. Aim for **up to ten distinct retained
candidates**, not exhaustive scraping; stop early after enough varied,
high-quality local leads. Count failures, retries and fetch batches
truthfully. Do not change Hermes configuration or install paid providers.

Use a working page reader (such as DonSeTch `web_fetch` if currently
available) rather than retrying `web_extract` when the search backend
cannot read pages. Tool interfaces vary: confirm arguments before use
rather than guessing. Batch compatible URLs when the reader supports it.
After a blocked/error page, use one credible alternative; avoid repetitive
retries and permanent source blacklists. Search snippets are leads, never
proof of exact-date availability. Child results should be **one compact
JSON object each** with candidate title, exact session date/location,
activity type, source URL, verification status, short child-fit reason,
tool counts, calendars checked and any failures. No verbose transcripts
or duplicate JSON.

If delegation is unavailable or fails twice, do bounded direct research
with the remaining budget, return any usable findings, and report the
subagent shortfall. For a narrow single-venue/date follow-up, do not
spawn three agents.

## 4. Verify, rank and render

Deduplicate event occurrences, distinguish recurring venues from exact-date
sessions, and preserve **fresh independent discovery before history or
feedback**. After forming the fresh candidate pool, cached stable-place
pointers may supplement current verification but may not prove event
dates, current opening or pricing. Consult feedback only as a final ranking
adjustment, not as a way to suppress fresh options.

Verify the most promising **up to five** candidates against current
accountable/official event or booking pages **for their exact dates**.
Check: the actual session; exact venue/branch; both children's activities
and eligibility; mandatory total family cost; booking requirements and
available slots when booking is compulsory; requested radius when hard;
current closures/cancellations; and links after redirects. Unknown hard
requirements must not be called confirmed. If fewer than five are
supportable, return fewer, without fabricated filler. Up to two plausible
but unresolved leads may appear under **Needs checking** when permitted
by the helper; label missing evidence precisely.

For a date-specific one-pass shortlist, use the existing helper:
```sh
python3 <source_dir>/scripts/finalize_briefing.py --print-template --template-mode verified
```

Set `shortlist.effort_mode = "deep"` and
`shortlist.result_mode = "verified"` (the existing helper accepts up to
five verified options in deep mode). Fill the dynamic request and the
fresh candidate ledger, with at most **ten retained candidates**.
Include date-specific event source evidence and valid `link_checks`
for every displayed factual/booking link; follow the template's
`discovery`, `shortlist` and `render` fields. Finalize once and paste
`numbered_options_markdown` **verbatim**; do not bypass failed
validation, fabricate facts or hide honest budget-overage warnings.

Rank first by suitability and active participation for each child, then
practical distance from the resolved anchor, special/one-off value,
cost, timing/booking friction and weather. A wider-area event wins only
if materially better. Keep an indoor fallback where possible. A daily
rain probability does not mean rain all day.

## 5. Practical Telegram output and research summary

Give one concise response: the **top five or fewer verified picks** with
date/time, locality, what the children can do, mandatory group cost,
booking needs and **direct checked links**. If there are valuable
alternatives, mention 2–3 briefly only with evidence and clear uncertainty.
Suggest one main activity per requested day, with an indoor/weather backup
when relevant; never invent a nap schedule or travel time.

At the end include a **brief research summary** for this event-search
route (not for ordinary chat or an undated general menu):

- Subagents completed, e.g. `2/3`, or `not used`.
- **Distinct candidate events actually discovered**, if recorded; if not
  recorded, say `not tracked`. Never present the finalizer's capped
  candidate ledger as the full discovery total.
- Counts for **Priority 1 / 2 / 3** among deduplicated discoveries, if
  tracked. If attribution is unclear, mark the breakdown unavailable,
  rather than guessing.
- Official council, library and event calendars **actually checked**,
  not merely suggested in prompts.
- Material verification gaps, blocked sites and unverified availability.

The helper's `research_coverage`/ledger counts describe only candidates
**retained for validation** (at most ten), which may be fewer than all
candidates seen in searches. Do not imply that the helper confirms
children finished or that uncited agent counts are verified. Avoid
repeating entire event descriptions in the summary.