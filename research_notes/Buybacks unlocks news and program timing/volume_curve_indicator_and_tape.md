# Intraday Volume Curve / Pace Indicator, Program-Schedule Inference, and the 100-Share Tape Filter (US equities, as of Nov 2026)

**Read this first (source quality).** This session's network blocked direct page fetches for every site tried (nasdaq.com, cboe.com, memx.com, bmlltech.com, citadelsecurities.com, toslc.thinkorswim.com, usethinkscript.com). Every "Cited Finding" below therefore comes from search-engine result summaries of the linked page, not from my reading the page itself. Numbers are quoted as the summaries gave them; where a summary flagged doubt, the doubt is carried over. Nothing in this file was verified against a full primary text. Books (Kissell; Johnson, "Algorithmic Trading & DMA") could not be opened at all. Anything under "Inferences" is my reasoning, not documented fact. The thinkScript in this file is my own untested draft.

---

## 1. Modeling the normal intraday volume curve (static broker-style curve vs. dynamic academic models)

### Takeaway
The baseline everyone uses is a "rolling means" static curve: average volume (or percent of day volume) in the same time bin over the past N days. Published dynamic models beat it by a large margin on raw-volume forecasts (roughly 29% to 64% lower error, depending on paper) but by much less on volume *percentages* (about 7%) and on VWAP tracking (about 9% to 15%), which means the static percent-of-day curve is a reasonable indicator baseline and the hard part is forecasting today's *total* volume.

