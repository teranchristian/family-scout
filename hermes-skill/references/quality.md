# Recommendation quality guardrails

Read this detailed file for an explicit thorough/comprehensive request. Normal
recommendations use `recommendation.md`. This supplements `discovery.md` and
`briefing.md`; when more specific, follow this file.

## 0. Preserve research integrity before optimizing the answer

A broad recommendation must satisfy the discovery coverage rules in
`discovery.md`; finding a few valid candidates is not by itself evidence that the
search is complete. Do not let a loaded reference, familiar venue type, easy
municipal source or bad-weather forecast silently redefine a broad “things to
do” request into a much narrower category search.

Tool-usage telemetry must describe what actually happened. Never reduce or edit
counts to satisfy a normal-effort validator. When gaps remain, return fewer
results or put them under Needs checking. Use bounded `deep` mode only when the
user explicitly asks for a thorough/comprehensive search, set `effort_mode`
accordingly, and save actual counts. Never persist falsified telemetry.

## 1. Resolve the newest applicable official evidence first

Do not stop at the first current-looking official page. Before asserting that a
venue, sub-facility or promoted feature is usable on the requested date, look for
an official notice, calendar, news item or programme page that is more specific
to that date.

Use this precedence for conflicting or overlapping evidence:

1. newest applicable date-specific official closure, maintenance, cancellation,
   programme-replacement or special-hours notice;
2. current dated calendar/session/programme page for the exact activity;
3. current official facility or organizer page;
4. regular weekly/seasonal hours;
5. accountable secondary source when primary evidence is unavailable.

A newer or more date-specific official notice overrides older general wording.
Do not give an outdated reason merely because the conclusion happens to be
correct. For example, if an old programme ended but a newer official notice says
the sub-facility is closed for maintenance on the requested date, report the
maintenance closure as the reason.

For date-sensitive verification, search the official site for the requested
month/date plus locally relevant terms for closure, maintenance, renovation,
cancellation, temporary hours, programme change and reopening. Apply this check
to important sub-facilities separately from the host venue.

If two official sources still conflict and specificity/recency does not resolve
the conflict, state the conflict and downgrade the claim rather than choosing the
more convenient source.

## 2. Match wording to evidence strength

Use these user-facing opening-status levels consistently:

- **Confirmed open:** a current date-specific official source affirmatively
  establishes opening or the exact dated session.
- **Scheduled to be open:** regular official hours cover the requested date and
  applicable current official closure/exception notices were checked with none
  found. Say: “Scheduled to be open based on regular hours; no applicable
  closure notice found.”
- **Opening status not established:** current evidence is incomplete, unreadable
  or conflicting. Do not include the venue as a confirmed option if opening is
  a hard requirement.

Never summarize a group of venues as “all confirmed open” when some are only
scheduled to be open from regular hours. Absence of a closure notice is not
positive date-specific confirmation.

For commercial venues that explicitly warn that temporary closures are
announced on another official channel, check that channel when possible. If it
cannot be checked within the search budget, preserve the “scheduled” wording and
name the limitation.

## 3. Preserve semantic fidelity

Do not make a source sound more specific, child-focused or feature-rich than it
is. Examples:

- “playroom” does not become “dedicated toddler playroom”;
- “children may use the facility” does not become “designed for toddlers”;
- “animal interaction available” does not prove a particular feeding or handling
  session is running;
- “storytelling is held periodically” does not prove storytelling is available
  on the requested date or during the requested time window;
- a venue age range does not prove equal activity fit for each child.

A stronger description is allowed only when a current source explicitly
supports it. If a separate toddler area, session or sub-facility exists, verify
its requested-date availability before using it as a selling point. For any
scheduled activity, verify the exact requested date and usable time window; if
that schedule was not established, mark the activity **unknown** rather than
combining it with an open host facility.

## 4. Keep a good venue when one feature is unavailable

Treat the **venue** and each **activity/sub-facility** as separate availability
questions. An unavailable planetarium, workshop, show, pool, ride, exhibition,
feeding session or other optional feature does **not** make the whole venue
unavailable.

