# Helper CLI contract

The helper owns deterministic validation, distance calculations, identity and
safe persistence. Hermes owns language understanding, live search, source
reading, evidence selection and qualitative ranking.

Read `installation.json` beside the installed skill, then invoke:

```sh
python3 <source_dir>/scripts/family_scout.py --data-dir <data_dir> status
```

Commands emit JSON on stdout. Validation and state errors emit JSON on stderr
and exit with status 2. Never bypass an error by editing or replacing private
state. Payloads are JSON files or JSON on stdin with `--input -`. For append-only
writes, create a lowercase operation ID and reuse exactly that ID after an
uncertain retry. Stable-place cache writes instead upsert one exact identity.

## Read context

```sh
python3 <source_dir>/scripts/family_scout.py --data-dir <data_dir> \
  context --at 2030-04-06T09:00:00Z --location auto
```

`context` returns the full private profile, applicable location, enabled sources,
recent shortlists and effective feedback. Do not quote or send this object to a
web tool. `--location home` explicitly ignores active travel. `status` is the
redacted setup check.

## Exact ages on an activity date

The private `profile.yaml` may store an optional `date_of_birth` for any
`group_members` entry as an ISO `YYYY-MM-DD` date. This is private data:
never commit actual birthdates or include them in external searches or
`delegate_task` contexts. Ask for and save birthdates only when the user
explicitly provides and approves them.

`context` and `discovery_context.py` expose
`effective_member_ages` and `age_as_of` for the current **local**
date, without altering the saved profile. If the activity is on another
date, **always** calculate on that activity date before checking age
eligibility:

```sh
python3 <source_dir>/scripts/family_scout.py --data-dir <data_dir> \
  ages-on --date 2030-04-07
```

The local `ages-on` command returns member IDs, effective ages and their
basis; it does not include birthdates. `date_of_birth` overrides a legacy
numeric `age`; where it is absent, the existing numeric age remains a
fallback and may become stale. For an event range crossing a birthday,
calculate separately on each relevant date. A child who has not been born
by the requested historical date returns an unknown age rather than a
negative age. Leap-day birthdays advance on 1 March in non-leap years.
Pass only derived ages or age bands to child agents and external tools.

When updating the `group_members` list, provide the **complete** list of
members, retaining their IDs and other saved fields: profile-update
replaces lists rather than merging individual members. Never infer
missing birthdates from ages.

## Update explicit profile facts

```json
{
  "operation_id": "op-profile-example",
  "reviewed_at": "2030-04-06T09:00:00Z",
  "source": "explicit_user",
  "changes": {
    "home": {
      "label": "Example City",
      "latitude": 0,
      "longitude": 0,
      "timezone": "Etc/UTC"
    },
    "travel": {
      "label": "Sample Town",
      "latitude": 1,
      "longitude": 1,
      "timezone": "Etc/UTC",
      "expires_at": "2030-04-08T23:59:59+00:00"
    }
  }
}
```

```sh
python3 <source_dir>/scripts/family_scout.py --data-dir <data_dir> \
  profile-update --input update.json
```

Only persist facts the user explicitly asks to remember. To clear travel, set it
to `null`. The `.yaml` state documents are written as indented JSON, which is
valid YAML and can be parsed safely with the Python standard library. The two
original blank Phase 0 templates are migrated on the first write. Other YAML
styles are never rewritten automatically; the helper reports an error and
preserves their bytes.

## Manage custom sources

Add a source with an operation ID:

```json
{
  "operation_id": "op-source-example",
  "source": {
    "name": "Example Events",
    "url": "https://events.example.org",
    "enabled": true,
    "scope": {"place": "Example City"},
    "query_guidance": "Use for public activity leads"
  }
}
```

```sh
python3 <source_dir>/scripts/family_scout.py --data-dir <data_dir> source-add --input source.json
python3 <source_dir>/scripts/family_scout.py --data-dir <data_dir> source-disable --id <source-id> --operation-id op-disable-example
python3 <source_dir>/scripts/family_scout.py --data-dir <data_dir> source-enable --id <source-id> --operation-id op-enable-example
python3 <source_dir>/scripts/family_scout.py --data-dir <data_dir> source-remove --id <source-id> --operation-id op-remove-example
```

Never query disabled or removed sources deliberately.

## Venue cache disabled for recommendations

Do not read or write `places.jsonl` in recommendation sessions. Do not call
`place-cache-leads`, `place-cache-lookup` or `place-cache-upsert`, even
after finding an otherwise interesting venue. These old commands are retained
only for backwards compatibility; normal shortlist saving no longer updates
the venue cache. Keep the existing private file untouched.

Current-run evidenced addresses can still be supplied as `place` blocks to
generate navigation links. Saving exact shortlist history, family settings and
explicit feedback is separate from caching venue candidates.

## Calculate distance and classify candidates

`distance` returns Haversine distance in kilometres. Coordinates must come from
evidence; the command does not geocode.

```sh
python3 <source_dir>/scripts/family_scout.py distance \
  --origin-lat 0 --origin-lon 0 --venue-lat 0.01 --venue-lon 0.01
```

