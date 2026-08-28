# 05 — Open questions

The list you asked for. Grouped, and prioritized: **§0 blocks everything else.**

Answer §0 in a sitting with your trading partner and write the answers into
`01-setup-definition.md`. The rest can be answered by the data — but only once
§0 has made the questions well-posed.

---

## §0 — Answer these ten first (everything downstream depends on them)

1. **"$5 million traded" — shares or dollars?** And measured *when*? As written
   it's a look-ahead (you don't know the day's volume at 10:30). Proposal in
   `01-setup-definition.md`: ADDV ≥ $50M pre-open, cumulative $25M at trigger,
   plus a 1-minute capacity floor. Do those numbers match what you mean?

2. **What is a "strong open," in a number you'd accept before seeing the
   outcome?** Held above VWAP the whole hour? Closed the 10:30 bar in the top
   third of the range? Cleared PMH and never lost it? Pick the definition, then
   let the sweep tell you the threshold.

3. **Is clearing the premarket high a hard gate or an enhancer?** You wrote it as
   a requirement. Confirm — because as a gate it may cut the sample by half or
   more, and that changes whether this study is powered at all.

4. **Must the pullback hold above VWAP, or may it wick through and reclaim?**
   A wick-and-reclaim is a materially different (and often better) trade. Decide
   whether it's the same setup or a sibling archetype, because you cannot pool
   them and then interpret the result.

5. **Is 10:30–12:00 a hard window or the center of a distribution?** Does a
   12:20 trigger count? A 10:15 one? Suggestion: keep the window wide for
   collection, log `trigger_time` as a feature, and let the data draw the edges.
   Filtering first throws away the evidence you'd need to set the filter.

6. **"Second leg" — second leg of what, exactly?** Second impulse leg of the day
   including the opening drive? Or the first pullback *after* the PMH clear
   regardless of what happened at 9:30? This determines `leg_index` and it's
   ambiguous in every description of the setup.

7. **Long-only for v1?** The short-side mirror is a different archetype with
   different mechanics (borrow, squeeze risk, asymmetric volume signature). Don't
   pool them.

8. **What's your data budget?** Premarket 1-min history for a 6-year universe is
   the binding constraint on this entire project. Polygon flat files, Databento,
   something else? **Answer this before writing another line of code** —
   everything else is contingent.

9. **One trade at a time, or a portfolio?** If three candidates trigger at 11:05
   on the same theme, do you take all three? This changes MC-1 (correlated
   trades), MC-4 (sizing), and the definition of a "trade" in the results.

10. **What's the smallest edge you'd actually trade?** Write the number in
    `03-study-design.md` under go/no-go **now**, before you see any results. If
    it's decided afterward, it will be whatever you happen to find.

---

## §A — The setup definition

11. Does the impulse leg have to originate at the open, or can it start from a
    10:00 base?
12. Does the pullback have to be the *first* of the day, or the first after the
    PMH clear?