Keep the venue in the confirmed shortlist when all of these are true:

- the host venue itself is open or scheduled to be open at the required evidence
  level;
- at least one concrete activity is confirmed available on the requested date;
- the remaining available activities still make the venue a genuinely useful
  choice for the attending children and current request.

Present the venue around what the family **can do today**. List available
activities first. Then add a concise warning for a notable unavailable feature,
including the verified reason and next availability/reopening date when the
current official evidence provides one. For example:

`⚠️ Planetarium unavailable today — closed for projector maintenance through 11 Sep; reopens 12 Sep.`

If the next availability cannot be established, say so rather than guessing:

`⚠️ Planetarium unavailable today; reopening date not established.`

Do not remove an otherwise strong venue merely because one advertised feature is
closed. Do not hide the closure either. The unavailable feature cannot improve
the venue's rank, and the venue must be reranked using only the activities that
are actually available.

Remove or demote the venue only when the unavailable feature was essential to
the request or the main reason the venue was useful and the remaining verified
activities no longer make it a good recommendation. If no concrete activity is
confirmed available, the venue cannot remain a confirmed option.

When a future reopening/session date is known and relevant, mention it as useful
planning context, but keep today's recommendation based only on today's available
activities.

## 5. Google Maps is for navigation, not status

When an accountable source provides the exact current venue address:

1. preserve that address in the saved option and include it in the rendered
   card body;
2. create a Google Maps navigation/search URL for the same venue and verified
   address, preferably:
   `https://www.google.com/maps/search/?api=1&query=<URL-encoded venue + address>`;
3. perform a current reachability check;
4. store the exact checked URL in `link_checks` with purpose `map` and result
   `reachable`;
5. show both the address and Google Maps link in the final option card.

The Google Maps query must identify the same venue and address as the official
evidence. If the address cannot be established, omit the map link rather than
guessing a branch or location.

Google Maps is navigation evidence only. Do not use its opening hours,
“temporarily closed”/“permanently closed” labels, reviews or business metadata as
the authority for Family Scout operating status when an official source is
available. Official closure/maintenance information remains authoritative.

The map link is an extra convenience; it never replaces the direct current
official/factual link.

## 6. Make access useful without inventing travel time

Keep radius filtering based on the helper's evidenced straight-line distance,
but make the final card useful for leaving the house:

- show the verified address and Google Maps link prominently when available;
- treat straight-line distance as a compact secondary fact;
- show walking, driving or transit time only when a current route/access source
  supports the exact origin, exact venue and mode;
- never turn straight-line kilometres into an estimated drive/walk time.

## 7. Keep weather claims proportional to the forecast

Distinguish:

- current conditions;
- probability of precipitation;
- expected amount/intensity;
- expected timing/duration;
- alerts.

A daily precipitation probability near 100% does not by itself mean “heavy rain
all day”. Use “rain likely”, “periods of rain”, “heavy rain expected during
parts of the day”, or similarly bounded wording unless hourly/current evidence
supports continuous heavy rain for the stated period.

Weather should change ranking and practical advice and may justify extra search
for weather-safe backups. Unless the user explicitly says indoor-only, it should
not cause broad discovery to skip museums, animals, commercial attractions,
workshops or other plausible categories merely because an easy indoor venue type
has already been found.

## 8. Remove repetition from the briefing

The rendered option card is the canonical detail block. Do not repeat the same
activity, hours, age fit or opening claim in the intro, card body and practical
notes.

For each card:

- `body` should carry only concise decision context: what the place is, opening
  status wording, hours/cost/booking/weather, verified address, getting-there
  facts and why it ranks there;
- `activities` owns the concrete “what you can do” facts, including notable
  unavailable activities when they help explain a warning or future reopening;
- `family_fit` owns child-by-child participation and limitations;
- `link_checks` owns official/booking/map URLs.

Outside the numbered block, give only information that helps choose between the
options: the top pick, a backup, or one to three practical notes. Do not restate
the full cards.

Prefer one compact message over splitting into `(1/2)` and `(2/2)` merely because
the same facts were repeated.
