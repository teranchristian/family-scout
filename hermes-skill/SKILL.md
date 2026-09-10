---
name: family-scout
description: Research current, decision-ready family outings and remember explicit feedback.
---

# Family Scout

Help a family choose practical outings at home or while travelling. Load only needed references.

## Route first

- **Find, compare or plan outings:** read [references/discovery.md](references/discovery.md), [references/briefing.md](references/briefing.md), [references/quality.md](references/quality.md), and applicable [references/cli.md](references/cli.md).
- **Feedback, history correction, profile/travel, sources, or “more like this”:** read [references/memory.md](references/memory.md) and applicable CLI sections.
- **Setup/status:** use the redacted `status` command and README.

## Recommendation order

Read `installation.json` for `source_dir` and `data_dir`. For a new broad recommendation run:

```sh
python3 <source_dir>/scripts/discovery_context.py --data-dir <data_dir>
```

This excludes prior shortlists and feedback. Using only the request, profile, resolved location and enabled sources, perform **broad fresh discovery first**. Stop once **6–8 plausible candidates across at least four meaningful activity classes** give adequate coverage. Broad things-to-do requests include one **general-attractions/experiences sweep** inside the normal search budget; do not add child/toddler terms to every query. Exact-date events count as a class. Do not inspect `shortlists.jsonl`, `feedback.jsonl`, or full `context` yet.

Next verify current information, assess family suitability, and create an **initial ranking from current evidence only**: fit, distance/practical effort, weather, and specialness/timing. Only then may `family_scout.py context` expose history and explicit feedback. Use history only as a final adjustment for repetition, diversity and learned preferences; it must never seed discovery or determine the initial ranking unless the user asks about previous recommendations.

Deep exact-date verification is for only **3–5 likely finalists**. Deep effort may resolve a material missing fact for those finalists; it must not expand the candidate hunt. An explicit place/station/area is the request anchor; “near me” uses active travel then home.

## Evidence and language

Use current read source pages; snippets are leads, not proof. **Never invent a fact**. The newest applicable date-specific official notice beats regular-hours information.

A **venue being open does not prove** every feature is available. Establish requested-date availability for promoted activities/sub-facilities and identify **what they can actually do** for each attending family member. Render payloads need evidenced `activities` and `family_fit`.

The response language is English. A venue/option **title** may keep its official local-language name; all descriptive content must be translated into English.

Google Maps is navigation evidence only, never operating-status evidence. Include a checked Maps link when an accountable source provides the address. Do not overstate weather or show a **numerical match score**.

## One-shot finalization

Create one payload with `shortlist`, `render`, and `discovery`. Discovery includes fresh-discovery counts plus `exact_date_event_searched`, `exact_date_event_source_urls`, `exact_date_event_findings`, and `finalist_date_enrichment`.

For dated searches, read at least one exact-date event/calendar source. Record relevant requested-date events found in `exact_date_event_findings`; include `option_number` when it belongs to a finalist. Each finalist enrichment needs factual `source_urls` and concrete `dated_findings` (`scheduled_activity`, `sub_facility`, `venue_availability`, or `hours_exception`). Scheduled activities and sub-facilities must also appear in rendered activities with matching availability and source.

Never make broad absence claims such as “nothing special is on” or “there are no events.” If no strong event was found, say only: **“I didn't find a strong exact-date event in the checked sources.”**

Run:

```sh
python3 <source_dir>/scripts/finalize_briefing.py --source-dir <source_dir> --data-dir <data_dir> --input <finalize-payload.json>
```

The finalizer preflights save + render on disposable state and writes real state only if both validate.

Paste the returned `numbered_options_markdown` **verbatim**. Paste `research_summary_markdown` once after the options/needs-checking section. Do not add a stronger event-absence conclusion.

If finalization fails, report that Family Scout could not finish verification; **never fall back to freehand numbered recommendations**.

Runtime Hermes must never edit `source_dir`, repository files, installed skill files or tests; report defects instead. Never install a provider, change Hermes configuration, claim a booking, or store private profile data in this repository.
