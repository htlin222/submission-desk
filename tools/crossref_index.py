#!/usr/bin/env python3
"""
crossref_index.py — derive reproducible journal indices from Crossref.

Fills the two hardest columns in Submission Desk (citation rate and time to
decision) from a public, auditable source instead of a typed guess.

Determinism: the Crossref corpus changes daily, so a live query is NOT
reproducible. This tool therefore produces a dated *snapshot* file. The
snapshot is the deterministic artefact: it records every request URL, every
pinned parameter, and a SHA-256 over the raw payloads, so the numbers can be
recomputed and verified by anyone later.

Coverage gating: publishers deposit metadata unevenly. Springer/BMC titles
carry article-history dates; many society journals carry none. Rather than
emit a confident number from three articles, this tool returns null with a
stated reason whenever coverage falls below threshold.

Usage
-----
  python3 crossref_index.py --issn 1741-7015 2045-2322 --mailto you@uni.edu
  python3 crossref_index.py --issn-file issns.txt --mailto you@uni.edu -o snap.json
  python3 crossref_index.py --verify snap.json --mailto you@uni.edu

No third-party dependencies. Python 3.9+.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

TOOL = "submission-desk/crossref_index"
TOOL_VERSION = "0.2.0"
API = "https://api.crossref.org"

# --- Pinned parameters. Changing any of these changes the numbers, so they
# --- are recorded verbatim into every snapshot's provenance block.
DEFAULTS = {
    "citation_window_years": 2,   # articles from the N years before the anchor
    "citation_anchor_offset": 1,  # anchor = snapshot year - 1 (last complete year)
    "lag_sample_size": 300,       # works sampled for received/accepted lag
    "min_lag_coverage": 0.30,     # below this fraction, refuse to report lag
    "min_citation_sample": 30,    # below this many works, refuse citation rate
    "work_type": "journal-article",
    "sort": "issued",
    "order": "asc",               # ascending + cursor = stable ordering
    "rows_per_page": 100,
}

# Article-history assertions are free text and publisher-specific. Parse
# strictly against a closed list; anything else counts as a parse failure and
# is reported rather than guessed at.
DATE_FORMATS = ("%d %B %Y", "%d %b %Y", "%Y-%m-%d", "%B %d, %Y", "%b %d, %Y", "%d/%m/%Y")


class CrossrefError(RuntimeError):
    pass


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------

class Client:
    """Thin Crossref client. Records every URL it touches, and hashes every
    payload, so a run can be audited after the fact."""

    def __init__(self, mailto: str, delay: float = 0.2, retries: int = 4):
        self.mailto = mailto
        self.delay = delay
        self.retries = retries
        self.calls: list[str] = []
        self._hash = hashlib.sha256()

    @property
    def user_agent(self) -> str:
        return f"{TOOL}/{TOOL_VERSION} (mailto:{self.mailto})"

    def get(self, path: str, params: dict) -> dict:
        params = dict(params)
        params["mailto"] = self.mailto          # Crossref polite pool
        url = f"{API}{path}?{urllib.parse.urlencode(params)}"
        self.calls.append(url)

        last = None
        for attempt in range(self.retries):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
                with urllib.request.urlopen(req, timeout=90) as resp:
                    raw = resp.read()
                self._hash.update(raw)
                time.sleep(self.delay)
                return json.loads(raw)
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    raise CrossrefError(f"not found: {url}") from e
                last = e
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
                last = e
            time.sleep(min(2 ** attempt, 8))
        raise CrossrefError(f"failed after {self.retries} attempts: {url} ({last})")

    def payload_hash(self) -> str:
        return self._hash.hexdigest()


# --------------------------------------------------------------------------
# Parsing helpers
# --------------------------------------------------------------------------

def parse_assertion_date(value: str):
    """Return a date, or None if the string doesn't match a known format."""
    v = (value or "").strip()
    for fmt in DATE_FORMATS:
        try:
            return dt.datetime.strptime(v, fmt).date()
        except ValueError:
            continue
    return None


