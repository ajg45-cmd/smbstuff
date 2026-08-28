# 04 — The eye test

You said you want to trade clean price action and need to check the charts. Good
— but an eye test bolted onto a study *after* you know the outcomes isn't a
filter, it's a way of laundering hindsight into rules.

Built correctly, it does something much better: **it turns your discretion into a
measured variable**, tells you whether your eye actually adds value, and
reverse-engineers what your eye is seeing into features you can compute.

## The protocol: blind, then reveal

1. The scanner produces candidates. **You never choose which ones to look at.**
2. For each candidate the tool renders two panels, **truncated at the trigger
   bar** — nothing after it exists:
   - **Intraday:** 1-min and 15-min, from premarket through the trigger bar,
     with VWAP, PMH, ORH, PDH, EMA9(15m), and a volume pane.
   - **Context:** daily, 6 months, with the 20/60/252-day range highs marked.
3. You grade **before** seeing any outcome:

   | Field | Scale |
   |---|---|
   | `eye_clean` | 1–5 — how orderly is the pullback |
   | `eye_level_grade` | 1–10 — Playbook level grade at the reset level |
   | `eye_take` | yes / no — would you take this |
   | `eye_size_band` | probe / A / A+ |
   | `eye_note` | one line: what you're seeing |

4. **Only after submitting** does the tool reveal the forward path.
5. Grade in sessions of 25–50. Log grader identity and timestamp.

## Decoys are mandatory

Mix in, unlabeled and shuffled:

- ~20% **near-miss** candidates (failed one filter — no PMH clear, depth 0.75,
  volume expanded on the pullback)
- ~10% **random** 10:30–12:00 entries in the same names

Without decoys you are grading a list you already know is pre-filtered, and every
chart looks like a setup. The decoys are what make the grades mean anything.

## What this unlocks

**1. Does your eye add anything?** Fit two models on the same trades —
mechanical features only, vs. mechanical + `eye_clean`. Compare **out-of-sample**
performance. If the grade adds incremental predictive power, your discretion is a
real edge and should be formalized as a gate. If it doesn't, you have learned
something genuinely valuable and slightly uncomfortable, and you can automate
with a clear conscience.

**2. Do you and your partner mean the same thing by "clean"?** Both grade the
same 200 candidates independently; compute **Cohen's κ**. Low agreement means
"clean" isn't a shared concept yet, and no amount of modeling fixes that — you
sit down and define it from the disagreements. Do this **first**; it's the
cheapest, highest-yield experiment in the repo and you can run it on 200 charts
in two evenings.

**3. What is your eye actually seeing?** Regress `eye_clean` on the mechanical
features. Whatever loads highest — `overlap_ratio`, `max_pb_bar_range_atr`,
`level_confluence`, `duration_bars` — **is** your pattern recognition, written
down. This is the mechanism that converts discretion into code, and it's the most
interesting output of the whole project.

**4. Are you calibrated?** Build a reliability diagram: when you say A+, what is
the realized hit rate and mean R? Versus A? Versus probe? If A+ and A have the
same expectancy, your bands are not carrying information yet and sizing 80% on
A+ is not "earning the right" — it's variance. That check feeds straight back
into `06-odds-enhancer-scorecard.md`.

## Implementation

Two paths, in order of how fast you'll have it:

**A. Static (recommended for Phase 0).** The scanner writes
`candidates.parquet` plus a folder of pre-rendered PNGs (matplotlib/mplfinance).
A single self-contained HTML page loads a JSON manifest, shows one chart at a
time with the grading form, and appends rows to a CSV via download or a tiny
local Flask endpoint. No infrastructure, works offline, done in an afternoon.

**B. Interactive (Phase 2+).** Streamlit or a small React app with a real
charting library, so you can zoom and change timeframe. Worth it once you're
grading hundreds and the truncation logic is proven.

**Non-negotiable in either path:** rendering must be **physically incapable** of
including post-trigger bars — slice the dataframe at the trigger index before it
ever reaches the plotting call, don't just set an x-limit. A visible axis that
extends past the trigger leaks the outcome, and you cannot un-see it.

## Schema

```
candidate_id, grader, graded_at, eye_clean, eye_level_grade,
eye_take, eye_size_band, eye_note, seconds_spent, is_decoy
```

Keep `seconds_spent`. If grades made in 4 seconds predict as well as grades made
in 40, that itself is a finding about how much deliberation the read requires.
