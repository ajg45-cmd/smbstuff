# 02 — Feature dictionary

Every feature carries a **known-as-of** timestamp. **No feature may have a
known-as-of later than its candidate's trigger time.** This single rule kills
most of the ways a backtest lies to you.

`ATR` unqualified means `ATR14` on daily bars. `ATR15` means ATR14 on 15-min bars.

---

## §1 Universe / context — known-as-of 09:29

| Feature | Formula | Trap |
|---|---|---|
| `gap_pct` | `(open - prev_close) / prev_close` | Must be split- and dividend-adjusted consistently on both sides |
| `gap_atr` | `(open - prev_close) / ATR` | The comparable version across price levels |
| `addv20_usd` | 20-session mean of `close × volume` | Excludes today. Recompute daily; don't use a static snapshot |
| `atr_pct` | `ATR / prev_close` | Your volatility normalizer for everything else |
| `adr20_pct` | mean of `(high-low)/close` over 20 sessions | Better than ATR for "how much does this thing move intraday" |
| `range_expansion_20` | `(high_at_trigger - max(high, 20 prior sessions)) / ATR` | Negative = still inside the range |
| `range_expansion_60` | same, 60 sessions | |
| `range_expansion_252` | same, 252 sessions | |
| `is_ath` | `high_at_trigger >= max(high, all history)` | |
| `base_tightness` | percentile rank of `(high_20d - low_20d)/close` vs. its own trailing 2y | Low = tight base. This is the "coiled" measure |
| `prev_close_position` | `(prev_close - prev_low)/(prev_high - prev_low)` | Did it close strong into the print |

`range_expansion_*` is technically known at trigger, not 09:29 — it uses the
session high. Listed here because the *reference* (the prior range high) is
pre-open. Keep the split straight in code.

---

## §2 Open quality — known-as-of 10:30

| Feature | Formula |
|---|---|
| `pct_above_vwap` | fraction of 1-min bars 9:30–10:30 closing > session VWAP |
| `range_position_1030` | `(close_1030 - low_0930_1030) / (high_0930_1030 - low_0930_1030)` |
| `pmh_clear_atr` | `(high_0930_1030 - premarket_high) / ATR` |
| `trend_quality` | `MFE / (MFE + MAE)` from the 9:45 close to 10:30 |
| `open_strength` | mean of the four above, each clipped to [0,1] |
| `or_high`, `or_low` | 9:30–10:00 high/low |
| `opening_drive` | `1` if the 9:30 5-min bar closed in its top 25% and the session made a new high after it |

---

## §3 Pullback structure — known-as-of trigger

| Feature | Formula |
|---|---|
| `depth` | `(H1 - L2) / (H1 - L0)` — retracement of the impulse leg |
| `depth_atr` | `(H1 - L2) / ATR15` |
| `duration_bars` | 15-min bars from `H1` to `L2` |
| `leg_index` | count of completed impulse legs today at trigger (H3) |
| `reset_level_type` | categorical: VWAP / PMH / ORH / PDH / EMA9_15 / ROUND (H6) |
| `level_confluence` | count of level types within `0.35 × ATR15` of `L2` |
| `level_touches` | times price came within tolerance of the reset level today |
| `vwap_distance_atr` | `(L2 - vwap_at_L2) / ATR15` — signed |
| `overlap_ratio` | mean bar-to-bar overlap across pullback bars — **the "orderly" measure**; high overlap = drift, low = impulsive selling |
| `max_pb_bar_range_atr` | largest single pullback bar's range in ATR15 — one wide-range down bar is a seller, not a drift |
| `higher_low` | `L2 > L0` (gate, but log it) |
| `trigger_time` | minute of the trigger |
| `trigger_bucket` | 10:30–11:00 / 11:00–11:30 / 11:30–12:00 |

`overlap_ratio` and `max_pb_bar_range_atr` are the two most likely computable
proxies for what your eye calls **"clean."** They are the first things to check
against the eye-test grades in `04-eye-test.md`.

---

## §4 Volume signature — the core, and the one you must get right

### The problem with the hypothesis as stated

"Decreasing volume on the pull-in" is **almost always true** between 10:30 and
12:00, because that is the daily volume trough. Every stock, every day, follows
a U-shaped intraday volume curve. If you measure raw declining volume you will
confirm your hypothesis on ~most of the sample and learn nothing.

### The fix: normalize against the clock

Build a **baseline intraday volume curve** — for each symbol, the median volume
per minute-of-day over the trailing 20 sessions (fall back to a cross-sectional
day-1-earnings composite curve when history is thin, which it often is after a
gap).

| Feature | Formula |
|---|---|
| `pvr_raw` | mean vol/min during pullback ÷ mean vol/min during impulse |
| `pvr_expected` | baseline vol/min over pullback minutes ÷ baseline vol/min over impulse minutes |
| **`npvr`** | **`pvr_raw / pvr_expected`** — **the primary variable (H1)** |
| `npvr_resid` | `npvr` residualized on `depth`, `duration_bars`, `trigger_time` — **this is what H1 is actually tested on** |
| `vol_slope_pb` | OLS slope of log(vol/min) across pullback bars, clock-detrended |
| `trigger_vol_ratio` | trigger bar volume ÷ mean vol/min of pullback |
| `spring_ratio` | `trigger_vol_ratio / npvr` (H2) |
| `dollar_vol_at_trigger` | cumulative session $ volume 9:30 → trigger |

`npvr < 1` means **drier than the clock alone explains**. That is the real
signal. `npvr ≈ 1` means "it's just lunchtime."

### Composition beats magnitude (phase 2, if you get tick data)

