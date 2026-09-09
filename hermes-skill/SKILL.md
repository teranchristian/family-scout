---
name: family-scout
description: Research current, decision-ready family outings and remember explicit feedback.
---

# Family Scout

Help a family choose practical outings at home or while travelling. This is a
thin router; load only references needed for the task.

## Route first

- **Find, compare or plan outings:** read
  [references/discovery.md](references/discovery.md),
  [references/briefing.md](references/briefing.md),
  [references/quality.md](references/quality.md), and applicable
  [references/cli.md](references/cli.md) sections.
- **Feedback, history correction, profile/travel, sources, or “more like this”:**
  read [references/memory.md](references/memory.md) and applicable CLI sections.
  For “more like this”, also read the recommendation references.
- **Setup/status:** use the redacted `status` command and README.

## Recommendation context order

Read `installation.json` for `source_dir` and `data_dir`. For a new broad
recommendation, first run:

```sh
python3 <source_dir>/scripts/discovery_context.py --data-dir <data_dir>
```

Keep that output private. It intentionally excludes prior shortlists and feedback.
Using only the request, profile, resolved location and enabled sources, perform
fresh discovery and build a plausible candidate pool. Do not inspect
`shortlists.jsonl`, `feedback.jsonl`, or full `context` before that pool exists.

After fresh discovery, run normal `context` and use history/feedback only for
deduplication, repetition awareness, explicit learned feedback and final
diversity/ranking. A previously known venue may win again, but must survive fresh
comparison. For requests explicitly about prior suggestions or “more like this”,
history may be loaded first.

Current instructions override saved preferences. Use an explicit origin or
explicit “home”; otherwise unexpired travel, then home. Travel never replaces
home. The attending group is request-specific; never attach it to a saved
location or assume everyone attends. Ask only when a missing fact blocks
verification.

## Shared boundaries

Use current read source pages; snippets are leads, not proof. Never invent a fact
or candidate to complete a list. Resolve freshness before hard claims: the newest
applicable date-specific official notice beats a general official page, regular
hours, then secondary sources.

Say **confirmed open** only when date-specific evidence establishes it. If
regular hours apply and current official exception notices were checked with none
found, say **scheduled to be open based on regular hours; no applicable closure
notice found**. Never turn absence of a closure notice into “confirmed open”.

A venue being open does not prove every advertised feature is available.
Establish requested-date availability for every promoted activity, sub-facility,
program or interaction. For each attending family member, identify what they can
actually do and any material limitation.

Google Maps is navigation evidence only, never operating-status evidence. When
an accountable source provides the current address, put it in the card and add a
checked Google Maps link for that venue/address to `link_checks` with purpose
`map`.

Do not overstate weather. Save numbered options before display; learn only from
explicit feedback; never show a numerical match score.

After `shortlist-save`, build one render card per option and run:

```sh
python3 <source_dir>/scripts/render_briefing.py --data-dir <data_dir> \
  --search-id <search_id> --input <render-payload.json>
```

Paste the returned `numbered_options_markdown` **verbatim**. If rendering fails,
repair the input; never fall back to freehand numbered cards.

The helper validates structured facts but cannot create evidence. Preserve
malformed/private state and stop affected writes. Runtime Hermes must never edit
`source_dir`, repository files, installed skill files or tests; report an
implementation defect instead. Never install a provider, change Hermes
configuration, claim a booking, or store private profile data in this repository.
Phase 1 remains a thin probe: no database, background scraper, provider framework,
booking integration, web UI or machine learning.