13. Minimum bars in the pullback? (One 15-min bar down isn't a reset — or is it?)
14. If price grinds sideways instead of pulling back, is that the same setup?
    A time-based reset and a price-based reset may behave very differently.
15. What invalidates it *before* the trigger — a lost VWAP? A lower low? How many
    bars of chop before you stop watching?
16. Does the trigger require a *close* above the pullback high, or is a trade
    through it enough? (Trade-through fills better; close confirms better. Test
    both; the answer is probably size-dependent.)
17. Is there a maximum extension from VWAP at trigger beyond which you're chasing?
18. If it triggers, stops, then re-sets and triggers again — is that a second
    trade or the same trade re-entered? Decide before it happens in the data.

## §B — The volume hypothesis (your core question)

19. Do you accept that **raw** declining volume into midday is near-universal and
    therefore uninformative? (`02-feature-dictionary.md` §4.) If yes, `npvr` is
    the variable, not raw volume — this is the most important reframing in this
    repo.
20. Which baseline for the clock: the stock's own trailing 20-session curve, or a
    cross-sectional day-1-earnings composite? (Own history is cleaner but often
    unrepresentative *because* yesterday was a normal day and today isn't.)
21. Volume dry-up relative to the **impulse leg**, or relative to the **whole
    session so far**? These give different numbers and different stories.
22. How much of what you call dry-up is really just **shallow and short**? This
    is the confound that most likely explains the whole effect — H1 is only
    tested within depth × duration buckets for this reason.
23. Is the ideal signature low *total* volume, or **collapsing down-volume with
    persistent up-volume**? If the latter, you need trade-level data and that's a
    budget decision.
24. Does volume expansion on the **trigger** bar matter more than dry-up on the
    pullback? (H2.) Plausibly the dry-up is context and the expansion is signal.
25. Is there a level of dry-up that's *too* dry — where nobody cares anymore and
    the name is simply dead?
26. Should volume be measured in shares, dollars, or trade count? Trade count is
    the least manipulated by a single block print and is worth testing separately.
27. Do block prints and odd-lots need excluding? One 500k print inside a quiet
    pullback wrecks the ratio — and may also be the single most informative event
    in the window.

## §C — Timeframe

28. Does the edge form a **plateau** across 5/10/15/20/30-min triggers, or a
    spike at one? (A spike means you fit it.)
29. Should the *structure* timeframe and the *trigger* timeframe be the same?
    (E.g. structure on 15-min, trigger on the 5-min break of the 15-min high.)
30. Does the best timeframe scale with the stock's ADR — faster names on 5-min,
    slower on 30-min?
31. Is 30-min usable at all inside a 90-minute window, or is it strictly a
    context lens here?

## §D — RVOL, float, supply

32. Do you accept that RVOL is **range-restricted** inside a day-1 earnings
    population, so a null result there is *not* evidence RVOL doesn't matter?
33. Is `float_rotation` the variable you actually mean when you say "RVOL matters
    on low float"? (It measures how much of the supply has changed hands — the
    actual mechanism.)
34. Which float buckets? Proposal: <20M / 20–75M / 75–300M / >300M. Does that
    match how you think about names?
35. Is your float data point-in-time, or a current snapshot applied to 2019?
    (Almost certainly the latter — document it as a known limitation rather than
    pretending otherwise.)
36. Does short interest add anything beyond float, or is it collinear?
37. Are you willing to run a **second study on non-earnings names** to get the
    RVOL variance needed to answer the RVOL question properly?
38. Does the setup behave differently in a $2B name vs. a $200B name — and should
    mega-caps be excluded entirely as a different regime?

## §E — Range expansion and sizing

39. Which range defines "longer-term" — 20, 60, or 252 days?
40. Is it the *break* that matters, or the **tightness of the base** it broke out
    of? (`base_tightness` may dominate.)
41. Does expectancy scale monotonically with the timeframe of the range broken?
    (H4 — if yes, this *is* your sizing rule, derived rather than guessed.)
42. All-time high: its own category, or just the extreme of the same scale?
43. How far above the range is too far — at what point is the expansion already
    spent?
44. Does the size-up condition need to hold **at the trigger**, or is a break
    later in the day still a valid upgrade?
45. Do your existing bands (probe/A/A+ = 15/30/80% of stop) survive contact with
    the measured conditional expectancies?

## §F — Entry, stop, exit

46. Stop below the pullback low, or below the reset level? They're different
    trades with different R.
47. What's the widest R (in % and in ATR) you'll accept before the location is
    simply wrong?
48. Does the answer to "best exit" depend on the enhancer stack? (Almost
    certainly — an A+ range-expansion day should probably be held very differently
    from a probe.)
49. **How does the EMA9(5-min) hot key score against the alternatives on this
    exact candidate set?** This is Phase 2 and it directly validates or replaces
    the tool you're already using.
50. Should the exit rule switch timeframes once you're up X ATR — your "5-EMA
    failover" idea? Test it; don't assume it.
51. Is there a time stop? What does the MFE-vs-time curve look like — does the
    trade stop working at 13:00?
52. Do you hold overnight when the trade is also a multi-month range breakout?
    (`ret_nextclose_R` will tell you, and it's likely where the real money is.)
53. Does the 15:30 cutoff you sketched for the hot key actually improve
    expectancy, or does it cut the tail that pays for everything?
54. Scale out, or all-or-nothing? Scaling smooths the equity curve and lowers
    expectancy — is that trade worth it at your account size?

## §G — The eye test

55. Will you commit to grading **blind**, with decoys, before seeing outcomes?
    (If not, the eye test is hindsight and adds nothing.)
56. How many charts can you realistically grade per week? That sets the pace of
    everything discretionary.
57. Will your partner grade the same 200 charts independently, so you can measure
    agreement? **Do this first** — it's two evenings and it may reveal you're
    testing two different setups.
58. If your grade adds no out-of-sample predictive power, will you accept that
    and automate?
59. If it adds a lot, will you accept that the setup can't be fully automated and
    the scanner's job is triage, not selection?

## §H — Statistics and Monte Carlo

60. Will you actually keep `results/trials_log.csv` — every threshold, feature,
    and timeframe tried? (Without it you cannot know how much you've overfit, and
    the count is always higher than memory suggests.)
61. Will you hold 2025 genuinely untouched until the end?
62. What's the minimum candidate count below which you won't interpret a result?
    (Suggest: 30 per cell, and no interaction claims under 300.)
63. Block bootstrap or iid for MC-1? (Block — trades cluster by day and theme, and
    iid will flatter your drawdowns.)
64. Do you want risk of ruin against a **fixed** account or a compounding one?
65. What drawdown, in R and in %, would make you stop trading the setup? Decide
    now; compare it to MC-1's distribution. If your pain threshold is inside the
    normal range of the edge, the edge is untradeable *for you* at that size —
    which is a sizing problem, not a signal problem.
66. Are you willing to kill the project on MC-3 Null A?

## §I — Execution reality

67. What's your actual fill quality on a 15-min bar break at 11:15 in a $60
    stock — measured, from your own fills, not assumed?
68. What size can you take without moving it? (`capacity_R`.)
69. Does the edge survive at 25% of one minute's volume, or only at 10%?
70. Are you triggering manually, on alert, or automated? The latency difference
    is worth real basis points at this timeframe.
71. Does the hot key infrastructure you already have (`ktg.interfaces`) support
    entry automation, or only exits?
72. How many candidates can you monitor simultaneously without degrading
    execution on any of them?

## §J — The catalyst layer (later, but design for it now)

73. Does gap size **relative to the options-implied move** predict continuation
    better than gap size alone? (H7 — the cleanest quantitative proxy for "the
    Street was surprised," and the best single catalyst feature.)
74. Does the *type* of earnings surprise matter — beat-and-raise vs. beat-only vs.
    revenue-beat-EPS-miss?
75. Does analyst-revision direction in the 24h after the print add anything?
76. Does `theme_breadth` (how many names in the sector are also in play) matter —
    the "broken slot machine" question?
77. Does the setup work on **non-earnings** day-1 catalysts (FDA, guidance,
    M&A, contract wins), or is the earnings mechanism specific?
78. Day 2 and Day 3 — does the same reset pattern work on subsequent days with
    decaying edge? That's a natural sample-size multiplier if it does.

## §K — Scope and process

79. What's the one result that would make you trade this tomorrow?
80. What's the one result that would make you drop it entirely?
81. Who owns which half — data/code vs. chart grading/rules?
82. What's the review cadence, and what gets written down each time?
83. Are you prepared for the most likely outcome — that the setup shows a **real
    but modest** edge (0.2–0.4R) that is **highly conditional** on two or three
    enhancers, and needs the range-expansion filter to be worth sizing? That is
    what these studies usually find, and it's a good outcome, not a failure.
