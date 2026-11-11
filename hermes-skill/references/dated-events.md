# Dated family events — one-pass, local-first shortlist

This self-contained route is for an explicit day, date range, or "this/next
weekend". Undated general outings use `recommendation.md` instead.

## 1. Resolve the request once

Read `installation.json`, run `discovery_context.py` once, and retain its
exact `run_started_at`. Resolve relative dates in the **activity location's IANA timezone**.
Use the user's **explicit location and radius** first; otherwise use the
saved **home/travel** profile. Always resolve the real date window and
resolved anchor at runtime: **never assume a particular country, city, suburb**
or a date from an example. Use `ages-on --date YYYY-MM-DD` for each relevant
activity date when birthdates are saved. Pass derived age bands to web tools,
never private birthdates, home coordinates or a full family profile.

## 2. Find useful candidates (local-first and bounded)

Search fresh sources, locally first:

- **Priority 1:** named locality, local council, library, community events.
- **Priority 2:** neighbouring suburbs/councils inside the requested scope.
- **Priority 3:** unusual wider experiences only when genuinely worthwhile.

A broad request for activities on a date is **not events-only** unless the user
explicitly says so. Discover both exact-date sessions and dependable everyday
experiences. Aim for **6–8 plausible distinct leads across at least four useful
experience classes when available** before ranking: local one-off events,
library/community play, hands-on classes, museums/culture, nature/animals,
and a general attractions/experiences sweep **not framed only around children**.
These are coverage goals, not result quotas: search relevant alternatives when
a class is unsuitable; never invent leads or extend the user's hard radius.
Count a class as searched only when a relevant query or source was actually
inspected, not because a snippet mentioned it. Include general local experiences
such as age-appropriate **cinema screenings**, shows, planetariums and unusual
interactive attractions when useful. They are **examples, never required picks**:
confirm actual date/time, price and age fit before promotion; do not pad the list
with unsuitable films or performances.

Cover the requested dates **day by day**. Inspect the official
**general events calendars AND library/event-program calendars** as separate
discovery sources where available, alongside current organiser/booking pages. Do not
assume a council's general calendar includes its library sessions or small
community events. Prefer events with **active participation** for each child,
rather than merely allowing children inside. Everyday venues remain useful
alternatives when no exceptional dated events are evidenced.

**For broad weekend/event searches, start with bounded direct research.**
Only use optional delegation when the user explicitly requests thorough
regional coverage or important nearby sources cannot be covered within a
normal search. If delegation is warranted, read [parallel-research.md](parallel-research.md)
and call `delegate_task` **once with three tasks in one batch**.
Use distinct geographic scopes, share one research budget and reserve calls
for verification and finalization. **Do not add more by default.**
Do not launch subagents for a narrow venue check or a selected follow-up.
If delegation is unavailable, continue with bounded direct research.
Do not let coordination overhead prevent delivering the shortlist.

For this dated route use the existing `effort_mode: "deep"` ceiling: **six searches and twenty-four external calls total**, including
searches, page reads, forecast and geocoding (also delegated calls).
These are ceilings, not targets. Keep at most **ten retained candidates** in the finalizer's ledger, and verify **up to five** best candidates.

**Finish discovery before choosing or saving:** if delegation was used, wait
for its results (or explicit failures). Complete planned direct research within
the remaining budget, merge and deduplicate all discovered leads, and rank the
**complete fresh pool**. A strong nearby find from the last search must compete
fairly with earlier candidates. Only then choose finalists, verify and
finalize once. **Never run a residual discovery sweep after finalization** or
append an unsaved "bonus find" to the rendered shortlist. When a promising lead
cannot be verified, use **Needs checking** if supported, or report the
evidence gap; do not call it confirmed or ask the user to repair an already
known omission.

Complete planned local-calendar coverage and the broad-experience sweep before
picking finalists. **Do not stop after three good leads** or treat three verified
options as proof that discovery was complete. Stop when meaningful coverage is
achieved or the shared budget is exhausted, not to fill a quota. If coverage
was cut short, state which calendars/classes were missed; return fewer results
rather than inventing them. Distinguish total discovered leads from those
retained for validation.

Fresh discovery comes before past shortlist/feedback. Rank the **fresh pool
before loading history or feedback**: meaningful age-appropriate activity for
each child first, then practical proximity, one-off value, total cost, time and
booking friction. Prefer a worthwhile local hands-on activity to a farther,
mostly passive outing when the evidence and other constraints are comparable.
Keep useful variety: don't let passive shopping, markets or one venue class
crowd out verified interactive alternatives. Distinguish an explicit hard
**free-only** or price ceiling from a soft **free or low-cost preference**:
consider relevant affordable paid experiences within the request's constraints
rather than silently interpreting "low-cost" as "free-only". Apply prior
feedback only as a final ordering adjustment; it must not suppress fresh
discovery.