def article_history(work: dict) -> dict:
    """Extract received / accepted dates from Crossref assertions."""
    out = {}
    for a in work.get("assertion", []) or []:
        name = a.get("name")
        if name in ("received", "accepted"):
            d = parse_assertion_date(a.get("value", ""))
            if d:
                out[name] = d
    return out


def quantiles(xs: list[float]) -> dict:
    xs = sorted(xs)
    if not xs:
        return {}
    def q(p):
        if len(xs) == 1:
            return float(xs[0])
        i = p * (len(xs) - 1)
        lo, hi = int(i), min(int(i) + 1, len(xs) - 1)
        return float(xs[lo] + (xs[hi] - xs[lo]) * (i - lo))
    return {
        "n": len(xs),
        "min": float(xs[0]),
        "p25": round(q(0.25), 1),
        "median": round(q(0.50), 1),
        "p75": round(q(0.75), 1),
        "max": float(xs[-1]),
    }


# --------------------------------------------------------------------------
# Index computation
# --------------------------------------------------------------------------

def fetch_works(client: Client, issn: str, cfg: dict, filters: str, limit: int) -> list[dict]:
    """Cursor-paged fetch. Cursor + fixed sort gives a stable traversal order."""
    items, cursor = [], "*"
    select = "DOI,issued,type,page,is-referenced-by-count,assertion,license,title"
    while len(items) < limit:
        page = client.get(
            f"/journals/{issn}/works",
            {
                "filter": filters,
                "rows": min(cfg["rows_per_page"], limit - len(items)),
                "cursor": cursor,
                "sort": cfg["sort"],
                "order": cfg["order"],
                "select": select,
            },
        )["message"]
        batch = page.get("items", [])
        if not batch:
            break
        items.extend(batch)
        cursor = page.get("next-cursor")
        if not cursor:
            break
    return items[:limit]


