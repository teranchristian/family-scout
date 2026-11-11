---
name: family-scout
description: Find fresh, age-appropriate activities near the family, with dates, links and weather.
---

# Family Scout

Find age-appropriate outings: **read family context, search local and nearby events, check daily weather, recommend**.

## Start every request

1. Read `installation.json` and [references/profile.md](references/profile.md); load private context and location-matched URLs with `discovery_context.py`, without inspecting helper source.
2. Resolve dates in the activity timezone. Explicit location, attendees, radius and hard requirements override defaults. **Free-only, budget and booking are not default exclusions**; enforce only when explicitly requested. "My kids" means the profile's children, aged **on each activity date**. Without dates, use the next seven days for event searches (state that), or leave timeless ideas undated.
3. Find the anchor suburb and **nearby suburbs within the user's geographic preferences/radius**. Prefer strong local finds; never hardcode places or ages.

## Research

For broad searches read [references/research.md](references/research.md). Make **one `delegate_task` call containing three tasks** (including when `location_sources.urls` is non-empty):

- **Agent 1 — local events:** independent fresh discovery in anchor suburb/surroundings, plus matched `location_sources.urls` as **additional leads**, never exclusive or preferred sources.
- **Agent 2 — nearby events:** same discovery instructions, different nearby suburbs; avoid overlap.
- **Agent 3 — weather:** forecast each requested day; no event research.

Use three concise task strings in **one valid delegation payload**; send matched source URLs **only to Agent 1**. Pass public areas, absolute dates, derived age bands and criteria, never private profile, coordinates, names or birthdates. If delegation JSON fails, retry once using shorter, schema-valid arguments; **never split into sequential single-agent calls**. If delegation remains unavailable, search directly. Named-venue checks need direct verification.

Merge and deduplicate, verify official pages, then rank by child participation, novelty, convenience and weather, not source. Include free and paid options; unknowns go under Needs checking. **Fresh discovery comes before old shortlists or feedback**. No numeric match scores.

## Telegram-friendly answer

Start with daily weather. **Group by requested day**, any weekday or weekend day; show **up to five worthwhile activities per day** when found, not a combined top-five. Never pad results. Include promising unverified leads under **Needs checking**. Each entry includes:

**Title · day/time (or unverified) · venue/suburb · FREE / group price / price unknown · child-by-child fit · brief description · direct official/event link · Google Maps link for evidenced addresses.** Show booking required / not required / unknown and what needs checking.

Highlight a best pick and wet-weather alternative per day without hiding other good options. Keep it Telegram-friendly; skip telemetry unless asked.

## Boundaries

**Git-owned skill — read-only in Hermes.** Never auto-edit it via `skill_manage`, curator, background learning or subagents. Submit a **proposed Git change** for review. Update private state only with **private Family Scout state commands** when requested.

Never invent events, dates, eligibility, prices, booking slots, URLs or forecasts. Venue opening hours and Google Maps do not verify an event session. Label unverified requirements honestly. Research needs no saving or finalizer.
