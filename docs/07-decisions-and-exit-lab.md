# 07 — Decisions, and the exit lab

## What changed

The primary question is no longer "does the midday reset have an edge." It is:

> **Given a VWAP continuation entry, which exit logic keeps a trend trader in
> the trend — and in what universe is that advantage significant?**

That is a better-posed study than the one in `00-thesis.md`, and it is worth
saying why rather than just switching.

**Comparing exits on the same trades is a paired design.** Every rule is scored
on an identical set of entries, so the entry noise that swamps an absolute-EV
study cancels in the *difference* between two rules on the same trade. A paired
comparison resolves an effect roughly an order of magnitude smaller than two
independent samples of the same size. The sample-size problem in
`03-study-design.md` — where 900 candidates only bought you a 0.34R minimum
detectable effect — mostly goes away, because you are no longer comparing
groups of trades; you are comparing rules within trades.

**The one caveat that has to stay in view.** Exit rankings are conditional on
the entry having positive expectancy. If entry EV ≤ 0, the optimal exit
degenerates to "exit immediately," and a leaderboard of trailing rules is
ranking ways of losing more slowly. So entry EV > 0 still has to be established
— but it comes free from the same dataset and it is a low bar, not the study.

**On the volume hypothesis.** Kept, demoted. `npvr` (clock-normalized) and
`pvr_raw` (the simple version) are both logged on every signal, but volume
dry-up is now a **conditioning variable** — one of the universe slices the exit
result gets checked across — rather than the headline. The RVOL-relative
version stays parked until there is a reason to build it.

---

## Decisions record

Answers from the trader, 2026-08-28. These are settled; changing one is a
deliberate act, not a default.

| # | Question | Decision | Where it lives |
|---|---|---|---|
| 1 | Liquidity filter | **5,000,000 shares cumulative at time of entry** — point-in-time, not the day's total | `v1.MIN_CUM_SHARES` |
| 2 | "Strong open" | **Movement larger than normal for that name** — measured against its own ATR, not an absolute % | `v1.open_move()` |
| 3 | Premarket high | **Enhancer, not a gate.** Logged as `beyond_pmh`, never filtered on | `v1.Signal.beyond_pmh` |
| 4 | VWAP touch | **Wick through and hold, OR come within 0.10 × daily ATR.** It does not have to print the line | `v1.TOUCH_TOL_ATR` |
| 5 | Window | **10:30–12:00 hard for now**, widen after a result | `features.WINDOW_*` |
| 6 | Which leg | **Second leg of the first directional program** → the *first* qualifying signal of the day. Later ones logged in their own bucket, never pooled | `is_first_of_day` |
| 7 | Direction | **Longs and shorts.** Mirrored logic, separate populations, never pooled in a result | `find_signals(side=...)` |
| 8 | Data | Build on KTG; see the data-gap list below | — |
| 9 | Concurrency | **Multiple positions allowed**; still clustered by day for statistics | `day_symbol` |
| 10 | Bar | **Prove edge first, refine after** | go/no-go below |

Two consequences worth noting, because they follow from the answers rather than
from anything anyone chose:

- Answer 6 mostly **dissolves the clustering problem**. Trading only the first
  signal of the day means one observation per name per day, which is what the
  statistics want anyway. The later signals are still logged, so "is the second
  one worth taking?" stays an answerable question instead of an assumption.
- Answer 1 is a **hard filter**. 5M shares by 11:00 is a genuinely restrictive
  bar — it selects the true Stocks In Play. Cumulative *dollars* is logged
  beside it so the threshold can be swapped without re-running the scan. Count
  how many signals survive it in Phase 0 before committing to it.

---

## The two timeframe axes

"Test 5 and 15 min" is really two questions, and they cross:

|  | **Exit on 5-min** | **Exit on 15-min** |
|---|---|---|
| **Entry on 5-min** | fast in, fast out | fast in, patient hold |
| **Entry on 15-min** | patient in, fast out | patient in, patient hold |

The off-diagonal cells are the interesting ones, and the top-right is the
hypothesis your problem statement implies: **enter on structure, hold on
structure, but do not trail tighter than the frame you entered on.**

A trailing rule that runs on a faster frame than the entry will exit on noise
that the entry timeframe does not even register as a pullback. That is the
mechanical reason a 5-min EMA9 trail shakes a 15-min trend trader out — and it
is exactly what your current hot key does. In the synthetic sessions in
`tests/test_exit_lab.py`, EMA9 on 5-min returns **0.94R** against **2.28R** for
the same rule on 15-min bars, on identical trades. That is a demonstration of
the mechanism on hand-built data, not evidence — but it is the first thing the
real dataset should be asked about.

---

## The rule set

Every rule runs through one engine (`exits.run_exit`) so the only difference
between two rows of the leaderboard is the rule itself. Within-bar ordering is
deliberately pessimistic: adverse levels are assumed hit before favorable ones,
because on a 5- or 15-min bar you cannot know the sequence, and the optimistic
assumption is how backtests manufacture edge.

