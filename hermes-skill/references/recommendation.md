# Fast recommendation workflow

This is the complete runtime contract for a normal Family Scout recommendation.
Do not load the longer detailed references and do not inspect Python source unless
the user explicitly asks for a thorough/comprehensive search.

## 1. Interpret once

Read `installation.json`, then run `discovery_context.py` once. Resolve the
public search anchor, absolute date/window, timezone, attending ages, radius and
hard cost/indoor requirements. Do not send names, private coordinates or the full
profile to web tools.

Weather ranks the eventual pool; it does not narrow discovery unless indoor or
outdoor is an explicit hard requirement.

## 2. Build a generic candidate pool

Use at most **three search queries**:

1. one broad, local-language family activity sweep across several locally useful
   experience classes;
2. one broad general attractions/experiences sweep that is not restricted to
   child-focused wording; and
3. for a dated request, one exact-date events/calendar sweep. Otherwise use the
   third query only when the first two leave a material coverage gap.

Keep the standing discovery language category-based. Useful generic classes
include events, play/community spaces, learning/culture,
animals/nature, commercial attractions, hands-on experiences and outdoor
options. Cover at least four relevant classes across the combined searches. Do
not name one special venue or niche activity in the standing query instructions.
Search results and aggregators are leads only.

Keep **4–6 plausible candidates**. Adjacent areas may be included inside the same
queries when they plausibly fall within the requested radius; the named place or
station remains the anchor.

After the fresh searches, optionally load one recent cached lead for the exact
public area:

```sh
python3 <source_dir>/scripts/family_scout.py --data-dir <data_dir> \
  place-cache-leads --area "<public area>" --limit 1
```

The cache may contribute at most one finalist and never proves current facts.
At least two finalists in a three-option answer must come from fresh discovery.

## 3. Verify only likely finalists

Select at most **three likely finalists** before detailed verification. Stop as
soon as two strong options plus one useful backup are confirmed; returning two
is better than slow padding.

For each finalist:

- establish the exact venue/branch/address and check its current official page;
- check requested-date closure, exceptions and any activity being promoted;
- verify hours, mandatory family cost, eligibility and mandatory booking;
- validate every factual or map link that will be shown;
- try geocoding once. If it fails, do not retry or invent distance. A hard radius
  then remains unverified, so omit the venue or put it under Needs checking.

Use no more than **12 external calls total**, including searches, page fetches,
forecast and geocoding. A failed page gets at most one alternate accountable
source. Do not expand candidate discovery while verifying.

For a useful venue with an unavailable optional feature, rank only its verified
available activities and show the unavailable feature as a short warning.

## 4. Rank and answer compactly

Rank by child fit, practical effort, weather, and specialness/timing. History and
explicit feedback may adjust the final order only after current evidence creates
the initial ranking.

Return at most three options. Each compact card needs:

- concise opening wording, hours, family cost, booking, address and reason;
- one to four decision-relevant activities with availability and evidence;
- child-specific fit only where participation or limits materially differ;
- direct verified information and map links.

Do not repeat card details in the introduction. Do not display research telemetry
unless the user asks for an audit.

## 5. Finalize once; cache automatically

Get the supported compact payload shape instead of reading validator source:

```sh
python3 <source_dir>/scripts/finalize_briefing.py --print-template
```

Mark each option `discovery_origin` as `fresh` or `cache`. Include its stable
`place` block when current evidence supports it; shortlist saving automatically
upserts those stable pointers without blocking the recommendation if cache state
is unusable. Never place hours, events, closure, price, booking or weather in the
stable place block.

Run `finalize_briefing.py` once with the completed payload. Paste its
`numbered_options_markdown` verbatim. If finalization fails, report the validation
gap; never replace it with unsupported freehand recommendations.