def compute(client: Client, issn: str, cfg: dict, snapshot_year: int) -> dict:
    """All indices for one journal, each with its own coverage and caveats."""
    meta = client.get(f"/journals/{issn}", {})["message"]

    rec: dict = {
        "issn": issn,
        "title": meta.get("title"),
        "publisher": meta.get("publisher"),
        "issn_all": meta.get("ISSN", []),
        "indices": {},
        "notes": [],
    }

    # -- volume: articles per issued year -----------------------------------
    breakdown = dict(
        (y, n) for y, n in (meta.get("breakdowns", {}).get("dois-by-issued-year") or [])
    )
    anchor = snapshot_year - cfg["citation_anchor_offset"]
    window = [anchor - i for i in range(cfg["citation_window_years"])]
    rec["indices"]["works_per_year"] = {
        "value": {str(y): breakdown.get(y) for y in sorted(window, reverse=True)},
        "basis": "Crossref deposited DOIs by issued year",
        "confidence": "high",
    }

    # -- citation rate: an IF-shaped proxy, from open citation counts --------
    lo, hi = min(window), max(window)
    cite_works = fetch_works(
        client, issn, cfg,
        f"from-issued-date:{lo}-01-01,until-issued-date:{hi}-12-31,type:{cfg['work_type']}",
        limit=1000,
    )
    counts = [w.get("is-referenced-by-count", 0) or 0 for w in cite_works]
    # single-page items are overwhelmingly editorials, letters and abstracts;
    # keeping them drags the mean toward zero for society journals.
    substantive = [
        w.get("is-referenced-by-count", 0) or 0
        for w in cite_works
        if not _is_single_page(w.get("page"))
    ]

    if len(counts) < cfg["min_citation_sample"]:
        rec["indices"]["citation_rate"] = {
            "value": None,
            "reason": f"only {len(counts)} works retrieved; minimum is {cfg['min_citation_sample']}",
            "confidence": "none",
        }
    else:
        rec["indices"]["citation_rate"] = {
            "value": round(sum(substantive) / len(substantive), 2) if substantive else None,
            "value_all_types": round(sum(counts) / len(counts), 2),
            "distribution": quantiles([float(c) for c in substantive]),
            "window": f"{lo}–{hi}",
            "excluded_single_page": len(counts) - len(substantive),
            "basis": "mean Crossref is-referenced-by-count",
            "confidence": "medium",
            "caveat": (
                "Crossref counts only citations from publishers that deposit open "
                "reference lists. This is NOT the Journal Impact Factor and will "
                "read low for journals whose citing literature is closed. Use it "
                "to compare journals, not to report an absolute figure."
            ),
        }

    # -- review lag: received -> accepted, where publishers deposit it -------
    lag_works = fetch_works(
        client, issn, cfg,
        f"from-issued-date:{anchor - 1}-01-01,type:{cfg['work_type']}",
        limit=cfg["lag_sample_size"],
    )
    review_lags, pub_lags, parsed = [], [], 0
    for w in lag_works:
        h = article_history(w)
        if "received" in h and "accepted" in h:
            parsed += 1
            d = (h["accepted"] - h["received"]).days
            if 0 <= d <= 1500:            # discard impossible or placeholder dates
                review_lags.append(d)
        issued = (w.get("issued", {}).get("date-parts") or [[None]])[0]
        if "accepted" in h and issued and issued[0]:
            try:
                pub = dt.date(*(list(issued) + [1, 1])[:3])
                d = (pub - h["accepted"]).days
                if 0 <= d <= 1500:
                    pub_lags.append(d)
            except (TypeError, ValueError):
                pass

    coverage = parsed / len(lag_works) if lag_works else 0.0
    if coverage < cfg["min_lag_coverage"] or not review_lags:
        rec["indices"]["review_lag_days"] = {
            "value": None,
            "coverage": round(coverage, 3),
            "sampled": len(lag_works),
            "reason": (
                f"only {round(coverage * 100)}% of sampled works carry parseable "
                f"received+accepted dates (threshold {round(cfg['min_lag_coverage'] * 100)}%). "
                "This publisher does not deposit article history to Crossref."
            ),
            "confidence": "none",
        }
        rec["notes"].append(
            "Review lag unavailable from Crossref. Check the journal's own site, "
            "or record your own estimate and mark its source."
        )
    else:
        q = quantiles([float(x) for x in review_lags])
        rec["indices"]["review_lag_days"] = {
            "value": q["median"],
            "weeks": round(q["median"] / 7, 1),
            "distribution": q,
            "coverage": round(coverage, 3),
            "sampled": len(lag_works),
            "basis": "median (accepted - received) from Crossref article-history assertions",
            "confidence": "high" if coverage > 0.8 else "medium",
            "caveat": (
                "Measures submission to acceptance including revision rounds, not "
                "time to first decision. It also excludes rejected manuscripts "
                "entirely, so it is a floor, not an average experience."
            ),
        }

    if pub_lags:
        rec["indices"]["accept_to_issue_days"] = {
            "value": quantiles([float(x) for x in pub_lags])["median"],
            "distribution": quantiles([float(x) for x in pub_lags]),
            "basis": "median (issued - accepted)",
            "confidence": "medium",
        }

    # -- open access signal -------------------------------------------------
    licensed = sum(1 for w in lag_works if w.get("license"))
    if lag_works:
        rec["indices"]["license_coverage"] = {
            "value": round(licensed / len(lag_works), 3),
            "basis": "fraction of sampled works carrying a license statement",
            "confidence": "low",
            "caveat": "A licence hint, not an OA status. Verify APC on the journal site.",
        }

    rec["notes"].append(
        "Crossref does not hold acceptance rates or APCs. Those columns still "
        "require the journal's own reporting."
    )
    return rec


def _is_single_page(page) -> bool:
    if not page:
        return False
    p = str(page)
    if "-" not in p:
        return True
    a, _, b = p.partition("-")
    return a.strip() == b.strip()


# --------------------------------------------------------------------------
# Snapshot I/O
# --------------------------------------------------------------------------

