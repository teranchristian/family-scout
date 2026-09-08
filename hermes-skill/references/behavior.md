# Recommendation and evidence contract

Read this reference when producing or refining a shortlist. The CLI reference
owns persistence and deterministic calculations.

## Dates and request context

- Resolve dates in the activity location's IANA timezone. Show the absolute
  interpretation before the options.
- On weekdays, “this weekend” is the upcoming Saturday and Sunday. On Saturday
  or Sunday, it is the usable remainder of the current weekend.
- A named weekday means its next occurrence, including today when a usable time
  window remains.
- Check the event year, correct recurrence/session, opening window, last entry
  and booking conditions. Exclude prior editions and sessions that have ended.
  Do not assume late entry is allowed.
- An explicit request location affects only that request. Persist travel only
  when an interval is supplied; resolve its expiry to the end of the stated local
  day. Expired travel is ignored. Explicit “home” always means saved home.
- Weather-driven wording such as “indoors today” is not a lasting preference.

## Discovery and source use

General search remains available when custom sources are empty. Useful source
classes include official venue/organizer pages, government and tourism calendars,
libraries, museums, parks, event platforms and credible community sources.

Use discovery pages for leads. Prefer the current organizer or venue page for
event facts and the booking page for availability. A fresh search result does
not prove an event is current. Re-read source pages for each new search or a
follow-up asking whether an outing remains available.

Within the overall budget, consult up to two enabled custom sources relevant to
the place or request. Prioritize an explicitly requested or newly added source,
then geographic relevance. Do not deliberately query or cite a disabled/removed
source; ignore it when general search returns it. Record which sources were
consulted and explain a material omission or failed fetch.

Use only the location and suitability facts necessary for external searches.
Do not send names, precise home coordinates or a full profile. A public source
URL may be sent through an existing reader. One failed source must not fail the
whole search, and it never authorizes installing a new browser or provider.

## Hard requirements and evidence

Classify each applicable hard requirement separately:

- **Confirmed match:** current evidence establishes compliance.
- **Confirmed failure:** evidence establishes failure; exclude it.
- **Unverified:** evidence cannot establish the fact; do not present it as compliant.

Hard requirements include requested date/window, radius, free/budget/indoor
limits, participation ages, confirmed closure/cancellation and required booking
availability when relevant. Optional facilities and subjective fit may remain
unknown without exclusion.

- Unknown price does not pass “free only”. Include mandatory adult, child,
  activity and booking fees for the attending group. Optional extras are separate.
- A numeric budget defaults to total admission/activity cost for the attending
  group in the destination currency when unambiguous. Echo currency and basis.
  Ask when party size, age pricing or a currency symbol prevents verification.
  Transport, meals and parking are excluded unless requested.
- Use evidenced origin and venue coordinates with the helper's Haversine result.
  Compare the unrounded value to the inclusive radius, then display it as
  **straight-line distance**. Unknown or ambiguous coordinates do not pass.
  Do not infer walking/driving time from distance.
- “No age limit found” is not verified eligibility for a restricted activity.
  When a cutoff matters, a broad age band may be insufficient. A session that
  excludes one attending child is not suitable for the whole attending group.
- If booking is mandatory but availability cannot be read, say so and keep it
  unverified. Never state or imply that a booking was made.
- A venue, an activity/event and a dated session are distinct. Combine source
  evidence for the same occurrence; retain different sessions at one venue.

Normally return three confirmed options. Return fewer when evidence is
insufficient, and use four or five only when the extra choices are genuinely
useful. Never exceed five. Add no more than two promising leads under **Needs
checking**, each with the exact missing hard requirement. Never relax constraints
silently.

## Ranking and weather

Apply hard requirements first. Among confirmed matches, order by:

1. Suitability for each attending child and current request.
2. Evidence-backed interests and explicit feedback.
3. Practical effort.
4. Weather fit.
5. Variety, special timing and sensible revisits.

Use reasons, no scores. With no feedback, use only explicit profile facts. A
requested revisit can outrank novelty. Weather cannot override closure or an
indoor-only constraint.

Retrieve an appropriate forecast and record the public source and retrieval
time, rain, temperature, wind and alerts when available. Rain can favor indoor
options without excluding every outdoor option. A missing or far-future forecast
stays unknown; do not substitute climate, current conditions or expired data.

## Feedback and similarity

Persist only explicit feedback. Support all listed states. Separate activity
features from visit context. Do not generalize one crowded visit. Explicit and
repeated feedback outweigh tentative feedback. Corrections supersede prior
events. The current request wins. “More like this” uses evidenced selected
features and does not itself persist a preference.

## Response contract

Start with place, absolute date/window and constraints. Use numbered options and
no scores. For each option include name and time, straight-line distance,
mandatory cost and basis, indoor/outdoor status, why it fits, booking caveat and
a current source. A **Needs checking** section is optional. End with a short
weather/logistics note and one to three practical items when useful. Distinguish
sourced requirements from common-sense advice. Do not assert food, shelter,
accessibility, parking or crowd facts without evidence. Expand details only after
the user selects an option.
