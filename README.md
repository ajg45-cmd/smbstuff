# smbstuff — Midday Reset Continuation research

Research repo for one question: **is the midday reset a real, tradeable edge, or
is it a story we tell about charts we already know worked?**

The setup being tested is the *Midday Reset Continuation (long)* — a day-1
earnings name that clears the premarket high in the first hour, pulls back into
a reference level between 10:30 and 12:00 on volume that dries up, and resumes.

## Read in this order

| File | What it settles |
|---|---|
| `docs/00-thesis.md` | What the trade is, why it should work, and what would prove it doesn't |
| `docs/01-setup-definition.md` | The rules, written so code (not judgment) picks candidates |
| `docs/02-feature-dictionary.md` | Every variable, its exact formula, and its known-as-of timestamp |
| `docs/03-study-design.md` | Population, labeling, splits, controls, Monte Carlo protocol |
| `docs/04-eye-test.md` | The blind chart-grading tool that turns "clean price action" into a number |
| `docs/05-open-questions.md` | **The question list.** Start here if you only read one file |
| `docs/06-odds-enhancer-scorecard.md` | The new Playbook archetype scorecard for this setup |

## Code

- `src/midday_reset/features.py` — reference implementation of leg detection,
  the normalized volume ratio, candidate scanning, and forward labeling.
- `src/midday_reset/evaluate.py` — the four Monte Carlo simulations, the
  permutation test, and the random-entry control.

Both are written to be read as much as run. Where a definition in the docs is
ambiguous, the code is the tiebreaker — that is the point of having it.

## Status

Phase 0 (data + scanner + candidate frequency count). Nothing has been tested
yet. No claim in this repo is an empirical result until it appears in a results
file with a sample size next to it.