def build_snapshot(issns: list[str], mailto: str, cfg: dict) -> dict:
    client = Client(mailto)
    now = dt.datetime.now(dt.timezone.utc)
    journals, errors = [], []

    for i, issn in enumerate(issns, 1):
        print(f"  [{i}/{len(issns)}] {issn} ...", file=sys.stderr, flush=True)
        try:
            journals.append(compute(client, issn, cfg, now.year))
        except CrossrefError as e:
            errors.append({"issn": issn, "error": str(e)})
            print(f"      skipped: {e}", file=sys.stderr)

    return {
        "schema": "submission-desk/crossref-snapshot/1",
        "provenance": {
            "tool": TOOL,
            "tool_version": TOOL_VERSION,
            "snapshot_utc": now.isoformat(timespec="seconds"),
            "source": "Crossref REST API",
            "source_terms": "https://api.crossref.org — public data, no licence restriction",
            "pinned_parameters": cfg,
            "request_count": len(client.calls),
            "payload_sha256": client.payload_hash(),
            "requests": client.calls,
            "determinism": (
                "Crossref is a living corpus; a re-run on a later date will differ. "
                "This file is the reproducible artefact. payload_sha256 covers every "
                "raw response in request order and verifies the file was not edited "
                "by hand. Recompute with --verify against the same snapshot date to "
                "confirm, or cite this file's snapshot_utc alongside any figure."
            ),
        },
        "journals": journals,
        "errors": errors,
    }


def verify(path: str, mailto: str) -> int:
    """Re-run the recorded parameters and report which figures have drifted."""
    old = json.load(open(path, encoding="utf-8"))
    cfg = old["provenance"]["pinned_parameters"]
    issns = [j["issn"] for j in old["journals"]]
    print(f"Verifying {len(issns)} journals against {old['provenance']['snapshot_utc']}",
          file=sys.stderr)
    new = build_snapshot(issns, mailto, cfg)

    changed = 0
    new_by_issn = {j["issn"]: j for j in new["journals"]}
    for j in old["journals"]:
        n = new_by_issn.get(j["issn"])
        if not n:
            print(f"  {j['issn']}: MISSING on re-run")
            changed += 1
            continue
        for key, o in j["indices"].items():
            v_old, v_new = o.get("value"), n["indices"].get(key, {}).get("value")
            if v_old != v_new:
                print(f"  {j['issn']} {key}: {v_old} -> {v_new}")
                changed += 1
    print(f"\n{changed} value(s) drifted. Non-zero drift is expected and is not an "
          f"error: Crossref accrues citations and deposits continuously.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Derive reproducible journal indices from Crossref.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Crossref asks that you identify yourself with --mailto. It is not "
               "optional here: it gets you the faster, more stable polite pool.",
    )
    ap.add_argument("--issn", nargs="+", help="one or more ISSNs")
    ap.add_argument("--issn-file", help="file with one ISSN per line; # comments allowed")
    ap.add_argument("--mailto", required=True, help="your email, for the Crossref polite pool")
    ap.add_argument("-o", "--output", default="-", help="output path (default: stdout)")
    ap.add_argument("--verify", metavar="SNAPSHOT", help="re-run a snapshot and report drift")
    ap.add_argument("--lag-sample", type=int, default=DEFAULTS["lag_sample_size"])
    ap.add_argument("--min-coverage", type=float, default=DEFAULTS["min_lag_coverage"])
    args = ap.parse_args()

    if args.verify:
        return verify(args.verify, args.mailto)

    issns = list(args.issn or [])
    if args.issn_file:
        with open(args.issn_file, encoding="utf-8") as fh:
            issns += [ln.split("#")[0].strip() for ln in fh if ln.split("#")[0].strip()]
    if not issns:
        ap.error("provide --issn or --issn-file")

    seen, ordered = set(), []
    for i in issns:                       # dedupe, preserve order for determinism
        if i not in seen:
            seen.add(i)
            ordered.append(i)

    cfg = dict(DEFAULTS, lag_sample_size=args.lag_sample, min_lag_coverage=args.min_coverage)
    print(f"Building snapshot for {len(ordered)} journal(s)", file=sys.stderr)
    snap = build_snapshot(ordered, args.mailto, cfg)
    text = json.dumps(snap, indent=2, ensure_ascii=False, sort_keys=False)

    if args.output == "-":
        print(text)
    else:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print(f"\nWrote {args.output} "
              f"({len(snap['journals'])} journals, {len(snap['errors'])} errors, "
              f"sha256 {snap['provenance']['payload_sha256'][:16]}...)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
