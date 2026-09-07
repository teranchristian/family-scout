# Phase 0 verification record

This record separates repository/local evidence from checks that must run in a
fresh conversation on the actual Hermes host. Test data and paths were temporary
and synthetic. No family or personal configuration was used.

Repository: <https://github.com/teranchristian/family-scout>

## Repository checks — 2026-09-07 UTC

| Check | Outcome | Evidence |
| --- | --- | --- |
| Shell syntax | Passed | `bash -n install.sh uninstall.sh` |
| Python syntax | Passed | `python3 -m py_compile scripts/setup.py` |
| Hermes skill structure | Passed | Skill Creator `quick_validate.py` reported `Skill is valid!` |
| Fresh local fixture install | Passed | Copied the skill and created all four missing state files in paths containing spaces |
| Repeated install | Passed | Refreshed the skill once and preserved an existing synthetic state file byte-for-byte |
| Normal uninstall | Passed | Removed only owned skill/metadata and preserved synthetic state byte-for-byte |
| Reinstall | Passed | Reused all preserved state through an explicit custom data directory |
| Edited installed skill | Passed | Both update and removal refused; the edited file remained byte-for-byte intact |
| Foreign skill collision | Passed | Installation refused and left the foreign directory and file intact |
| Malformed ownership record | Passed | Installation refused and preserved the installed skill unchanged |
| Repository-local private state | Passed | Installation refused and did not create the requested state directory |
| Repeated uninstall | Passed | Returned success without changing preserved state |
| New private-state permissions | Passed | New data directory was `0700`; all four new state files were `0600` |
| Missing Hermes home | Passed | Reported setup pending and created neither the missing home nor state directory |

The fixture exercise used the public blank templates and one deliberately
non-profile synthetic file to prove that setup preserves existing bytes rather
than parsing, replacing or repairing them. The temporary fixture was removed
after the run.

## Actual Hermes host — pending

This build session did not have a route to the Hermes host, so these outcomes
are deliberately not inferred from filesystem fixture checks:

- [ ] Confirm the actual active profile and install into its supported skill path.
- [ ] Confirm a fresh conversation discovers and loads `family-scout`.
- [ ] Confirm the installed skill can read the private profile; record blank or
  configured status without publishing its values.
- [ ] Run a public web search at an arbitrary public location and record the URL.
- [ ] Open a returned source page and confirm its contents can be read.
- [ ] Retrieve a dated forecast from an available tool or readable source, or
  explicitly record unavailability and the attempted source/tool.
- [ ] Run repeat install, normal uninstall and reinstall on the actual host and
  confirm the intended private state is preserved.

Missing search or source-page reading blocks Phase 1 live integration. An
explicitly recorded unavailable forecast is allowed. Phase 0 remains **host
verification pending** until every required actual-host outcome is recorded.