**Saved profile preferences are ranking signals, not discovery filters.**
The `profile.preferences` list, earlier likes/dislikes, past visits and familiar
venues may mildly boost or lower otherwise suitable choices only **after fresh
discovery and initial ranking**. Never exclude a cinema, workshop, attraction
or other useful class from searches, the candidate ledger, or the shortlist
solely because it is absent from, or conflicts with, previous preferences.
Keep genuinely new options visible. Only a **clear hard constraint** in the
current request or an explicitly saved lasting `profile.constraints` rule
(e.g. a strict budget, date or distance) can disqualify a candidate; do not
promote casual preference wording into an exclusion. A current user request
takes precedence over past soft preferences.

**Weather affects ranking and backups, not discovery coverage**, unless the
user explicitly requested indoor-only or another hard weather constraint.
Offer a weather-safe alternative where possible, without falsely calling a
covered outdoor venue fully indoors. Do not read or write the saved venue cache; previously seen places are
not discovery leads for a new request.

## 3. Verify each finalist, including its links

For every event, open an accountable **source URL** showing the actual requested
date and activity. Search snippets or a regular venue page alone are not proof.
Check the current venue/branch, exact session and time, eligibility and meaningful
activity for each child, mandatory group cost, closures, and indoor/outdoor fit.
A venue being open does not prove a scheduled feature is running; keep a good
venue if another concrete suitable activity is available. Unknown hard
requirements belong under **Needs checking**, never among confirmed picks.

**Booking matters even when entry is free.** Open the event/ticket page and
check whether registration or a free ticket is required. Say "no booking" only
when the official evidence supports walk-in/no-registration. If booking is
mandatory, verify a specific available slot or mark the event Needs checking.
A booking-page link alone does not establish availability. Record the checked
booking link using the `booking` purpose in `link_checks`.

Always record direct checked event/organiser URLs as factual `link_checks`.
Add the official address and stable `place` block where evidenced; the helper
generates the corresponding Google Maps link. Maps is for navigation only, not
hours or closure verification. If weather is unavailable, say so; do not invent
weekend-specific forecasts. Make indoor/outdoor implications practical.

## 4. Finalize once; never lose checked links

Use the helper's own valid, compact example instead of writing a JSON schema
from memory; do not inspect helper or validator source code:

```sh
python3 <source_dir>/scripts/finalize_briefing.py --print-template --template-mode verified
```

Fill the example with current facts. Set `shortlist.effort_mode = "deep"`,
`shortlist.result_mode = "verified"` and add at most five options.
**Do not call `evaluate` or manually fill `constraint_results`.** Saving
already checks hard date, distance, price, indoor and booking requirements;
rendering checks that each attending child is matched to an available activity.
Keep current official-page evidence and link checks: simpler input is not a
license to guess eligibility or availability. The usual
compact payload does **not** need optional duplicated
`finalist_date_enrichment` or `dated_findings` structures; the built-in
per-option checked source and available activity evidence is enough.
Do not invent `slot_verified: true`, coordinates, distances or unread sources.
A source link must be in both `source_urls` and the matching content-verified
facts `link_checks`. Keep consulted sources and candidate ledger truthful.
Run `finalize_briefing.py` with the JSON input, once. If it succeeds, paste
`numbered_options_markdown` verbatim: the renderer includes direct checked
links and Google Maps links automatically. Do not hand-compose a substitute.

If finalization fails, **do not discard the links**. The error JSON may contain
`fallback_markdown`: copy it exactly with its clear **not saved / not validated**
disclaimer. It contains only already checked sources, booking pages and maps.
It is **not** a confirmed shortlist. Report the error; do not invent extra
verification or claim the save succeeded. Correct one obvious payload mistake
only if possible within the remaining calls. Never conceal failure or repeatedly
debug schemas until the tool-call budget is exhausted.

## 5. Concise Telegram response and research summary

Show **up to five** verified picks, each with: actual date/time, activity,
cost, registration status, individual child fit, address and direct checked
event/booking/map links. Present **choices, not a fixed itinerary**.
Optionally highlight one strong choice per requested day and a weather-safe
alternative; do not stack outings
or imply the user selected them unless asked to build a plan.

Keep the research summary brief and evidence-led: **Subagents completed**
(e.g. "3/3", "2/3", or "not used" for normal direct research), **Distinct candidate events actually discovered** (or
"not tracked"), counts in **Priority 1 / 2 / 3** when tracked, calendars
**actually checked**, and material **verification gaps**. Do not invent
counts or present the helper's candidates retained for validation as the
full number of discoveries.