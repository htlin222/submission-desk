// GET /api/journals?q=<query>
// Same-origin Cloudflare Pages Function. Free journal enrichment.
//
// Primary source: OpenAlex "sources" — gives if_proxy (2-year mean citedness,
// an impact-factor-LIKE proxy, NOT the official Clarivate JIF), APC, DOAJ.
// Fallback: Crossref "journals" — robust from Workers' shared egress IPs when
// OpenAlex rate-limits (HTTP 429); returns real titles + ISSN, metrics blank.
// When CLARIVATE_API_KEY is set, enrichWithClarivate() can override with the
// official JIF (adapter reserved below). Verify official JIF at JCR.

const OPENALEX = "https://api.openalex.org/sources";
const CROSSREF = "https://api.crossref.org/journals";

export async function onRequestGet(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const q = (url.searchParams.get("q") || "").trim();
  if (q.length < 2) return json({ results: [], source: "none" });

  const cache = caches.default;
  const cacheKey = new Request(
    `${url.origin}/api/journals?q=${encodeURIComponent(q.toLowerCase())}`,
    request
  );
  const cached = await cache.match(cacheKey);
  if (cached) return cached;

  const mailto = env.OPENALEX_MAILTO || "submission-desk@users.noreply.github.com";
  const headers = { "User-Agent": `submission-desk (mailto:${mailto})` };

  let results = null;
  let source = "openalex";

  // 1) OpenAlex (rich metrics)
  try {
    const api =
      `${OPENALEX}?search=${encodeURIComponent(q)}&filter=type:journal` +
      `&sort=cited_by_count:desc&per_page=8&mailto=${encodeURIComponent(mailto)}`;
    const r = await fetch(api, { headers });
    if (r.ok) {
      const data = await r.json();
      results = (data.results || []).map(mapSource);
    }
  } catch (_e) {
    /* fall through to Crossref */
  }

  // 2) Crossref fallback (titles + ISSN only) when OpenAlex is unavailable/limited
  if (!results || results.length === 0) {
    try {
      const api = `${CROSSREF}?query=${encodeURIComponent(q)}&rows=8&mailto=${encodeURIComponent(mailto)}`;
      const r = await fetch(api, { headers });
      if (r.ok) {
        const data = await r.json();
        const items = (data.message && data.message.items) || [];
        if (items.length) {
          results = items.map(mapCrossref);
          source = "crossref";
        }
      }
    } catch (_e) {
      /* give up gracefully */
    }
  }

  results = results || [];

  // 3) Optional official JIF override
  if (results.length && env.CLARIVATE_API_KEY) {
    try {
      results = await enrichWithClarivate(results, env);
      source = source + "+clarivate";
    } catch (_e) {
      /* keep proxy values */
    }
  }

  const res = json({ results, source });
  if (results.length) {
    res.headers.set("Cache-Control", "public, max-age=86400");
    context.waitUntil(cache.put(cacheKey, res.clone()));
  }
  return res;
}

function mapSource(s) {
  const ss = s.summary_stats || {};
  let ifp = ss["2yr_mean_citedness"];
  ifp = ifp == null || ifp === 0 ? null : Math.round(ifp * 100) / 100;
  return {
    id: s.id,
    name: s.display_name,
    issn: s.issn_l || (s.issn && s.issn[0]) || "",
    publisher: s.host_organization_name || "",
    if_proxy: ifp,
    apc_usd: s.apc_usd ?? null,
    in_doaj: !!s.is_in_doaj,
    is_oa: !!s.is_oa,
    works: s.works_count ?? null,
    homepage: s.homepage_url || "",
  };
}

function mapCrossref(j) {
  const issn = (j.ISSN && j.ISSN[0]) || "";
  return {
    id: issn ? `issn:${issn}` : (j.title || ""),
    name: (j.title || "").trim(),
    issn,
    publisher: j.publisher || "",
    if_proxy: null,
    apc_usd: null,
    in_doaj: false,
    is_oa: false,
    works: null,
    homepage: "",
  };
}

// --- Clarivate WoS Journal API adapter (RESERVED) --------------------------
// Activates only when env.CLARIVATE_API_KEY is set. Docs:
//   https://developer.clarivate.com/apis/wos-journal
// For each ISSN, request the official Journal Impact Factor and override
// if_proxy with the real JIF (set r.jif and r.if_source = "clarivate").
async function enrichWithClarivate(results, env) {
  // TODO: implement once a key is available, e.g.:
  //   const r = await fetch(
  //     `https://api.clarivate.com/apis/wos-journal/v1/journals?issn=${issn}`,
  //     { headers: { "X-ApiKey": env.CLARIVATE_API_KEY } });
  // Respect the documented rate limits; cache aggressively.
  return results; // no-op until implemented
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8" },
  });
}
