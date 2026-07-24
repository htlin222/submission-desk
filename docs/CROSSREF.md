# Crossref indices

How Submission Desk pulls journal figures from a public source instead of asking you to type an estimate, and what "deterministic" can and cannot mean when the source is a living database.

## The determinism problem

Crossref is continuously updated: citations accrue, publishers backfill metadata, records get corrected. A query run today and the same query run next month will disagree. So a live API call is *reproducible in procedure* but not *reproducible in result* — which is the weaker of the two properties, and not the one you want when a number ends up in a methods section.

The fix is to make the artefact, not the query, the deterministic object:

```
ISSN list  +  pinned parameters  →  [Crossref]  →  snapshot.json  →  the tool
                                                   ▲
                                          this file is the fixed point
```

`tools/crossref_index.py` writes a dated snapshot recording:

- every request URL it issued, in order
- every pinned parameter that shaped the result
- a SHA-256 over the concatenated raw responses
- the UTC timestamp of the run

Given that file, the numbers are fixed forever, their derivation is inspectable, and the hash shows nobody edited them by hand afterwards. Re-running is a *drift check*, not a reproduction attempt — `--verify` reports what moved and expects movement.

Cite the snapshot date alongside any figure you take from it.

## What Crossref can give you

| Column in the tool | Crossref index | Confidence |
|---|---|---|
| Impact factor | `citation_rate` — mean open citations to articles from a two-year window | Medium |
| Weeks to decision | `review_lag_days` — median (accepted − received) from article-history assertions | High **where deposited**, otherwise unavailable |
| — | `accept_to_issue_days` — median (issued − accepted) | Medium |
| — | `works_per_year` — deposited DOIs by issued year | High |
| — | `license_coverage` — fraction of works carrying a licence | Low |

## What it cannot

**Acceptance rate.** Not in Crossref, and mostly not published anywhere. This remains a manual column and is the single biggest source of uncertainty in the model.

**APC.** Not in Crossref. `license_coverage` hints at open access but does not price it. Check DOAJ or the journal site.

**Fit.** Not a property of the journal at all — it is a property of the pairing between your manuscript and the journal, and no database holds it. This is the column you have to think about, which is also why it is the one the evidence says matters most.

## Coverage gating

Metadata deposit is wildly uneven. Measured on 2024–2025 articles:

| Journal | Publisher | Article-history coverage | Review lag |
|---|---|---|---|
| Scientific Reports | Springer Nature | 100% | 125 d (17.9 wk) |
| BMC Cancer | Springer / BMC | 97% | 128 d (18.2 wk) |
| BMC Medicine | Springer / BMC | 97% | 160 d (22.9 wk) |
| Haematologica | Ferrata Storti Foundation | **0%** | *unavailable* |

Springer Nature deposits article history consistently. Many society journals deposit none at all, and their lag simply cannot be computed from Crossref — no amount of querying will conjure it.

So the tool **refuses to report a figure below 30% coverage**, returning `null` with a stated reason rather than a median over a handful of outliers. Silence is the honest output when the data is not there; a number computed from 3% of articles would look identical to one computed from 97%, and that is exactly the failure mode worth designing against.

Every reported index carries its own `coverage`, `confidence` and `caveat` fields. Read them.

## Two caveats that matter

**`citation_rate` is not the Impact Factor.** Crossref counts citations only from publishers that deposit open reference lists. Coverage is good and improving but not universal, so the figure reads low for journals whose citing literature sits behind closed deposits. In the sample above, Haematologica scores 2.35 — far below its actual standing. Use `citation_rate` to compare journals within a similar publishing ecosystem; do not report it as an absolute, and do not mistake it for a JIF.

Also note that single-page items — editorials, letters, meeting abstracts — are excluded from the mean, because society journals deposit large numbers of them and they drag the average toward zero. The unfiltered figure is kept as `value_all_types` so you can see the effect.

**`review_lag_days` measures submission to acceptance, not time to first decision.** It includes every revision round, so it runs longer than the "weeks" the scoring model wants. It also only counts manuscripts that were *accepted* — rejected submissions leave no Crossref record at all, so this is a floor on the experience, not an average of it. The import routine says so on screen. If you are modelling time to first decision, adjust downward.

## Usage

```bash
# one-off
python3 tools/crossref_index.py --issn 1741-7015 2045-2322 \
    --mailto you@university.edu -o data/snapshots/mine-2026-07-24.json

# from a list, with a bigger sample for tighter lag estimates
python3 tools/crossref_index.py --issn-file my-issns.txt \
    --mailto you@university.edu --lag-sample 500 \
    -o data/snapshots/oncology-2026-07-24.json

# check drift against an existing snapshot
python3 tools/crossref_index.py --verify data/snapshots/mine-2026-07-24.json \
    --mailto you@university.edu
```

Then open the tool and use **Load Crossref snapshot**. The file is read locally through the browser's file API — the tool still makes no network calls and still stores nothing.

`--mailto` is required. It puts you in Crossref's polite pool, which is faster and more stable, and it is the courtesy the API asks for in return for being free and unauthenticated.

## Pinned parameters

Changing any of these changes the numbers, so all of them are written into every snapshot's provenance block:

| Parameter | Default | Effect |
|---|---|---|
| `citation_window_years` | 2 | Matches the JIF window, for comparability of shape |
| `citation_anchor_offset` | 1 | Anchors on the last complete year |
| `lag_sample_size` | 300 | Works sampled for the lag estimate |
| `min_lag_coverage` | 0.30 | Below this, lag returns `null` |
| `min_citation_sample` | 30 | Below this, citation rate returns `null` |
| `sort` / `order` | `issued` / `asc` | With cursor paging, gives a stable traversal |

## Adding a snapshot to the repo

Snapshots are small, plain JSON and are meant to be committed — they are the evidence for whatever ranking you produced. Put them in `data/snapshots/` named `<scope>-<YYYY-MM-DD>.json`. Bulk working pulls belong in `data/raw/`, which is gitignored.
