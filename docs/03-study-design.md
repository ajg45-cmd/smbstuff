# 03 — Study design

## Population and period

- **Primary population:** day-1 post-earnings gap-ups passing Stage 1.
- **Period:** 2019-01-01 → present. Long enough for four distinct regimes;
  short enough that market structure is comparable.
- **Regime blocks** (the edge must appear in **at least three**, even if weaker):
  2019 pre-COVID · 2020–21 liquidity/meme · 2022 bear · 2023–24 AI-led ·
  2025–present.

**Survivorship bias is a live risk here.** A 2019–2025 sample of mid-caps that
excludes delisted, acquired, and bankrupt symbols will be biased upward, and
gappers skew toward exactly those names. Your data source must be
point-in-time with delisted symbols included, or you are measuring the returns
of companies that survived.

## Data requirements

| Need | Why | Notes |
|---|---|---|
| 1-min OHLCV **including pre/post market** | PMH is a gate — no premarket, no study | Polygon.io flat files or Databento are the realistic options. Retail sources (yfinance) do not give reliable premarket 1-min or enough history. **This is a hard blocker, price it first** |
| Earnings calendar with **BMO/AMC session** | Decides which day is "day 1" | Getting AMC/BMO wrong silently shifts half your sample by one day and quietly destroys the study. Cross-check two vendors on a 50-name sample before trusting either |
| Split & dividend adjustments | Gap %, levels, and all price math | Adjust consistently across the whole history, not per-request |
| Delisted symbols | Survivorship | |
| Float / shares outstanding | H5 | Point-in-time float is genuinely hard; most vendors give current-only, which is a lookahead. Use buckets and document the limitation rather than pretending precision |
| Short interest | Squeeze fuel | Bimonthly, lagged — honor the publication date |
| SPY / QQQ / VIX / sector ETFs, 1-min | Big-picture stack | |
| Trade-level (tick) data | Volume composition (§4) | Phase 2. Biggest single upgrade to the core hypothesis |
| Options implied move | H7, catalyst quality | Phase 3. ORATS or Polygon options |

## Data splits — decide now, honor later

| Split | Period | Use |
|---|---|---|
| **Development** | 2019 – 2023 | Build features, explore, fail, iterate freely |
| **Validation** | 2024 | Check the pre-registered H1 once |
| **Holdout** | 2025 – present | **Touch exactly once, at the very end** |
| **Forward log** | from today | The only truly out-of-sample data you will ever have |

Start the forward paper log on **day one**, in parallel with everything else. In
six months it is the most credible evidence you own, and it costs nothing today.

## Sample size and what you can honestly detect

Per-trade R has a heavy-tailed distribution; assume σ ≈ 1.5R for `mfe_60`.

For a two-sample comparison at α=0.05, 80% power:

```
n_per_group = 2 σ² (z_α/2 + z_β)² / Δ²
```

| Effect you want to detect | n per group |
|---|---|
| Δ = 0.20R | ~880 |
| Δ = 0.30R | ~390 |
| **Δ = 0.34R** | **~300** ← what tercile-splitting ~900 candidates buys you |
| Δ = 0.50R | ~140 |

**Read that honestly.** If Phase 0 yields ~900 candidates across the development
window, you can reliably detect a **large** effect in a **single** pre-registered
hypothesis. You **cannot** reliably resolve `rvol × float` interactions, or a
six-way enhancer stack. Anyone who tells you otherwise is fitting noise.

The discipline that follows: **one primary hypothesis (H1). Everything else is
exploratory and generates the hypothesis you pre-register next.**

## Costs — apply before declaring anything

Many intraday edges live entirely inside the cost model. Apply costs to every
trade before any expectancy number is quoted.

```
entry_fill = trigger_price + 0.5 * spread + impact
impact     = k * (shares / mean_1min_volume) * ATR15     # start k = 0.10 [T]
exit_fill  = exit_price - 0.5 * spread - impact
costs      = commission + SEC/TAF fees + borrow (shorts only)
```

Report expectancy at **three** size assumptions: 10%, 25%, and 50% of one
minute's volume. If the edge only survives at 10%, that is your capacity ceiling
and it belongs in the headline, not a footnote.

## Statistical protocol

1. **Primary test (H1).** Tercile split on `npvr_resid`, within `depth` ×
   `duration` buckets. Report mean `mfe_60` spread, its bootstrap CI, and the
   permutation p-value.
