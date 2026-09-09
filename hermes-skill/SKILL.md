---
name: family-scout
description: Research current, decision-ready family outings and remember explicit feedback.
---

# Family Scout

Help a family choose practical outings at home or while travelling. This is a thin router; load only references needed for the task.

## Route first

- **Find, compare or plan outings:** read [references/discovery.md](references/discovery.md), [references/briefing.md](references/briefing.md), [references/quality.md](references/quality.md), and applicable [references/cli.md](references/cli.md) sections.
- **Feedback, history correction, profile/travel, sources, or “more like this”:** read [references/memory.md](references/memory.md) and applicable CLI sections. For “more like this”, also read the recommendation references.
- **Setup/status:** use the redacted `status` command and README.

## Recommendation context order

Read `installation.json` for `source_dir` and `data_dir`. For a new broad recommendation, first run:

```sh
python3 <source_dir>/scripts/discovery_context.py --data-dir <data_dir>
```

Keep that output private. It excludes prior shortlists and feedback. Using only the current request, profile, resolved location and enabled sources, perform **fresh discovery first**. For the current Phase 1 runtime, aim for about **6–8 plausible candidates across at least four meaningful activity classes**; this smaller target overrides larger numeric targets in older reference text. Exact-date events count as a class. Do not inspect `shortlists.jsonl`, `feedback.jsonl`, or full `context` until a fresh candidate pool exists.

After fresh discovery, normal `family_scout.py context` may be used for deduplication, repetition awareness, explicit learned feedback and final diversity/ranking. History may adjust ranking but must never seed or replace fresh discovery unless the user explicitly asks about previous recommendations.

Deep exact-date verification is for the likely **4–5 finalists**, not every discovery lead. A previously known venue may win again, but it must survive current comparison.

Current instructions override saved preferences. An explicit place/station/area is the search anchor for that request; “near me” uses active travel then home. The attending group is request-specific.

## Evidence and language boundaries

Use current read source pages; snippets are leads, not proof. **Never invent a fact** or candidate to complete a list. The newest applicable date-specific official notice beats general regular-hours information.

A **venue being open does not prove** every feature is available. Establish **requested-date availability** for promoted activities/sub-facilities and identify **what they can actually do** for each attending family member. Render payloads must contain evidenced `activities` and `family_fit`.

The response language is English. A venue/option **title** may keep its official local-language name, but all descriptive content must be translated into English: activity names, explanations, warnings, child-fit text, logistics, costs, practical notes and research summary. Do not mix Japanese or other local-language prose into the body.

Google Maps is navigation evidence only, never operating-status evidence. Include a checked Maps link when an accountable source provides the address. Do not overstate weather or show a **numerical match score**.

## One-shot finalization

Create one complete payload containing:

- `shortlist`: the normal `shortlist-save` payload;
- `render`: one renderer card per finalist, with English descriptive content;
- `discovery`: `fresh_discovery_completed`, `candidates_considered`, unique `activity_classes_searched`, `exact_date_event_searched`, and `finalist_numbers_date_enriched`.

Then run:

```sh
python3 <source_dir>/scripts/finalize_briefing.py --source-dir <source_dir> \
  --data-dir <data_dir> --input <finalize-payload.json>
```

This overrides older broad-recommendation text that calls save/render separately. The finalizer preflights both on disposable state and writes real state only if both validate.

Paste `numbered_options_markdown` **verbatim**. Paste `research_summary_markdown` once after the options/needs-checking section; never invent or recalculate its counts. A short English intro/weather/practical note may surround the rendered output.

If finalization fails, report that Family Scout could not finish verification; **never fall back to freehand numbered recommendations**.

Runtime Hermes must never edit `source_dir`, repository files, installed skill files or tests; report implementation defects instead. Never install a provider, change Hermes configuration, claim a booking, or store private profile data in this repository.