`evaluate --input evaluation.json` accepts a `request` object and a `candidates`
array. Provide only facts supported by current sources. It classifies radius,
date overlap, free/budget, indoor-only, attending-member age eligibility,
closure/cancellation and mandatory-booking availability as `confirmed_match`,
`confirmed_failure` or `unverified`. If any hard requirement fails, exclude the
candidate. If one remains unverified, it may appear only under **Needs checking**.

## Save the exact shortlist

For recommendations, do not inspect validator source. Print the appropriate
compact one-shot payload template instead:

```sh
python3 <source_dir>/scripts/finalize_briefing.py --print-template --template-mode explore
python3 <source_dir>/scripts/finalize_briefing.py --print-template --template-mode verified
```

Normal effort allows an initial `explore` menu of at most eight options or a
selected `verified` result of at most three options, with three search queries
and twelve external calls total across search, source reading, forecast and
geocoding. All options originate in fresh discovery; omit the optional
`discovery_origin` field. A current-run evidenced `place` block is useful
for generating a map link, not for caching. Honest overages are saved with
`budget_status: exceeded`; they are never rejected or rewritten.

Call `shortlist-save` before displaying the response. The request stores an
origin reference and public place label, never private coordinates or an address.
Each option needs current source URLs and a retrieval timestamp. This arbitrary
example is deliberately unrelated to any person:

```json
{
  "operation_id": "op-search-example",
  "created_at": "2030-04-06T09:00:00Z",
  "conversation_ref": "conversation-example",
  "effort_mode": "normal",
  "result_mode": "verified",
  "request": {
    "origin_ref": "explicit",
    "place_label": "Example City",
    "date_start": "2030-04-07",
    "date_end": "2030-04-07",
    "timezone": "Etc/UTC",
    "radius_km": 10,
    "attending_member_ids": [],
    "free_only": true
  },
  "weather": {
    "status": "unknown",
    "reason": "outside forecast coverage"
  },
  "options": [
    {
      "title": "Example Activity",
      "venue": "Example Hall",
      "date_start": "2030-04-07T10:00:00+00:00",
      "date_end": "2030-04-07T11:00:00+00:00",
      "checked_at": "2030-04-06T09:00:00Z",
      "source_urls": ["https://events.example.org/example-activity"],
      "link_checks": [
        {
          "url": "https://events.example.org/example-activity",
          "purposes": ["facts"],
          "result": "content_verified",
          "checked_at": "2030-04-06T09:00:00Z"
        }
      ],
      "distance_km": 1.2,
      "cost": {"status": "known", "amount": 0, "currency": "XXX", "basis": "attending group"},
      "indoor_status": "indoor",
      "booking": {"required": false, "availability": "not_applicable"},
      "why": "The current listing confirms a free, hands-on session.",
      "constraint_results": [
        {"requirement": "radius", "status": "confirmed_match", "reason": "inside inclusive boundary"},
        {"requirement": "date", "status": "confirmed_match", "reason": "usable interval overlaps"},
        {"requirement": "free_only", "status": "confirmed_match", "reason": "mandatory group cost is zero"}
      ],
      "features": ["hands-on"]
    }
  ],
  "needs_checking": [],
  "consulted_sources": [
    {"url": "https://events.example.org/example-activity", "status": "read"}
  ],
  "tool_usage": {"search_queries": 1, "source_fetches": 1,
                 "forecast_lookups": 0, "geocode_lookups": 0}
}
```

Copy each option's applicable `requirements` from the `evaluate` result into
`constraint_results`; the helper refuses a displayed option when a hard result
is missing, failed or unverified. The result returns a stable `search_id`.
Reusing the same operation ID does not
append a duplicate. Different pages for the same activity occurrence belong in
one option's `source_urls`; different dated sessions receive separate session
identities.

`link_checks` is the complete list of links that may appear in the option card.
Every `source_urls` entry must have a matching `content_verified` check with the
`facts` purpose. A mandatory booking needs a `content_verified` link with the
`booking` purpose. A manually checked navigation link may use `reachable`; the
helper's exact-address Google Maps link uses `generated`, both with purpose
`map`. Do not put `failed`, unchecked, search-handle, 404/soft-404 or
wrong-target URLs in `link_checks`, and do not add a link to the displayed answer
after `shortlist-save` succeeds. Apply the same structure to a **Needs checking**
lead whenever it includes a link.

Resolve later phrases such as “number 1” with one unambiguous reference:

```sh
python3 <source_dir>/scripts/family_scout.py --data-dir <data_dir> \
  resolve-option --number 1 --search-id <search-id>
```

If a conversation reference matches multiple shortlists, the helper refuses to
guess. Ask the user which search or activity they mean.

## Append explicit feedback or a correction

```json
{
  "operation_id": "op-feedback-example",
  "search_id": "<search-id>",
  "option_number": 1,
  "state": "liked",
  "features": [{"feature": "hands-on", "sentiment": "positive"}],
  "member_ids": [],
  "context": null,
  "original": "We liked the hands-on part."
}
```

```sh
python3 <source_dir>/scripts/family_scout.py --data-dir <data_dir> feedback-add --input feedback.json
```

Valid states are `liked`, `disliked`, `saved`, `interested`, `visited`, `bored`,
`too_crowded`, `too_expensive`, `too_much_walking`, `note` and `retracted`.
Separate multiple observations into feature objects. For a correction or
retraction, append a new event with `supersedes_event_id`; never edit JSONL.