### Cited Findings
- Rolling means (RM) is described as "the fundamental approach, predicting volume by averaging volume traded within the same interval over the past days"; it is the benchmark in the Kalman-filter paper. — [Chen, Feng, Palomar summary (alphatrade docs)](https://alphatrade.readthedocs.io/en/latest/_volume_kalman.html)
- Satish, Saxena, Palmer (FlexTrade; Journal of Trading 2014): versus a historical-average base case, raw volume prediction improved 29%, volume-percentage prediction improved 7%, and a VWAP algorithm using their predicted percentages improved 9% versus one using historical averages. Accuracy metric for raw volume is MAPE. Figures are from FlexTrade's own summary page. — [FlexTrade summary](https://flextrade.com/resources/predicting-intraday-trading-volume-and-volume-percentages/); [paper PDF](https://flextrade.com/wp-content/uploads/2015/01/Predicting-Intraday-Trading-Volume-and-Percentages.pdf)
- Chen, Feng, Palomar (Kalman filter, state-space model with EM calibration, Lasso-based outlier handling): summaries report it outperforms RM and CMEM "by 64% and 29% respectively in terms of volume prediction and by 15% and 9% respectively in VWAP trading." The search summary could not confirm these are MAPE reductions. One third-party page lists different authors; the SSRN copy lists Ran Chen, Yiyong Feng, Daniel Palomar. — [alphatrade docs](https://alphatrade.readthedocs.io/en/latest/_volume_kalman.html); [SSRN copy via Scribd](https://www.scribd.com/document/466427502/SSRN-id3101695)
- Brownlees, Cipollini, Gallo (J. Financial Econometrics 2011, 9(3) 489-518): Component Multiplicative Error Model (CMEM) splitting volume into a daily component, an intraday periodic (time-of-day) component, and an intraday non-periodic dynamic component; data include SPY and QQQQ turnover 2002-2006; abstract says it "significantly outperforms common forecasting methods" and gives more precise VWAP predictions. Exact tracking-error numbers not surfaced. — [EconPapers record](https://econpapers.repec.org/RePEc:oup:jfinec:v:9:y:2011:i:3:p:489-518); [working paper](https://labdisia.disia.unifi.it/area01/pubblicazioni_DS/wp/2009/wp2009_01.pdf)
- Bialkowski, Darolles, Le Fol (J. Banking & Finance 2008, 32, 1709-1722): decompose volume into a market-wide component and a stock-specific component (modeled with ARMA / SETAR); CAC 40 stocks, roughly Sept 2003 to Aug 2004. A third-party summary says VWAP tracking error falls "over 10% on average and up to 50% for some stocks" (secondhand, unverified). — [HAL record](https://hal.archives-ouvertes.fr/hal-02877984); [alphatrade summary](https://alphatrade.readthedocs.io/en/latest/_vwap_2007.html)
- A 2025 arXiv paper (machine learning volume forecasts) confirms the intraday U- or J-shape and reports VWAP tracking error reductions of 20% to 57% against CMEM. — [arXiv 2505.08180](https://arxiv.org/html/2505.08180v1)
- Credit Suisse AES sales note: "Most VWAP strategies run on a historical volume schedule with limited real-time consideration." — [GlobalTrading / Credit Suisse AES](https://www.globaltrading.net/?p=31156)

### Inferences
- Indicator design consequence: build two things, not one. (a) A percent-of-day curve p(t) = average over N days of [cumulative volume to t / that day's total volume], and (b) an expected-total-volume estimate. Projected end-of-day volume = today's cumulative volume to t / p(t). The literature's large raw-volume gains versus small percentage gains say (a) is fairly stable and (b) is where error lives.
- The projection is noisiest early: at 10:00 ET p(t) is small, so a small error in p(t) is a large error in projected volume. This is arithmetic, not a sourced claim.
- Use median or trimmed mean across the N days rather than a plain mean if earnings days, index rebalance days and option expirations are in the window; Chen et al. needed an explicit outlier-robust version, which supports treating outlier days specially.

### Gaps
- No source found for typical broker lookbacks (20-30 days) or bin sizes, or for how brokers handle half days, expiration days, earnings days and auctions in their curves. Common practice as I understand it (separate curves for triple-witching, index rebalance and half days; auctions modeled as separate bins) is unsourced here.
- No sourced number for the absolute error of a static curve (for example MAPE per 15-minute bin), and none for day-to-day curve stability by market cap. The papers above report improvements relative to the baseline, not the baseline's absolute level, in what I could see.
- "Markov & others" not researched.

---

## 2. Current shape of the US intraday volume curve (numbers)

### Takeaway
I could not obtain a current (2023-2026) bucket-by-bucket table. Sourced points: first 30 minutes about 11.0% to 12.6% of volume (NYSE, data apparently through 2021), last hour about 21% (Nasdaq, 2021), closing auction roughly 5% to 10% of consolidated volume in 2024-2025 with large month-to-month swings. Sources use different denominators and disagree by a factor of two or more on the close.

### Cited Findings
- First half hour (9:30-10:00): "11.0% to 12.6% of total volume," with "some reversion to the smile shape"; the curve has shifted toward the period after the opening auction. Data appear to run through late 2021. — [NYSE Data Insights](https://www1.nyse.com/data-insights/opening-auction-filling-behaviors-opportunities-early-in-the-day)
- Opening auction: about 1% to 1.2% of NYSE-listed volume; averaged 44 million shares a day in the first four months of 2024. — [NYSE](https://nyse.com/data-insights/buyers-and-sellers-meeting-earlier-in-the-nyse-opening-auction)
- Last hour: "an average of 21.2% of total volume was traded within the final hour" in 2021, peaking over 30% in March 2021. — [Nasdaq, M-ELO: the final hour of trading (2021)](https://www.nasdaq.com/articles/m-elo%3A-the-final-hour-of-trading-2021-06-22)
- Closing auction, academic series: 3.11% of daily dollar volume in 2010 rising to 7.48% in 2018; the share of volume in 3:30-3:55pm *declined* over 2010-2018. — [Bogousslavsky & Muravyev, AEA draft](https://aeaweb.org/conference/2021/preliminary/paper/H9T4hef7)
- Closing auction, 2024: about $50 billion notional a day, roughly 9% of total daily volume (BMLL); NYSE says Q2 2024 closing auctions across US markets matched $55.5bn/day, 9.44% of notional, record highs. — [BMLL](https://www.bmlltech.com/news/market-insight/into-the-close-unpacking-u-s-closing-auction-dynamics-and-the-impact-of-the-russell-reconstitution); [NYSE](https://nyse.com/data-insights/nyse-closing-auction-price-discovery-opportunities-reach-new-highs)
- Closing auction, March 2024: "Nearly 10% of all US shares were traded in that closing auction last month" (Rosenblatt via Bloomberg, article dated April 29, 2024). — [WealthManagement / Bloomberg](https://www.wealthmanagement.com/equities/stocks-trade-for-390-minutes-a-day-increasingly-only-10-matter)
- Closing auction, 2025 monthly (Rosenblatt, share of total equity volume): June 8.55%, September 7.87%, October 5.19%, November 6.68%; a 9.74% figure appears in the 2025 year-in-review (month not identified). — [Rosenblatt Oct 2025](https://www.rblt.com/market-structure-reports/us-securities-volumes-october-2025); [Nov 2025](https://www.rblt.com/market-structure-reports/us-securities-volumes-november-2025); [2025 review](https://www.rblt.com/market-structure-reports/us-securities-volumes-2025-year-in-review)
- Conflicting figure: Instinet data via State Street put the US closing auction at 15.39% of daily volume in December 2025 (Europe 34.82%). This is about double Rosenblatt's consolidated figures, so the denominator almost certainly differs. — [State Street](https://www.ssga.com/us/en/institutional/insights/how-passive-investing-reshaping-microstructure)
- Conflicting figure: Nasdaq documents give the closing cross as "almost 10%" of Nasdaq ADV in one FAQ and "almost 16%" of Nasdaq volume (open about 4%) in another piece. Venue-specific, not consolidated. — [Nasdaq closing cross FAQ](https://www.nasdaqtrader.com/content/productsservices/Trading/ClosingCrossfaq.pdf); [Nasdaq auctions article](https://www.nasdaq.com/articles/auctions-automated-market-structure-delivers-best-execution-outcomes-2021-11-04)
- NYSE closing auction: 5% to 8% of NYSE-listed volume on an average day; the three largest NYSE closing auctions in history occurred in 2025. — [NYSE](https://www.nyse.com/research/insights/nyse-closing-auction-timing-shifts-and-marketability-trends); [ICE via FXNewsGroup](https://fxnewsgroup.com/forex-news/exchanges/ice-announces-record-milestones-reached-in-2025-across-its-global-derivative-and-nyse-equity-nyse-options-markets/)
- 2018 reference: more than 25% of NYSE trading happened after 3:30pm (ITG via CNBC). — [CNBC](https://www.cnbc.com/2018/03/15/investors-are-waiting-until-the-very-end-of-the-day-to-make-their-trades.html)
- Less than a third of intraday volume trades on lit venues at the NBBO (Nasdaq / Mackintosh, "It's darkest in the middle of the day"). — [Nasdaq](https://nasdaq.com/articles/its-darkest-middle-day)
- 2025 volume backdrop: ADV 17.6 billion shares, up 44.6% year over year. — [Cboe 2025 review](https://www.cboe.com/insights/posts/2025-u-s-equities-year-in-review)

### Inferences
- The closing auction share moved between about 5% and 10% of consolidated volume within 2025 alone. A curve that includes the close as a fixed percent will misstate "pace" on index rebalance, expiration and month-end days. Keep the auction out of the continuous-session curve and model it separately.
- A high retail share in 2025 (heavy off-exchange and sub-dollar volume) lowers the auction's *percentage* without the auction shrinking in dollars; percent-of-day curves are sensitive to the retail mix. This is my reading of the Rosenblatt swings, not a sourced statement.
- Do not use one market-wide curve: compute the curve per symbol from its own history.

### Gaps
- No current sourced table of percent of volume by half hour or hour. Per-hour figures for 2023-2026 are missing. Build it from your own bar data.
- Citadel Securities ("Crowd Surfing"), BMLL, Virtu and Goldman notes were not readable; Citadel's piece reportedly covers retail versus institutional intraday curves.
- Nasdaq/Mackintosh "volume smile" article not located.

---

## 3. Existing indicator implementations and the standard formula (thinkorswim, TradingView, others)

### Takeaway
The standard definition is documented by TradingView: today's volume (per-bar or cumulative from the session anchor) divided by the average of the same quantity at the same time offset over the last N sessions. I found no verified thinkScript implementation of the cumulative time-of-day version; the common thinkorswim RVOL scripts use daily averages or a simple moving average of bars, which is not the same thing.

### Cited Findings
- TradingView built-in "Relative Volume at Time": "checks the time offset between the current bar and the start (anchor) of the most recent period, then selects the bars with corresponding time differences from a specified number of historical anchors." Cumulative mode "uses accumulated volume from the beginning of each period"; Regular mode uses non-cumulative volume. Length is the number of historical periods averaged. Lower chart timeframes improve fidelity. — [TradingView help](https://in.tradingview.com/support/solutions/43000705489); [calculation note](https://in.tradingview.com/support/solutions/43000635874)
- Community Pine scripts define RVOL as cumulative volume so far today divided by the average cumulative volume at the same minute over prior sessions, and note the session definition must match the market for "time-matched" to be consistent. A community script claims TradingView's default length is 5 while its own is 20 (third-party claim). — [TradingView community script](https://id.tradingview.com/script/3Zv6IuBl-Intraday-RVOL-Overlay-Time-Of-Day-Relative-Volume/); [RVOL script](https://www.tradingview.com/script/rIYfibKb-RVOL/)
- thinkorswim community RVOL scripts found use `volume / Average(volume, 21)[1]` or `Volume(period = AggregationPeriod.DAY) / Average(volume(period = AggregationPeriod.DAY), 20)`; forum fragments use `GetYYYYMMDD()`, `RegularTradingStart()` and `GetAggregationPeriod()` to build a session cumulative total but do not finish the same-time-prior-days comparison. A reply points to the built-in `RelativeVolumeStDev`. — [usethinkscript RVOL thread](https://usethinkscript.com/threads/rvol-relative-volume-indicator-watchlist-for-thinkorswim.1014); [Trade-Ideas-style single-bar RVOL thread (title only seen)](https://usethinkscript.com/threads/trade-ideas-intraday-single-bar-relative-volume-rvol-for-thinkorswim.16051/latest)
- thinkorswim limits: intraday aggregations cannot span more than 360 days; tick aggregations not more than 5 days. — [thinkorswim manual, chart time frame](https://tlc.thinkorswim.com/center/howToTos/thinkManual/charts/Chart-Aggregation/Setting-up-Chart-Time-Frame)
- thinkScript: a secondary aggregation period cannot be less than the chart's primary aggregation. — [thinkScript tutorial ch. 11](https://toslc.thinkorswim.com/center/reference/thinkScript/tutorials/Advanced/Chapter-11---Referencing-Secondary-Aggregation)

### Inferences
- Standard formulas (consistent with the TradingView definition):
  - Cumulative RVOL at time t: `RVOL(t) = CumVol_today(t) / mean over k=1..N of CumVol_day-k(t)`.
  - Percent-of-day curve: `p(t) = mean over k of [CumVol_day-k(t) / TotalVol_day-k]`.
  - Projected end-of-day volume: `Proj(t) = CumVol_today(t) / p(t)`.
  - Pace versus normal day: `Proj(t) / mean daily volume over N days`. With a mean-of-ratios p(t) this is close to, not identical to, RVOL(t).
- Because thinkScript cannot pull a lower aggregation than the chart, the indicator must run on the intraday chart itself, with N limited by how many days that chart loads.
- Untested thinkScript draft (my own; assumes an RTH-only chart, extended hours OFF, no half days in the window, fixed bars per day; check it against a hand calculation before trusting it):

```
# Cumulative RVOL by time of day - UNTESTED DRAFT
# Requirements: intraday chart, extended-hours display OFF, lookback days loaded on chart.
input days = 20;
def barsPerDay = RoundDown(23400000 / GetAggregationPeriod(), 0);  # 390 min RTH
def newDay = GetYYYYMMDD() != GetYYYYMMDD()[1];
def cumVol = if newDay then volume else cumVol[1] + volume;
def sumPrior = fold i = 1 to days + 1 with s = 0
               do s + GetValue(cumVol, i * barsPerDay);
def avgPrior = sumPrior / days;
plot RVOLcum = if avgPrior > 0 then cumVol / avgPrior else Double.NaN;
plot One = 1;
```

  Known weaknesses of this draft: half days (1:00pm closes) and any missing bars in thin stocks shift the fixed offset so "same bar N days ago" is no longer the same clock time; the first `days` sessions on the chart are invalid; it ignores the closing auction print unless the vendor folds it into the last bar. A sturdier version indexes bars by `SecondsFromTime(0930)` and stores per-day values, which is heavier in thinkScript.
- The built-in `RelativeVolumeStDev`, as I recall it, compares each bar's volume with a moving average and standard deviation of the preceding chart bars, so it is not time-of-day normalized. I could not open the reference page to confirm.

### Gaps
- thinkorswim per-aggregation history depth (for example how many days of 1-minute bars) not confirmed; only the 360-day intraday ceiling was sourced.
- TrendSpider, TC2000 and Trade-Ideas documentation not researched. Trade-Ideas' relative volume is widely described as time-of-day adjusted, but I have no source here.
- No verified, complete thinkScript for cumulative time-of-day RVOL was found; the forum pages could not be opened.

---

## 4. How schedule-based algos behave when behind or ahead, and what an outsider can infer

### Takeaway
Documented: most VWAP algos follow a historical volume schedule, execute mostly passively, and cross the spread when they must to keep to schedule; POV algos scale with realized volume and raise their rate when lagging. Not available to any outside observer: the parent order's size, side, start time, end time, or schedule. So "a program is behind schedule" cannot be observed from the tape; only conditions under which schedule-based orders in general must be behind or ahead can be.

### Cited Findings
- Credit Suisse AES: "Most VWAP strategies run on a historical volume schedule with limited real-time consideration. This means that even though the bid only has 1,000 shares, a buy VWAP order that needs to trade 10,000 shares right now will go right ahead to post and subsequently cross the spread to keep to schedule." The same note markets newer tactics that cross only "when opportunities are right" (vendor claim). — [GlobalTrading / Credit Suisse AES](https://www.globaltrading.net/?p=31156)
- Observed mix for a standard VWAP algo (ITG-based study, cited by a blog): "65.3% of trades were passive; 21.9% were midpoint trades; and 12.57% were aggressive." — [Themis Trading blog](https://blog.themistrading.com/?p=6148)
- Child orders are non-random, "generating strategic runs which oscillate between the aggressive or passive side of the spread"; institutional trading involves order splitting and many passive orders that go unexecuted. — [NBER conference paper on buy-side algorithms](https://conference.nber.org/conf_papers/f145256/f145256.pdf)
- IBKR best-efforts VWAP: benchmark runs from submission to the close; it tries not to take liquidity, which can mean missed fills; the user can allow it to keep working past the end time if unfilled. — [IBKR VWAP algo](https://interactivebrokers.co.uk/en/trading/orders/vwap-algo.php)
- IBKR percent-of-volume: targets a percentage of market volume, limits 0.01% to 50%. Time-variant POV recalculates on remaining size, so a lagging fill raises the effective rate (example: 1.00% rising to 3.32% by midday). — [IBKR algos](https://www.interactivebrokers.com/en/index.php?f=14369); [IBKR POV lesson](https://www.interactivebrokers.com/campus/trading-lessons/percentage-of-volume/)
- Sağlam, "Order anticipation around predictable trades" (Financial Management 2020, 49(1) 33-67; SSRN 2828363): more than 20,000 parent orders and more than 2.5 million child executions, all VWAP-benchmarked; three predictability signals built from child-order statistics (the first from the volatility of child trade sizes); stronger predictability correlates with higher execution cost; the effect shrinks when anticipation is made harder; results "mostly consistent with the back-running theory." The signals use the broker's own child-order data, not the public tape. — [EconPapers](https://econpapers.repec.org/RePEc:bla:finmgt:v:49:y:2020:i:1:p:33-67); [SSRN copy via Scribd](https://www.scribd.com/document/462910636/SSRN-id2828363-pdf)
- Closing auction evidence: closing price deviations largely reverse overnight (fully for large stocks, mostly for small), with one-third to one-half of the reversal in the first half hour after the close, consistent with uninformed price pressure. — [Bogousslavsky & Muravyev](https://aeaweb.org/conference/2021/preliminary/paper/H9T4hef7)
- NYSE MOC imbalance affects prices even before the imbalance is published (older NBER conference paper); a 2020 Imperial thesis found mixed, sometimes insignificant, predictability from published imbalances in the last 10 minutes; the indicative match price is strongly mean-reverting. — [NBER conference paper](https://projects.nber.org/confer/2009/mms09/spatt.pdf); [Imperial thesis](https://t4awstest.cc.ic.ac.uk/media/imperial-college/faculty-of-natural-sciences/department-of-mathematics/math-finance/MORAND_CLEA_01805978.pdf); [arXiv 1802.01921](https://arxiv.org/pdf/1802.01921)

### Inferences
- What the pace indicator can say (logic, not evidence):
  - A fixed-quantity VWAP/TWAP order sized off expected volume trades its planned shares per bin regardless of market volume. If market volume runs BELOW the curve, that order is a larger fraction of each bin than planned (higher participation, more footprint) and, because it relies on passive fills that depend on counterparty flow, it is more likely to fall behind and cross the spread. That is a statement about any such order, if one exists.
  - A POV order trades a fixed fraction of realized volume. Volume BELOW the curve means POV orders have done fewer shares than their owners expected and carry more residual into the afternoon and close. Volume far ABOVE the curve means POV orders complete early and stop.
  - The indicator measures market volume against history. It does not show whether any program exists, which side it is on, or how big it is.
- The Sağlam result does not license tape-based detection by a discretionary trader: the predictability was measured with child-order data the public does not have, and the people shown to exploit it are fast algorithmic traders.
- A defensible proxy stack, in descending order of support: (1) pace versus curve (objective); (2) persistent one-sided aggressor volume over many bars (subject to the classification bias in section 5); (3) published closing-auction imbalance feeds after their release times, which are actual order information. Everything else is pattern reading.

### Gaps
- No empirical study found linking a light morning/midday volume day to a heavier or more directional close or closing auction. Treat "light midday means a catch-up close" as an untested hypothesis.
- Kissell and Johnson ("Algorithmic Trading & DMA") on tracking bands and catch-up logic could not be opened; no page-level citations. Goldman, UBS, Instinet, Virtu, Jefferies VWAP documents not found (Jefferies' IBKR-hosted volume-participation page describes volume limits and auction settings only).
- No source quantifies how wide tracking bands are or what share of parent orders finish behind schedule.

---

## 5. Signed-volume / aggressor proxies and the misclassification of passive buying

### Takeaway
Trade-signing rules identify who *took* liquidity, not who wanted to own the stock. They are right about 75% to 85% of the time on the initiator, worst inside the spread. Since a standard VWAP algo was measured at about 65% passive fills, most of a patient institutional buyer's fills print at the bid and get counted as selling in any bid/ask "delta" tool.

### Cited Findings
- Ellis, Michaely, O'Hara (JFQA 2000, Nasdaq): quote rule, tick rule and Lee-Ready correctly classify 76.4%, 77.66% and 81.05% of trades; all rules have "only a very limited success in classifying trades executed inside the quotes." — [Cambridge / JFQA](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/accuracy-of-trade-classification-rulesevidence-from-nasdaq/A2CAD2206B562784527548F5283A9ECB)
- Chakrabarty, Moulton, Shkilko: Lee-Ready misclassifies up to 32% of short sales and up to 31% of long sales at the trade level (about 21% with quotes lagged one second); misclassification is near zero at the daily aggregate level. — [Cornell copy](https://sha.cornell.edu/wp-content/uploads/sites/4/2019/04/ShortsLongsandLeeReady_JFMforthcoming.pdf)
- Short sales are often classified as buyer-initiated by Lee-Ready and similar rules. — [NBER w14158](https://www.nber.org/papers/w14158.pdf)
- Reported accuracy range across studies: 75% to 93%; newer methods cut misclassification by half on second-stamped data (Jurkatis, Bank of England working paper). — [Bank of England WP](https://www.bankofengland.co.uk/-/media/boe/files/working-paper/2020/inferring-trade-directions-in-fast-markets.pdf)
- Tick rule and Lee-Ready classify better than bulk volume classification for stocks of all sizes (Chakrabarty, Pascual, Shkilko). — [SSRN 2182819](https://papers.ssrn.com/abstract=2182819)
- VWAP algo fill mix: 65.3% passive, 21.9% midpoint, 12.57% aggressive. — [Themis Trading blog citing ITG-based study](https://blog.themistrading.com/?p=6148)
- After decimalization and Reg NMS, a small trade is much more likely to be a piece of a large institutional order, so trade size is an unreliable retail/institution marker (Hvidkjaer, as summarized). — [search summary of trade-classification literature; see NBER buy-side paper](https://conference.nber.org/conf_papers/f145256/f145256.pdf)

### Inferences
- Mechanism (follows from the definitions; the search found no paper that measures it directly): a passive buyer rests a bid. It is filled only when someone sells to that bid. The print is at the bid, the tick/quote rule signs it as a sell, and delta goes negative while the institution accumulates. With about 65% passive plus about 22% midpoint fills, only roughly one in eight of that algo's fills would show as a "buy at the ask."
- So cumulative delta measures net *urgency*, not net *accumulation*. Heavy volume at the bid with price not falling is ambiguous: it is equally the picture of a passive buyer absorbing and of sellers hitting a bid that later gives way.
- Midpoint and inside-quote prints (dark pools, wholesalers) are where every rule is weakest, and off-exchange volume was about half of all volume in 2025 (see section 6), so platform delta numbers for a full tape carry large error.

### Gaps
- No study found that quantifies how often passive institutional buys are tagged seller-initiated in public data. The claim above is logical, not measured.
- Accuracy figures are from 2000-2012-era data; no sourced accuracy number for 2023-2026 markets with sub-penny wholesaler prints.

---

## 6. Odd lots, the round-lot filter, trade sizes, and large prints

### Takeaway
A 100-share-minimum time-and-sales filter now hides about two-thirds of all US equity trades (66% odd lots, Aug 2025) and more than 80% of trades in stocks above $250, but a much smaller share of volume (the only sourced figures, from 2021, are about 6% of exchange share volume overall and under 30% in high-priced stocks). Because algos slice into small pieces, the filter removes most institutional child orders in high-priced names; it does not preferentially show institutions.

### Cited Findings
- Odd-lot share of trades (MEMX): 57% in Jan 2023 rising to 66% in Aug 2025; 60.6% in Feb 2024 and 64.4% in Feb 2025. By price: above $250, 83.4% of trades in Feb 2025 (80.7% a year earlier); sub-$1 stocks, 29.0% in Feb 2025. MEMX says odd-lot share "is not a great measure of retail activity." — [MEMX](https://memx.com/insights/equity-adv-option-contracts-and-odd-lot-trades-all-up-year-over-year); [MEMX retail insights](https://memx.com/insights/retail-trading-insights)
- 261 symbols priced over $250 were 3.6% of share volume but 33.1% of notional. — [MEMX](https://memx.com/insights/equity-adv-option-contracts-and-odd-lot-trades-all-up-year-over-year)
- Odd-lot share of volume (older data): Cboe, Oct 2021: odd lots 54.8% of trades (43% at start of 2020), about 6.3% of executed share volume on Cboe's four exchanges in Sept 2021, about 10.7% of share volume in the most liquid stocks; odd-lot volume share rises with price. Nasdaq, 2021: under 30% of shares in high-priced stocks. — [Cboe](https://www.cboe.com/insights/posts/an-in-depth-view-into-odd-lots); [Nasdaq](https://www.nasdaq.com/articles/odd-facts-about-odd-lots-2021-04-22)
- Historical baseline: SEC data highlight shows typical odd-lot rates of 18% to 24% of trades for stocks around 2013; SEC publishes odd-lot rate and odd-lot volume series (download covers 2012 Q1 to 2025 Q3). — [SEC odd-lot rates](https://www.sec.gov/about/odd-lot-rates); [SEC post-transparency highlight](https://www.sec.gov/about/odd-lot-rates-post-transparency-world); [SEC MIDAS odd-lot volume](https://www.sec.gov/marketstructure/datavis/ma_exchange_oddlotvolume.html)
- O'Hara, Yao, Ye (J. Finance 2014, 69(5) 2199-2236), 120 Nasdaq stocks 2008-2011, when odd lots were off the tape: median 24% of trades missing, some stocks over 60%; Amazon odd lots rose from about 22% to 46% of trades and Apple 17% to 38%; Google about 53% in 2011; odd lots were about 4% to 4.9% of share volume; attributed to algorithms that slice orders, and the odd-lot trades were highly informative. Figures are from press and presentation summaries. — [EconPapers](https://econpapers.repec.org/RePEc:bla:jfinan:v:69:y:2014:i:5:p:2199-2236); [Warwick release](https://www.wbs.ac.uk/news/millions-of-hidden-share-trades-to-be-revealed/); [NBER working version](https://conference.nber.org/confer/2011/MMf11/Ye_O'Hara_Yao.pdf)
- Round-lot redefinition is live: the exclusive SIPs implemented it in November 2025 (industry notices: Nov 3, 2025). Tiers by average closing price: up to $250 = 100 shares; $250.01 to $1,000 = 40; $1,000.01 to $10,000 = 10; above $10,000 = 1. About 4,700 stocks keep 100; around 15 stocks got 10-share lots (MELI, AZO, BKNG named). — [SEC exemptive order 34-104612](https://sec.gov/files/rules/exorders/2026/34-104612.pdf); [Nasdaq](https://www.nasdaq.com/articles/new-round-lot-rules-help-issuers-high-priced-stocks); [IBKR FAQ](https://www.interactivebrokers.com/support/faq/content/1264790077)
- Effects: Nasdaq projected the change would cut odd-lot volume share by about 33% (projection). Netflix odd-lot trades fell from about 94% in October to about 66% after the round-lot change and to about 35% after its split (MEMX). In the $1,000 to $10,000 group, average inside size fell from about 99 to about 32 shares (Cboe). — [Nasdaq](https://www.nasdaq.com/articles/new-round-lot-rules-help-issuers-high-priced-stocks); [MEMX](https://memx.com/insights/retail-trading-insights); [Cboe](https://www.cboe.com/insights/posts/the-impact-round-lot-reform-had-on-u-s-equities-market-quality)
- Odd-lot quotes on the SIP: original compliance date first business day of May 2026; industry notices say the CTA and UTP SIPs activated odd-lot quote dissemination on April 27, 2026, top-of-book odd lots at or better than the NBBO only; additional odd-lot depth deferred to May 2028. Odd-lot quotes are not protected quotations. — [Cboe notice](https://www.cboe.com/notices/content/?id=59495); [dxFeed](https://dxfeed.com/odd-lot-quote-data-cta-utp-sip-changes/); [Federal Register Nov 17, 2025](https://www.govinfo.gov/content/pkg/FR-2025-11-17/html/2025-19926.htm); [IBKR odd-lot NBBO FAQ](https://www.interactivebrokers.com/support/faq/content/1436617069)
- Trade size: a Cboe monthly briefing cites an average trade size of 210 shares (year not confirmed). A third-party site citing Cboe files says 2025 off-exchange was 50.61% of consolidated share volume at an average print of 200.5 shares, and that the all-market average print fell from 155.21 to 127.04 shares between August 2025 and August 2026 (unverified third party). NYSE's Q1 2026 fractionals factsheet gives a median TRF-reported trade size of 20 shares. — [Cboe briefing](https://www.cboe.com/insights/posts/market-metrics-that-matter-u-s-cash-equities-november-volume-briefing); [Axis Intelligence](https://axis-intelligence.com/retail-trading-statistics/); [NYSE factsheet](https://www.nyse.com/publicdocs/nyse/Q1_2026_Fractionals_Factsheet.pdf)
- Odd-lot quotes are less reliable liquidity in stress (OFR working paper 25-02, 2025). — [OFR](https://www.financialresearch.gov/working-papers/files/OFRwp-25-02_there-when-you-dont-need-it-the-reliability-of-odd-lot-liquidity.pdf)
- TRF modifiers: `.W` marks weighted-average / special-pricing-formula trades whose price "may bear no relation to the current market"; FINRA's modifier table lists which modifiers do not update last sale (for example error correction, print protection, qualified contingent trades, average-price trades). — [FINRA trade reporting notice 8/19/10](https://www.finra.org/rules-guidance/notices/trade-reporting-notice-081910); [FINRA modifier/LULD table](https://www.finra.org/filing-reporting/trf/trade-report-modifiers-and-applicability-limit-uplimit-down-luld-price-bands); [FINRA trade reporting FAQ](https://www.finra.org/filing-reporting/market-transparency-reporting/trade-reporting-faq)

### Inferences
- What the 100-share filter hides (trade count is sourced; volume is my estimate from dated figures):
  - Sub-$1 to low-priced stocks: roughly 30% of prints hidden, very little volume. The filtered tape is close to the real tape.
  - Typical $20 to $250 stocks: on the order of half to two-thirds of prints hidden; volume hidden probably single digits to low teens percent (extrapolated from the 2021 6% to 11% figures with odd-lot trade share having risen since; no current source).
  - Above $250: more than 80% of prints hidden; volume hidden was "under 30%" in 2021 and is plausibly higher now. In $250 to $1,000 names a 100-share filter also hides 40-share round lots, and in $1,000-plus names 10-share round lots, which now set the NBBO.
- Bias direction: toward block and retail-wholesaler prints of 100-plus shares and away from algorithmic child orders in mid- and high-priced names. Child orders tend to be sized to displayed quote size; with inside size about 32 shares in $1,000-plus names, 100-share fills there are uncommon. In sub-$20 names child orders of several hundred shares are normal and the filter costs little.
- A 100-share print is not evidence of an institution; a 7-share print is not evidence of retail (MEMX and the academic work both say so).
- Large-print filters (10,000-plus shares): on the TRF these are a mix of wholesaler-internalized retail orders, dark-pool blocks, and trades reported with modifiers (average-price, prior-reference-price, late, derivatively priced). Prints carrying such modifiers do not reflect a trade at that moment's market and should be excluded from tape reading and from VWAP-style calculations. The modifier facts are sourced above; the "what large TRF prints usually are" breakdown is general market knowledge without a number or source here.

### Gaps
- No 2024-2026 figure for odd-lot share of *volume* overall or by price tier (the SEC MIDAS series exists but could not be pulled).
- No source for the share of institutional child orders that are odd lots or exactly 100 shares, or for typical child order size.
- Johnson, Van Ness, Van Ness on odd lots not located.
- The date odd lots first printed on the consolidated tape (December 2013, as I recall) is implied by the SEC "post-transparency" data highlight but not confirmed from text.
- Dollar trade size by price tier not found.
- Post-reform (after Nov 2025) odd-lot trade share for the whole market not found.

---

## 7. "Held bid" mechanics: reserve / refreshing orders on the tape

### Takeaway
Exchange rules confirm that a reserve order shows a small displayed size that is replenished from a hidden remainder after it trades. On time and sales that produces repeated prints at one price while the displayed size keeps coming back. The tape alone cannot prove a reserve order, its size, or its owner.

### Cited Findings
- Nasdaq Equity 4, Rule 4703(h): when the displayed portion falls below a normal unit of trading, "a new displayed order will be entered and receive a new timestamp, while the size of the non-displayed order will be reduced by the same amount and will not receive a new timestamp." The refreshed slice goes to the back of the displayed queue at that price; the hidden remainder keeps its own priority. — [Federal Register, Feb 18, 2021](https://www.govinfo.gov/content/pkg/FR-2021-02-18/pdf/2021-03214.pdf); [SEC release 34-90793](https://www.sec.gov/rules/sro/nasdaq/2020/34-90793.pdf)
- SR-NASDAQ-2020-090: a replenished displayed order that would lock a resting order posts at the locking price instead of executing, so replenishment does not remove liquidity. — [Nasdaq filing](https://listingcenter.nasdaqomx.com/assets/rulebook/nasdaq/filings/SR-NASDAQ-2020-090.pdf)
- NYSE-family rules: "each time a Reserve Order is replenished from reserve interest, a new working time is assigned to the displayed portion." — [Federal Register, NYSE American filing](https://www.federalregister.gov/documents/2020/03/18/2020-05553/self-regulatory-organizations-nyse-american-llc-notice-of-filing-of-proposed-rule-change-amending)
- Nasdaq order type guide lists reserve and non-displayed orders. — [Nasdaq order types guide](https://m.nasdaqtrader.com/content/ProductsServices/Trading/OrderTypesG.pdf)

### Inferences
- What it looks like: many prints at the bid price, cumulative volume traded at that price well beyond the size ever displayed there, and the displayed bid size snapping back to a similar number after each fill, on one venue.
- Why it is not proof:
  - The same picture is produced by fully non-displayed orders, by several participants each re-posting, by a market maker requoting, or by an algo sending a new child order after each fill. A new-order refresh and a reserve replenishment are not distinguishable on a consolidated feed.
  - Retail and prop platforms show aggregated size by price, usually top of book per venue, and time and sales does not say which resting order was hit. Trades at the bid price on other venues or off-exchange are mixed into the same tape.
  - Refreshed size takes a new timestamp, so in a deep queue the refresh is not visible as a distinct event.
  - A "held bid" does not reveal remaining size. It can vanish on the next print.
  - Per section 5, the prints at a held bid are sell-initiated by definition; delta will read negative while the bid absorbs.
- With a 100-share filter on, absorption in mid- and high-priced stocks is undercounted because much of the selling into the bid arrives as odd lots.

### Gaps
- No academic or vendor source found on iceberg detection accuracy from public data, and nothing on how often displayed-size refresh corresponds to a true reserve order.
- No source located for how specific prop platforms display venue-level size or reserve refresh events.