| Family | Variants | What it is testing |
|---|---|---|
| **`hold_to_close`** | — | **The benchmark.** Initial stop only, hold to the bell |
| Moving-average trail | EMA 5 / 9 / 21 | The hot key's family |
| MA trail + cushion | EMA9 ± 0.25 / 0.5 / 1.0 ATR | Your v2 ATR-buffer idea, measured |
| VWAP loss | plain, +0.5 ATR | The loosest trend definition |
| Swing trail | lowest low of last 1 / 2 / 3 bars | Pure structure |
| Chandelier | 1.5 / 2 / 3 ATR from the running extreme | Volatility-scaled |
| Fixed target | 1 / 2 / 3 / 4R | The no-trend baseline |
| Time stop | 12:30 / 13:30 / 15:30 | Does it stop working midday? |
| Hybrid | breakeven at 1R, then trail | The common discretionary pattern |

**The benchmark is the point.** `hold_to_close` is scored on every trade
because a trailing rule that cannot beat "initial stop, hold to the bell" is
costing money to feel busy. Traders almost never check this, and it is the
cheapest way for this study to be worth its own cost.

---

## Reading the leaderboard honestly

`exits.leaderboard()` reports, for each rule: mean R, median, win rate, p90,
percentage of available MFE captured, and the **paired difference against the
benchmark** with a cluster-bootstrapped 95% interval.

Three rules for interpreting it:

1. **Rank on the paired difference, not on mean R.** Mean R is dominated by
   which trades happened to be in the sample; the difference is not.
2. **Pick the plateau, not the peak.** If EMA9 wins but EMA5 and EMA21 are
   poor, that is a fitted parameter. If EMA5/9/21 all beat the benchmark and 9
   is best, that is a real effect with a best setting.
3. **~50 rules is ~50 tests.** Apply Benjamini–Hochberg across the leaderboard
   and log every variant in `results/trials_log.csv`. A leaderboard's top row
   is the maximum of 50 noisy numbers and is biased upward by construction —
   the honest estimate of the winner's edge comes from a held-out period, not
   from the row that won.

---

## "In what universe does it prove significant"

`exits.universe_report()` re-runs one rule's paired edge inside each slice:

side · entry frame · first signal vs. later · liquidity filter on/off ·
abnormal open · beyond PMH · dry vs. wet approach (`npvr` terciles) ·
strong vs. weak trend (VWAP slope) · tight vs. wide initial risk

A rule that wins overall but only inside one slice has not been shown to work —
it has been shown where to look next. The bar to clear: **the winner beats the
benchmark in most slices, and its advantage does not reverse in any of them.**
A rule that is +0.4R in strong trends and −0.4R in weak ones is not an exit
rule, it is a trend filter you have not written down yet.

---

## Data — what this actually needs (answering Q8)

The good news: **the exit lab needs almost no exotic data.** I cannot inspect
your KTG interfaces from here, so this is the requirement list to map onto
them rather than a claim about what KTG has.

**Minimum to start — nothing else required:**

1. **1-minute OHLCV including premarket**, for your in-play names, as much
   history as you can get. 5-min and 15-min are resampled from it; no separate
   feed needed.
2. **Daily OHLCV** for ATR. Trivial anywhere.
3. **A symbol/date list of names that were in play.** For a first pass this can
   simply be the names you traded or watched — the exit question does not need
   a clean universe definition to produce a first answer.

**One thing to verify before trusting any of it:** confirm that the VWAP
computed here matches the VWAP on your screen. Session VWAP differs between
platforms on two choices — whether it starts at 9:30 or includes premarket, and
which venues' prints are included. If the backtest's VWAP is not the line you
were actually looking at, every touch is measured against the wrong level and
the study answers a question you did not ask. `features.session_vwap()` starts
at 9:30 and uses typical price; change it to match KTG if KTG differs.

**Needed later, for the universe slicing — likely a Polygon/vendor gap:**

| Data | For | Note |
|---|---|---|
| Earnings calendar with BMO/AMC | The day-1 population | Polygon or FMP. Getting the session flag wrong shifts half the sample by a day |
| Float / shares outstanding | Low-float slicing | Polygon has share-class data; quality is mixed. Use buckets, not point values |
| Delisted symbols | Survivorship | Polygon flat files include them; most convenience APIs do not |
| Options implied move | Catalyst quality (H7) | ORATS or Polygon options. Phase 4, not now |

**Tell me which of these KTG already exposes** and I will write the loader
against it; where it does not, the Polygon flat-file path is the fallback.

---

## Go / no-go for "prove edge"

Keeping it to the bar you set — prove it, then improve it:

- **Entry is worth trading at all:** mean `ret_eod_R` > 0 with a
  cluster-bootstrapped 95% interval excluding zero, after costs.
- **The exit work paid for itself:** the best rule beats `hold_to_close` by a
  margin whose paired interval excludes zero, holds in most universe slices,
  and sits on a parameter plateau.
- **It survives the honesty checks:** it holds on a period held out from the
  rule search, and the effect does not vanish once the ~50-test leaderboard is
  corrected for multiplicity.

Anything short of all three is a lead, not a result.
