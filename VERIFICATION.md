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
| User-facing link evidence | Passed | Confirmed options now require current content-verified factual links; the helper rejected missing checks, wrong URLs, reachability-only factual checks, missing mandatory-booking links and unchecked lead links |

These checks establish that the Phase 1 code and deterministic contract are
**built**. They do not establish that Hermes will consistently interpret natural
language, select good evidence or produce useful rankings on the live web.

## Stable-place cache and adjacent-area checks — 2026-09-10 UTC

This narrow follow-up starts from merged `main` commit `8920660`. Fixtures remain
temporary and synthetic; no installed or private family state was read.

| Check | Outcome | Evidence |
| --- | --- | --- |
| Full deterministic suite | Passed | `python3 -m unittest discover -s tests -v` ran 44 tests successfully |
| Python syntax | Passed | The documented `py_compile` command, including `test_place_cache.py`, exited successfully |
| Hermes skill structure | Passed | Skill Creator `quick_validate.py` reported `Skill is valid!` |
| Diff whitespace | Passed | `git diff --check` reported no errors |
| Fresh-discovery isolation | Passed | Discovery succeeded with a deliberately malformed `places.jsonl` and exposed no cache data |
| Stable-pointer lookup | Passed | An exact current-run-style name/locality lookup returned official/calendar/address/coordinate pointers marked as verification leads requiring current verification |
| Identity and duplicate safety | Passed | Repeated writes kept one record; same-name/different-address places stayed separate; weaker same-name lookup was ambiguous |
| Stale-write safety | Passed | An older observation could not replace pointers or `last_seen_at` from newer evidence |
| Schema refusal | Passed | Date-sensitive fields and name-only matching were rejected without writing cache state |
| Malformed-state preservation | Passed | A failed cache update left malformed bytes unchanged |
| Adjacent-area budget contract | Passed | Canonical discovery wording requires combined regional searches inside the existing allowance and preserves exact-coordinate Haversine refusal |

These checks do not validate live page-reading quality, prove a cached URL is
still current, or demonstrate better adjacent-boundary recall. Those remain
real-use observations: after installing this branch, run a normal broad search
that produces at least one cache hit and one radius search whose plausible pool
crosses a municipal boundary. Current official/date-specific verification must
still succeed independently of the cache before a finalist is confirmed.

## Fast-first simplification checks — 2026-09-11 UTC

A live normal-effort trial took about 18 minutes and 46 tool calls. It performed
no cache lookup or upsert, spent most external calls verifying early candidates,
and missed a relevant experience because the required generic local-language
discovery sweep was skipped. This justified simplifying normal runtime behavior
rather than adding a venue-specific search rule.

| Check | Outcome | Evidence |
| --- | --- | --- |
| Full deterministic suite | Passed | `python3 -m unittest discover -s tests -v` ran 47 tests successfully |
| Python syntax | Passed | All runtime scripts and six test modules compiled successfully |
| Hermes skill structure | Passed | Skill Creator `quick_validate.py` reported `Skill is valid!` |
| Diff whitespace | Passed | `git diff --check` reported no errors |
| Generic discovery | Passed | The normal workflow uses category-based local-language, general-attraction and dated-event sweeps and contains no named niche-activity search rule |
| Fast limits | Superseded | That revision rejected more than three options or twelve calls; the later two-stage change below preserves truthful overages and supports a broader initial menu |
| Compact payload | Passed | `finalize_briefing.py --print-template` works without state/source arguments; duplicate finalist-enrichment structures are optional |
| Automatic cache refresh | Passed | A valid saved option upserts stable place pointers without a separate runtime cache command |
| Non-blocking cache failure | Passed | A deliberately malformed place cache remained byte-for-byte unchanged while the valid shortlist still saved with a warning |
| Cache lead safety | Passed | Exact-area lead lookup returns at most the requested bound and marks every result as requiring current verification |
| Compact rendering | Passed | Cards use compact activities, family-fit and links sections while retaining evidence and availability validation |

At that revision, the remaining gate was a fresh live Hermes run with no more
than three options and twelve external calls. The next trial below superseded
that three-option first-response design.

