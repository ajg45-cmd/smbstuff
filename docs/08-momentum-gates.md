# 08 — Momentum gates, VWAP anchors, and the filter ladder

New requirements from 08-29, all implemented and testable. Three of them are
worth more than a line in a table.

## What's new

| Requirement | Implementation |
|---|---|
| Does a **guidance raise** on day-1 earnings raise EV? | `guidance` carried as an event attribute, sliced and laddered |
| **Session VWAP vs Day VWAP** | `vwap_anchor` is a swept parameter; both are run |
| **Both gap directions** eligible | `gap_pct` and `gap_direction` logged, never filtered |
| Entry must be **out of the premarket range** | Gate: above PM high for longs, below PM low for shorts |
| Entry bar **closes beyond all EMAs** (5/9/21) | Gate on the entry frame |
| **Everything upsloping, proven by the first 30 min** | Gate: all EMAs sloping with the trade, established by 10:00 |
| "**Closes above the 21 EMA ~90% of the time**" | Persistence measured on 2-min and 5-min |
| **5 / 10 / 15-minute** frames | All three, crossed with the exit frame |

---

## 1. Continuous EMAs — a correctness fix, not a preference

A 21-period EMA on 15-minute bars needs 21 bars, which is over **five hours**.
At 10:00 a session-only EMA21 has seen **two** bars. Gating on it would be
testing something that is not the line on your chart.

Charting platforms compute EMAs on a **continuous multi-session series**, so
that is what the study does: prior sessions plus today, reindexed onto today.

This matters most for exactly the gate you asked for — "everything upsloping
proven by the first 30 minutes" is only meaningful with a warmed-up EMA. It
also means the loader needs prior sessions for every day you want to test,
which the runner already handles.

Confirmed in the test suite: with sessions that repeat identically (a large
overnight gap down every morning), the continuous EMA21 sits *above* price and
the long-side gate fails for reasons that have nothing to do with the gate.
Chaining the sessions so each opens near the prior close makes the gates behave.
Real data is chained by construction — but it is a live failure mode for any
symbol with a big gap, and the gate will read differently on gap days for a
real reason.

## 2. Session VWAP vs Day VWAP — they are not a cosmetic difference

Both anchors run on every session, and the runner reports how much they even
**agree** on which bars qualify.

On the generated exports the overlap was **39%**. That is the finding worth
carrying: on a gap up with real premarket volume, the **day-anchored VWAP is
dragged toward the premarket average and sits well below price**, so pullbacks
reach it far less often — and when they do, they are much deeper.

So these are not two ways of drawing one line. They select **different trades**:

- **Session VWAP (09:30)** — the shallower, more frequent pullback. More signals.
- **Day VWAP (premarket included)** — a rarer, deeper reset. Fewer signals, and
  on a gap-up day it may produce none at all.

Below roughly 70% overlap, treat them as two strategies and evaluate them
separately. Pooling them and reporting one number would average two different
things.

## 3. The filter ladder — the trap in "does the EV move?"

Every clean-price-action gate **cuts the sample**. Stack five filters that each
remove 40% and you keep 8% of the trades — and the survivors will show a higher
mean *almost regardless of whether the filters carry information*, because you
have taken a smaller, noisier subset and kept the good-looking one.

So "EV went up when I added the filter" is not evidence. `ablation.py` reports
three things alongside it:

1. **n at every rung.** A lift arriving with an 80% sample cut is a different
   claim from one arriving with a 10% cut.
2. **`p_random_beats` — the same-size random control.** Would selecting the same
   *number* of trades at random have produced the same lift? If a random draw
   beats the filtered mean 30% of the time, the filter told you nothing. This is
   the control that separates a real filter from arithmetic.
3. **`lift_within_trend` — the confound control.** Momentum filters are
   *mechanically* correlated with trending: a name above all its EMAs all
   morning **is** a trending name. This recomputes the lift inside trend-strength
   strata. A filter that merely selects strong trends scores near zero here.
   Without it you are rediscovering "trends trend" and calling it an edge.

**The ladder order is pre-specified** (`ablation.LADDER_ORDER`): structural gates
first, momentum next, cleanliness last — so the cleanliness claim is tested on
top of everything cheaper rather than credited for it. Ordering by whatever
raises EV most would produce a monotonic-looking ladder on any dataset, signal
or not.

### Verified on planted data

The generated exports carry a **genuinely predictive** `guidance=raise` flag and
a set of momentum gates that are **deliberately uninformative**. The harness:

| Filter | n | lift | `p_random_beats` | `lift_within_trend` |
|---|---|---|---|---|
| `guidance_raised` | 204 | **+2.78R** | **0.000** | **+2.80** |
| `beyond_all_emas` | 157 | −1.96R | 1.000 | −1.33 |
| `ema_ribbon` | 101 | −2.78R | 1.000 | −2.07 |
| `clean_90pct_ema21` | 58 | −2.34R | 1.000 | −0.78 |

It found the real effect and refused to credit the noise. That is the property
that makes the ladder worth trusting when the answers are not known in advance
— it does not mean the EMA gates are worthless in real data, only that this
harness will not flatter them.

## 4. Guidance — the one input bars cannot give you

`guidance` is not derivable from price. It comes from a sidecar file next to
the exports:

```
data/samples/events.csv
symbol,date,guidance,surprise_pct,notes
NVDA,2025-02-26,raise,12.4,
```

`guidance` ∈ `raise` / `maintain` / `cut` / `unknown`. Missing rows read as
`unknown` and land in their own slice rather than being dropped.

For a first pass this is **hand-fillable** — you are testing tens of events, not
thousands, and you likely remember or can look up the guide on each. Automating
it later means an earnings vendor (Polygon, FMP) plus parsing, which is real
work for a variable you can type in an afternoon.

**One caution.** Guidance is announced with the print, so it is known before the
entry and carries no look-ahead. But it is also *correlated with the gap itself*
— a raise is much of why the stock gapped. So a guidance lift may partly be a
gap-size lift wearing a different label. Slice by `gap_direction` and control on
`gap_pct` before concluding guidance adds anything beyond "it gapped more."

## 5. The premarket-range gate supersedes an earlier answer

On 08-28 the premarket high was recorded as an **enhancer, not a gate**. The
08-29 instruction — entry must be out of the premarket range — makes it a
**gate**, now generalized to both sides (above PM high for longs, below PM low
for shorts).

Implemented as a gate. `beyond_pm_range` is still logged on every signal, and
the scan runs with gates **off** so the ladder prices each one — so the
gate-versus-enhancer question stays measurable rather than settled by
instruction. Re-run with `require_pm_break=False` to see what it costs.

## Running it

```
python3 scripts/run_study.py data/samples --out results
```

Order of business, deliberately: VWAP reconciliation → session vs day anchor →
the filter ladder → the exit leaderboard → the universe report for the winner.
The reconciliation runs first because if the study's VWAP is not the line that
was on your screen, nothing downstream is worth reading.
