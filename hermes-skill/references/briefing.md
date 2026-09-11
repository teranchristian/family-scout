# Ranking and decision-ready briefing

Read this file before ranking or presenting outing recommendations. Discovery owns
research/confirmation; the CLI owns persistence.

## Rank current evidence first

Apply hard requirements before qualitative ordering. Create the **initial ranking
without prior shortlist history or learned feedback**. Among confirmed matches,
rank using only current-request evidence:

1. suitability for every attending child and the current request;
2. practical effort, straight-line distance, usable hours and booking friction;
3. weather fit;
4. specialness, exact-date timing and how worthwhile the experience is.

Use reasons, never numerical scores. A genuinely useful exact-date activity that
matches the children's ages/time window should receive meaningful weight over a
generic everyday venue when the practical trade-offs remain reasonable.

Only after this current-evidence ranking exists may recommendation history and
explicit learned feedback be loaded. History is a **final adjustment**, not an
input to discovery or the initial ranking. Use it to:

- avoid unnecessary repetition of recently recommended venues/experiences;
- improve final shortlist diversity when current options are otherwise close;
- apply explicit learned preferences or dislikes;
- honor an explicit user request to revisit or avoid something.

Do not insert a candidate merely because it exists in history. Do not suppress a
clearly superior current option merely because it is familiar. If history changes
the order, keep the current-evidence candidate pool and make only the smallest
useful adjustment.

For a normal broad search, first show a lightweight menu aiming for **6–8 varied
possibilities**. Do not turn those choices into an itinerary. After the user
selects, deeply verify at most three options; return fewer when evidence is
insufficient. Add at most two selected leads under **Needs checking**, each
naming the exact missing hard requirement.

### Preserve useful variety

Before history is consulted, avoid a current shortlist dominated by one easy
venue class when reasonably useful verified alternatives exist. Assign each
candidate a primary experience such as children's free play, museum/science,
animals, immersive/unusual attraction, workshop/class, commercial indoor play,
library/culture or outdoor exploration.

For broad requests, normally no more than half the confirmed shortlist should
share essentially the same primary experience when a useful verified alternative
from another searched class exists. Repetition is allowed when explicit
constraints make it genuinely useful; never invent variety.

After the initial ranking, history may further demote recently repeated venues
when similarly strong fresh alternatives exist. This is the only stage where past
recommendation repetition affects ordering.

Weather can reorder the broadly discovered verified pool. It should not excuse
skipping plausible categories unless the user explicitly imposed a hard weather
constraint.

Unavailable or unverified features cannot improve rank. If a venue's strongest
advertised attraction is not running, rerank using only activities actually
available. An unavailable optional feature does not automatically disqualify the
venue when it still has **at least one concrete activity confirmed available**
and that remaining experience is worthwhile.

## Make the two stages useful

Start with interpreted place, absolute date/window, attending age context and any
important weather/cost basis. The first answer is a concise numbered choice menu.
It must distinguish known facts from details that will be verified after selection.
Do not announce a recommended daily flow before the user chooses.

For every selected, deeply verified option include:

- **What it is:** concrete activities/facilities/program content the family can
  actually use on the requested date.
- **Activity availability:** separate everyday facilities, scheduled activities,
  sub-facilities and interactions. State unavailable/unknown features as caveats.
  When a closed feature has a verified next date, show it (for example,
  **Planetarium unavailable today — reopens 12 Sep**).
- **Fit by child:** a separate line for each attending child tied to named
  available activities and meaningful limitations. Never replace this with only
  “both children fit”.
- **When:** requested-date hours/session time and last entry when relevant.
- **Cost:** mandatory breakdown and total for the attending group, or the exact
  unresolved fact under Needs checking.
- **Booking:** walk-in/booking status and verified availability when mandatory.
- **Weather/setting:** indoor, outdoor or mixed with practical implication.
- **Getting there:** straight-line distance. Route time only when the **exact
  origin, exact venue**, mode and current route/access source support it.
- **Links:** direct current factual/official page, booking link when applicable,
  and a map link generated from the exact accountable address when available.
  Only show links recorded in `link_checks`.
- **Why it ranks here:** concise current-evidence reason plus any material caveat.

Keep cards scannable. Distinguish dated events from ordinary opening-day
activities.

The renderer card uses a URL-free `body`, evidenced `activities`, and
`family_fit`. The deterministic renderer owns **What you can actually do** and
**Fit for each attending family member**; do not duplicate or contradict those
sections outside its block.

For multi-day requests, create a **recommended plan for each day** only after the
user chooses or explicitly asks Family Scout to choose. For weather-sensitive
plans, pair the main choice with a realistic backup.

## Final quality gate

Before saving and answering, check:

- Did broad discovery cover genuinely different experience classes, including a
  general-attractions/experiences sweep rather than only child-focused searches?
- Was every candidate in the initial ranking discovered independently of history?
- Was the **initial ranking based only on current evidence** before history or
  learned feedback was exposed?
- Was history used only as a final repetition/diversity/preference adjustment?
- Did weather reorder verified choices rather than narrow discovery too early?
- Did every likely finalist receive exact-date/time enrichment for calendars,
  programs, notices and each important **promoted sub-facility**?
- Does every confirmed option have at least one concrete requested-date activity?
- Are scheduled activities supported for the exact requested date/time?
- Were all relevant requested-date activities found on a finalist's calendar
  captured rather than stopping at the first one?
- Were unavailable/unknown advertised features removed from positive selling
  points and the ranking reconsidered?
- Does each child have a separate fit explanation tied to available activities?
- Are requested-date hours, total group cost, eligibility, closure and mandatory
  booking verified where applicable?
- Does each venue's **current name, address and host** match its evidence/map?
- Is every route-time claim sourced for exact origin/venue/mode?
- Did **every user-facing link** pass current exact-target validation?
- Could the user choose and leave without another clarification?

If a material answer is no and bounded research remains, continue verification.
If the deep budget is exhausted, return only verified work and state the remaining
gap plainly. Never falsify telemetry, invent variety or promote an unverified lead.

Call `shortlist-save` with the exact numbered options, evidence snapshot and
successful `link_checks` before display. Reuse its operation ID after an uncertain
retry and do not alter links after save.
