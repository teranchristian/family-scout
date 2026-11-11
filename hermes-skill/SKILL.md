---
name: family-scout
description: Find fresh, age-appropriate activities near the family, with dates, links and weather.
---

# Family Scout

Find useful outings for the people and dates the user requests. Keep the process small: **read the saved family context, search local and nearby events, check each day's weather, then recommend**.

## Start every request

1. Read `installation.json` beside this skill. Follow [references/profile.md](references/profile.md) to load the private profile and location-matched source URLs via `discovery_context.py`; do not inspect helper source.
2. Resolve the user's requested dates in the activity location's timezone. Explicit location, dates, attendees, radius and budget override saved defaults. For "my kids", use the children in the profile and their ages **on each activity date**; do not silently target adults or generic "all ages" events. If the date is unspecified, use the next seven days for an event search and say so; a request for timeless ideas can remain undated.
3. Identify the anchor suburb and **nearby suburbs within the user's geographic preferences/radius**. Prefer local gems over equally good farther attractions. Do not hardcode a city, children or sample ages.

## Research

For a **broad activity search**, read [references/research.md](references/research.md). Start **one `delegate_task` call containing three tasks** when delegation is available (four only when `location_sources.urls` is non-empty):

- **Agent 1 — local events:** discover events in the anchor suburb/immediate surroundings.
- **Agent 2 — nearby events:** use **the same discovery instructions as Agent 1**, changing only the assigned suburbs/area. Avoid overlap.
- **Agent 3 — weather:** forecast **each requested day**, with practical indoor/outdoor advice; do not repeat event discovery.
- **Agent 4 — saved sources (conditional):** check only the URLs in `location_sources.urls` for activities on the requested dates. Do not launch if empty; see the shared verification rules in the research reference.

Pass only public areas, absolute dates, derived age bands, requested budget, activity criteria and public saved-source URLs to their assigned agent. Never send the private profile, home coordinates, names or birthdates. If a batch fails, retry once with a shorter valid payload; if delegation is unavailable, cover the three scopes directly rather than running serial subagents. A named-venue check or follow-up needs direct verification, not three agents.

Combine and deduplicate leads, confirm important facts against current official/organiser pages, then rank for actual participation by the requested children, novelty, convenience, cost and weather. **Fresh discovery comes before old shortlists or feedback**. No numeric match scores.

## Telegram-friendly answer

Start with a short weather summary for each day. Show a ranked **top five when there are five good options**, plus up to 3–5 additional worthwhile choices if found; never pad the list. Each entry includes:

**Title · day/date and time · suburb/venue · free or group price (if known) · child-by-child fit for the actual attending children from the profile · a one-sentence description · direct official/event link · Google Maps link when an exact address is evidenced.** Mention booking and meaningful uncertainties. State which child can actually participate, not just a vague age range.

For multi-day requests, suggest one best option per day and a realistic wet-weather alternative, without assuming a booking. Keep it readable and skip internal research telemetry unless asked.

## Boundaries

**Git-owned skill — read-only in Hermes.** Never edit, re-install or auto-improve this skill, repository, references or scripts via `skill_manage`, curator, background learning or subagents. Report a **proposed Git change** for deliberate review. Personal updates belong only in **private Family Scout state commands** when explicitly requested.

Never invent a fact, event, age restriction, price, booking slot, URL or weather forecast. A venue being open does not prove that a particular activity is running. Google Maps is navigation evidence only, not opening-status evidence. If a hard requirement is unverified, say so rather than labelling it confirmed. Research does not require saving or a finalizer.
