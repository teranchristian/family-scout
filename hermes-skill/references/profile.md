# Load saved context — no new profile system

Read the installed `installation.json` beside `SKILL.md`. It has absolute `source_dir` (Git checkout) and `data_dir` (private state). **Read these paths, never change the manifest.**

At the start of an activity search run this existing helper **once**:

```sh
python3 <source_dir>/scripts/discovery_context.py --data-dir <data_dir>
```

Use its `resolved_location`, `profile`, `enabled_sources`, `effective_member_ages` and `age_as_of` only for local reasoning. The context intentionally contains **no prior shortlists or feedback**; do fresh discovery first. Do not print the full private context in the reply, send it to a subagent or include it in web queries.

## Interpret the request

- **Location:** explicit request first; otherwise the helper's current travel/home location. Derive public nearby suburbs from the anchor area and the user's saved radius/geographic preferences. Don't automatically expand beyond a specified hard radius. If nearby boundaries aren't certain, search plausible public suburbs but don't claim an exact distance.
- **Attendees:** "my kids" means the children in `profile.group_members`, not every adult; a named child limits the age target accordingly. For "family", consider the attending family members but still explain fit for each child.
- **Ages:** for an outing on another date, calculate exact **effective ages** using the helper, not a remembered age or birthdate given to web tools:

```sh
python3 <source_dir>/scripts/family_scout.py --data-dir <data_dir> ages-on --date YYYY-MM-DD
```

  Repeat for a separate date only when necessary, including birthdays within the window. Birthdate-derived ages override saved numeric ages. Only send age bands to agents.
- **Preferences:** favour explicit interests, free/affordable options, travel convenience and the current instruction. A preference is not a hard exclusion unless saved as a constraint. Enabled custom sources are leads, not substitutes for discovery; skip disabled ones.
- **Dates:** resolve "today", "tomorrow" and weekday/weekend references in the activity location's timezone; use absolute dates for every agent.

## Safe memory actions — only when asked

Ordinary searches are **read-only**. Preserve all existing private files (`profile.yaml`, `sources.yaml`, `shortlists.jsonl`, `feedback.jsonl`) and do not edit or delete them. If the user explicitly asks to save a lasting profile change, add a source or record feedback, use the **existing** `family_scout.py` CLI (`profile-update`, `source-add`/`source-disable`/`source-enable`/`source-remove`, `feedback-add`) and inspect the relevant `--help` plus an existing valid payload contract; never hand-edit data. Do not treat merely selecting an activity or asking a follow-up as positive feedback. Never turn personal facts into edits to the Git-owned skill.
