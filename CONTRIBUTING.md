# Contributing

Thanks for looking. This is a small, deliberately simple project — the whole tool is one HTML file per language, and it should stay that way.

## What helps most

**Calibration data.** The weakest part of this tool is the fit multipliers (`0.5 / 0.75 / 1.0 / 1.3 / 1.6`), which are an educated guess. If you have submission records — a fit score assigned *before* submission, plus the outcome — that is the single most valuable contribution possible here. Open an issue before doing any work so we can agree on a format and on anonymisation.

**Crossref snapshots for your field.** Run `tools/crossref_index.py` over the journals you care about and contribute the snapshot to `data/snapshots/`. These accumulate into something genuinely useful and cost you one command.

**Field-specific presets.** Real acceptance rates and decision times for a set of journals in your field, with the source for each number. These are hard to find and worth sharing.

**Corrections to the evidence claims.** If the README or `docs/METHOD.md` overstates what a cited paper found, that is a bug and a serious one. Please file it.

**Translations.** Copy `index.html`, translate the strings, and place it at `<lang-tag>/index.html` using a BCP 47 tag. Add a link in the header language switcher of every other version.

**Accessibility fixes.** Keyboard navigation, focus visibility, screen-reader labels, contrast.

## Ground rules

- **Single file, no dependencies.** No bundler, no framework, no package manager. If a change needs a build step, it probably belongs in a fork.
- **No storage, no network calls from the page.** The Crossref tool is a separate CLI; the browser only ever reads a local file.
- **No storage, no network calls.** The tool holds everything in memory and sends nothing anywhere. Please keep it that way; people put unpublished work into it.
- **Label uncalibrated numbers.** Any new parameter that is not traceable to a source gets marked `heuristic` in the UI and added to the provenance table in `docs/METHOD.md`. Honest defaults beat confident ones.
- **Keep both language versions in sync.** A change to logic or layout in one should land in the other in the same pull request.

## Making a change

```bash
git clone https://github.com/htlin222/submission-desk.git
cd submission-desk
python3 -m http.server 8000    # then open http://localhost:8000
```

Before opening a pull request, check that:

- both `index.html` and `zh-TW/index.html` still work
- the layout holds down to a 360px viewport
- keyboard focus is visible on every control
- `prefers-reduced-motion` is still respected
- no console errors

There is no test suite. `node --check` on the extracted script block catches syntax errors:

```bash
sed -n '/<script>/,/<\/script>/p' index.html | sed '1d;$d' > /tmp/check.js && node --check /tmp/check.js
```

## Reporting problems

Open an issue with what you expected, what happened, and your browser. For anything touching the evidence claims, please include the DOI.
