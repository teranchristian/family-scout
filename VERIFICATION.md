# Verification record

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

## Actual Hermes host — passed 2026-09-08 SGT

A fresh Hermes conversation reported these results at 08:04 +08 using Singapore
Botanic Gardens as an arbitrary public test location. It used no family data,
made no recommendations and did not modify private state or Hermes configuration.

- [x] The active `default` profile listed `family-scout` as enabled. Hermes loaded
  it with `skill_view` from `~/.hermes/skills/family-scout/SKILL.md`.
- [x] `profile.yaml`, `sources.yaml`, `shortlists.jsonl` and `feedback.jsonl`
  were readable. The profile was reported as blank and the source list empty;
  private values were not needed for the test.
- [x] Live search returned the official [Singapore Botanic Gardens general
  information page](https://sbg.nparks.gov.sg/visit/general-info/) for an opening
  hours and admission query.
- [x] Hermes opened and read that official source page, rather than relying only
  on a search snippet.
- [x] Hermes retrieved a dated 8 September 2026 forecast from the [AccuWeather
  Singapore daily forecast](https://www.accuweather.com/en/sg/singapore/300597/daily-weather-forecast/300597).

On this host, `web_extract` provides search but not page extraction. Source-page
reading and the forecast therefore used the existing `curl`/`r.jina.ai` reader
path. This satisfies the Phase 0 capability requirement because both live pages
were actually read and no replacement package or Hermes configuration was added.
It is still a third-party reliability dependency to observe during the Phase 1
trial; it is not a reason to add a provider before evidence shows one is needed.

The destructive-path acceptance checks—repeat install, normal uninstall and
reinstall with byte-for-byte state preservation—already passed against temporary
synthetic state. They were not repeated solely as host ceremony because the
actual installation reported no material path or permission difference.

**Phase 0 result: passed. Phase 1 may begin when requested.**

## Phase 1 repository checks — 2026-09-08 UTC

All automated fixtures use invented people, places, URLs, dates and currency.
They run in temporary directories and do not read or modify the installed private
profile on the Hermes host.

| Check | Outcome | Evidence |
| --- | --- | --- |
| Python syntax | Passed | `python3 -m py_compile scripts/setup.py scripts/family_scout.py tests/test_phase1.py` |
| Shell syntax | Passed | `bash -n install.sh uninstall.sh` |
| Hermes skill structure | Passed | Skill Creator `quick_validate.py` reported `Skill is valid!` for the main skill and references |
| Deterministic Phase 1 suite | Passed | `python3 -m unittest discover -s tests -v` ran 12 tests successfully |
| Phase 0 → Phase 1 upgrade | Passed | A schema-1 installation record upgraded to schema 2 and installed the owned reference tree |
| Repeat install and ownership safety | Passed | Private bytes survived repeat install; edited installed reference blocked both update and uninstall |
| Interrupted setup recovery | Passed | A missing recorded file was restored on install and a partial uninstall completed without touching state |
| Profile and travel | Passed | Explicit profile update was idempotent; travel, forced-home and expired-travel precedence resolved correctly |
| Original blank migration | Passed | The exact Phase 0 blank profile loaded and converted to JSON-compatible YAML only on an explicit write |
| Source lifecycle | Passed | Add/retry, disable/retry, enable, remove and repeat-remove behaved deterministically |
| Hard constraints | Passed | Match, radius failure, unknown cost, ended session, age failure, unknown mandatory booking and closure classifications matched the contract |
| Shortlist identity and retry | Passed | Exact option saved once; repeat operation did not duplicate; duplicate sessions, private address persistence and excess normal fetches were rejected |
| Concurrent retry | Passed | Four simultaneous writes with one operation ID produced one JSONL record and three duplicate acknowledgements |
| Cross-search references | Passed | Stable search resolution worked and an ambiguous conversation reference was refused rather than guessed |
| Explicit feedback | Passed | Feedback retry was idempotent; correction and retraction stayed append-only; fresh context exposed only effective signals |
| Malformed-state preservation | Passed | Malformed profile and JSONL writes failed without changing a byte |

These checks establish that the Phase 1 code and deterministic contract are
**built**. They do not establish that Hermes will consistently interpret natural
language, select good evidence or produce useful rankings on the live web.

## Phase 1 real-use validation — pending

- [ ] Complete 3–5 real Family Scout searches with current source pages.
- [ ] Give explicit feedback, then verify it affects a relevant recommendation
  in a later fresh Hermes conversation without weakening current constraints.
- [ ] Complete a practical search from a second explicit location.
- [ ] Run at least two equivalent searches with ordinary Hermes and compare
  evidence correctness, usefulness and latency.
- [ ] Record page-reader and dated-forecast successes/failures, especially the
  existing `curl`/`r.jina.ai` reader path observed in Phase 0.

**Phase 1 result: built; trial pending.** Do not mark it validated or start
Phase 1.5 solely because the deterministic suite passes.
