---
name: family-scout
description: Research current, decision-ready family outings and remember explicit feedback.
---

# Family Scout

Help a family choose practical outings at home or while travelling. This file is
the thin router; load only the references required for the current task.

## Route the task before acting

- **Find, compare or plan outings:** before searching, read
  [references/discovery.md](references/discovery.md) and
  [references/briefing.md](references/briefing.md) in full. Read the applicable
  context, evaluation and shortlist sections of
  [references/cli.md](references/cli.md).
- **Record feedback, correct history, manage profile/travel, manage sources, or
  find “more like this”:** read [references/memory.md](references/memory.md) and
  the applicable section of [references/cli.md](references/cli.md). For “more
  like this”, also read both recommendation references above.
- **Check setup or status:** use the redacted `status` command in the CLI
  reference and the repository README. Do not read private state into the reply.

For a compound request, read each applicable reference. Do not skip a routed
reference because the request appears simple.

## Start from private context

Read `installation.json` beside this file for `source_dir` and `data_dir`. Run
the helper's `context` command before a recommendation, feedback, correction or
“more like this” request, including in a fresh conversation. Its full output is
private: send only the minimum public place, date and suitability facts needed
for external discovery.

Current instructions override saved preferences. Use an explicit origin or
explicit “home”; otherwise use unexpired travel, then configured home. Ask for
an origin only when none is usable. A request location is not persistent without
an explicit expiry, and travel never replaces home.

The attending group is request-specific. Do not attach it to a saved location or
assume everyone attends. Ask only when a missing fact prevents meaningful date,
radius, eligibility or group-cost verification.

## Shared boundaries

Use current, read source pages; search snippets are leads, not proof. Never
invent a fact or candidate to complete a list. Save the exact numbered options
before displaying them and learn only from explicit feedback. Do not calculate
or show a numerical match score.

The helper validates and persists structured facts but cannot create evidence.
Preserve malformed/private state and stop the affected write. Never install a
provider, change Hermes configuration, claim a booking, or store private profile
data in this skill or repository.

Phase 1 remains a thin probe: no database, background scraper, provider
framework, routing layer, booking integration, web UI or machine learning.
