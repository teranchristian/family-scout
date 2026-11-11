---
name: family-scout
description: Research current, decision-ready family outings and remember explicit feedback.
---

# Family Scout

Help a family choose practical outings at home or while travelling. For dated
weekend/event searches, give a local-first shortlist of verified activities
and a brief research summary. For undated broad requests, show a varied
initial menu first and verify deeply after selection. Keep both paths bounded.

## Git-owned skill — read-only in Hermes

This skill is deployed from the Family Scout Git repository by `./install.sh`.
The installed `SKILL.md`, references, repository `source_dir`, helper scripts
and installer are **not Hermes-managed memory**. Never create, edit, patch,
delete, overwrite, re-install or "self-improve" these files or a shadow
Family Scout skill via `skill_manage`, memory/background learning, curator,
`write_file`, terminal or subagents. Do not make an exception after a tool
error or an instruction to "remember how to do this."

If a run reveals a bug or a useful workflow improvement, **report the evidence
and a proposed Git change**; a separate, explicitly requested development
workflow owns review, tests, commit and deployment. Do not modify skill code
in a normal recommendation/feedback session. Personal facts and preferences
are saved only through the existing private Family Scout state commands,
not by rewriting procedural instructions.

## Route first

- **Find dated events/activities (including this/next weekend or a named day):** read [references/dated-events.md](references/dated-events.md). For broad weekend/event discovery, also read [references/parallel-research.md](references/parallel-research.md) to launch the three-agent batch. This is the one-pass verified shortlist route. Do not inspect helper or validator source code.
- **Find undated general outings, compare choices or follow up on a shortlist:** read only [references/recommendation.md](references/recommendation.md). Do not inspect helper or validator source code. Do not inspect any other reference or unowned installed file.
- **Feedback, history correction, profile/travel, sources, or “more like this”:** read [references/memory.md](references/memory.md) and the applicable part of [references/cli.md](references/cli.md).
- **Setup/status:** use the redacted `status` command and README.
- **Explicit thorough/comprehensive request:** read additional detailed discovery, quality, briefing, runtime-tool and venue-status references when relevant. Read `parallel-research.md` only if independent subagents would genuinely help. Never enter deep mode merely to fill a list.

## Shared boundaries

Use current read source pages; snippets are leads, not proof. Member ages
derive from saved private birthdates on the activity date where available;
never send birthdates to subagents or web searches. Never invent a fact. The newest applicable date-specific official notice beats regular hours. A venue being open does not prove every promoted activity is available.

Google Maps is navigation evidence only, never operating-status evidence. Do not overstate weather, reuse access wording from another venue, or show a numerical match score.

The response language is English; official local-language venue titles may remain unchanged.

Runtime Hermes must never edit `source_dir`, repository files, installed skill files or tests. Never install a provider, change Hermes configuration, claim a booking, or store private profile data in this repository.