Magnitude tells you how much traded; composition tells you *who*.

| Feature | Formula |
|---|---|
| `sell_vol_dryup` | pullback down-volume ÷ impulse down-volume, clock-normalized |
| `updown_ratio_pb` | up-volume ÷ down-volume across the pullback |
| `pct_up_minutes_pb` | fraction of pullback 1-min bars closing green |
| `signed_vol_imbalance` | Lee-Ready (or tick-rule) classified buy − sell volume, normalized by total |

**The ideal signature is not "low volume."** It is **down-volume collapsing while
up-volume persists** — the seller is gone but the buyer is still there. If you
can only afford one data upgrade, make it trade-level data for this.

---

## §5 Supply, float, RVOL — where your instinct needs restating

| Feature | Formula | Note |
|---|---|---|
| `rvol_cum` | cumulative session volume ÷ baseline cumulative at same minute | **Range-restricted in this population** — see below |
| `rvol_daily` | today's projected volume ÷ ADV20 | |
| `float_shares` | free float | Vendor-dependent, often stale. **Use log buckets, not a continuous value**: <20M / 20–75M / 75–300M / >300M |
| **`float_rotation`** | **cumulative shares traded 9:30 → trigger ÷ free float** | **The variable you actually mean (H5)** |
| `si_pct_float` | short interest ÷ float | Bimonthly and lagged — respect the publication date |
| `days_to_cover` | short interest ÷ ADV20 | The squeeze-fuel measure |
| `mcap` | shares out × price | |

**Why RVOL will look useless here and why that isn't the answer to your
question.** You chose day-1 earnings precisely *because* they guarantee RVOL.
That means within your sample every name is 5–30× — the variable has almost no
variance left to explain anything with. Getting a null on RVOL in this study is
**range restriction, not evidence that RVOL doesn't matter.**

Two consequences:

1. Use **`float_rotation`** as the primary supply variable. It has real
   cross-sectional variance even inside an earnings population, and it is the
   actual mechanism behind "RVOL matters on low float" — it measures how much of
   the available supply has changed hands, i.e. how exhausted the float is.
2. If you genuinely want to test RVOL, you need a **second population with RVOL
   variance** — non-earnings sympathy/news names. That is a separate study, and
   worth queuing.

The interaction you're after — `MFE ~ rvol + log(float) + rvol:log(float)` — is
an interaction term, and interactions need roughly **4× the sample** of main
effects. See the power calculation in `03-study-design.md`. Be prepared for this
question to be unanswerable at your sample size, and to answer it with the
forward log instead.

---

## §6 Market & theme context — known-as-of trigger

Mirrors the Playbook Big Picture stack, so a candidate row and a Playbook entry
speak the same language.

| Feature | Formula |
|---|---|
| `spy_vs_vwap` | `(SPY - SPY session VWAP) / SPY ATR` at trigger |
| `qqq_vs_vwap` | same for QQQ |
| `vix_chg` | VIX % change on the session at trigger |
| `sector_etf_vs_vwap` | same for the mapped sector ETF (SMH/XLF/XLE/… — **SMH not SOXL**) |
| `rs_vs_sector` | candidate's return since 9:30 − sector ETF's, in ATR units |
| `rs_daily_rank` | percentile of 20-day return vs. the S&P 1500 |
| `is_leader` | `rs_vs_sector > 0 AND rs_daily_rank > 0.80` |
| `theme_breadth` | # of same-sector names also passing the day's Stage-1 filter — the "hot theme / broken slot machine" count |

`theme_breadth` is worth its own look. A reset in a name whose whole theme is
bid is a different trade than a lone gapper.

---

## §7 Execution reality — known-as-of trigger

| Feature | Formula |
|---|---|
| `spread_bps` | median quoted spread over the 5 min before trigger |
| `vol_1min_usd_p15` | median 1-min $ volume, prior 15 min |
| `capacity_shares` | shares tradable at ≤10bps impact ≈ `0.10 × mean 1-min volume` `[T]` |
| `capacity_R` | `capacity_shares × R` — **the dollar risk this trade can actually carry** |

`capacity_R` is the feature that decides whether an edge is a business or a
curiosity. Compute it in Phase 0. An 0.4R edge you can only put $400 of risk
into is not a strategy.

---

## §8 Discretionary — known-as-of trigger (recorded blind)

| Feature | Source |
|---|---|
| `eye_clean` | 1–5, blind grade (`04-eye-test.md`) |
| `eye_level_grade` | 1–10, Playbook level grade |
| `eye_take` | would you take it, yes/no |
| `eye_size_band` | probe / A / A+ |
| `eye_grader` | who graded it — you and your partner grade independently |
| `eye_note` | free text, one line |

---

## §9 Outcome labels — known-as-of *after* trigger (never a model input)

| Label | Definition |
|---|---|
| `mfe_15/30/60/120` | max favorable excursion in R at each horizon |
| `mae_15/30/60/120` | max adverse excursion in R |
| `mfe_eod`, `mae_eod` | through 15:55 |
| `ret_eod_R` | close at 15:55, in R |
| `ret_nextopen_R`, `ret_nextclose_R` | overnight and day-2 continuation |
| `time_to_mfe` | minutes from entry to `mfe_eod` |
| `hit_1R_before_stop` | binary, the simplest sanity label |
| `stopped` | binary, MAE ≤ −1R |
| `exit_*_R` | realized R under each candidate exit rule, incl. the EMA9 hot key variants |

**Keep labels in a separate table from features, joined on `candidate_id`.**
Physical separation is the cheapest defense against accidentally training on the
future, and it will save you at least one wasted week.
