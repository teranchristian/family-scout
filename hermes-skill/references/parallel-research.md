# Parallel weekend discovery — three specialists

Read for a **broad dated weekend search**. Do not delegate a narrow venue
check, a selected option follow-up or a routine undated menu.

## One parallel call

Build the model-first geographic preflight in [dated-events.md](dated-events.md)
**before** calling `delegate_task` (one web lookup only when needed). Give all three agents the same concise
public search-area plan (anchor, specific local suburbs, adjacent councils/
suburbs and permitted wider region) plus a clearly **assigned scope**. The
local specialist searches the local tier, the adjacent specialist searches
the adjacent tier, and the wider specialist searches only exceptional options
in the wider tier. Do not ask each agent to rediscover neighbouring suburbs
or delegate using only vague labels such as "nearby". User-specified tiers
take precedence over the model's suggestions; do not extend a hard radius.
Each agent finds its own official council calendars and other event sources;
do not add a separate pre-delegation council-site search.

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
      "context": "Area plan: anchor=<public suburb/city>; local=<specific local suburbs>; adjacent=<specific nearby councils/suburbs>; wider=<allowed wider region>. Assigned scope: local only. Dates/timezone=<dates>; ages=<bands>. Check council general calendar AND library programs, community venues, parks, swaps, workshops; return distinct leads with source URLs and unknowns."
    },
    {
      "goal": "Find nearby council and community events",
      "context": "Area plan: anchor=<public suburb/city>; local=<specific local suburbs>; adjacent=<specific nearby councils/suburbs>; wider=<allowed wider region>. Assigned scope: adjacent only. Dates/timezone=<dates>; ages=<bands>. Check neighbouring council calendars, libraries, galleries and community events; avoid local duplicates; return distinct leads with source URLs and unknowns."
    },
    {
      "goal": "Find exceptional wider events and weather alternatives",
      "context": "Area plan: anchor=<public suburb/city>; local=<specific local suburbs>; adjacent=<specific nearby councils/suburbs>; wider=<allowed wider region>. Assigned scope: wider exceptional options and weather only. Dates/timezone=<dates>; ages=<bands>. Search standout events, paid experiences worth travelling for, forecast and indoor backups; avoid local and adjacent duplicates; return source URLs and unknowns."
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
