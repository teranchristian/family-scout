# Parallel weekend discovery — three specialists

Read for a **broad dated weekend search**. Do not delegate a narrow venue
check, a selected option follow-up or a routine undated menu.

## One parallel call

Call `delegate_task` **once with three tasks in one batch**, not as three
serial calls. Give **every agent** the public geographic anchor and scope,
absolute dates/timezone, attending age bands, free/paid preferences and the
instruction to return direct source URLs and what remains unverified. Never
send private birthdates, full family profiles or precise home coordinates.

- **Agent 1 — local specialist:** nearest suburb/council and surrounding
  neighbourhoods. Inspect the council's actual **general events calendar**
  **and its library/program calendar** separately; seek community events,
  sustainability hubs, parks, neighbourhood groups, workshops and swaps.
  Don't stop after finding a few large advertised attractions.
- **Agent 2 — adjacent-area specialist:** neighbouring councils/suburbs,
  libraries, galleries, community organisations, small markets and seasonal
  events inside the requested scope. Avoid duplicating Agent 1.
- **Agent 3 — wider-area and weather specialist:** genuinely exceptional
  city-wide experiences, worthwhile paid options, indoor rainy-day alternatives
  and the relevant forecast. Do not dominate the result with familiar
  attractions available every day.

Ask each for several **distinct candidates**, so the combined pool aims for
**10–15 across all three agents when available**. Each lead should identify
event, venue/area, requested date and time if known, cost or unknown, age fit,
direct source URL and a short note on uncertainty. **Search each requested day
separately.** Return concise findings, not verbose transcripts or a forced
ranking. Do not invent a lead to reach the target.

<!-- begin single-batch-example -->
```json
{
  "tasks": [
    {
      "goal": "Find small local family events for the requested dates",
      "context": "Anchor: <public area>; dates/timezone: <resolved dates>; ages: <age bands>; priorities: official local council events calendar AND library programs, community venues, parks, swaps, workshops; find several distinct leads; return concise dated sources and unknowns."
    },
    {
      "goal": "Find nearby council and community events",
      "context": "Anchor: <public area>; scope: <neighbouring areas>; dates/timezone: <resolved dates>; ages: <age bands>; priorities: neighbouring council calendars, libraries, galleries and community events; avoid duplicating local leads; return concise dated sources and unknowns."
    },
    {
      "goal": "Find exceptional wider events and weather alternatives",
      "context": "Anchor: <public area>; scope: <wider area allowed by request>; dates/timezone: <resolved dates>; ages: <age bands>; priorities: special city-wide events, paid experiences worth the travel, weekend forecast and indoor backups; return concise dated sources and unknowns."
    }
  ]
}
```
<!-- end single-batch-example -->

Wait for the batch if possible, deduplicate and compare **all results** before
ranking, and verify the most promising entries against accountable current
sources. If an agent fails or the tool is unavailable, search the missing
area directly where possible, report the gap and still return a useful answer.
Never recover by launching the three subagents separately. Do not modify
Hermes configuration or skill files to make delegation work.

Do not spend remaining tool calls on a save schema or elaborate research
telemetry. **Present the findings first**, with checked links and clearly
labelled uncertainty. Optional persistence must not block the answer.
