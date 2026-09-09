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

Keep that output private. It excludes prior shortlists and feedback. Using only the current request, profile, resolved location and enabled sources, perform **fresh discovery first**. For the current Phase 1 runtime, aim for about **6–8 plausible candidates across at least four meaningful activity classes**; this smaller runtime target overrides larger numeric discovery targets in older reference text. Exact-date events count as a class. Do not inspect `shortlists.jsonl`, `feedback.jsonl`, or full `context` until a fresh candidate pool exists.

After fresh discovery, normal `family_scout.py context` may be used for deduplication, repetition awareness, explicit learned feedback and final diversity/ranking. History may adjust ranking but must never seed or replace fresh discovery unless the user explicitly asks about previous recommendations.

Deep exact-date verification is for the likely **4–5 finalists**, not every discovery lead. A previously known venue may win again, but it must survive current comparison.

Current instructions override saved preferences. An explicit place/station/area is the search anchor for that request; “near me” uses active travel then home. The attending group is request-specific.

## Evidence boundaries

Use current read source pages; snippets are leads, not proof. **Never invent a fact** or candidate to complete a list. The newest applicable date-specific official notice beats general regular-hours information.

A **venue being open does not prove** every feature is available. Establish **requested-date availability** for promoted activities/sub-facilities and identify **what they can actually do** for each attending family member. Render payloads must contain evidenced `activities` and `family_fit`.

Google Maps is navigation evidence only, never operating-status evidence. Include a checked Maps link when an accountable source provides the address. Do not overstate weather or show a **numerical match score**.

## One-shot finalization

Do not build and repeatedly patch a temporary shortlist file. After research, create one complete payload containing:

- `shortlist`: the normal `shortlist-save` payload;
- `render`: the normal renderer payload with one card per finalist;
- `discovery`: `fresh_discovery_completed`, `candidates_considered`, unique `activity_classes_searched`, `exact_date_event_searched`, and `finalist_numbers_date_enriched`.

Then run:

```sh
python3 <source_dir>/scripts/finalize_briefing.py --source-dir <source_dir> \
  --data-dir <data_dir> --input <finalize-payload.json>
```

This one-shot path overrides reference text that says to call `shortlist-save` and `render_briefing.py` separately for a broad recommendation. The finalizer preflights save + render on disposable state, then performs the real save + render only if both validate. For dated requests it requires exact-date event search and date enrichment for every finalist.

Paste the returned `numbered_options_markdown` **verbatim**. A short intro/weather/practical note may surround it. If finalization fails, report that Family Scout could not finish verification; **never fall back to freehand numbered recommendations**.

Runtime Hermes must never edit `source_dir`, repository files, installed skill files or tests; report implementation defects instead. Never install a provider, change Hermes configuration, claim a booking, or store private profile data in this repository.
