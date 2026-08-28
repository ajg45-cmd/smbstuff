# 00 — The thesis

## What you are actually looking for

> A day-1 earnings name that gapped, held the gap, and **cleared the premarket
> high** in the first hour; that then makes an **orderly first pullback** into a
> reference level (session VWAP, reclaimed PMH, or the opening-range high)
> between **10:30 and 12:00**, on volume that is **drier than the midday clock
> alone would explain**; and that then **resumes with a volume expansion**
> through the pullback high.
>
> You are buying the **second leg of an accumulation program** at the point where
> the day's supply has been demonstrated *absent*. Risk is the pullback low.
> Size is a function of how many independent confirmations stack, with the
> largest single upgrade being that today is also a **breakout from a
> multi-month range** — because that converts a day trade into a position with
> multi-day continuation.

That paragraph is the whole project. Everything else here exists to make each
bolded phrase a number.

## Why it should work (the mechanism)

A large buyer does not fill in one push. They work an order in legs — pausing
when price gets away from them, resuming when it comes back to their level.

The pullback on drying volume is the visible signature of that pause: **price is
drifting because the buyer stepped off the bid, not because a seller arrived.**
That is the entire distinction the setup rests on. A pullback where volume
*expands* is a seller hitting bids — that is distribution and you do not want it.
A pullback where volume *contracts* is an absence of participation — the prior
demand has not been met with new supply.

Three supporting mechanics:

1. **The first hour clears overnight supply.** Gap-fill sellers, overnight
   holders taking the pop, and shorts covering all transact in 9:30–10:30.
   Clearing the premarket high is the evidence that the day session has absorbed
   them. This is why a VWAP pullback *below* PMH is a different and worse trade —
   there is still untested overnight supply above you.
2. **10:30–12:00 is disproportionately programmatic.** Retail and news-reaction
   flow concentrates in the first hour. What is left at 11:15 is more likely to
   be a schedule-driven institutional order, which is exactly the participant
   whose behavior the setup is trying to detect.
3. **Day-1 earnings guarantees the repositioning is real.** Funds do not rebuild
   a position on a sympathy move. They do on a quarter that changed the model.

## The honest counter-case

Write this down now, before any data, so you can't quietly forget it:

- **The midday window is also the daily volume trough.** Volume declines from
  10:30 to 12:00 on *every stock, every day*. So "volume decreased on the
  pullback" will appear true in ~most of your sample regardless of whether it
  means anything. **This is the single biggest trap in your hypothesis as
  currently stated** — see `docs/02-feature-dictionary.md` §4 for the fix
  (normalize against the stock's own intraday volume curve).
- **Midday is also thin.** Wider spreads, worse fills, more false triggers,
  and a well-documented tendency toward chop and mean reversion. Less supply is
  good for the thesis; a thinner book is bad for the execution.
- **"Midday reversal" is the competing folk theory** and it points the other
  direction. Both cannot be right in the same window on the same population.
- **Rarity may kill it even if it's real.** If the full filter stack produces 3
  candidates a month, it is a supplement, not a strategy. Counting candidate
  frequency is a Phase 0 output precisely because it can cheaply reshape the
  project before you build anything.

## Primary hypothesis (pre-registered — do not edit after seeing results)

**H1.** Among day-1 post-earnings candidates meeting the structural filters in
`01-setup-definition.md`, the **time-of-day-normalized pullback volume ratio
(nPVR)** is inversely related to the forward MFE of the continuation leg.

Concretely: candidates in the **bottom nPVR tercile** produce a mean
`MFE_60min` at least **0.30R higher** than candidates in the **top nPVR
tercile**, with a permutation p-value < 0.05, after controlling for pullback
depth and duration.

**Falsification.** If the tercile spread is < 0.15R, or p > 0.05, or the spread
disappears when depth and duration are controlled for, then **volume dry-up does
not carry this setup on its own** and you go back to the structural variables.

### The control you must not skip

nPVR is mechanically correlated with **pullback depth** and **duration** — a
shallow, three-bar pullback has low volume almost by construction. If you don't
residualize or bucket on those, you will "discover" that shallow pullbacks work
and publish it to yourself as a volume finding. H1 is only tested *within* depth
and duration buckets.

## Secondary hypotheses (exploratory — hypothesis-generating only)

These do **not** get to be conclusions from this dataset. They generate the
hypothesis you pre-register for the *next* study or the forward paper log.

- **H2 (spring).** Dry-up alone is inert; dry-up *followed by expansion* is the
  signal. `trigger_vol_ratio / nPVR` ("spring ratio") beats either alone.
- **H3 (leg count).** `leg_index == 2` outperforms `leg_index >= 4`. The second
  leg is the trade; the fourth is the exit.
- **H4 (range expansion scales size).** Expectancy increases monotonically with
  the *timeframe* of the range being broken (20d < 60d < 252d < ATH). If true,
  this replaces guessed size bands with measured ones.
- **H5 (float rotation, not RVOL).** Within a day-1 earnings population, RVOL is
  range-restricted and will look useless. **Float rotation** (cumulative shares
  traded ÷ free float at trigger) carries the information you *mean* when you
  say "RVOL matters on low float," because it measures how much of the available
  supply has actually changed hands. See `05-open-questions.md` §D.
- **H6 (level type).** Which level the pullback resets against (VWAP / PMH /
  ORH / PDH) is itself a categorical predictor, not decoration.
- **H7 (catalyst quality).** Gap size *relative to the options-implied move* —
  not gap size alone — predicts multi-day continuation. This is the eventual
  catalyst link, and it is the cleanest quantitative proxy for "the Street was
  surprised."

## How this connects to the EMA9 hot key script

The exit script and this study are the same project from two ends.

The study logs the **full forward path** (MFE/MAE at every horizon) rather than
one exit. That means once you have the candidate set you can evaluate your
actual exit tool against alternatives on the *same trades*:

- EMA(9) on 5-min close (what the hot key does today)
- EMA(9) on 15-min close
- EMA(9) with the ATR buffer you were considering as v2
- VWAP loss
- Trailing 15-min swing low
- Fixed 2R / 3R
- Time stop at 12:30 / 14:00 / EOD

The v2 upgrades you sketched (ATR buffer, RVOL filter, 5-EMA failover, 15:30
cutoff) should not be guessed — every one of them is a parameter this dataset
can score. Build the dataset first; the script's v2 falls out of it.
