# Dated activities — discover first, recommend directly

Use this route for a named date, date range or this/next weekend. A normal
weekend request is **one research-and-recommendation turn**, not a mandatory
multi-stage JSON/save operation. Undated general outings use
`recommendation.md`.

## 1. Resolve the request

Read `installation.json` and run `discovery_context.py` once to use saved
home/travel location, family ages, hard constraints and enabled sources. User
instructions override defaults. Resolve the **date window** using the
**activity location's IANA timezone**. Honour the user's **explicit location
and radius** before the saved **home/travel** profile; **never assume a particular
country, city, suburb** or example date. Derive ages on the activity date when
birthdates are available. Share only broad age bands, public location, dates and
search criteria with search tools or subagents; never private names, birthdates,
home coordinates or full profiles.

## 2. Find more local events before picking winners

**Priority 1 — local:** the named suburb and immediate surroundings. Inspect
official council **general event calendars**, separately inspect council
**library/event-program calendars**, and look at community centres, parks,
sustainability/environment hubs, neighbourhood groups and organisers. Look for
small one-off community events, swaps, workshops, animal events and seasonal
programs that generic family-attractions searches often miss.

**Priority 2 — adjacent:** neighbouring suburbs and councils inside the
requested geographic scope, including local libraries, galleries and community
organisations.

**Priority 3 — wider:** standout city-wide events or indoor backups only when
they offer something substantially better than local choices. A major attraction
does not win merely because it is famous.

For a **broad weekend/event search, use three parallel research specialists**
(local, adjacent and wider/weather) as described in
[parallel-research.md](parallel-research.md), with `delegate_task` **once as
one three-task batch**. If delegation is unavailable or fails, search directly
rather than losing the entire answer. Narrow venue or single-event follow-ups
do not need agents.

Aim to **discover about 10–15 distinct relevant candidates** across the
specialists, if available, **before final ranking**. This is a discovery goal,
not a required minimum and not a reason to invent events. Do not stop when
you have found five attractive options. Search **Saturday and Sunday separately**
(or each requested date), including event calendars and organiser listings.
Include unusual, educational, interactive, seasonal and free council/community
events alongside genuinely worthwhile paid options. Explore beyond events
labelled explicitly "for kids", then assess fit. An ordinary playground or
everyday attraction is a backup, not the automatic top pick.

Merge the findings and remove duplicates. If sources or an area were not
searched, say so briefly; do not claim complete coverage. **Fresh discovery
comes before history or feedback**. Saved preferences are gentle ranking signals
applied afterwards, never a reason to hide genuinely new candidates. A clear
current or saved hard constraint still applies.

## 3. Check important facts, not paperwork

Prefer the **current official council, organiser, venue or booking page** for
the particular event. One trustworthy source is sufficient for each fact it
actually establishes; do not repeatedly cross-check clear date, time or price
details just to satisfy a procedural step. An official council listing of a
third-party event is a useful lead; when it disclaims verification, check the
organiser or ticketing source for critical details. Search snippets alone are
not confirmation.

For the recommendations, check the actual event date and time, location,
age/height restrictions and **what each child can actively do**, total family
cost (including mandatory fees), closures and whether booking is required.
Check an exact ticket slot only if asserting live availability. If a significant
fact cannot be confirmed, label it **Needs checking** rather than inventing
it. A venue being open does not prove every separate program is operating;
keep a good venue if other age-appropriate activities there are confirmed.

Check the forecast for the requested dates when available. Rain changes
practicality, not whether an outdoor event is discovered: retain distinctive
outdoor options with a clear wet-weather warning and an indoor alternative.
Consider nap times, travel, accessibility and cost. If weather is not available,
say so.

## 4. Rank and present the Telegram shortlist

Rank **the full discovered pool** by active fun for the children, nearby
convenience, unusual/one-off value, cost and weather practicality. Local events
get a fair chance against polished CBD attractions. Include exceptional
age-specific activities when worthwhile; state which child benefits.

Show roughly **5–8 distinct worthwhile choices**, if they exist. For each:
event and venue, exact day/time, family cost or **price unknown**, whether
booking is required or **not confirmed**, **per-child age-specific
suitability**, area,
official source link, and a Google Maps link when an evidenced address exists.
Use short reasons and any weather warning. Clearly mark uncertain events.
Finish with a brief list of the calendars/areas checked and important gaps;
avoid long audit logs, internal schema details and false research counts.
Present choices, not an assumed fixed itinerary.

**Never discard a researched answer over a schema, fit label or save error.**
For a normal dated-event request, **do not call `evaluate`,
`finalize_briefing.py`, `shortlist-save` or the renderer as a prerequisite
to responding**. Do not build a large payload in a scratch file or patch it
repeatedly. Respond directly from the source evidence. A source check is a
claim about the page read, not a guarantee of live booking.

If the user explicitly requests **saving**, attempt the existing persistence
helper separately, but show the useful shortlist regardless and say clearly
whether saving succeeded. If they choose option numbers in the same conversation,
use the already shown options for follow-up planning; do not demand a saved
search ID. Keep family profile, feedback, and shortlist-history workflows for
their explicit purposes. Normal outing searches must not alter skill files.
