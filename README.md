# 📮 Submission Desk

*Where do I send this manuscript? — answered by arithmetic instead of by 3 a.m. despair.*

You wrote a paper. Congratulations, you beautiful disaster. Now comes the part nobody trained you for: picking a journal without (a) aiming so high you spend eight months collecting rejection emails like Pokémon, or (b) aiming so low your advisor makes That Face.

Submission Desk turns "where do I submit?" from a vibes-based coin flip into a **repeatable, boring, wonderfully defensible procedure**: hard gates → scoring → a ranked ladder. Same inputs, same answer, every time. It has no opinions about your h-index.

**[▶ Open the tool](https://submission-desk.pages.dev/)** · **[▶ 繁體中文版](https://submission-desk.pages.dev/zh-TW/)**

No build step. No install. No tracking. No account. No "we value your privacy" banner that values the opposite. One HTML file that works offline on a plane — which is where most of these decisions get made anyway.

---

## What it actually does (in tabs, so it fits a slide)

1. **Gates** — five yes/no questions. Fail one and the journal is ejected *before* it can charm you with its impact factor. Non-negotiable, like a bouncer with a rubric.
2. **Candidates** — an editable table: IF, acceptance rate, fit (1–5), weeks-to-decision, APC. Two ranking modes: *Expected Yield* (default, the grown-up choice) and *Balanced* (sliders, for when you need to feel in control).
3. **Verdict** — a ranked ladder with a `→ SUBMIT HERE` stamp on the winner. The stamp is deeply satisfying. That's most of the value, honestly.
4. **Sensitivity · Trade-off · Simulation · Compare** *(the 繁中 version has the full quant pack)* — a tornado chart, a Pareto trade-off scatter, a seeded Monte Carlo ("is your #1 actually robust or just lucky?"), and an Expected-Yield-vs-Balanced bump chart. For the moment 15 minutes into the talk when someone asks "but how sensitive is that?"
5. **Flow + Timeline** — eight fixed submission states and an editable Gantt with an "add a rejection cycle" toggle, so the true cost of Aiming High is measured in weeks instead of optimism.

## The one formula you should know

```
P_accept = clamp( (rate/100) × fitFactor , 0.02 , 0.95 )    fitFactor: 0.5 0.75 1.0 1.3 1.6 for fit 1–5
EIM      = P_accept × IF / (weeks / 4.345)
```

Translation: raw impact factor flatters journals that (a) won't take you and (b) take forever to say no. Dividing by time-to-decision politely tells those journals to sit down. Full derivation, provenance, and a candid list of where the model is frankly guessing: **[docs/METHOD.md](docs/METHOD.md)**.

## Is any of this real, or did you just make it up?

Both! And — refreshingly — the tool tells you which is which:

- **Backed by actual research:** fit-first ranking (Rees et al. 2022: prioritising fit roughly *doubled* first-choice acceptance odds, OR 2.11), and time-discounted expected value (Salinas & Munch 2015, whose properly-derived index `EIM` shamelessly simplifies).
- **Vibes, clearly labelled `heuristic` in the UI:** the fit multipliers, the multiplicative form, the clamp bounds, the default weights. Plausible. Internally consistent. Uncalibrated. If you have data to fix them, that's the best pull request this repo could receive.

The honest one-liner the evidence supports: **descending the impact-factor ladder costs you little in citations, but a lot in time and first-try success.** Counter-evidence and references live in [docs/METHOD.md](docs/METHOD.md).

## Run it (the hard way, i.e. not hard)

```bash
git clone https://github.com/htlin222/submission-desk.git
cd submission-desk
open index.html        # macOS   ·   xdg-open (Linux)   ·   start (Windows)
```

Browser being precious about local files?

```bash
python3 -m http.server 8000   # → http://localhost:8000
```

## Deploying your own copy → Cloudflare Pages

This repo ships a GitHub Actions pipeline that publishes the site to **Cloudflare Pages** on every push to `main`. Add two repository secrets and you're live:

| Secret | Where to get it |
|---|---|
| `CLOUDFLARE_API_TOKEN` | Cloudflare dashboard → My Profile → API Tokens → *Create Token* → **"Cloudflare Pages — Edit"** template |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare dashboard → Workers & Pages → Account ID in the right sidebar |

The workflow **creates the Pages project on first run**, so you never have to touch the dashboard's click-maze. Set the secrets under *Settings → Secrets and variables → Actions*, then re-run the workflow. (A GitHub Pages workflow is also included, for traditionalists.)

## Filling the table without guessing

Two of the five columns can come from Crossref instead of your imagination:

```bash
python3 tools/crossref_index.py --issn 1741-7015 2045-2322 --mailto you@uni.edu -o data/snapshots/mine.json
```

Then hit **Load Crossref snapshot** in the tool. Read locally, no network call, nothing stored. Acceptance rate, APC, and fit stay manual because the universe refuses to make them easy. More: **[docs/CROSSREF.md](docs/CROSSREF.md)**.

## Cite · Contribute · License

- **Cite:** there's a [CITATION.cff](CITATION.cff) (GitHub renders a "Cite this repository" button). But please cite the *actual papers* for any actual claim — they did the work.
- **Contribute:** calibration data beats everything. Translations, field presets, and a11y fixes are all welcome. Keep each version single-file and dependency-free. See [CONTRIBUTING.md](CONTRIBUTING.md).
- **License:** [MIT](LICENSE). Do whatever. We are not going to email you.

---

*Nothing is stored or transmitted. Reloading the page nukes everything — a tiny, private, academic Etch A Sketch.*
