# Observable footprint of VWAP/TWAP/POV execution programs on the tape, book and chart (US equities)

Research-session caveats (read first):
- Evidence labels used throughout: **STRONG** = replicated peer-reviewed/large-sample empirical result; **MODERATE** = single study, exchange/regulator documentation, or a result that is real but measured with proprietary data a tape reader does not have; **ANECDOTAL** = credible practitioner claim with no published test; **FOLKLORE** = retail claim with no test found.
- Three hosts were unreachable from this session (network allowlist): `www.smbtraining.com`, `pages.stern.nyu.edu`, `www.johnhcochrane.com`. SMB and Hasbrouck-Saar material below is therefore from search-result excerpts of those pages, not full-text reads. Anything I could not source in-session is in a Gaps list, not in Cited Findings.
- The central structural point for the end reader: almost every *strong* result below was established with data that identifies the parent order (broker/buy-side/TCA databases such as ANcerno, AllianceBernstein, exchange member IDs). The results prove that metaorders exist and leave statistical traces; they do **not** prove that a human watching a public tape can identify one in real time.

---

## 1. Documented statistical signatures of sliced parent orders

### Takeaway
Order splitting is the best-documented fact in the field: trade signs are long-memory, and at horizons under a few hours that persistence comes overwhelmingly from single investors splitting orders, not from herding. Clock-time periodicity, odd-lot slicing and half-hour return/volume periodicity are also documented, but each is an aggregate statistical property, not a per-stock real-time detector.

### Cited Findings

