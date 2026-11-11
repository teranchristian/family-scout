# Parallel weekend discovery — three specialists

Read for a **broad dated weekend search**. Do not delegate a narrow venue
check, a selected option follow-up or a routine undated menu.

## One parallel call

Build the model-first geographic preflight in [dated-events.md](dated-events.md)
**before** calling `delegate_task` (one web lookup only when needed).
Use the public search-area plan: anchor, specific local suburbs, neighbouring
councils/suburbs, and allowed wider region. Pass the same plan and the
absolute requested dates/timezone, attending age bands and cost preferences
to all three agents. Keep the user's geographic priority and hard radius.

Read `preferred_event_urls` from `discovery_context.py`. Pass those public
URLs **only to Agent 1**, and **only if** `resolved_location.origin_ref` is
`home` and no explicit location override was requested. The list is a
**preference, not an exclusive allowlist**, and its entries may have changed
since they were saved. If it is empty, Agent 1 searches the local council
general calendar, library/program calendar and community sources directly.
Never pass private birthdates, family profiles, street addresses or precise
home coordinates to agents. The home `label`, not latitude/longitude,
supplies the public suburb anchor; coordinates are used only for venue distance.

- **Agent 1 — preferred-source specialist:** check the supplied preferred
  event URLs for each requested date, including official local council
  general events and library programs where relevant. Follow event links to
  verify the exact date, not a site's generic opening hours. If a preferred
  URL is broken, inaccessible or irrelevant, report it and continue searching
  other relevant local official sources. Do not assume saved URLs have fresh
  event details.
- **Agent 2 — independent discovery specialist:** perform **fresh web
  discovery** covering the local tier first, then neighbouring council areas,
  and exceptionally worthwhile wider events within permitted scope. Search
  council calendars, libraries, organisers and unusual community activities.
  Do not limit exploration to Agent 1's URLs or reuse the previous shortlist.
  Check each requested day separately and avoid unnecessary duplicate work.
- **Agent 3 — weather and indoor-backup specialist:** check the **forecast**
  for the requested days, distinguish rain probability from storms, and look
  for useful indoor or undercover alternatives where weather may disrupt
  the outing. Report practical weather considerations; suggest new event leads
  only if supported by current sources. Do not spend the whole task repeating
  Agents 1 and 2's event research.

Call `delegate_task` **once with three tasks in one batch**, not as three
serial calls. Ask the discovery agents for several **distinct candidates**
toward **10–15 across all three agents when available**. For each candidate,
return event, venue/area, exact date/time if known, cost or unknown, child age
fit, direct source URL and uncertainties. **Search each requested day
separately.** Do not invent events to hit a quota. Weather is useful even
when it supplies no additional event candidates.

<!-- begin single-batch-example -->
```json
{
  "tasks": [
    {
      "goal": "Check home preferred event sources and nearby official calendars",
      "context": "Area plan: anchor=<public suburb/city>; local=<local suburbs>; adjacent=<neighbouring councils/suburbs>; wider=<allowed wider region>. Dates/timezone=<dates>; ages=<bands>. Preferred URLs=<home URLs only if eligible, otherwise none>. Check preferred pages, local council general events AND library programs, return dated leads, source URLs and unknowns. If URLs are missing or stale, search local official sources."
    },
    {
      "goal": "Independently discover fresh local-to-wider family events",
      "context": "Area plan: anchor=<public suburb/city>; local=<local suburbs>; adjacent=<neighbouring councils/suburbs>; wider=<allowed wider region>. Dates/timezone=<dates>; ages=<bands>. Fresh independent search of local areas first, neighbouring council events next, exceptional wider events last; check each date separately. Do not restrict to preferred URLs or previous shortlists; return new leads with source URLs and unknowns."
    },
    {
      "goal": "Check forecast, weather risk and indoor alternatives",
      "context": "Area plan: anchor=<public suburb/city>; local=<local suburbs>; adjacent=<neighbouring councils/suburbs>; wider=<allowed wider region>. Dates/timezone=<dates>; ages=<bands>. Check forecast for each date, distinguish showers from storms, and find a few well-sourced indoor/undercover backups if needed. Report weather uncertainty and practical family considerations."
    }
  ]
}
```
<!-- end single-batch-example -->

Wait for the batch if possible, deduplicate and compare **all results** before
ranking, then verify the best leads against current official or organiser
sources. If an agent fails or the tool is unavailable, search the missing
area directly where possible, report the gap and still **return a useful answer**.
Never recover by launching the three subagents separately. Do not modify
Hermes configuration or skill files to make delegation work.

Do not spend remaining tool calls on a save schema or elaborate research
telemetry. **Present the findings first**, with checked links and clearly
labelled uncertainty. Optional persistence must not block the answer.
