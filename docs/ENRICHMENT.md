# Journal enrichment & data sources

How the **Add journal** search works, what the numbers mean, and where to get
the *official* figures. Short version: the tool auto-fills real journal data so
you stop typing mock numbers — but the impact-factor column is a **proxy**, and
the honest official number lives at JCR.

## Using the search

On the **Candidates** tab, type into **🔍 Search real journals**:

1. Before you type, the box shows a **built-in cached list** of ~40 well-known
   journals. This works offline and never rate-limits.
2. As you type, it queries the live API (`/api/journals`) for anything else.
3. Pick a result → a row is added with the **real name, IF proxy, APC, and DOAJ
   status** pre-filled. Acceptance rate, fit and weeks stay yours to set
   (they are not in any public dataset — see [METHOD.md](METHOD.md)).

`+ Blank row` still adds an empty row for fully manual entry.

## What the IF column actually is

The auto-filled IF is OpenAlex's **2-year mean citedness** — mean citations per
document across *all* document types. It is impact-factor-*shaped* but:

- it runs **lower** than the official JIF (which counts only "citable items"), and
- for news/editorial-heavy journals it can be misleadingly low (we blank obvious
  artifacts rather than show a fake `0`).

**It is NOT the official Clarivate Journal Impact Factor.** Treat it as a
starting estimate and overwrite it. For the real number, use **JCR** (linked in
the app's **Resources** tab).

## Where the data comes from (the pipeline)

`GET /api/journals?q=…` is a Cloudflare Pages Function (`functions/api/journals.js`):

1. **OpenAlex** `sources` — rich metrics (IF proxy, APC, DOAJ, publisher).
2. **Crossref** `journals` — fallback when OpenAlex rate-limits the shared
   Workers egress IP; returns real titles + ISSN, metrics blank.
3. Successful responses are edge-cached for 24h.

If both APIs are unreachable, the front end falls back to the embedded cached
list, so the dropdown always offers real journals.

The seed list is regenerated with `python3 tools/build_seed.py data/journals-seed.json`
(snapshotted, so numbers stay reproducible).

## Getting the official Journal Impact Factor (Clarivate WoS)

The Function has a **reserved adapter** for the official JIF. To turn it on:

1. Get a key at <https://developer.clarivate.com/apis/wos-journal>.
2. Add it as a Pages environment variable named `CLARIVATE_API_KEY`
   (Cloudflare dashboard → your Pages project → Settings → Environment variables,
   encrypted). No code change needed to store it.
3. Implement the `TODO` in `enrichWithClarivate()` in `functions/api/journals.js`
   (per-ISSN request, read the JIF, override `if_proxy`). When the key is
   present the API reports `source: "…+clarivate"`.

Until then, everything runs on the free OpenAlex/Crossref path.

## Curated resources (the Resources tab)

Every column and gate maps to a real tool — official metrics (JCR, Scopus),
journal finders (JANE, Elsevier/Springer/Wiley, WoS Manuscript Matcher),
legitimacy (DOAJ, Think-Check-Submit, COPE), **APC/fees**
([Taylor &amp; Francis OA Cost Finder](https://authorservices.taylorandfrancis.com/choose-open/publishing-open-access/open-access-cost-finder/),
DOAJ, cOAlition S Journal Checker), and indexing (PubMed, Scopus). Open the
**Resources** tab in the app for the full, clickable list.