**Order-sign long memory (evidence: STRONG)**
- Lillo, Mike & Farmer (2005) attribute long memory in order flow to delayed market clearing: large hidden orders are sliced into small revealed pieces, and the sign of executed orders follows a long-memory process. — [arXiv cond-mat/0412708](https://arxiv.org/abs/cond-mat/0412708); [Phys. Rev. E 71, 066122](https://www.doi.org/10.1103/PHYSREVE.71.066122)
- The LMF model links the sign-autocorrelation exponent to the tail of the hidden-order size distribution (γ = β − 1 as reported in a companion paper). — [Mike & Farmer, arXiv physics/0509194](https://arxiv.org/pdf/physics/0509194)
- Tóth, Palit, Lillo & Farmer (J. Econ. Dynamics & Control 2015): order signs are positively autocorrelated "out to time lags of tens of thousands of orders, corresponding to many days." — [arXiv 1108.1632](https://arxiv.org/abs/1108.1632v1); [JEDC 51:218-239](https://econpapers.repec.org/RePEc:eee:dyncon:v:51:y:2015:i:c:p:218-239)
- Same paper, using London Stock Exchange data with member identifiers: "On timescales of less than a few hours the persistence of order flow is overwhelmingly due to splitting rather than herding." At longer horizons different investors' behaviour is anti-correlated. — [arXiv 1108.1632](https://arxiv.org/abs/1108.1632v1)
- Caveat in that paper: exchange members mostly act as brokers, so broker-level patterns are not the same as single-investor patterns; the authors had to model brokerage choice to correct for this. — [arXiv 1108.1632](https://arxiv.org/abs/1108.1632v1)
- Sato & Kanazawa (2023) state that the order-splitting hypothesis had not been tested directly at the individual-trader level until their study, which estimates metaorder-length distributions by classifying traders as splitters or random traders (a quantitative test of the LMF model). — [arXiv 2301.13505](https://arxiv.org/abs/2301.13505v2)
- A 2021 review reports similar splitting-dominates results when data are labelled by agents rather than brokers. — [Order flow and price formation, arXiv 2105.00521](https://arxiv.org/pdf/2105.00521)

**Clock-time periodicity (evidence: MODERATE for existence; weak as a per-stock detector)**
- Hasbrouck & Saar, "Low-Latency Trading" (J. Financial Markets 2013), NASDAQ order-level data time-stamped to the millisecond: they contrast algorithms that react to market events within about 2-3 ms with others that "seem to cycle in wall-clock time (e.g. access the market every second)", and attribute wall-clock periodicities in market activity to the latter group rather than to the millisecond strategies. — [SSRN 1695460](https://papers.ssrn.com/abstract=1695460); [JFM 16(4):646-679](https://econpapers.repec.org/RePEc:eee:finmar:v:16:y:2013:i:4:p:646-679)
- "Order anticipation around predictable trades" (SSRN 2828363): dataset of more than 20,000 parent orders / more than 2.5 million child executions, all executed to match the VWAP realised over the parent's lifetime. Builds three simple predictability signals from child-order statistics (the first is the volatility of child-order trade sizes) and finds stronger signals are correlated with higher execution costs. States that predictable patterns from these algorithms "can be even discerned by human traders". — [vLex listing](https://law-journals-books.vlex.com/vid/order-anticipation-around-predictable-855675772); [Scribd copy of SSRN-id2828363](https://www.scribd.com/document/462910636/SSRN-id2828363-pdf)
- Same paper shows a Coca-Cola price chart for 19 July 2012 with a "sawtooth trading pattern that is potentially caused by schedule-based algorithms", highs near the half-hour mark and lows at the start of each hour. (This is the well-known 19 July 2012 KO/IBM/MCD/C episode; note the paper's own hedge: "potentially caused".) — [Scribd copy of SSRN-id2828363](https://www.scribd.com/document/462910636/SSRN-id2828363-pdf)
- Chen, Tran & Horst (2023 discussion paper, 110 NASDAQ stocks): liquidation strategies "exhibit invariant patterns in execution behavior, such as TWAP/VWAP leaving a constant stream of 'blips' in trading volume". — [LMU Munich discussion paper 368](https://epub.ub.uni-muenchen.de/94308/1/368%20%281%29.pdf)
- Crypto analogue: Hansen, Kim & Kimbrough (2021), Bitcoin/Ether on Binance, Coinbase Pro, Uniswap V2: "strong evidence of periodicity in volatility and liquidity for day-of-the-week, hour-of-the-day, as well as within the hour"; they attribute many patterns to algorithmic trading and report the patterns have strengthened over time. — [arXiv 2109.12142](https://arxiv.org/pdf/2109.12142)

**Odd-lot slicing (evidence: STRONG that it exists; it is now the norm, so it no longer discriminates)**
- O'Hara, Yao & Ye, "What's Not There: Odd Lots and Market Data" (J. Finance 2014): the median share of odd-lot trades in their sample is 24% of trades, and 60%+ in some stocks; odd lots account for about 35% of price discovery, read as consistent with informed traders slicing into odd lots to avoid detection. — [J. Finance 69(5):2199-2236](https://ideas.repec.org/a/bla/jfinan/v69y2014i5p2199-2236.html)
- 2011 working-paper version: odd lots contributed 30% of price discovery and 100-share trades another 50%. — [NBER conference draft](https://conference.nber.org/confer/2011/MMf11/Ye_O'Hara_Yao.pdf)
- Sample was 120 Nasdaq stocks 2008-2011; Amazon's odd-lot trades rose from roughly 22% to 46% of trades and Apple's from 17% to 38%; at the time odd lots were not on the consolidated tape. — [Warwick Business School summary](https://www.wbs.ac.uk/news/millions-of-hidden-share-trades-to-be-revealed/)
- Current base rate: odd-lot trades were 64.4% of trades in February 2025, up from 60.6% in February 2024, and the share is higher in higher-priced stocks. — [MEMX](https://memx.com/insights/equity-adv-option-contracts-and-odd-lot-trades-all-up-year-over-year)
- OFR working paper 25-02: small exchange orders inside the spread (odd lots) disappear for less than a millisecond around an off-exchange trade. — [OFR, "The Reliability of Odd-Lot Liquidity"](https://www.financialresearch.gov/working-papers/2025/06/05/the-reliability-of-odd-lot-liquidity/)

**Half-hour periodicity in returns and volume (evidence: STRONG, cross-sectional)**
- Heston, Korajczyk & Sadka (J. Finance 2010): splitting the day into 13 half-hour intervals, there is "significant continuation of returns at half-hour intervals that are exact multiples of a trading day, and this effect lasts for forty trading days". — [J. Finance 65(4):1369-1407](https://econpapers.repec.org/RePEc:bla:jfinan:v:65:y:2010:i:4:p:1369-1407)
- "Volume, order imbalance, volatility, and bid-ask spreads exhibit similar patterns, but do not explain the return patterns." Not driven by firm size, systematic risk premia or S&P 500 membership. — [J. Finance 65(4):1369-1407](https://econpapers.repec.org/RePEc:bla:jfinan:v:65:y:2010:i:4:p:1369-1407)
- Short-term reversal is driven by temporary liquidity imbalances lasting less than an hour and bid-ask bounce. — [Kellogg research summary](https://www.kellogg.northwestern.edu/academics-research/research/detail/2010/intraday-patterns-in-the-cross-section-of-stock-returns)

### Inferences
- The strong result is "persistent one-sided aggressor flow over minutes-to-hours is mostly one participant (or one participant type) splitting." For a tape reader that supports the practitioner heuristic "sustained same-side prints = someone working an order", but only as a base-rate statement; the papers measure autocorrelation over thousands of trades, not a rule a human can apply to 50 prints.
- Odd-lot prints cannot be used as an institutional tell in 2026: with roughly 60%+ of all trades being odd lots, "lots of small odd-lot prints" describes nearly every liquid high-priced stock all day.
- Heston et al. implies the same stocks tend to be bought (or sold) at the same half-hour on successive days, which is what multi-day institutional programs with similar daily schedules would produce. The paper documents the pattern; the link to specific execution schedules is an interpretation, and the effect is small per stock (it is a cross-sectional portfolio result).
- The "Order anticipation" paper is the closest thing found to direct evidence that schedule-based VWAP child orders are detectable, including by humans. But it measures predictability using the broker's own child-order records, and the cost of being predictable, not a public-tape detector's hit rate.

### Gaps
- Exact Hasbrouck-Saar numbers (which millisecond offsets after the second show the activity peak, 2007/2008 sample months) could not be read: the full text host was blocked. I recall the paper showing a spike in message activity just after the whole-second boundary with a 1-second clock cycle, but I could not verify this in-session; treat as unverified.
- Could not locate in-session the specific literature on trades clustering at whole-minute marks in equities/futures (the brief mentions it; a Broussard & Nikiforov "Intraday periodicity in algorithmic trading" search returned nothing). No verified source for a whole-minute TWAP signature in US equities was found.
- "Repeated same-size prints" as a signature: no academic source found that tests it on public data. The only related evidence is the Order-anticipation paper's signal based on low volatility of child-order sizes (broker data). On a public tape, 100-share and small odd-lot prints are the modal size anyway.
- No study was found reporting precision/recall of any metaorder detector built on public TAQ-style data alone.

---

## 2. Passive vs aggressive programs on the tape and Level 2: held bids, refreshing/iceberg, absorption, steady lifting

### Takeaway
Reserve/iceberg replenishment is a real, exchange-documented mechanism that produces a "bid that keeps reloading", but exchanges also offer randomised display sizes and the replenished slice loses time priority, so the footprint is deliberately noisy. The "clean held bid" is a credible SMB desk pattern, explicitly described by Bellafiore as rare in the HFT era; nobody has published a hit rate for it.

### Cited Findings

**Exchange mechanics (evidence: STRONG, documentation)**
- Nasdaq reserve (iceberg) orders have a displayed and a non-displayed part; the total quantity is available for matching. — [Nasdaq Reserve Order factsheet](https://www.nasdaq.com/docs/2020/01/20/Factsheet_Reserve_Order_Iceberg_GTMS.pdf)
- On replenishment "a new timestamp is created for the replenished portion of the order each time it is replenished from reserve, while the reserve portion retains the time-stamp of its original entry." — [SEC release 34-91109](https://www.sec.gov/file/34-91109)
- Nasdaq RASH "random reserve": the displayed amount changes every time the displayed shares are depleted; spec example is a 5,000-share order with 300 max floor and 200 random reserve displaying between 100 and 500 shares at random on each refresh. — [Nasdaq RASH specification](https://m.nasdaqtrader.com/content/technicalsupport/specifications/Tradingproducts/rash_sb_ETMF.pdf)
- IEX's 2021 filing allowed odd-lot display sizes and an optional random replenishment display quantity. — [Federal Register 2021-20453](https://govinfo.gov/content/pkg/FR-2021-09-22/pdf/2021-20453.pdf)
- Each exchange displays iceberg replenishment differently, so no single mechanism finds hidden liquidity on every venue. — [Exegy, "Hiding (and Seeking) Liquidity With Iceberg Orders"](https://www.exegy.com/hiding-and-seeking-with-iceberg-orders)
- Bookmap's iceberg tracker looks for new limit orders appearing right after executions at a price level; its documentation states the older detection approach "isn't reliable anymore" because the sequence of events in market data changed. — [Bookmap knowledge base, Iceberg Orders Tracker](https://bookmap.com/knowledgebase/fr/docs/KB-Bookmap-Wiki-Iceberg-Orders-Tracker)

**SMB Capital / Bellafiore (evidence: ANECDOTAL, credible desk source, no published statistics)**
- "A Held Bid in a stock above an important technical resistance level, or above an important support level gets our attention." Bellafiore says held bids are rare in the current HFT-dominated market and that "these clean held bids matter most in this market." — [SMB blog, "The Clean Held Bids Matter Most"](https://www.smbtraining.com/blog/the-clean-held-bids-matter-most)
- SMB claim that "one pattern we see repeat is the clean held bid foreshadowing a big move", on the argument that prices rarely repeat in an algorithmic market. — [SMB blog post 16808](https://www.smbtraining.com/blog/?p=16808)
- SMB "Clean Up Print" post: after heavy buying, "a big volume spurt and a bid that suddenly seemed weaker" was treated as the buyer finishing and a short entry ("the modern day Clean Up Print"); another SMB example describes "a nsdq buyer at 74.70 that never dropped." — [SMB blog, "Clean Up Print"](https://www.smbtraining.com/blog/clean-up-print)

**How other participants react to a working order (evidence: MODERATE, European data)**
- Van Kervel & Menkveld (J. Finance 2019), proprietary institutional child-order data on European exchanges with labels for ten large HFT firms: HFTs initially lean against large institutional orders (i.e. provide liquidity to them) but eventually turn and trade in the order's direction for the most informed orders; institutional trading cost differs materially between the lean-against and with-the-wind cases. — [J. Finance 74(3):1091-1137](https://econpapers.repec.org/RePEc:bla:jfinan:v:74:y:2019:i:3:p:1091-1137); [Tinbergen DP 17-092](https://papers.tinbergen.nl/17092.pdf)

### Inferences
- Three different things produce a "bid that won't drop": (1) a single reserve order replenishing, (2) an algo re-posting child orders at the same price, (3) many unrelated participants joining a visible level. Exchange documentation proves (1) exists; nothing public lets a tape reader separate the three with certainty. Prints exceeding displayed size at an unchanged bid is the logical evidence of (1) or (2), consistent with how Bookmap-type detectors work.
- Because replenished slices get a new timestamp (back of queue) and random reserve varies the shown size, a competently configured reserve order will not show a constant "500 x 500 x 500" reload; a perfectly regular reload suggests an unsophisticated or deliberately visible order.
- Van Kervel-Menkveld implies the "absorption without price moving" phase (others leaning against the flow) and the later "price starts going with the buyer" phase are both expected stages of a long-lived informed metaorder. That matches the practitioner narrative, but the study is European and uses identified data.
- SMB's own framing ("rare", "clean") is an implicit admission that most apparent held bids in 2026 are not tradeable signals; the exit rule embedded in their examples is the bid dropping / a volume spurt followed by a weaker bid.

### Gaps
- Jigsaw Trading / Peter Davies, John Carter, Linda Raschke and Bookmap blog material on icebergs/absorption/"big buyer": searches returned no primary pages, and SMB's site could not be fetched. No verified quotes from those sources are included. Bellafiore's books ("One Good Trade", "The Playbook") could not be quoted directly.
- No published test (hit rate, expectancy) of the held-bid, "refresh" or absorption patterns was found from any source. All of it is desk experience.
- "Steady lifting of offers at regular intervals" and "tight channel with shallow pullbacks": no source found that verifies these as signatures of a buy program versus any other persistent demand. Status: practitioner description consistent with the order-splitting literature, untested as a detector.
- No data found on what fraction of institutional algo volume is posted passively versus taking, by algo type, in 2026.

---

## 3. Price behaviour relative to VWAP; impact shape during a metaorder and reversion after it ends

### Takeaway
Impact during a metaorder is concave (square-root-like, possibly logarithmic) and partially reverts when the order ends: roughly one third of peak impact is given back by the same day's close, with further decay over weeks. This is strongly documented with identified institutional data. The claim that a buy program "makes VWAP act as support" is arithmetic plus practitioner belief; no empirical study testing VWAP as a support level was found.

### Cited Findings

**Impact shape (evidence: STRONG)**
- Almgren, Thum, Hauptmann & Li (2005, Citigroup; Risk, July 2005 pp. 57-62): model splits cost into a permanent component associated with information and a temporary component; summarised result is a 3/5 power law of block size with dependence on duration, daily volume, volatility and shares outstanding. — [Direct Estimation of Equity Market Impact (UPenn-hosted PDF)](https://www.cis.upenn.edu/~mkearns/finread/costestim.pdf); [Risk.net](https://www.risk.net/derivatives/structured-products/1500270/equity-market-impact)
- Zarinelli, Treccani, Farmer & Lillo, "Beyond the square root": several million US-equity metaorders (large, mid and small caps); a logarithmic form fits impact better than a square root across about five orders of magnitude; they introduce an "impact surface" in duration and participation rate. — [arXiv 1412.2152](https://arxiv.org/pdf/1412.2152)
- Bucci et al., "Co-impact" (ANcerno data): square-root impact for large volume fractions, near-linear for smaller ones; crowding of same-direction metaorders matters. — [arXiv 1804.09565](https://arxiv.org/pdf/1804.09565)
- Bucci, Benzaquen, Lillo & Bouchaud, "Crossover from linear to square-root market impact". — [arXiv 1811.05230](https://arxiv.org/pdf/1811.05230)
- Moro et al. (2009) "Market impact and trading profile of large trading orders in stock markets" is the early hidden-order study in this line. — [arXiv 0908.0202](https://arxiv.org/pdf/0908.0202)

**Reversion after the metaorder ends (evidence: STRONG)**
- Bucci, Benzaquen, Lillo & Bouchaud (2019), more than 8 million ANcerno metaorders in US equities: "relaxation takes place as soon as the metaorder ends"; at the end of the same day impact is on average about 2/3 of peak; decay continues over following days to an asymptote at about 50 days equal to about 1/2 of end-of-day-one impact, i.e. about 1/3 of peak. — [arXiv 1901.05332](https://arxiv.org/pdf/1901.05332)
- Same paper: metaorder signs are significantly autocorrelated over multiple days, so observed impact must be deconvolved to isolate the decay of a single metaorder. — [arXiv 1901.05332](https://arxiv.org/pdf/1901.05332)
- Bershova & Rakhlin (Quantitative Finance 2013), large buy-side orders in US equities (about 300,000 AllianceBernstein metaorders per a later table): impact grows roughly as the square root of duration; post-trade reversion is also roughly square-root in time; permanent impact is about 2/3 of the impact at the last fill; results support the Farmer et al. hidden-order arbitrage theory. — [Quantitative Finance 13(11):1759-1778](https://ideas.repec.org/a/taf/quantf/v13y2013i11p1759-1778.html)
- Brokmann, Sérié, Kockelkoren & Bouchaud (2014, CFM proprietary data), a different paper with a near-identical title: after removing the informational content of trades, impact decays slowly, possibly as a power law, to zero or a small value. — [arXiv 1407.3390](https://arxiv.org/pdf/1407.3390)

**VWAP as benchmark (evidence: MODERATE that it is a benchmark; ANECDOTAL that it acts as support)**
- VWAP has been used since 1988 as a measure of institutional execution quality; Shannon calls it the daily benchmark for institutional buy and sell orders. — [Yahoo Finance interview with Brian Shannon](https://sg.finance.yahoo.com/video/breaking-down-anchored-vwap-alphatrends-155349084.html); [AlphaTrends, "Anchoring the VWAP for better timing"](https://alphatrends.net/?p=623098)
- Shannon: institutions often use anchored-VWAP levels as performance benchmarks; as price returns to an anchored VWAP, longs may look to break even while short sellers may offer there. — [Yahoo Finance clip](https://uk.finance.yahoo.com/video/chart-anchored-vwap-multiple-time-140029041.html)

### Inferences
- Why a persistent buy program keeps price above VWAP (arithmetic, not a cited finding): with concave rising impact, each later print is above most earlier prints, so last price sits above the cumulative average. Price above a rising VWAP is therefore a *consequence* of persistent net buying. It does not show VWAP is a level where buyers defend; any monotone drift produces the same picture.
- The reversion results give the most actionable, well-evidenced expectation: when a large order finishes, expect a partial give-back (order of one third of the move attributable to it by the close, on average), not a full round trip. The averages are over millions of orders; single-order dispersion is large and Bucci et al. warn that same-sign orders tend to follow on subsequent days.
- Concavity means the first part of a program moves price most per share; a long program therefore looks like an initial push followed by a slower grind, which matches the "grinding channel" description, but so does any decaying-urgency flow.
- A VWAP-benchmarked buy algo that is passive when price is at/below VWAP and less aggressive above it would mechanically add demand on dips toward VWAP. This is a plausible mechanism for "VWAP holds as support" but is my inference; no source found measures it.

### Gaps
- No empirical study found testing (a) bounce probability at session VWAP, (b) whether holding above VWAP all day predicts continuation in single stocks, or (c) how price behaves as a schedule-based algo falls behind/ahead of schedule. The behind-schedule "catch-up" aggression is described in broker algo marketing but I found no public measurement.
- Shannon's book "Maximum Trading Gains with Anchored VWAP" could not be quoted directly. A Yahoo topic page attributes a "100% accuracy" claim to a VWAP-vs-open rule; I could not verify it and regard it as unreliable.
- Third-party AVWAP guides quoting win rates were found but are unverified and were excluded.
- Could not verify in-session which dataset Zarinelli et al. used (search summary was inconclusive on ANcerno).

---

## 4. Index-level program trading: TICK, ADD, baskets

### Takeaway
"Program trading" has a precise historical NYSE meaning (15+ stocks, $1M+) and was a large share of NYSE volume; TICK extremes are a mechanical consequence of many stocks printing on the same side at once. What TICK "reliably says" beyond that is practitioner convention; no academic validation of TICK thresholds was found.

### Cited Findings
- NYSE definition: program trading covers a range of portfolio strategies involving the purchase or sale of a basket of at least 15 stocks with a total value of $1 million or more. — [The Practical Guide (O'Reilly excerpt quoting NYSE)](https://www.oreilly.com/library/view/the-practical-guide/9780470455104/tagl_9780470455104_oeb_c05_r1.html); [Wikipedia, Program trading](https://Www.Wikipedia.org/wiki/Program_trading)
- NYSE's crossing session accepted baskets of at least 15 securities and counted these as program trades. — [Archived NYSE trading-info page](https://webarchive.library.unt.edu/web/20170117005756/https://www.nyse.com/markets/nyse/trading-info)
- NYSE weekly releases show the scale under that definition: e.g. program trading averaged 19.2% of NYSE volume in one late-April week and 54.8% in one September week (years vary by release; see archive). — [Mondo Visione, 19.2%](https://mondovisione.com/media-and-resources/news/program-trading-averaged-192-percent-of-nyse-volume-during-april-2428); [Mondo Visione, 54.8%](https://mondovisione.com/media-and-resources/news/program-trading-averaged-548-percent-of-nyse-volume-during-sep-710)
- TICK is the count of NYSE stocks whose last trade was an uptick minus those whose last trade was a downtick; readings beyond about ±1000 are conventionally treated as extremes; basket executions hit many symbols within seconds and flip their last trades to the same side, pushing TICK to extremes (vendor explanation, evidence: ANECDOTAL/mechanical). — [LuxAlgo TICK index reference](https://www.luxalgo.com/library/concept/tick-index/)
- Gamma hedging tied to index products drives *market-level* intraday momentum, and stock-level end-of-day effects are distinct from it (Baltussen et al. follow-up). — [Baltussen, Da et al., EOD working paper](https://www3.nd.edu/~zda/EOD.pdf)

### Inferences
- A TICK spike is direct evidence only that many NYSE names last-printed on the same side within a short window. A basket/index-arb/ETF create-redeem program is the natural cause, but so is any macro headline. TICK contains no size information and counts a 1-share uptick the same as a block.
- Index programs propagate to individual large caps mechanically (the basket includes them), so a large cap can show "buy program" tape that reflects index flow and nothing stock-specific. For a single-stock tape reader this is a confound: check whether the peer group/ES/SPY printed the same burst at the same second.
- The NYSE 15-stock/$1M definition dates from a floor-centric market; in 2026 nearly all institutional flow is algorithmic and basket-like, so the historical statistic is not a current measure of anything observable.

### Gaps
- No academic or exchange study was found validating TICK ±1000 thresholds, "TICK above zero all day", ADD, or cumulative TICK as predictors. These remain practitioner conventions (ANECDOTAL). One forum description of cumulative TICK on trend-down days was found and is a single trader's account.
- Whether NYSE still publishes program-trading statistics, and the exact years of the cited weekly releases, were not verified.
- No sourced quantification found of how quickly/strongly index basket flow shows up in individual large-cap tapes.

---

## 5. Trend days: frequency, characteristics, link to persistent flow, gamma, leveraged ETFs

### Takeaway
The market-level mechanism for late-day continuation is well documented (rest-of-day return predicts last-half-hour return; stronger when dealers are short gamma; leveraged-ETF rebalancing contributes). A rigorous US frequency statistic for "trend days" was not found; available numbers are informal and definition-dependent (roughly one day in ten).

### Cited Findings
- Gao, Han, Li & Zhou (JFE 2018), SPY 1993-2013: the first half-hour return predicts the last half-hour return; predictive R² 1.6% (out-of-sample 1.2%); predictability rises with volatility and volume. (evidence: STRONG, but small R²) — [JFE 129(2):394-414](https://econpapers.repec.org/RePEc:eee:jfinec:v:129:y:2018:i:2:p:394-414); [Alpha Architect summary](https://alphaarchitect.com/2014/08/attention-prop-traders-the-first-half-hour-of-trading-predicts-the-last-half-hour/)
- Baltussen, Da, Lammers & Martens (JFE 2021), 60+ futures 1974-2020: the last-30-minute return is positively predicted by the return over the rest of the day; the effect reverts over the following days; linked to gamma hedging by option dealers and leveraged-ETF rebalancing. (evidence: STRONG) — [JFE 142(1):377-403](https://econpapers.repec.org/RePEc:eee:jfinec:v:142:y:2021:i:1:p:377-403); [working paper](https://www3.nd.edu/~zda/intramom.pdf)
- Intraday momentum is much more pronounced on negative net-gamma-exposure days; on positive-gamma days there is no significant intraday momentum. — [Alpha Architect summary of Baltussen et al.](https://alphaarchitect.com/hot-topic-does-gamma-hedging-actually-affect-stock-prices/)
- Informal frequency data: on India's Nifty (data from 1998), using a rule of open within 20% of one end of the range and close within 20% of the other, trend days occurred about once in 11 days. (evidence: ANECDOTAL, non-US) — [Capitalmind](https://capitalmind.in/2011/06/trend-days-on-the-nifty/)
- A Linnsoft study of 1,900 sessions (instrument not confirmed) found 372 days with the low in the first 60 minutes and high in the last 60 minutes, and 257 days with the reverse, i.e. about 33% of days by that loose definition. (evidence: ANECDOTAL) — [Linnsoft opening statistics](https://www.linnsoft.com/videos/homework-opening-statistics-0)
- Common practitioner definitions use open within 15-20% of one range extreme and close within 15-20% of the other, sometimes with a range-expansion condition. — [TradingView Trend Day Identification script](https://th.tradingview.com/script/3tRKY7B0-Trend-Day-Indentification); [gitbook day-type notes](https://cre8r-1.gitbook.io/the-art-of-surviving-the-trading-jungle/terrain-mapping-market-analysis/technical-analysis/types-of-market-days/trend-day)

### Inferences
- The two frequency numbers (about 9% versus about 33%) differ only because of definition; "trend day frequency" is not a stable empirical quantity. Any figure quoted without the definition is meaningless.
- The documented driver of *index* late-day continuation is hedging flow (gamma, leveraged ETFs), which is distinct from a single institution's VWAP program in one stock. A low-volatility one-way day in a single name is consistent with a full-day parent order, but the academic trend-day evidence is about index-level hedging, not single-stock execution.
- Baltussen's reversal over following days parallels the metaorder-reversion result: flow-driven moves partly give back.

### Gaps
- No rigorous published US statistic found for trend-day frequency, or for "price stays one side of VWAP all day" frequency, in indices or single stocks.
- Linda Raschke's trend-day framework: no primary source retrieved; not quoted.
- No study found directly linking single-stock trend days to identified institutional parent orders.

---

## 6. What cannot be seen, and how reliable buy/sell volume classification is

### Takeaway
About half of US equity volume now executes off-exchange and prints via the TRF up to 10 seconds after execution with no visible resting quote; hidden, midpoint and randomised reserve orders remove much of the rest of the footprint. Aggressor-side classification is roughly 75-85% accurate at trade level in the published studies and worst for trades inside the quote, which is exactly where midpoint and dark executions occur.

### Cited Findings

**Off-exchange and hidden liquidity (evidence: STRONG, industry data/regulation)**
- TRF (off-exchange) share rose 300 bp to 47% of total consolidated volume in 2024. — [Cboe North American Equities Year in Review](https://www.cboe.com/insights/posts/north-american-equities-year-in-review)
- MEMX reported a record TRF share of 48.8%; Nasdaq's Mackintosh noted November 2024 was the first month in which more volume executed off-exchange than on. — [MEMX](https://memx.com/insights/retail-and-trf-share-options-activity-is-diverse); [Nasdaq, "Exchange trading increases across all types of stocks"](https://www.nasdaq.com/articles/exchange-trading-increases-across-all-types-stocks)
- Off-exchange midpoint executions add to around 8-9% of total traded volume across the market-cap spectrum. — [Nasdaq, "Tight NBBO matters to off-exchange trades too"](https://www.nasdaq.com/articles/tight-nbbo-matters-to-off-exchange-trades-too)
- FINRA Regulatory Notice 13-19: since 4 November 2013, OTC equity trades must be reported "as soon as practicable, but no later than 10 seconds" after execution; later reports are marked late; manual trades get consideration for complexity. — [FINRA Regulatory Notice 13-19](https://www.finra.org/rules-guidance/notices/13-19)
- Off-exchange NMS trades are reported through a Trade Reporting Facility or the ADF. — [FINRA TRF page](https://www.finra.org/filing-reporting/trade-reporting-facility-trf)
- Randomised reserve display is available at exchange level (Nasdaq random reserve; IEX random replenishment). — [Nasdaq RASH specification](https://m.nasdaqtrader.com/content/technicalsupport/specifications/Tradingproducts/rash_sb_ETMF.pdf); [Federal Register 2021-20453](https://govinfo.gov/content/pkg/FR-2021-09-22/pdf/2021-20453.pdf)

**Trade-side classification accuracy (evidence: STRONG)**
- Ellis, Michaely & O'Hara (JFQA 2000, Nasdaq): quote rule, tick rule and Lee-Ready correctly classify 76.4%, 77.66% and 81.05% of trades; all rules perform poorly on trades executed inside the quotes. — [JFQA, "The Accuracy of Trade Classification Rules: Evidence from Nasdaq"](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/accuracy-of-trade-classification-rulesevidence-from-nasdaq/A2CAD2206B562784527548F5283A9ECB)
- Chakrabarty, Pascual & Shkilko (JFM 2015): bulk volume classification (BVC) underperforms the tick rule and Lee-Ready even after optimisation; TR and LR give more accurate VPIN-type order-imbalance estimates. — [SSRN 2182819](https://papers.ssrn.com/abstract=2182819); [JFM 25:52-79](https://ideas.repec.org/a/eee/finmar/v25y2015icp52-79.html)
- A later literature summary reports Lee-Ready accuracy of around 85% in Chakrabarty et al. (secondhand figure). — [Bank of England WP, Jurkatis, "Inferring trade directions in fast markets"](https://www.bankofengland.co.uk/-/media/boe/files/working-paper/2020/inferring-trade-directions-in-fast-markets.pdf)
- Jurkatis (BoE): the Holden-Jacobsen interpolation method and BVC "do not offer improvements". — [Bank of England WP](https://www.bankofengland.co.uk/-/media/boe/files/working-paper/2020/inferring-trade-directions-in-fast-markets.pdf)
- O'Hara, Yao & Ye: omitting odd lots biases order-imbalance measures (historical issue; odd lots are now on the tape). — [J. Finance 69(5)](https://ideas.repec.org/a/bla/jfinan/v69y2014i5p2199-2236.html)

### Inferences
- "Buy volume vs sell volume", delta and cumulative delta on a retail platform are an estimate with roughly a 15-25% per-trade error rate on lit trades, and are close to uninformative for TRF/midpoint prints (the published studies say inside-quote trades are where the rules fail). With about half of volume off-exchange, a large fraction of the tape has no reliable side.
- A TRF print tells you size, price and (delayed) time. It does not tell you side, whether it was a dark-pool cross, a wholesaler internalising retail flow, or a block; a print between bid and ask is consistent with either side being the initiator.
- An institutional algo that executes mostly via dark pools, midpoint pegs and conditional orders can complete a meaningful share of a parent order with no displayed quote and only side-less prints. The lit-tape footprint of a program is therefore a lower bound on, and a biased sample of, its activity.
- Things that cannot be reliably determined from public data: the identity or type of the participant; the total parent size or remaining quantity; whether flow is one parent or several; the benchmark (VWAP vs TWAP vs POV vs IS); the end time; whether a held level is one order or many.

### Gaps
- Could not verify in-session the SIP sale-condition/venue coding details for TRF prints (the brief's "exchange code D" and absence of a side flag); FINRA rule text confirming "no side disseminated" was not retrieved, though no public tape field for aggressor side exists to my knowledge (unverified in-session).
- VPIN (Easley, Lopez de Prado, O'Hara) and the Andersen-Bondarenko critique: only indirectly covered via Chakrabarty et al.; the critique itself was not retrieved.
- No public data found on the share of institutional algo parent volume executed dark versus lit in 2026, or on how widely anti-gaming randomisation of child timing/size is used (broker marketing asserts it; no measurement found).
- Share of lit exchange volume that is hidden/non-displayed in 2026 was not retrieved.

---

## Summary table for the report writer: signature vs evidence strength

| Signature a tape reader might use | What is actually established | Evidence |
|---|---|---|
| Persistent same-side aggressor flow for minutes-hours | Sign persistence is real and, under a few hours, mostly order splitting (LSE member data) | STRONG that it exists; no public-tape detector validated |
| Concave impact, then partial give-back when the buyer finishes | Square-root/log impact; about 1/3 of peak reverts by same-day close, more over weeks (ANcerno, AllianceBernstein) | STRONG |
| Prints at regular clock intervals | Wall-clock-cycling algos exist (Hasbrouck-Saar); VWAP child patterns measurably predictable with broker data; one "potentially" schedule-driven sawtooth example | MODERATE; whole-minute equity evidence not found |
| Same half-hour behaviour on successive days | Half-hour return continuation at daily lags for 40 days | STRONG (cross-sectional, small per stock) |
| Odd-lot slicing | Real, informed, but now 60%+ of all trades | STRONG that it exists; useless as a discriminator |
| Reloading / iceberg bid | Reserve orders documented; display size can be randomised; venue-specific | STRONG mechanism; detection MODERATE at best |
| "Clean held bid" above a key level | SMB desk pattern, self-described as rare | ANECDOTAL |
| Price holding above VWAP = buy program / VWAP as support | Follows arithmetically from persistent buying; no test found | ANECDOTAL (mechanism plausible) |
| TICK ±1000 = buy/sell program | Mechanically reflects broad simultaneous same-side prints; thresholds untested | ANECDOTAL |
| Trend day = institutional flow | Index late-day momentum tied to gamma/LETF hedging; single-stock link untested | STRONG for index mechanism; ANECDOTAL for single stocks |
| Delta / buy-vs-sell volume | 75-85% trade-level accuracy on lit trades, poor inside the quote; BVC worse | STRONG (as a limitation) |
| Reading dark/TRF prints for direction | About half of volume, up to 10 s delay, no side | STRONG (as a limitation) |
