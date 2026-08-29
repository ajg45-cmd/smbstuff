# smbstuff — Midday Reset Continuation research

Research repo for one question: **given a VWAP continuation entry, which exit
logic keeps a trend trader in the trend — and in what universe is that
advantage significant?**

Entry is a 15-min (or 5-min) VWAP continuation inside 10:30–12:00, taken by
hand. Exit is the part being automated, and the part being studied. See
[`docs/07`](docs/07-decisions-and-exit-lab.md) for the decisions record and why
the exit question is better-posed than the entry question.

## Read in this order

| File | What it settles |
|---|---|
| `docs/00-thesis.md` | What the trade is, why it should work, and what would prove it doesn't |
| `docs/01-setup-definition.md` | The rules, written so code (not judgment) picks candidates |
| `docs/02-feature-dictionary.md` | Every variable, its exact formula, and its known-as-of timestamp |
| `docs/03-study-design.md` | Population, labeling, splits, controls, Monte Carlo protocol |
| `docs/04-eye-test.md` | The blind chart-grading tool that turns "clean price action" into a number |
| `docs/05-open-questions.md` | The question list (§0 now answered) |
| `docs/06-odds-enhancer-scorecard.md` | The new Playbook archetype scorecard for this setup |
| `docs/07-decisions-and-exit-lab.md` | Decisions record, the exit rule set, and the universe slices |
| `docs/08-momentum-gates.md` | **Current.** Momentum gates, VWAP anchors, and the filter ladder |
| `docs/09-connecting-data.md` | Getting exports to Claude automatically |

## Shareable summary

The whole plan as one readable page: `docs/midday-reset.html`
(published at https://claude.ai/code/artifact/d31c3fea-92ff-495c-a235-2435a2dc735c)

## Code

- `src/midday_reset/features.py` — shared primitives: session VWAP, the
  clock-normalized volume baseline, ATR zigzag legs, side-aware forward labeling.
- `src/midday_reset/v1.py` — the traded signal: VWAP continuation, long and
  short, on 5-min or 15-min bars, with every decision from `docs/07` applied.
- `src/midday_reset/ablation.py` — **the filter ladder.** Does clean price
  action move EV, or just shrink n? Reports the same-size random control and
  the lift after stripping out trend strength.
- `src/midday_reset/exits.py` — **the exit lab.** One engine, ~50 rules across
  both frames, a paired leaderboard against a do-nothing benchmark, and the
  universe slicing.
- `src/midday_reset/evaluate.py` — Monte Carlo, permutation test, random-entry
  control, cluster bootstrap.

Both are written to be read as much as run. Where a definition in the docs is
ambiguous, the code is the tiebreaker — that is the point of having it.

## Tests

```
cd tests && python3 test_smoke.py && python3 test_vwap_rejection.py && python3 test_exit_lab.py
```

Contract tests on hand-built sessions. They pin the mechanics down — the zigzag
does not flip inside a bar, a VWAP touch is judged against the *concurrent*
VWAP, no entry precedes its own signal, no exit loses more than 1R past its
stop. They prove nothing about markets and do not claim to.

## Status

Phase 0: pipeline built, no market data run through it. Nothing has been tested
yet. No claim in this repo is an empirical result until it appears in a results
file with a sample size next to it.
