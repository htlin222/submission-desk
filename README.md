# Submission Desk

A single-file, dependency-free tool for deciding **where to send a manuscript** — repeatably.

Journal choice is usually made by feel, or by walking down an impact-factor list. Submission Desk splits it into three steps that give the same answer every time you feed it the same inputs: **hard gates → scoring → ranked ladder**, plus a status flow and a timeline so you can see what a stretch submission actually costs in weeks.

**[Open the tool →](https://YOUR-USERNAME.github.io/submission-desk/)** · **[繁體中文版 →](https://YOUR-USERNAME.github.io/submission-desk/zh-TW/)**

No build step, no install, no tracking, no storage. Open `index.html` in a browser and it works offline.

---

## Contents

- [What it does](#what-it-does)
- [The method](#the-method)
- [Evidence base](#evidence-base) ← read this before trusting the numbers
- [Filling the table from Crossref](#filling-the-table-from-crossref)
- [Running it](#running-it)
- [Repo layout](#repo-layout)
- [Contributing](#contributing)
- [Citing](#citing)
- [License](#license)

---

## What it does

**1. Hard gates.** Five binary requirements — scope match, indexing, legitimacy, APC within budget, article type accepted. Fail any one and the journal is out; no scoring happens until all five clear. This is what stops the shortlist from being a matter of taste.

**2. Scoring.** An editable table of candidates: impact factor, acceptance rate, fit (1–5), weeks to first decision, APC. Two ranking modes:

- **Expected Yield** — ranks by impact captured per unit time. Default.
- **Balanced** — a weighted blend of prestige, acceptance odds, speed and cost, with sliders.

**3. Verdict.** A ranked ladder. Same inputs, same order, every time.

**4. Flow.** Eight fixed submission states, with the reject → next-journal loop made explicit so a rejection doesn't restart the deliberation.

**5. Timeline.** An editable Gantt of the phases, with a toggle that adds a rejection-and-resubmission cycle so the cost of aiming high is visible in weeks rather than vibes.

## The method

Acceptance probability is modelled as the published acceptance rate modified by how well the manuscript fits:

```
P_accept = clamp( (rate / 100) × fitFactor , 0.02 , 0.95 )
fitFactor = 0.5 / 0.75 / 1.0 / 1.3 / 1.6   for fit scores 1–5
```

**Expected Yield** then ranks by expected impact per month:

```
EIM = P_accept × IF / (weeks / 4.345)
```

The intuition: raw impact factor over-rewards journals you are unlikely to get into and that take a long time to say no. Dividing by time-to-decision discounts that.

**Balanced** min-max normalizes each criterion across the candidate set and combines them under user-set weights.

Full derivation, parameter provenance, and known weaknesses: **[docs/METHOD.md](docs/METHOD.md)**.

## Evidence base

Some of this tool is grounded in published research. Some of it is a reasonable-looking guess. The distinction matters, so it is documented rather than buried.

### Empirically supported

**Fit-first ranking.** Rees et al. (2022) surveyed 691 health-professions-education corresponding authors about a specific published paper. Prioritising fit roughly doubled the odds of acceptance at the first-choice journal (OR 2.11, 95% CI 1.55–2.88); prioritising speed of dissemination also helped (OR 1.80, 1.41–2.29). Prioritising *impact* cut the odds (OR 0.37, 0.28–0.49), as did deciding on the target journal late in the writing process (OR 0.77, 0.66–0.89). This is the strongest single result behind the tool's design.

**Time-discounted expected value.** Salinas & Munch (2015) derived a Markov decision process for submission sequences, parameterized with acceptance probability, submission-to-decision time and impact factor for 61 ecology journals. Their closed-form index has the same skeleton as `EIM` and correlates with their full model at Spearman ρ = 0.920. Their version is properly derived; `EIM` is a simplification of it.

**Default timeline values.** Taken from Rees et al.: mean 8.4 weeks to first decision, 19.6 weeks from first submission to final acceptance, 1.5 journals per paper, 6.7 weeks to first decision at the second journal, 98% of first-choice acceptances requiring revision.

### Not calibrated — author-set heuristics

These are labelled `heuristic` in the UI. They are plausible, internally consistent, and **unvalidated**:

- the fit multipliers (0.5 / 0.75 / 1.0 / 1.3 / 1.6)
- the multiplicative form `rate × fitFactor` itself
- the probability clamp bounds (0.02, 0.95)
- the default Balanced weights (35 / 30 / 20 / 15)
- dividing by months rather than discounting against a career time-horizon *T*, as Salinas & Munch do

If you have data that would calibrate any of these, that is the single most valuable contribution this repo could receive.

### Where the evidence pushes back

The tool's framing implies that walking down an impact-factor list is a poor strategy. Salinas & Munch tested exactly that and found it milder than expected: following the IF ranking never returned less than 90% of the optimal expected citations over horizons beyond three years, and stayed around 70% of optimal within subject-specific subsets. Their conclusion was that for an author who only wants citations and will keep resubmitting, the IF heuristic is not a bad strategy.

The cost of IF-chasing shows up elsewhere: in their model, authors willing to give up 4–14 citations could save 0.5–1.5 resubmissions and 30–150 days. Combined with the Rees finding above, the accurate claim is narrower than "IF is a trap":

> **Descending the IF ladder costs you relatively little in citations, but a lot in time and in first-submission success.**

Use Expected Yield if time and morale are the binding constraints. Use Balanced with prestige weighted high if a specific journal is a hard career requirement. Neither mode is a substitute for reading the journal.

### A data caveat you cannot design around

Acceptance rates and decision times are frequently unpublished. Salinas & Munch obtained usable data from only 61 of 131 journals contacted and closed their paper by urging journals to release these figures; a later emergency-medicine review described submission choice as a subjective, non-evidence-based step embedded in otherwise objective scientific work. The two hardest columns in this tool are hard for structural reasons. Treat them as estimates and record where each number came from.

### References

- Rees EL, Burton O, Asif A, Eva KW. A method for the madness: an international survey of health professions education authors' journal choice. *Perspectives on Medical Education*. 2022;11(3):165–172. doi:10.1007/s40037-022-00698-9
- Salinas S, Munch SB. Where should I send it? Optimizing the submission decision process. *PLOS ONE*. 2015;10(1):e0115451. doi:10.1371/journal.pone.0115451
- Rodriguez RM, Chan V, Wong AHK, Montoy JCC. A review of journal impact metrics and characteristics to assist emergency medicine investigators with manuscript submission decisions. *Western Journal of Emergency Medicine*. 2020;21(4). doi:10.5811/westjem.2020.4.47030
- Calcagno V, Demoinet E, Gollner K, Guidi L, Ruths D, de Mazancourt C. Flows of research manuscripts among scientific journals reveal hidden submission patterns. *Science*. 2012;338(6110):1065–1069. doi:10.1126/science.1227833
- Björk BC, Solomon D. The publishing delay in scholarly peer-reviewed journals. *Journal of Informetrics*. 2013;7(4):914–923. doi:10.1016/j.joi.2013.09.001

## Filling the table from Crossref

Two of the five columns can come from a public source instead of a guess:

```bash
python3 tools/crossref_index.py --issn 1741-7015 2045-2322 \
    --mailto you@university.edu -o data/snapshots/mine-2026-07-24.json
```

Then use **Load Crossref snapshot** in the tool. The file is read locally; no network call is made from the page, and nothing is stored.

Because Crossref is a living corpus, a live query is not reproducible. The snapshot is the deterministic artefact: it records every request URL, every pinned parameter, and a SHA-256 over the raw responses, so the figures stay fixed and stay auditable. `--verify` re-runs and reports drift.

**What it can supply:** a citation rate (an IF-shaped proxy from open citation counts), median submission-to-acceptance time, acceptance-to-issue time, annual article volume, and a licence-coverage hint.

**What it cannot:** acceptance rate and APC are not in Crossref and stay manual. Fit is a property of the manuscript-journal pairing, not of the journal, so no database will ever hold it.

**Coverage gating.** Metadata deposit is uneven — Springer Nature titles deposit article history on ~97–100% of articles, many society journals on none. Below 30% coverage the tool returns `null` with a reason instead of a median over stragglers. A figure computed from 3% of articles looks identical to one computed from 97%; that is the failure mode worth designing against.

Details, caveats and the pinned-parameter list: **[docs/CROSSREF.md](docs/CROSSREF.md)**.

## Running it

```bash
git clone https://github.com/YOUR-USERNAME/submission-desk.git
cd submission-desk
./tools/setup.sh your-github-username   # rewrites the placeholder URLs
open index.html          # macOS
xdg-open index.html      # Linux
start index.html         # Windows
```

Or serve it, if your browser is strict about local files:

```bash
python3 -m http.server 8000
# then visit http://localhost:8000
```

To publish your own copy: enable **Settings → Pages → Source: GitHub Actions**. The included workflow deploys on every push to `main`.

## Repo layout

```
submission-desk/
├── index.html              # the tool (English) — GitHub Pages entry point
├── zh-TW/index.html        # the tool (Traditional Chinese)
├── docs/METHOD.md          # derivation, parameter provenance, limitations
├── docs/CROSSREF.md        # deriving journal figures from Crossref
├── tools/crossref_index.py # snapshot builder (stdlib only)
├── data/snapshots/         # dated, hashed snapshots — committed as evidence
├── .github/workflows/      # Pages deployment
├── CITATION.cff            # citation metadata
├── CONTRIBUTING.md
├── CHANGELOG.md
└── LICENSE                 # MIT
```

Both HTML files are self-contained: markup, styles and logic in one document, no bundler, no runtime dependencies. Web fonts load from Google Fonts and degrade to system faces offline.

## Contributing

Calibration data is the most useful thing you can bring — see [CONTRIBUTING.md](CONTRIBUTING.md). Field-specific presets, translations, and accessibility fixes are all welcome. Please keep each version single-file and dependency-free.

## Citing

If this tool informs a methods section or a lab guide, cite it via [CITATION.cff](CITATION.cff) — GitHub renders a "Cite this repository" button from it. Please cite the underlying research directly for any claim about the method; the papers above did the work.

## License

[MIT](LICENSE). Swap it if your institution requires something else — the tool has no dependencies whose licenses would constrain you.

---

*Nothing in this tool is stored or transmitted. Reloading the page clears everything.*
