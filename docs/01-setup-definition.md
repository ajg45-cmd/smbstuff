# 01 — Setup definition

Rules written so a scanner picks candidates, not you. Every threshold marked
`[T]` is a tunable to be swept in the sensitivity analysis — the starting values
are priors, not findings.

Timezone is US/Eastern throughout. All bars are timestamped by **bar open**.

## Three-tier timeframe structure

Do not pick "the" timeframe. Use three, each for what it's good at:

| Tier | Timeframe | Used for |
|---|---|---|
| **Context** | Daily | Range expansion, ATR, ADDV, prior range high, float rotation base |
| **Structure** | **15-min** | Leg definition, pullback identification, the trigger |
| **Execution** | 1-min | VWAP, volume ratios, exact entry/stop, MFE/MAE path |

**Why 15-min and not 30-min for structure:** the 10:30–12:00 window is only
**three** 30-min bars. Three bars cannot express impulse → pullback → trigger.
15-min gives six, which is the minimum viable resolution for the pattern. 30-min
is a context lens here, not a trigger lens.

**But make it a tested parameter.** Run the whole study with the trigger defined
on 5 / 10 / 15 / 20 / 30-min bars. The requirement is not that 15-min wins — it
is that the edge forms a **plateau** across neighboring timeframes. An edge that
exists at 15-min and vanishes at 10-min and 20-min is a fitting artifact, and
finding that out early is worth more than a good backtest.

## Stage 1 — Universe (known before 9:30)

| Filter | Value | Note |
|---|---|---|
| Day-1 earnings | Prior-session AMC **or** this-session BMO report | Getting BMO/AMC right is the classic silent bug — see `03-study-design.md` |
| Price | `open >= $5` `[T]` | Below this the spread math stops working |
| Liquidity | 20-day ADDV `>= $50M` `[T]` | Point-in-time; uses only prior sessions |
| Gap | `abs(gap_pct) >= 3%` `[T]` | Bellafiore's fresh-order-flow threshold |
| Direction | Gap up (long-only for v1) | Short side is a separate archetype, not a mirror |
| Data integrity | Premarket 1-min bars present, split-adjusted | No PMH → no candidate |

**On your "$5M traded" filter:** as stated it is a look-ahead. Total volume "on
the day" is not known at 10:30. Convert it to three point-in-time filters:

1. **Pre-open:** 20-day ADDV ≥ $50M (known at 9:29).
2. **At trigger:** cumulative session $ volume from 9:30 to trigger ≥ `$25M` `[T]`.
3. **Capacity at trigger:** median 1-min $ volume over the prior 15 minutes ≥
   `$300k` `[T]` — this is the one that decides whether *you* can get filled.

Filter 3 is the one that matters and the one everyone omits.

## Stage 2 — Open quality (measured at 10:30, uses only 9:30–10:30)

"Strong open" needs to be a number. Compute an **Open Strength Score** from four
components, each scaled 0–1, then average:

| Component | Formula |
|---|---|
| `pct_above_vwap` | fraction of 1-min bars 9:30–10:30 closing above session VWAP |
| `range_position` | `(close_1030 - low_0930_1030) / (high_0930_1030 - low_0930_1030)` |
| `pmh_clear` | `(high_0930_1030 - premarket_high) / ATR14_daily`, clipped to [0,1] |
| `trend_quality` | `MFE / (MFE + MAE)` measured from the 9:45 close to 10:30 |

**Hard gates** (a candidate fails outright, regardless of score):

- Session **traded above the premarket high** at some point before 12:00, and
  the 15-min bar that broke it **closed** above it. *This is your "must clear
  premarket high" rule and it is a gate, not a score.*
- No 15-min **close** below session VWAP between 9:45 and the trigger.
- `close_1030 > open_0930` — the open did not fade.

Starting threshold: `open_strength >= 0.60` `[T]`. Sweep it; do not defend it.

## Stage 3 — Leg structure (the "buy program")

On 15-min bars, detect swings with an ATR-scaled zigzag (reversal threshold
`0.75 × ATR14_15min` `[T]`; see `features.py:swing_points`).

**Impulse leg (leg *n*)** — from swing low `L0` to swing high `H1`:

- `H1` occurs at or after 09:45 and before 11:45
- Advance `>= 1.0 × ATR14_15min` `[T]`
- No 15-min close below VWAP during the leg
- `leg_index` = how many impulse legs have completed today. **The trade is
  leg 2** — one prior impulse leg exists (H3). Log `leg_index` for every
  candidate; do not filter on it in v1, test it.

**Pullback leg** — from `H1` down to swing low `L2`:

- `L2` occurs in the **10:30–12:00** window (this is the setup's defining constraint)
- Retracement `depth = (H1 - L2) / (H1 - L0)`, required in `[0.20, 0.70]` `[T]`
  — shallower is noise, deeper breaks the leg
- Duration between `2` and `6` 15-min bars `[T]`
- **Never closes a 15-min bar below the reset level** (see below)
- `L2 > L0` (higher low — the leg structure is intact)

**Reset level** — the pullback must hold within `0.35 × ATR14_15min` `[T]` of at
least one of these, and you **record which one** (`reset_level_type`, an H6
predictor):

| Type | Definition |
|---|---|
| `VWAP` | session volume-weighted average price |
| `PMH` | premarket high, now acting as support after the clear |
| `ORH` | opening-range (9:30–10:00) high |
| `PDH` | prior day high |
| `EMA9_15` | 9-period EMA on 15-min closes — *the same line the hot key exits on* |
| `ROUND` | nearest whole/half dollar for price > $50 |

Log **all** levels within tolerance and the count (`level_confluence`), not just
the first. Confluence is itself a candidate enhancer.

## Stage 4 — Trigger

**Entry:** first 1-min trade above `H_pb + 0.02` where `H_pb` is the high of the
pullback's final 15-min bar, occurring before **12:00**.

**Volume confirmation:** the trigger bar's volume must be `>= 1.5 ×` `[T]` the
mean per-minute volume of the pullback leg. Dry-up without expansion is a
non-event — this is the second half of H2 and it is not optional.

**Entry price for the study:** trigger price + a slippage model
(`max(1 tick, 0.5 × quoted spread) + impact`), never the bar close. See
`03-study-design.md` §Costs.

## Stage 5 — Risk

- **Stop:** `L2 - 0.10 × ATR14_15min` `[T]` (structural: below the pullback low).
- `R = entry - stop`. Record `R_pct = R / entry` and `R_atr = R / ATR14_15min`.
- **Location filter:** skip if `R_pct > 2.5%` `[T]`. A stop that wide means you
  are not at the level — you are chasing. Log the skips; they are their own study.

## Stage 6 — Exits: do not choose one yet

**Log the path, derive the exit later.** For every candidate record MFE and MAE
in R at `+15, +30, +60, +120` minutes, `15:55`, next-day open, next-day close,
plus `time_to_MFE`.

That gives you the full exit surface, and it lets you score every candidate exit
rule — including the EMA9 hot key as it currently exists — on the same trades.
Choose the **plateau** on that surface, not the peak.

## Sizing (to be *derived*, not assumed)

Your existing Playbook bands are probe / A / A+ → 15% / 30% / 80% of stop. The
output of this study is an **empirical** mapping from stacked enhancers to those
bands. See `06-odds-enhancer-scorecard.md`. Until then, every candidate is a
probe.
