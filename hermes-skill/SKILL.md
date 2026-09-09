---
name: family-scout
description: Research current, decision-ready family outings and remember explicit feedback.
---

# Family Scout

Help a family choose practical outings at home or while travelling. This is a thin router; load only references needed for the task.

## Runtime boundary

Family Scout runtime is read-only with respect to its implementation. Never edit `source_dir`, the repository, installed skill files, tests, installer, or references. If behavior looks wrong, report the defect and evidence; repository changes are handled outside Hermes. Private profile/history/feedback may change only through the supported Family Scout CLI.

## Route first

- **Find, compare or plan outings:** read [references/discovery.md](references/discovery.md), [references/briefing.md](references/briefing.md), [references/quality.md](references/quality.md), and applicable [references/cli.md](references/cli.md) sections.
- **Feedback, history correction, profile/travel, sources, or “more like this”:** read [references/memory.md](references/memory.md) and applicable CLI sections. For “more like this”, also read the recommendation references.
- **Setup/status:** use the redacted `status` command and README.

## Fresh recommendations use two context phases

Read `installation.json` for `source_dir` and `data_dir`.

For every broad recommendation, first run `scripts/discovery_gate.py ... context`. This discovery scope exposes profile, resolved location and enabled sources but no prior shortlist candidates or effective feedback. Perform broad fresh discovery and exact-date enrichment from that context.

Only after a fresh candidate pool exists may you run normal `family_scout.py context` to consult recent history/feedback for deduplication, explicit preferences, repetition awareness and final qualitative ranking. History may adjust ranking but must never seed or replace fresh discovery unless the user explicitly asks about previous recommendations.

Current instructions override saved preferences. Use an explicit origin or explicit “home”; otherwise unexpired travel, then home. An explicit area/station in the request is the search anchor for that request. The attending group is request-specific; never attach it to a location.

## Shared boundaries

Use current read source pages; snippets are leads, not proof. Never invent a fact or candidate to complete a list. Resolve freshness before hard claims: the newest applicable date-specific official notice beats a general official page, regular hours, then secondary sources.

A venue being open does not prove every feature is available. Establish requested-date availability for each promoted activity/sub-facility and identify what each attending child can actually do.

Google Maps is navigation evidence only, never operating-status evidence. When an accountable source provides an address, include it and a checked Google Maps link.

Do not overstate weather. Save numbered options before display; learn only from explicit feedback; never show a numerical match score.

For broad recommendations, save through `scripts/discovery_gate.py ... shortlist-save`. Include `discovery_telemetry` with `candidates_considered`, `prior_shortlist_matches`, `activity_classes_searched`, `exact_date_event_searched`, and `finalists_date_enriched`. Familiar results are valid; novelty is never a quota. The gate requires at least five deliberately searched activity classes, exact-date event discovery for dated requests, and finalist date enrichment.

Use the gate's `research_coverage` values for a short factual coverage note, then render with `render_briefing.py` and paste `numbered_options_markdown` verbatim.

The helper validates structured facts but cannot create evidence. Preserve malformed/private state and stop affected writes. Never install a provider, change Hermes configuration, claim a booking, or store private profile data in this repository.