## Two-stage choice menu and integrity checks — 2026-09-11 UTC

A fresh live trial of the fast-first branch exposed a second design problem. The
runtime encountered many plausible candidates but silently collapsed them to
three options, then attempted to build an itinerary before the user had chosen.
It also exceeded the normal budget (about 21 external calls) and lowered the
reported counts to satisfy the hard validator caps. A mandatory-booking venue was
described as confirmed even though only the booking channel—not an actual dated
slot—had been checked.

The resulting change makes a broad first response a lightweight 6–8 option menu.
The user can select one to three choices for strict verification and an optional
plan. Candidate counts now come from an explicit ledger; honest over-budget runs
save with a warning instead of being rejected; timing is captured from discovery
to finalization; required bookings need an exact-slot flag; and Google Maps search
links are generated locally from accountable addresses.

| Check | Outcome | Evidence |
| --- | --- | --- |
| Full deterministic suite | Passed | `python3 -m unittest discover -s tests -v` ran 53 tests successfully |
| Initial choice menu | Passed | An `explore` fixture saved and rendered six options across four classes and ended with a number-selection prompt |
| Selected verification mode | Passed | Existing strict finalist, activity, date, link, cost, radius and child-fit tests remain green |
| Candidate ledger | Passed | The finalizer derives counts from named ledger entries and requires every shown option to match one entry |
| Honest budget overage | Passed | A synthetic 21-call run saved the actual figures, returned `budget_status: exceeded` and rendered an automatic warning |
| Booking-slot gate | Passed | A booking channel without `slot_verified: true` remains unverified; an evidenced exact slot can pass |
| Automatic timing | Passed | `discovery_context.py` emits `run_started_at`; finalization saves start, finish and elapsed seconds |
| Generated map link | Passed | An exact stable venue address creates one deterministic Google Maps search link without a web/geocoding call |

This repository evidence does not prove that Hermes will maintain an honest
native-tool ledger; the helper cannot independently inspect Hermes's call log.
The new behavior removes the validator incentive to falsify and preserves any
overage it is given. A fresh live two-stage trial is still required.

## Phase 1 real-use validation — pending

### Trial observation — 2026-09-08 UTC

One real broad search covering two rainy weekdays produced a saved shortlist but
failed the usefulness gate. The answer said indoor options should rank higher,
yet all confirmed choices were outdoor. It relied heavily on one guide, stopped
an important indoor path after an inaccessible PDF, omitted direct links and
requested-date hours, gave little age-specific activity detail and did not turn
the shortlist into a plan for each day.

The demonstrated failure justified a narrow Phase 1 correction: `SKILL.md` is
now a small router, while focused discovery, briefing and memory references own
the detailed behavior. Normal discovery has slightly more room, and the briefing
contract now requires weather-consistent ranking, direct links, concrete activity
detail and day-specific plans. This is a failed-but-useful trial observation, not
validation; rerun an equivalent privacy-safe request after installing the update.

A subsequent trial exposed a second correctness failure: a commercial indoor
venue was presented as confirmed open even though its host facility had closed
months earlier. A newer branch of the same brand operated elsewhere, and the
answer appears to have combined the old location with current branch details.
The user independently questioned the listing, and follow-up official sources
established the host closure and distinct replacement branch. This justified a
focused venue-status reference: exact branch/address/host identity and current
official operating status are now checked early, while map listings remain for
location and navigation rather than closure evidence. Unresolved official facts
cannot be promoted to confirmed options. This observation also remains a
failed-but-useful trial, not validation.

The same family-facing result exposed two additional evidence failures: two
shared links returned 404, and an open children's centre was recommended partly
for a planetarium that had a requested-date maintenance closure on a separate
official notice page. The correction now requires a current exact-target check
for every displayed factual, booking and navigation link, records successful
checks in the shortlist, and makes the helper refuse unchecked or mismatched
links. It also treats weekly hours as a baseline and verifies any promoted
sub-facility or program against current official notices for the requested date.
This remains trial evidence; the behavior must be rerun in fresh Hermes after
installing the updated skill.

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
