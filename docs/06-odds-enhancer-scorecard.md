# 06 — Odds-enhancer scorecard: Midday Reset Continuation (long)

A new archetype for the Playbook, in the standard format. Per the Playbook
skill: *"New archetypes get their own fixed list built the same way the first
time they're archived."*

**Read this as v0 — hand-written priors.** The point of the study is to
**replace the ★ markings and the grade bands with measured ones.** Which
variables get stars should be an empirical result, not an opinion. Until Phase 3
returns, treat every candidate as a probe.

## The archetype

Day-1 earnings name, cleared premarket high in the first hour, first orderly
pullback into a reference level between 10:30 and 12:00 on clock-normalized
volume dry-up, resuming through the pullback high on volume expansion. Buying
the second leg of an accumulation program.

## Scorecard v0

| # | Variable | Present? | Note |
|---|----------|----------|------|
| 1 | ★ **Real day-1 catalyst** — earnings that changed the model, not sympathy (gap ≥ implied move is the quantitative version) | | |
| 2 | ★ **Premarket high cleared and held** — 15-min close above PMH, no reclaim failure | | |
| 3 | ★ **Clock-normalized volume dry-up** on the pullback (`npvr < 1`) — *not* raw declining volume | | |
| 4 | ★ **Volume expansion on the trigger bar** (≥1.5× pullback mean) — the dry-up is context, this is the signal | | |
| 5 | **Second leg**, not the fourth (`leg_index == 2`) | | |
| 6 | **Reset at a graded level** ≥7/10, ideally with confluence (VWAP + PMH, VWAP + PDH) | | |
| 7 | **Range expansion** — above the 20/60/252-day range high; the size-up condition | | |
| 8 | **Orderly pullback** — high bar overlap, no wide-range down bar, holds structure | | |
| 9 | **Leader quality** — daily RS + sector RS; leading, not lagging its stack | | |
| 10 | **Big-picture alignment** — SPY/QQQ/sector ETF supportive, VIX not spiking (SMH/SOXX, never SOXL) | | |
| 11 | **Float rotation** high enough that supply has genuinely turned over | | |
| 12 | **Tape** — bid holding or stepping up through the pullback; no seller stepping down | | |
| 13 | **Capacity** — `capacity_R` supports the size you want, spread not blown out | | |
| 14 | **Location** — R ≤ 2.5%; you're at the level, not chasing it | | |

**Key (★): 1, 2, 3, 4.**

- No **real catalyst** → it's a chart, not a trade.
- **PMH not cleared** → there is untested overnight supply above you; a VWAP
  pullback below PMH is a different and worse setup.
- **Volume dried up only as much as the clock explains** → you haven't observed
  anything; that's just lunchtime.
- **No expansion on the trigger** → nobody showed up; it's a drift, not a leg.

Any ★ missing → the setup may be **invalid** regardless of how many others are
checked.

## Grade bands (v0 — pending MC-4)

Same bands as the rest of the Playbook, applied here:

- **3–4 enhancers, no ★ missing** → probe / B, 15% of stop
- **Most present, all ★ strong** → A, 30%
- **Full stack including range expansion (#7)** → A+, 80% — "earned the right"
- **Any ★ absent** → pass, whatever the count

**Range expansion (#7) is the hypothesized biggest size upgrade** because it
converts a day trade into a multi-day position — the overnight and day-2
continuation is where the tail lives. H4 tests exactly this, and MC-4 checks
whether 80% of stop is justified or aspirational.

## What Phase 3 replaces here

1. Which variables earn ★ — by measured conditional expectancy, not intuition.
2. The band thresholds — how many enhancers actually separate a 0.2R trade from
   a 0.8R trade.
3. The size percentages — from MC-4's risk-of-ruin sweep against your account,
   not from the house default.
4. Whether the **eye-test grade** belongs on this card as variable #15 — it does
   if and only if it adds out-of-sample predictive power over rows 1–14
   (`04-eye-test.md`).

## Using it now

Copy the table into the Setup Variables section of any Playbook entry for this
archetype. Mark present/absent/partial with a one-line justification. Total,
check no ★ is missing, state the band, and confirm it matches the size you
actually took. Where it didn't, that gap is the leak — and it is also a data
point for Phase 3, so keep every scorecard you fill in.
