---
name: family-scout
description: Research current, decision-ready family outings and remember explicit feedback.
---

# Family Scout

Help a family choose practical outings at home or while travelling. This is the
thin router; load only references needed for the task.

## Route first

- **Find, compare or plan outings:** read
  [references/discovery.md](references/discovery.md) and
  [references/briefing.md](references/briefing.md), and
  [references/quality.md](references/quality.md), plus applicable sections of [references/cli.md](references/cli.md).
- **Feedback, history correction, profile/travel, sources, or “more like this”:**
  read [references/memory.md](references/memory.md) and the applicable CLI
  section. For “more like this”, also read both recommendation references.
- **Setup/status:** use the redacted `status` command and repository README.

## Start from private context

Read `installation.json` for `source_dir` and `data_dir`. Run `context` before a
recommendation, feedback, correction or “more like this” request. Keep its output private; expose only minimum public
place/date/suitability facts needed for discovery.

Current instructions override saved preferences. Use an explicit origin or
explicit “home”; otherwise unexpired travel, then configured home. Travel never
replaces home. The attending group is request-specific; do not attach it to a
saved location or assume everyone attends. Ask only when a missing fact blocks
verification.

## Shared boundaries

Use current read source pages; snippets are leads, not proof. Resolve freshness
before hard claims: the newest applicable date-specific official notice beats a
general official page, which beats regular hours, which beats secondary sources.
A later or more specific closure, maintenance, programme or special-hours notice
overrides older general information.

Use evidence-strength wording precisely. Say **confirmed open** only when
date-specific evidence establishes it. If regular hours apply and current
official exception notices were checked with none found, say **scheduled to be
open based on regular hours; no applicable closure notice found**. Never turn
absence of a closure notice into “confirmed open”.

A venue being open does not prove that every advertised feature is available.
Establish requested-date availability for every promoted activity, sub-facility,
program or interaction. Do not strengthen source wording: a generic playroom is
not a “dedicated toddler playroom” unless evidence says so. For each attending
family member, identify what they can actually do and any material limitation.

Google Maps is navigation evidence only, never operating-status evidence. When
an accountable source provides the current address, include that address
in the card and a checked Google Maps link for that venue/address
in `link_checks` with purpose `map`. Never use Google Maps hours or closure
labels instead of official evidence.

Do not overstate weather: distinguish precipitation probability, current
conditions and duration. Do not say “rain all day” unless the forecast supports
that duration. Save numbered options before display; learn only from
explicit feedback; never show a numerical match score.

After `shortlist-save`, build one render card per option and run:

```sh
python3 <source_dir>/scripts/render_briefing.py --data-dir <data_dir> \
  --search-id <search_id> --input <render-payload.json>
```

Each card contains `number`, URL-free `body`, `activities`, and
`family_fit`. Put the verified address in `body` when available; do not repeat
activity or child-fit details there. Every activity states kind, availability, concrete detail and a factual `source_url` accepted by saved
`link_checks`. `family_fit` has one entry per attending member; participating
members reference only available activities, while adults may use `guardian`.

Paste the returned `numbered_options_markdown` **verbatim**. A short intro,
weather summary, plan or practical notes may surround it, but do not repeat card
facts or alter links. If rendering fails, repair the input; do not fall back to
freehand numbered cards.

The helper validates structured facts but cannot create evidence. Preserve
malformed/private state and stop affected writes. Never install a provider,
change Hermes configuration, claim a booking, or store private profile data in
this repository. Phase 1 remains a thin probe: no database, background scraper,
provider framework, booking integration, web UI or machine learning.
