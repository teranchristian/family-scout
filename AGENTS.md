# Family Scout contributor instructions

## Current scope

Phase 0 establishes a small, reversible Hermes skill installation and private
state. Read `README.md`, `hermes-skill/SKILL.md` and the blank templates in
`examples/` before changing behavior. They are the in-repository contract.

Do not implement Phase 1 recommendations, shortlist/feedback processing or
future features until requested. Do not add provider packages, databases,
packaging systems or a separate doctor/purge command for anticipated needs.
Keep checks proportional to actual data-preservation and integration risks.

## Privacy and data

- Every example, fixture and screenshot must use invented details. Never use
  the user, their family, home, workplace, identifiers or credentials as examples.
- Blank templates are intentional. Never seed a real profile from conversation,
  personal context, repository metadata or another project during installation.
- Keep runtime state outside the checkout. `profile.yaml`, `sources.yaml`,
  `shortlists.jsonl` and `feedback.jsonl` are private and must remain untracked.
- Do not print private state while testing or log exact home coordinates.
- Preserve existing and malformed state. Normal uninstall keeps all private
  data and the checkout. Do not overwrite another skill's files.

## Skill changes and verification

`hermes-skill/SKILL.md` is canonical. The installed skill is a copy; the installer
must detect locally edited copies before updating or removing them. Preserve
uncommitted repository edits and reconcile intended installed changes into Git.
Keep personal preferences and feedback out of committed skill instructions.

After a setup change, check fresh install, repeated install, uninstall and
reinstall against temporary synthetic state. Check the relevant refusal paths
when changing ownership or update behavior. No dedicated test framework is
required. Record which checks ran and which were unavailable.

Filesystem smoke checks do not prove Hermes loading or live tool access. Do not
mark Phase 0 complete until a fresh conversation on the actual host has recorded
skill/profile access, live search, source reading and forecast availability or
an explicit unavailable result. Never claim a planned capability works.
