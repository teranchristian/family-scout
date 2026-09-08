# Runtime tools for discovery and evidence

Read this file before live discovery. It records operational lessons about which
of the available browser, search, fetching and geocoding tools reliably work for
which step, so effort is not wasted on a reader that cannot open a page. Treat
tool behaviour as situational: a given tool may or may not be present in this
Hermes environment, and may change behaviour. Verify on the first use of a
session rather than assuming a tool works.

## Search and discovery vs page reading

Some search backends are discovery-only: they return search results or snippets
but **cannot extract the body of an opened page** (for example a backend may
report "cannot extract URL content" when asked to read one). That is fine for
finding leads; it is not a reader.

- Use search tools to discover candidate URLs and facts.
- Use a **page-reading tool** that can actually open and return a current page's
  content for hard verification. Do not treat a snippet as proof of current
  opening, price or eligibility (see `discovery.md`).
- If the available page-reading tool works (e.g. a `web_fetch`/extraction MCP
  such as the one exposed under the `donsetch` name), prefer it for current
  pages over a search-only backend. Do not assume that named tool is always
  present; pick whatever reader is actually available.

## Geocoding public places and venues

When you need coordinates for a venue (for example to compare an inclusive
radius), geocode the **public place or venue** only — never a private address or
exact home location.

- Use a geocoding service that returns coordinates for a public place name. A
  plain `curl` to the Nominatim (OpenStreetMap) search endpoint is one reliable
  option where network access allows.
- Treat returned coordinates as evidence to feed the helper's `distance`
  calculation; the helper itself does not geocode.
- Keep venue/place coordinates in the shortlist as a public place label and
  coordinates, never as a private address.

## Opaque PDF link handles

Calendar and listing pages (including some municipal sites) may expose download
links (PDFs, documents) as an **opaque handle** rather than a real URL. Such a
handle often does not resolve when passed back to the page reader and may time
out.

- When you need a linked PDF, do a fresh search for the raw file URL instead of
  chasing the opaque handle.
- If the raw PDF still cannot be read, try an alternative reader path (below),
  then report the candidate as unverified if the important fact cannot be
  established.

## Alternative reader paths before giving up

One failed page, PDF or reader path must not end the relevant line of research.
Within the remaining budget, try another accountable source:

- the facility's own page, a municipal or civic index page,
- an accessible HTML version or a different document format (PDF vs. HTML),
- the booking or ticket page,
- a different tool that can open the same URL.

Record failed reads (as `failed` consulted sources). If the fact still cannot be
established, label the candidate unverified; never promote it to a confirmed
match, and never silently substitute a less relevant result.

## Validate every link before sharing

Every URL shown to the user must be checked during the current search. A search
result, snippet, cached title or previously saved URL is not a link check.

- For factual and booking links, open and read the exact URL after redirects.
  Confirm that the resulting page is the intended current venue, branch,
  activity or session and still contains the fact the link is meant to support.
- For a navigation link, perform a current reachability check and confirm that
  its destination or query names the same current venue and address. A map is
  navigation evidence only, never operating-status evidence.
- Replace a redirected URL with the current canonical destination when it still
  targets the intended content.
- Reject `404`/`410`, other HTTP error responses, failed reads, login/error
  interstitials, soft-404 pages such as “not found” content returned with a
  success code, and redirects to an unrelated or generic page.
- Opaque result handles are tool-local references, not user-facing URLs. Resolve
  the real `http(s)` target and check it before sharing.

Record every link intended for the answer in the option's `link_checks` with its
purpose, result and check time. Use `content_verified` only after reading the
correct factual or booking page; use `reachable` only for a navigation link that
was actually checked. If a useful nonessential link cannot be validated, omit it
and give the verified address or facts in text. If the link is essential to a
hard fact, the option is unverified and cannot be promoted.
