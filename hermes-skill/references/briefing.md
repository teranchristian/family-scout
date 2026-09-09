# Ranking and decision-ready briefing

Read this file in full before ranking or presenting outing recommendations. The
discovery reference owns research and confirmation; the CLI reference owns the
saved shortlist.

## Select and order useful options

Apply hard requirements before qualitative ordering. Among confirmed matches,
rank by:

1. suitability for every attending child and the current request;
2. evidence-backed interests and explicit feedback;
3. practical effort, usable hours and booking friction;
4. weather fit;
5. variety, special timing and sensible revisits.

Use reasons, never numerical scores. With no feedback, rely only on current
instructions and explicit profile facts. A requested revisit can outrank novelty.

For a broad search, target four or five genuinely useful confirmed options.
Return fewer when evidence is insufficient; never pad the list and never exceed
five. Add at most two promising leads under **Needs checking**, each naming the
exact missing hard requirement. A short, specific request may need fewer choices.

The ordering must agree with the explanation. If rain is a major factor, useful
verified indoor options should normally lead. Outdoor places may remain as
clearly labelled dry-window backups, but do not make an outdoor-only top list
while claiming the forecast favours indoor activities.

A feature that is unavailable or unverified on the requested date cannot improve
an option's rank. If a venue's strongest advertised attraction is not running,
rerank the venue using only the activities that are actually available.

## Make the first answer decision-ready

Do not defer essential details until the user chooses. Start with the interpreted
place, absolute date/window, radius, attending age context and cost basis. Then
give the best recommendation or plan first, followed by numbered option cards.

For every numbered option include:

- **What it is:** concrete activities, facilities or program content that the
  family can actually use on the requested date—not just “playground”, “museum”,
  “aquarium” or “children's centre”.
- **Activity availability:** distinguish everyday facilities, scheduled
  activities, sub-facilities and interactions. State unavailable or unknown
  advertised features as caveats; never mix them into the positive activity list.
- **Fit by child:** give a separate line for each attending child stating the
  available activities they can actually do, how strong the fit is, and any
  meaningful limitation. Technical admission eligibility alone is not enough.
  If ages differ, do not replace these lines with a combined “both children fit”.
- **When:** usable hours for the requested date/session, including last entry or
  session time when relevant.
- **Cost:** mandatory price breakdown and total for the attending group, or the
  precise unresolved price fact under **Needs checking**.
- **Booking:** walk-in/booking status and verified availability when mandatory.
- **Weather and setting:** indoor, outdoor or mixed, plus the practical weather
  implication.
- **Getting there:** straight-line distance. Add walking, driving or transit
  duration only when the exact origin, exact venue, mode and current route/access
  source support it. Never derive time from straight-line distance and never
  transfer access wording from a nearby venue.
- **Links:** a direct current official/factual page and a booking link when
  applicable. Add a map link only when it passed the current link check;
  otherwise give the verified address in text. Display only exact URLs recorded
  as successful in the saved option's `link_checks`.
- **Why it ranks here:** a concise evidence-backed reason based only on features
  available on the requested date, plus any material caveat or uncertainty.

Keep option cards scannable, but prefer concrete explanatory sentences over thin
labels. Distinguish dated events from venues or activities available on ordinary
opening days.

After `shortlist-save`, construct each renderer card with:

- a URL-free `body` for logistics, cost, booking, weather and ranking context;
- `activities`, one object per feature worth mentioning, with `name`, `kind`,
  requested-date `availability`, concrete `detail`, and a content-verified
  factual `source_url` from that saved option;
- `family_fit`, one entry per attending member. Participating members reference
  only activities marked available; accompanying adults may use `guardian`.

The renderer deterministically prints the **What you can actually do** and
**Fit for each attending family member** sections. Do not duplicate, contradict
or rewrite those sections outside the rendered block.

For a request spanning multiple days, finish with a recommended plan for each
day. For weather-sensitive plans, pair the main choice with a realistic backup.
Add one to three practical notes only when useful, distinguishing sourced facts
from common-sense advice.

## Final quality gate

Before saving and answering, check all of the following:

- Did discovery cover both dated events and everyday outings when the request
  was broad?
- Do the leading options actually match the forecast and family age context?
- Does every numbered option have at least one concrete activity confirmed
  available on the requested date?
- Is every promoted activity, sub-facility, interaction or scheduled program
  classified separately for requested-date availability with current evidence?
- If an advertised feature is unavailable or unknown, has it been removed from
  the positive selling points and the ranking reconsidered?
- Does every attending child have a separate fit explanation tied to named
  activities that are actually available, including material limitations?
- Does every numbered option have a current direct factual link and meaningful
  detail about what the family can do?
- Are requested-date hours, total group cost, eligibility, closure and mandatory
  booking verified wherever applicable?
- Does each venue's current name, address and host match across its official
  evidence and map link, with official closure or relocation information resolved?
- Is every walking/driving/transit claim tied to the exact origin, exact venue,
  mode and a sourced route/access estimate rather than straight-line distance?
- Did every user-facing link pass a current exact-target check after redirects,
  with no HTTP error, soft 404, failed read or wrong destination?
- Did a failed page or PDF cause an important category to be abandoned too soon?
- Are recurring attractions separated from scheduled events?
- Could the user choose and leave without first asking what each child can
  actually do there?

If any answer is no, use the remaining search budget to repair the gap. If the
budget is exhausted, return the verified work, state the material gap plainly and
offer one separate bounded deeper search. Never describe an unverified lead as a
confirmed option.

Call `shortlist-save` with the exact numbered options, evidence snapshot and
successful `link_checks` before displaying them. Reuse its operation ID after an
uncertain retry. Do not add or alter links after the save.
