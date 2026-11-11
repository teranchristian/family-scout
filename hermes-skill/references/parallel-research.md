# Parallel research — three-agent batch

Read for **broad weekend/event searches by default** and for explicitly
requested thorough regional comparisons. Not needed for a single venue,
a selected event follow-up, or an ordinary undated menu.

## One-call parallel delegation

Broad dated weekend/event discovery uses **three subagents** by default, each
covering a distinct region. Undated general Family Scout recommendations do
not need subagents unless the user explicitly requests them or a thorough
regional comparison warrants them. This changes orchestration, not budgets,
evidence requirements or finalization rules. More than three agents are not
automatically better; each shares the same research-call limit.

When delegation is useful:

1. Split independent discovery across **(a) the named local area first,
   (b) adjacent areas inside the requested scope, and (c) standout wider-area
   options/indoor backups**. Respect any tighter user geographic priority.
   Do not let the wider-area worker crowd out good local events. Local discovery
   should explicitly inspect both general council events and library/program
   calendars, and not stop at a few easy-to-find results. The wider-area
   worker should not spend calls duplicating the same local council pages.
2. Call `delegate_task` **exactly once with all three tasks in its `tasks`
   array**. Do not submit three separate `delegate_task` calls: those can run
   sequentially and caused a slow previous trial.
3. Build each `goal` and `context` as a short, self-contained **single-line
   string**; avoid embedded newlines and unnecessary quotation marks. Aim for
   roughly 1.5 KB or less per task and under 8 KB for the complete payload.
   Check that the JSON parses before dispatching. Pass the public area,
   absolute dates/timezone, attending **age bands**, relevant constraints and
   individual search/page-read limits to **each** child. Children have no
   parent conversation history. Never pass names, home coordinates, full
   profile, API keys or private state.
4. Give each agent a share of the **existing total** search and external-call
   allowance, reserving capacity for the parent's fresh general-attractions
   sweep, missed local coverage, final verification and weather. A suggested
   maximum allocation within the existing six-search ceiling is: **two local
   searches, one neighbouring, one wider, and up to two parent searches**.
   The parent can leave unused searches unspent. Reserve page reads within the
   same **twenty-four total external calls**; never interpret these as 24
   additional page reads after searches. Aggregate **actual** usage, including
   failures and retries, across children and parent.
   Three children do **not** create three fresh budgets. If usage is missing,
   report that gap; never assume the run was under budget.
5. Ask children to return one compact JSON result: a small set of **distinct**
   candidate titles, exact dates/areas, experience classes, direct source URLs,
   what is known vs unverified, concise reasons, calendars actually inspected
   and actual tool counts. Do not return verbose transcripts or repeat JSON.
   Agents gather leads rather than selecting the final top three. Search
   snippets alone are not proof; the parent still checks current source pages
   and the saved-link contract before displaying any claims or URLs.

One valid **illustrative JSON payload** (placeholders must be replaced by
resolved request/profile values before dispatch). The example allocates four
search calls and six page reads across the three agents, reserving up to two
searches and remaining external calls for the
parent's general-attractions sweep, coverage gaps, verification and weather:

<!-- begin single-batch-example -->
```json
{
  "tasks": [
    {
      "goal": "Find dated family activities in the named local area",
      "context": "Resolved public anchor: <area from request or profile>; dates: <resolved date window and timezone>; ages: <resolved age bands>; priority: distinct local council event and library-program calendars, plus community one-offs; budget: 2 searches and up to 2 page reads; return compact JSON candidates with official URLs, verification and actual tool counts."
    },
    {
      "goal": "Find dated family activities in nearby areas",
      "context": "Resolved public anchor: <area from request or profile>; adjacent areas: <nearby places inside scope>; dates: <resolved date window and timezone>; ages: <resolved age bands>; priority: neighbouring councils and community venues; budget: 1 search and up to 2 page reads; return compact JSON candidates with official URLs, verification and actual tool counts."
    },
    {
      "goal": "Find unusual wider-area options and weather-safe backups",
      "context": "Resolved public anchor: <area from request or profile>; dates: <resolved date window and timezone>; ages: <resolved age bands>; priority: exceptional wider events and weather backups; budget: 1 search and up to 2 page reads; return compact JSON candidates with official URLs, verification and actual tool counts."
    }
  ]
}
```
<!-- end single-batch-example -->

If the batched call is rejected for a parsing error, shorten the contexts,
validate the whole `tasks` object and **retry the batch once**. If it still
fails, report the delegation failure and perform only bounded direct research
with the **remaining shared budget**. **Never recover by launching the three
subagents separately.** Do not claim that the agents ran in parallel without
evidence from the actual invocation. For gateway delivery, do not repeatedly
poll the background handle.

Use the evidence, cache and finalization rules for the **selected** workflow:
the undated two-stage flow or the dated-events one-pass flow. Do not modify
Hermes configuration or installed files to enable this pattern.

