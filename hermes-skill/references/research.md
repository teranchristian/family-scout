# Event discovery and weather — one shared workflow

Use this reference for **any broad dated or undated activity search**. Local and nearby event agents receive the **same instructions**, differing only in their assigned area. Do not create separate local-vs-nearby rules.

## Shared instructions for Agent 1 and Agent 2

Inputs: public area/suburbs; absolute dates (or the stated undated horizon); children's **derived age bands**, any explicit attending subset, budget/radius/preferences and requested language. Never receive the private family profile, birthdates, names or home coordinates.

1. Search **fresh, current sources** in your assigned area: council **general event calendars**, library/event-program calendars, community centres, neighbourhood groups, parks, galleries, seasonal events, workshops, festivals, performances and hands-on experiences. Don't search only for pages labelled "kids"; interesting general events can fit families too.
2. **Discover a wide variety of interesting activities, both free and paid. Do not exclude activities because of price or booking requirements unless explicitly requested.** No default `free_only`, budget or booking hard filter; keep unknown prices and booking status as labelled details. Consider community and commercial events fairly. Prioritise one-off, seasonal, educational, interactive or surprising experiences over ordinary playgrounds and generic attractions. Include worthwhile everyday options when a date has few special events.
3. **Search every requested day equally**, whether weekday or weekend; cover all dates in each discovery round. Don't spend extra rounds on a day just because another has more results. A calendar listing or search snippet is a lead, not proof the event runs on the requested date. Read the current organiser/official event page when possible. Verify exact date/time, activity, age restrictions, group cost, booking and venue; check cancellations and closures. Ordinary opening hours do not prove a scheduled program is on.
4. Judge **participation for each attending child's age**, not only that a venue admits children. Note when one child can mainly watch while another participates. Keep a good venue if one promoted feature is closed **but another worthwhile activity is actually available**.
5. Return compact, deduplicable leads: `title, date/time, suburb, venue/address if evidenced, short description, child-age fit and limits, price, booking, official URL, verification status, caveat`. Include exact source URLs, not opaque search handles. Identify unverified facts explicitly. Don't invent candidates to meet a count.

**Research stopping rule:** For each discovery agent, perform **one broad search round** covering every requested date, then **at most one targeted gap-filling round** for under-covered dates or promising leads. Batch independent queries where supported. **Up to five worthwhile options per day is an output ceiling, not a discovery quota**: stop after the second round even with fewer than five, and stop sooner when results are strong. Verify the strongest leads first; include promising unverified leads under Needs checking. On a failed/blocked fetch, do not retry the same URL repeatedly; try at most one relevant alternative, then mark unverified and move on.

## Agent 1: optional saved suburb sources

Agent 1 **must still perform its ordinary fresh local search**, whether `location_sources.urls` is empty or not. If matched URLs exist, **fetch each saved page once as extra leads** within Agent 1's normal research rounds; investigate only plausible events on the requested dates. Do not favour saved-source results, duplicate known events, or start more generic searches to compensate for blocked/unhelpful URLs. A saved URL is not evidence that a particular event is running. **No separate Agent 4**; Agent 2 continues independent nearby research.

## Fetch tools and failures

Avoid repeated tool discovery. Where available, use the working DonSeTch `web_fetch` capability for page reading rather than unsupported `web_extract`; choose an available reader once, and do not retry known-unsupported tools in each agent. If no working page reader is available, keep promising leads labelled Needs checking instead of chasing dead ends.

## Agent 3: weather only

Check the forecast for **each requested date at the activity location** using available current weather data. Give high/low temperatures when supported, chance/amount of rain, wind or heat risks where relevant, and a concise outdoor/indoor implication. Note forecast uncertainty and dates outside forecast range. Do **not** research events or treat forecast as permission to ignore outdoor candidates unless the user asked for indoor-only.

## Parent: verify, rank and present

Merge both event lists, including any saved-source leads from Agent 1; deduplicate by event, venue and session date. Local discoveries get a fair chance: favour a strong nearby event over a similarly good famous attraction. Rank by actual enjoyment and age fit, specialness, distance/convenience, toddler practicality and forecast, **not by which agent/source found it**. Free/paid and booking status are displayed, not default exclusions. Only an explicit user-requested cost or booking constraint should exclude options.

Before recommending an item as confirmed, **open its direct official/organiser page** and check date/session, suitability, price when claiming "free", mandatory booking and relevant cancellations. A source page is proof only for what it says. **Keep promising leads with incomplete details under Needs checking** for the relevant day, specifying exactly what is unverified and linking the source; never silently discard them solely because a fact could not be confirmed. Do not present an unverified date/session as confirmed, or include events confirmed cancelled, outside the requested dates or unsuitable. If booking is required, say so; a booking requirement or unverified slot does not by itself exclude an event. Do not claim live availability without evidence.

Use an exact public venue address, when evidenced, to form a Google Maps search link; never invent coordinates or driving time. Do not present a generic council homepage as the direct event link if the event page exists. If the URL is broken, redirected to unrelated content or only a snippet, omit it or label it unverified. Check each factual link before displaying it.

Answer directly: short daily weather, then group activities **by each requested day** (any day of the week). Show **up to five worthwhile options per day**, if available, not a combined top-five across the request. Follow with a compact **Needs checking** group for promising unverified leads, labelled by day; identify the best pick and a wet-weather alternative for each day when useful. Never invent activities to reach five. Include an explicit **Good for: both / [one child] / the other child** line with a brief reason. Show **FREE / known price / price unknown**, **booking required / not required / unknown**, time, place, official URL and map when evidenced. Never pretend a recommendation is a booking. No mandatory saving, renderer, research audit or hard-coded quotas.
