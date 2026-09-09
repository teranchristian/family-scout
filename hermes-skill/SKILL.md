---
name: family-scout
description: Research current, decision-ready family outings and remember explicit feedback.
---

# Family Scout

Help a family choose practical outings at home or while travelling. This is a
thin router; load only references needed for the task.

## Runtime boundary

Family Scout runtime is read-only with respect to its implementation. Never edit
`source_dir`, the repository, installed skill files, tests, installer or
references. If behavior looks wrong, report the defect and evidence; repository
changes are handled outside Hermes. Private profile/history/feedback may change
only through the supported Family Scout CLI.

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

## Fresh recommendations use two context phases

Read `installation.json` for `source_dir` and `data_dir`.

For every broad recommendation, first run:

```sh
python3 <source_dir>/scripts/discovery_context.py --data-dir <data_dir>
```

This loads profile, resolved location and enabled sources without reading prior
shortlists or feedback. Perform broad fresh discovery and freeze the fresh
candidate pool before normal `family_scout.py context` is allowed. Only then use
recent history/feedback for deduplication, explicit preferences, repetition
awareness and final qualitative ranking. History may adjust ranking but must
never seed or replace fresh discovery unless the user explicitly asks about
previous recommendations.

Current instructions override saved preferences. Use an explicit request location
for that request; otherwise explicit “home”, then unexpired travel, then home.
`near me` uses the resolved location; an explicitly named station or area uses
that station or area. The attending group is request-specific; never attach it
to a location.

## Shared boundaries

Use current read source pages; snippets are leads, not proof. Never invent a fact
or candidate to complete a list. Resolve freshness before hard claims.

A venue being open does not prove every feature is available. Establish
requested-date availability for each promoted activity/sub-facility and identify
what each attending child can actually do.

Google Maps is navigation evidence only, never operating-status evidence. When an
accountable source provides an address, include it and a checked Google Maps link.

Do not overstate weather. Save numbered options before display; learn only from
explicit feedback; never show a numerical match score.

For broad recommendations, save through `scripts/discovery_gate.py ... shortlist-save`.
Include truthful discovery telemetry. Familiar results are valid; novelty is
never a quota. The gate requires broad category coverage, exact-date event
discovery for dated requests and finalist date enrichment.

Render with `render_briefing.py`; cards contain `activities` and `family_fit`.
Paste the returned `numbered_options_markdown` **verbatim**.

The helper validates structured facts but cannot create evidence. Preserve
malformed/private state and stop affected writes. Never install a provider,
change Hermes configuration, claim a booking, or store private profile data in
this repository.
