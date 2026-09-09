# Recommendation workflow

Use this order for every broad outing recommendation. The order is part of the
runtime contract, not a suggestion.

## 1. Load discovery context only

Read `installation.json`, then run:

```sh
python3 <source_dir>/scripts/discovery_context.py --data-dir <data_dir>
```

This returns profile, resolved location and enabled custom sources but does not
read or return prior shortlists or feedback. Use it to resolve the family,
request location, radius, explicit constraints and saved preferences needed for
the current request.

Do not read `shortlists.jsonl`, `feedback.jsonl`, recent recommendation text or
other prior candidate lists before fresh discovery. A request explicitly asking
to revisit previous suggestions is the exception.

## 2. Perform fresh discovery

Build the candidate pool from current public sources. Apply the coverage and
exact-date rules in `discovery.md`. Saved preferences may guide ranking later but
must not collapse a broad discovery pass into familiar categories.

For an explicitly named place, station or area, use that request location for
this search. `near me` or `near where we are staying` uses the resolved travel or
home location. An area request such as `in Kawagoe` is an area-search request,
not an instruction to recenter the search on the accommodation.

A previous venue can still be rediscovered naturally through current search. It
must not enter the candidate pool merely because it appeared in history.

## 3. Freeze the fresh candidate pool

Before consulting history, identify the plausible candidates found in the fresh
pass. Do not silently replace this pool with remembered venues afterward.

## 4. Consult history and feedback

Only now run the normal context command when history is useful:

```sh
python3 <source_dir>/scripts/family_scout.py --data-dir <data_dir> context
```

Use `recent_shortlists` and `effective_feedback` to:

- recognize places already suggested or visited;
- apply explicit likes, dislikes and corrections;
- avoid unnecessary repetition;
- improve diversity among otherwise comparable candidates.

History is comparison context, not discovery evidence and not an automatic
ranking boost. A previously suggested venue may still win when current evidence
makes it the best option.

## 5. Verify, enrich and rank

Apply hard constraints, exact-date enrichment, venue/activity separation, child
fit, current link checks and weather guidance from the other references. Verify
likely finalists from current source pages even when they were suggested before.

The desired pipeline is:

```text
profile + family + request location
        ↓
fresh discovery
        ↓
fresh candidate pool
        ↓
consult recent history / feedback
        ↓
dedupe + repetition awareness
        ↓
exact-date verification and enrichment
        ↓
qualitative ranking
        ↓
save + render
```

## Runtime source boundary

Family Scout runtime must not modify its own repository, `source_dir`, tests,
canonical `hermes-skill/` files or installed skill copy. If runtime use reveals a
bug or missing behavior, report the evidence and desired behavior. Repository
changes are made through the development workflow, then installed deliberately.
