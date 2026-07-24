#!/usr/bin/env python3
"""Build data/journals-seed.json from the free OpenAlex sources API.
Real numbers, snapshotted. 2yr_mean_citedness is an impact-factor-like proxy."""
import json, sys, time, urllib.parse, urllib.request

MAILTO = "submission-desk@example.com"

# Curated, field-diverse, medicine-weighted (this tool's audience).
NAMES = [
    "New England Journal of Medicine", "The Lancet", "JAMA",
    "BMJ", "Nature", "Science", "Cell",
    "Proceedings of the National Academy of Sciences", "Nature Medicine",
    "Nature Communications", "Scientific Reports", "PLOS ONE", "PLOS Medicine",
    "Journal of Clinical Oncology", "Circulation",
    "Journal of the American College of Cardiology", "Gastroenterology",
    "Diabetes Care", "Annals of Internal Medicine", "JAMA Internal Medicine",
    "The Lancet Oncology", "Blood", "Journal of Clinical Investigation",
    "Radiology", "Chest", "Critical Care Medicine", "Anesthesiology",
    "Medical Education", "Academic Medicine",
    "Advances in Health Sciences Education", "Perspectives on Medical Education",
    "BMC Medical Education", "Medical Teacher", "Teaching and Learning in Medicine",
    "BMJ Open", "PeerJ", "Cureus", "Heliyon", "eLife", "The Lancet Digital Health",
]

def fetch(name):
    q = urllib.parse.quote(name)
    url = (f"https://api.openalex.org/sources?search={q}"
           f"&filter=type:journal&per_page=1&sort=cited_by_count:desc&mailto={MAILTO}")
    req = urllib.request.Request(url, headers={"User-Agent": f"submission-desk ({MAILTO})"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.load(r)
    res = data.get("results") or []
    if not res:
        return None
    s = res[0]
    ss = s.get("summary_stats") or {}
    cites = ss.get("2yr_mean_citedness")
    concepts = s.get("x_concepts") or []
    field = concepts[0]["display_name"] if concepts else ""
    return {
        "name": s.get("display_name"),
        "issn": s.get("issn_l") or (s.get("issn") or [""])[0] or "",
        "publisher": s.get("host_organization_name") or "",
        "if_proxy": round(cites, 2) if cites is not None else None,
        "h_index": (ss.get("h_index")),
        "apc_usd": s.get("apc_usd"),
        "in_doaj": bool(s.get("is_in_doaj")),
        "is_oa": bool(s.get("is_oa")),
        "field": field,
        "openalex": s.get("id"),
        "homepage": s.get("homepage_url") or "",
    }

out = []
for n in NAMES:
    try:
        rec = fetch(n)
        if rec:
            out.append(rec)
            print(f"ok  {rec['name'][:40]:40} IF~{rec['if_proxy']}  APC={rec['apc_usd']}")
        else:
            print(f"MISS {n}", file=sys.stderr)
    except Exception as e:
        print(f"ERR {n}: {e}", file=sys.stderr)
    time.sleep(0.15)

# sort by if_proxy desc for a sensible default order
out.sort(key=lambda r: (r["if_proxy"] or 0), reverse=True)
snapshot = {
    "schema": "submission-desk/journals-seed@1",
    "source": "OpenAlex sources API (free). if_proxy = 2-year mean citedness, an "
              "impact-factor-like proxy — NOT the official Clarivate JIF.",
    "snapshot_utc": "2026-07-25",
    "count": len(out),
    "journals": out,
}
path = sys.argv[1] if len(sys.argv) > 1 else "journals-seed.json"
with open(path, "w", encoding="utf-8") as f:
    json.dump(snapshot, f, ensure_ascii=False, indent=2)
print(f"\nwrote {len(out)} journals -> {path}")
