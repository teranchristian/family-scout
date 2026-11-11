# Dated activities — any day, direct answer

Use this workflow whenever the user gives a date or date range: **today,
tomorrow, a named weekday, Saturday, Sunday, this weekend, next weekend or
specific dates**. Weekends are only a way to resolve dates, **not a separate
research workflow**. A narrow request about one venue needs a narrow check,
not a broad search. Undated general outings use `recommendation.md`.

## 1. Resolve the request

Read `installation.json` and run `discovery_context.py` once. Resolve the
requested **date window** in the **activity location's IANA timezone**.
Honour the user's **explicit location and radius** before the saved
**home/travel** context; never assume a particular country, city or suburb.
Use saved birthdates to derive children's ages on each activity date where
available, without sharing private names, birthdates, home coordinates or
the full profile with search tools.

Apply explicit hard constraints (for example, free-only, radius or indoor-only).
Use the family's stated priorities for location and activities. Do not ask for
details already in the request or saved context.

## 2. Discover useful options, local first

For a broad request, start with **current** local council general event calendars
and **library/event-program calendars**; also look at community centres,
parks, neighbourhood groups, workshops, swaps and other small events.
Then consider adjacent areas within the requested radius and exceptional
wider choices only if permitted. Include interesting general attractions,
not just searches labelled "kids". Check both one-off events and suitable
everyday activities.

Search the actual requested dates, not automatically Saturday and Sunday.
For short ranges, inspect each requested day; for longer ranges, search
calendars across the interval and confirm the dates of promising events.
Find enough varied, genuinely useful options for the request. There is
**no fixed candidate minimum, mandatory geographic preflight or required
three-agent delegation**. Search directly with existing Hermes tools; never
launch subagents just to satisfy a workflow.

**Fresh discovery comes before history or feedback.** Saved preferences are
gentle ranking signals afterwards, not a substitute for searching. Never
invent a candidate or claim that an incomplete search found everything.

## 3. Verify the important facts

Read an accountable current source, preferably the official council,
organiser, venue or booking page. **Search snippets alone are not proof.**
One trustworthy source is sufficient for a fact it actually establishes.

For each recommended option, check what matters to the decision:
- **Date and hours:** the specific event/session or venue, including current
  closures or cancellations; an open venue does not prove every activity runs.
- **Both children:** what each attending child can actually do, and any
  age, height or supervision restriction.
- **Cost and booking:** total family price and mandatory fees; required booking
  and a specific slot only if claiming live availability.
- **Place:** exact venue/branch and address; Google Maps link from an evidenced
  address. Keep the user's radius as a hard limit where specified.
- **Weather:** forecast for those dates when available, practical rain/heat
  cautions and an indoor alternative when useful.

If a hard requirement cannot be verified, mark the option **Needs checking**;
unknown price does not satisfy free-only. Keep a good venue when a promoted
sub-activity is unavailable but another worthwhile activity is confirmed;
mention the limitation. Never invent prices, times, bookings or URLs.

## 4. Reply directly

Return a short, practical shortlist: roughly **5–8 choices if enough good
ones exist**, otherwise fewer. For each give the date/time, location,
family price (or unknown), which children it suits, booking status,
official source and Google Maps link when supported. Explain why it is
worth considering and any important weather or availability warning.
Briefly note meaningful gaps in what was checked. Do not assume an itinerary;
let the family choose.

**Respond directly from the source evidence.** Do not call `evaluate`,
`finalize_briefing.py`, `shortlist-save` or a renderer as a prerequisite to
answering. Do not let a formatting, saving or tool error suppress useful
verified findings. Saving is optional unless expressly requested, and a
saving failure must not block the answer. When the user selects options,
use the options already shown in the same conversation; verify any remaining
details without repeating broad discovery or demanding a saved search ID.
