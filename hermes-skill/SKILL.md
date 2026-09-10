---
name: family-scout
description: Research current, decision-ready family outings and remember explicit feedback.
---

# Family Scout

Help a family choose practical outings at home or while travelling. This is a thin router; load only needed references.

## Route first

- **Find, compare or plan outings:** read [references/discovery.md](references/discovery.md), [references/briefing.md](references/briefing.md), [references/quality.md](references/quality.md), and applicable [references/cli.md](references/cli.md).
- **Feedback, history correction, profile/travel, sources, or “more like this”:** read [references/memory.md](references/memory.md) and applicable CLI sections. For “more like this”, also read recommendation references.
- **Setup/status:** use the redacted `status` command and README.

## Recommendation order

Read `installation.json` for `source_dir` and `data_dir`. For a new broad recommendation run:

```sh
python3 <source_dir>/scripts/discovery_context.py --data-dir <data_dir>
```

This excludes prior shortlists and feedback. Using only the request, profile, resolved location and enabled sources, perform **fresh discovery first**. Aim for **6–8 plausible candidates across at least four meaningful activity classes**. Exact-date events count as a class. Do not inspect `shortlists.jsonl`, `feedback.jsonl`, or full `context` until a fresh candidate pool exists.

Then normal `family_scout.py context` may inform deduplication, repetition awareness, explicit feedback and final ranking. History may adjust ranking but must never seed or replace fresh discovery unless the user asks about previous recommendations.

Deep exact-date verification is for likely **4–5 finalists**, not every lead. An explicit place/station/area is the request anchor; “near me” uses active travel then home. The attending group is request-specific.

## Evidence and language

Use current read source pages; snippets are leads, not proof. **Never invent a fact**. The newest applicable date-specific official notice beats regular-hours information.

A **venue being open does not prove** every feature is available. Establish **requested-date availability** for promoted activities/sub-facilities and identify **what they can actually do** for each attending family member. Render payloads need evidenced `activities` and `family_fit`.

The response language is English. A venue/option **title** may keep its official local-language name; all descriptive content must be translated into English.

Google Maps is navigation evidence only, never operating-status evidence. Include a checked Maps link when an accountable source provides the address. Do not overstate weather or show a **numerical match score**.

## One-shot finalization

Create one payload with `shortlist`, `render`, and `discovery`. Discovery must include `fresh_discovery_completed`, `candidates_considered`, unique `activity_classes_searched`, `exact_date_event_searched`, `exact_date_event_source_urls`, and `finalist_date_enrichment`.

For dated broad searches, `exact_date_event_source_urls` needs at least one exact-date event/calendar source actually read. Each `finalist_date_enrichment` item needs `option_number` plus factual `source_urls`; each URL must be saved for that option, have a `content_verified` facts check, and appear in `consulted_sources` as `read`. Do not claim “no special event” unless this evidence supports it.

Run:

```sh
python3 <source_dir>/scripts/finalize_briefing.py --source-dir <source_dir> --data-dir <data_dir> --input <finalize-payload.json>
```

The finalizer preflights save + render on disposable state and writes real state only if both validate.

Paste the returned `numbered_options_markdown` **verbatim**. Paste `research_summary_markdown` once after the options/needs-checking section. A short English intro/weather/practical note may surround it.

If finalization fails, report that Family Scout could not finish verification; **never fall back to freehand numbered recommendations**.

Runtime Hermes must never edit `source_dir`, repository files, installed skill files or tests; report defects instead. Never install a provider, change Hermes configuration, claim a booking, or store private profile data in this repository.
