# Context, feedback and similarity

Read this file for explicit feedback, corrections, profile/travel changes,
custom-source changes and “more like this” requests. The CLI reference owns the
exact commands and payloads.

## Separate memory from skill code

Family Scout's procedures come from its Git repository and installed read-only
skill. **Do not use Hermes's general memory, procedural learning, `skill_manage`
or a shadow skill to patch Family Scout's `SKILL.md`, references, helper code
or rules.** If feedback reveals a software defect or improved procedure,
report it for a separate reviewed Git change; never silently adopt a new
procedure in agent memory.

Store user-approved Family Scout preferences in the **private** `profile.yaml`
using `profile-update`; add explicit likes/dislikes with `feedback-add` and
approved custom sources through source commands. Keep these outside Git. Hermes
may keep general factual memory separately, but it must not be treated as an
automatic sync mechanism for Family Scout preferences, nor override the skill's
procedures or the user's current request.

## Persistent context

Persist only lasting facts the user explicitly asks Family Scout to remember.
Member `date_of_birth` is optional and private; collect/save it only with
explicit consent. Use `ages-on` for the outing date instead of copying a
stale static age. Updating `group_members` requires the complete list
because lists are replaced, so preserve all existing member fields.
Use `profile-update` for a home/profile correction, lasting preference or travel
interval with an explicit expiry. A temporary location, weather request or
attending group is not automatically persistent. Never attach a default party
to a saved location; outing attendance is request-specific.

Use source commands for explicit addition, enable/disable and removal. A new
applicable source is attempted on the next matching search. A broken source does
not fail the entire request.

## Explicit feedback only

For “number N”, use the current search ID or conversation reference with
`resolve-option`. If several saved shortlists could apply, ask which search or
activity; never guess.

Use `feedback-add` only for explicit liked/disliked, saved, interested, visited,
bored, crowded, cost, walking or free-form feedback. Preserve the user's concise
original wording. Separate distinct observations into traceable features and
distinguish the activity from visit-specific context. A selection, follow-up
question, displayed option or silence is not feedback.

Corrections and retractions append an event referring to the superseded event;
never rewrite JSONL. Effective context excludes superseded signals. Current
instructions override learned patterns, and one contextual complaint must not
blacklist a category. Explicit and repeated feedback outweighs tentative
feedback.

## More like this

Resolve the saved activity first. Use only evidenced features such as topic,
hands-on/passive format, activity type, age fit, duration or convenience. Ask
which feature matters only when the answer would substantially change the
search. “More like this” does not itself persist a preference.

Then follow the full discovery and briefing references. Continue to enforce the
current place, dates, group, cost and other constraints, and explain the
traceable similarity briefly.