2. **Multiple comparisons.** Keep a literal **count of every variant tested**
   (thresholds, timeframes, features) in `results/trials_log.csv`. Apply
   Benjamini–Hochberg to the exploratory set and report the effective number of
   trials. This number always ends up larger than you remember — logging it as
   you go is the only way it stays honest.
3. **Walk-forward.** Train on rolling 12 months, test on the next 3. An edge
   that only exists in-sample shows up here immediately.
4. **Sensitivity.** Perturb every `[T]` threshold by ±20%. The edge must survive
   all of them. Prefer the **parameter plateau** over the peak, always.
5. **Regime check.** Present in ≥3 of 5 regime blocks.

---

# The four Monte Carlo simulations

They answer four different questions. Running one and calling it "the Monte
Carlo" is the standard mistake.

### MC-1 — Trade-sequence bootstrap → *what does a normal bad stretch look like?*

Resample the realized R-multiples with replacement; 10,000 paths of length =
trades per year.

**Use a block bootstrap (blocks of 5–10 consecutive trades), not iid.** Setup
trades cluster — same day, same theme, same regime — so they are correlated, and
an iid bootstrap will understate drawdown badly.

Outputs: distribution of annual R · max drawdown quantiles · **longest losing
streak** · P(negative year).

**Purpose:** so that when you hit 11 losers in a row you know whether that is
within the distribution of a real edge or evidence it broke. This is the
simulation that prevents you from abandoning a working setup, and it is worth
more to your P&L than the significance test.

### MC-2 — Permutation test → *is the signal real?*

Hold the candidate set fixed. Shuffle `npvr_resid` across candidates 10,000
times; recompute the tercile spread each time. `p = fraction of shuffles ≥
observed`.

**Purpose:** the honest significance test. Robust to the fat-tailed, non-normal
return distribution in a way a t-test is not.

### MC-3 — Random-entry control → *is the setup real, or just the population?*

**The control everyone skips, and the one most likely to kill the project.**

Two nulls:

- **Null A (timing).** For each real candidate: same symbol, same day, random
  entry minute in 10:30–12:00, same stop in ATR units. K=20 draws each.
  *Answers: does the pattern beat "buy this name at a random midday moment?"*
- **Null B (catalyst).** Same structural rules applied to the same symbols on
  **random non-earnings days**. *Answers: how much of the edge is the catalyst
  versus the pattern?*

If the setup does not clearly beat Null A, you have discovered that **day-1
earnings gappers drift up**, not that the reset works — and the correct trade is
then a much simpler one. Run MC-3 in Phase 1, not at the end.

### MC-4 — Sizing and risk of ruin → *what can you actually bet?*

Sweep risk-per-trade from 0.25% to 3.0% of account over the MC-1 paths.

Outputs: P(−20% drawdown) · terminal wealth quantiles · half-Kelly fraction ·
the size at which median outcome peaks vs. the size at which ruin risk becomes
unacceptable (they are far apart, and the gap is the answer).

**Then check your Playbook bands against it.** Do the enhancer-conditional
expectancies actually justify probe/A/A+ = 15%/30%/80% of stop, or is 80%
aspirational? This is where the study writes back into the sizing rules you
already use.

---

## Phasing — each phase can kill the project cheaply

| Phase | Deliverable | Kill criterion |
|---|---|---|
| **0** | Data pipeline + scanner + candidate table + chart images. **No modeling.** | < 8 candidates/month, or `capacity_R` too small to matter |
| **1** | H1 tested + MC-2 + **MC-3** | Fails MC-3 Null A |
| **2** | Exit surface; EMA9 hot key scored against alternatives | — (this phase pays for itself regardless) |
| **3** | Enhancer scorecard fit; MC-1 + MC-4; sizing bands | — |
| **4** | Catalyst layer (implied move, guidance, theme) | — |
| **5** | Forward paper log review at 3 and 6 months | Forward expectancy < half of backtest |

Phase 0 is the highest-value work in the project and the part most likely to be
skipped in enthusiasm. Counting candidates and rendering charts, before any
model exists, is what tells you whether there is a business here.

## Pre-registered go / no-go (fill in *before* running Phase 1)

Write the numbers in now, so the decision isn't made by whatever you find.

- **Trade.** Post-cost expectancy ≥ ____ R, ≥ ____ trades/month, holds in ≥3
  regime blocks, beats MC-3 Null A by ≥ ____ R, `capacity_R` ≥ $____.
- **Iterate.** Signal present but under threshold → one named change, re-tested
  on validation only.
- **Kill.** Fails MC-3, or the H1 spread vanishes under the depth/duration
  control.
