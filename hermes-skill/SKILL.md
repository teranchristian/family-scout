---
name: family-scout
description: Verify Family Scout setup and private profile access.
---

# Family Scout — Phase 0

Use this skill when asked to check Family Scout installation, setup or readiness.
The recommendation probe, shortlist history and feedback behavior are planned
for Phase 1 and are not implemented. Do not simulate a working recommender.

## Locate the installation and state

1. Read `installation.json` beside this installed `SKILL.md`. It records
   `source_dir` (the repository) and `data_dir` (private state). If absent or
   unreadable, report setup pending and use the repository README for installation.
   Do not guess a different profile or silently create a replacement installation.
2. Read `profile.yaml` and `sources.yaml` from `data_dir` using available local
   file tools. Check that `shortlists.jsonl` and `feedback.jsonl` exist without
   dumping their contents. Empty source lists and history files are valid.
3. A new profile has null home fields and empty group data. Report it as blank;
   do not infer or populate family details. A missing precise home origin does
   not prevent a setup check using a user-approved public location.
4. Report missing files, malformed YAML or unavailable file access explicitly.
   Preserve existing bytes; do not reset, repair or rewrite state during a check.
   Do not show private profile values or history unless the user asks for them.

## Verify on the actual Hermes host

Run these checks in a fresh conversation when setup verification is requested:

- Confirm this installed skill is discoverable and loaded. Use the host's
  available skill-list/view capability where present; do not invent tool names.
- Read the installed private profile and report only whether access succeeds
  and whether required setup is still missing.
- Use an available web-search tool for a public query at an arbitrary public
  location. Do not use names, home coordinates or family details in the query.
- Open one returned source page and confirm its contents can actually be read;
  a search snippet alone does not establish page-reading access.
- Try a dated forecast for that public location, through an available weather
  tool or a readable forecast page. State the forecast date and source, or report
  unavailable and why. Do not present current conditions or climate averages
  as a forecast. If an actual attempt errors or lacks coverage, report it.

Give separate outcomes for skill loading, profile access, web search, source
reading, and forecast retrieval or explicit unavailability. Include the check
date and public source URLs. Do not claim a check passed unless it ran here.
Unavailable search or source reading blocks Phase 1 live integration. Explicit
forecast unavailability is an allowed result, but it must be stated. Do not
install replacement providers or change Hermes configuration automatically.

## Keep behavior and private data separate

The repository's `hermes-skill/SKILL.md` is the source of truth. Installation
copies it into Hermes. Rerunning `install.sh` refreshes that copy. If Hermes has
edited the installed skill, preserve those changes and reconcile the intended
non-private behavior back into the repository before reinstalling or removing it.
Do not put family preferences, precise origins or feedback into skill files.
Use invented names and details for any examples; never reuse the user's family.

Phase 0 ends with recorded host outcomes. Start Phase 1 only when requested and
the required Phase 0 checks pass. Leave purge commands, a separate doctor tool
and broader setup automation for a later review if real usage warrants them.
