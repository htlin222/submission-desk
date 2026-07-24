# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-07-24

Initial release.

### Added
- Gate–score–rank decision tool as a single dependency-free HTML file.
- Five binary eligibility gates that block scoring until all pass.
- Editable candidate table with live acceptance-probability and score recalculation.
- Two ranking modes: Expected Yield (`EIM`, default) and Balanced (weighted, adjustable).
- Fixed eight-state submission flow with an explicit reject → next-journal loop.
- Editable Gantt timeline with an optional rejection-and-resubmission cascade.
- Traditional Chinese version at `zh-TW/`.
- `docs/METHOD.md` with derivation, parameter provenance table, and limitations.
- GitHub Pages deployment workflow.

### Notes
- Timeline defaults are drawn from Rees et al. (2022); the fit multipliers,
  probability clamp bounds and default Balanced weights are uncalibrated
  heuristics and are labelled as such in the interface.
