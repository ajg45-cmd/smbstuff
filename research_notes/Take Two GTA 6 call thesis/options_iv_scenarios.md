# TTWO Options Market, Implied Volatility and Scenario Math for the June 17, 2027 $270 Call (as of Nov 18, 2026)

**Read this first (data-quality note).** In this research session every options-data site (Market Chameleon, Barchart, Nasdaq, Yahoo Finance, AlphaQuery, FlashAlpha, OptionsAnalysisSuite, Benzinga, Seeking Alpha, Treasury.gov) was blocked at the network level; pages could not be opened and no live option chain could be pulled. All "observed" figures below come from web-search result snippets of those pages, each with its own (often stale or missing) timestamp. Everything labelled **MODELED** is my own Black-Scholes calculation (pure-Python script, inputs stated). No figure here is a live quote. Nothing here is personalized investment advice.

Legend: **OBSERVED** = third-party figure from a search snippet. **MODELED** = my calculation. Source link "(calc)" means it came from the script described under "Black-Scholes" below.

---

## 1. Current options data for TTWO (IV, IV rank, implied move, put/call, unusual activity, OI at Jun-2027 $270) and the expiry date

### Takeaway
Live chain data could not be retrieved; the available snapshots show front-end ATM IV of roughly 70-74% in the two weeks before launch against 20-day realized vol near 30%, with IV rank/percentile already high (78/89) a month earlier. No source gave open interest for the June 2027 $270 call, a current put/call ratio, or a published launch-week implied move. The June 2027 monthly expiry on Thursday June 17, 2027 is confirmed by calendar logic and the 2026 precedent, but not from an OCC document.

### Cited Findings
Spot price context (OBSERVED)
- TTWO closed Tuesday Nov 17, 2026 at about $203.93, down 4.47% on the day (Yahoo quote page and Finviz); Yahoo's historical table shows $205.93 for the same day, an unexplained $2 discrepancy. Prior close Monday Nov 16 was $213.47 after a ~6.3% drop with no company news. — [Yahoo Finance quote](https://finance.yahoo.com/quote/TTWO/); [Finviz](https://finviz.com/stock?t=TTWO); [Trefis, "Why Did Take-Two Stock Fall 6% Before GTA VI?" Nov 17, 2026](https://www.trefis.com/stock/ttwo/articles/625817/why-did-take-two-stock-fall-6-before-gta-vi/2026-11-17)
- So the stock fell roughly 10% in the two sessions before launch eve (213.47 on Nov 16 was already -6.3%; 203.93 on Nov 17 another -4.5%). — [Trefis](https://www.trefis.com/stock/ttwo/articles/625817/why-did-take-two-stock-fall-6-before-gta-vi/2026-11-17); [Yahoo Finance quote](https://finance.yahoo.com/quote/TTWO/)
- Conflicting/stale price snapshots exist: a Benzinga "shares rise Monday" piece quotes $233.83, a TradingNews piece quotes $237, EarningsWhispers pages show ~$224-228; none carry a clear date and all are inconsistent with the Nov 16-17 closes above. Treat them as older. — [Benzinga](https://www.benzinga.com/trading-ideas/movers/26/11/63289414/take-two-shares-rise-monday-whats-going-on); [TradingNews](https://www.tradingnews.com/news/take-two-stock-climbs-to-237-ahead-of-gta-vi-launch-breakout-above-237-41-opens-266-usd-target)
- Fiscal Q2 2027 results were reported Nov 9, 2026: net bookings ~$1.6B (-18% y/y), FY27 net bookings guidance kept at $8.0-8.2B, fiscal Q3 net bookings guided to $3.35-3.50B; shares rose ~8.3% on Nov 10. — [Seeking Alpha PR](https://seekingalpha.com/pr/20719548); [Motley Fool, Nov 10, 2026](https://www.fool.com/investing/2026/11/10/why-take-two-stock-s-got-game-today/); [24/7 Wall St](https://247wallst.com/cards/take-two-interactive-q2-2027-earnings-ttwo-01m712jtt7dtqmd3g0kxygyrkz)

Implied volatility snapshots (OBSERVED, each dated differently)
- Market Chameleon option-chain page (snapshot ~Nov 13, 2026): Nov 20, 2026 expiry (7 days out, spans the launch) ATM IV 74.1%, volume 6,813; the Nov 13 expiry (pre-launch) ATM IV 37.4%. — [Market Chameleon TTWO option chain](https://marketchameleon.com/Overview/TTWO/OptionChain/)
- FlashAlpha (dated Nov 3, 2026 in one snippet): price $196.00, ATM IV 70.8%, 20-day historical vol 31.5%. — [FlashAlpha TTWO IV](https://flashalpha.com/stock/ttwo/iv)
- OptionsAnalysisSuite (as of Oct 14, 2026): ATM IV 51.7%, IV rank 77.6%, IV percentile 88.9%, 20-day realized vol 28.8% (IV-HV spread +22.9 points). — [OptionsAnalysisSuite IV/HV history](https://www.optionsanalysissuite.com/stocks/ttwo/iv-hv-history)
- ApexVol (as of Jul 2, 2026): 30-day IV 44.5%, IV rank 96.0 vs. 52-week range. — [ApexVol](https://apexvol.com/options/ttwo)
- Older baseline: a Nasdaq "December 2026 options now available" article cited implied vols of ~34-36% vs. trailing-12-month realized vol of 30% (stock then $251.61; the Dec 2026 $270 call bid $33.50). Undated, clearly earlier in 2026. — [Nasdaq](https://www.nasdaq.com/articles/december-2026-options-now-available-take-two-interactive-software-ttwo)

Implied move (OBSERVED)
- Before the Nov 9 earnings report, Bloomberg options data (via Investing.com) showed an implied move of 9.4%; another source put pre-earnings implied moves at ~8-9%. These were for earnings, not launch week. — [ts2.tech](https://ts2.tech/en/take-two-stock-just-got-its-gta-6-spark-next-week-brings-the-real-test/); [Seeking Alpha, "Options price in Take-Two event"](https://seekingalpha.com/news/4594176-options-price-in-take-two-event-as-grand-theft-auto-presale-buzz-builds)
- An earlier-cycle reference point: options implied a 5.1% post-earnings move for a prior quarter. — [TipRanks/The Fly](https://www.tipranks.com/news/the-fly/taketwo-interactive-software-options-imply-5-1-move-in-share-price-post-earnings)

Put/call and unusual activity (OBSERVED)
- A German-language Boerse-Express article headlined "Take-Two Aktie: Put-Volumen schiesst hoch" ("put volume shoots up") appeared in the launch run-up; the page could not be opened, so no numbers. — [Boerse-Express](https://www.boerse-express.com/news/articles/take-two-aktie-put-volumen-schiesst-hoch-930120)
- Aug 6, 2026: ~60,076 TTWO calls traded, +413% vs. average daily call volume of 11,712 (stock ~$233.50). — [MarketBeat](https://www.marketbeat.com/instant-alerts/take-two-interactive-software-target-of-unusually-large-options-trading-nasdaqttwo-2026-08-06/)
- May 22, 2026: call volume +640% vs. typical 8,909 calls. — [MarketBeat](https://www.marketbeat.com/instant-alerts/traders-buy-high-volume-of-take-two-interactive-software-call-options-nasdaqttwo-2026-05-22/)
- A Market Chameleon tracker reported open interest on the Sep 18, 2026 $270 call rising by 26,432 contracts (different, now-expired expiry; shows $270 was a popular speculative strike). — [Market Chameleon stock posts](https://marketchameleon.com/Overview/TTWO/StockPosts/)
- MarketXLS showed total TTWO call open interest of 212,625 contracts (undated, not by strike). — [MarketXLS](https://marketxls.com/stocks/TTWO/options)

Expiry date
- Juneteenth (June 19, 2027) falls on a Saturday and is observed Friday June 18, 2027; NYSE and Nasdaq are closed that day. — [fedratecalc.com](https://fedratecalc.com/is-the-stock-market-open-on-juneteenth/); [fedratecalc.com Juneteenth 2027](https://fedratecalc.com/juneteenth-2027/)
- CME's 2027 Juneteenth notice treats Thursday June 17 as the last normal settlement day before the holiday. — [CME Group](https://www.cmegroup.com/tools-information/holiday-calendar/files/2027/juneteenth-day-settlement-times-2027.pdf)
- Precedent: the June 2026 monthly expiration was Thursday June 18, 2026 because Juneteenth fell on Friday June 19, 2026 (Macroption, citing Cboe/OCC). — [Macroption expiration calendar](https://www.macroption.com/options-expiration-calendar/)
- My script confirms June 17, 2027 is a Thursday, June 18 a Friday (third Friday), June 19 a Saturday; Nov 18, 2026 to June 17, 2027 is 211 calendar days. — (calc)

### Inferences
- MODELED implied move for launch week: a 74.1% ATM IV with 7 days to expiry corresponds to an expected absolute move (straddle approximation 0.8 x sigma x sqrt(T)) of about 8.2% over that week (1 s.d. about 10.3%). If "ordinary" vol is 35-45%, the excess variance implies a single launch-event day of roughly 8.5-9% standard deviation (~7% expected absolute move). This is comparable to the 8-9.4% implied move reported for the Nov 9 earnings. (calc, from the Market Chameleon IV figure)
- The $12.50 price paid for the June 2027 $270 call backs out to ~47-48% IV (see section 3), below the 70%+ front-end IV but far above TTWO's ~30% realized vol and the ~34-36% long-dated IV quoted earlier in 2026. The buyer is paying an elevated, event-inflated vol level even 7 months out.
- The stock's ~10% slide on Nov 16-17 into the launch, with a "put volume" headline, suggests hedging/de-risking ahead of the event rather than uniformly bullish positioning; I could not verify this with put/call numbers.
- Calls expiring Thursday June 17, 2027 stop trading that day; that is after the expected mid/late-May fiscal Q4 report, so the contract does capture FY28 guidance, but with only ~4 weeks to spare.

### Gaps
- Open interest, volume, bid/ask and quoted IV for the June 17, 2027 $270 call: not found; no chain page could be opened.
- Current ATM IV for the June 2027 expiry, IV term structure, skew: not retrievable. The 47.8% figure is backed out from the user's $12.50 fill, not observed.
- Current IV rank/percentile (latest found is Oct 14, 2026), current put/call ratio (volume or OI), and a published launch-week implied move: not found.
- An official OCC 2027 expiration calendar was not found in results; the June 17 date rests on the holiday rule and 2026 precedent. Confirm on the broker chain (the contract symbol should read TTWO 270617C00270000).
- Hosts that must be allowed for live verification: marketchameleon.com, barchart.com, api.nasdaq.com, finance.yahoo.com, alphaquery.com, flashalpha.com, optionsanalysissuite.com, home.treasury.gov.

---

## 2. How TTWO implied volatility and the stock have behaved after past catalysts; typical IV contraction

### Takeaway
I found no historical IV time series for TTWO around past events, so "typical IV crush" cannot be quantified from sources. What is documented is price behavior: the stock sold off after the RDR2 launch despite record sales and dropped on each GTA VI delay. Modeling shows that removing a single launch-day event barely lowers a 211-day IV (1-3 points); a larger drop in the June 2027 IV would require the whole post-launch uncertainty premium to deflate toward the 34-36% level seen earlier in 2026.

### Cited Findings
- RDR2 launched Oct 26, 2018; first-three-day sell-through was over $725 million. — [Fortune](https://www.fortune.com/2018/10/30/red-dead-redemption-2-sales-record)
- TTWO "actually sold off following the release of Red Dead Redemption 2 on Oct. 26" before rebounding on the sales press release; it had hit a then-lifetime high near $140 in early October 2018 and later sold off with the broad market. — [Motley Fool, Nov 18, 2018](https://www.fool.com/investing/2018/11/18/why-take-two-interactive-is-up-3-so-far-in-2018.aspx)
- By the time of one InvestorPlace piece the stock was ~27% below its early-October 2018 high. — [InvestorPlace](https://investorplace.com/?p=1296253)
- At the fiscal Q3 report in Feb 2019 (RDR2 had sold 23 million copies in the quarter), the stock fell ~13% in a day. — [GamesBeat](https://gamesbeat.com/red-dead-redemption-2-gallops-to-23-million-copies-in-a-quarter-stock-falls-13/); [Motley Fool, Feb 6, 2019](https://www.fool.com/investing/2019/02/06/why-shares-of-take-two-interactive-tumbled-today.aspx)
- Pre-RDR2 options pricing was covered by Bloomberg ("Traders Are Getting Ready for One of the Hottest Video Game Releases of the Year", Oct 24, 2018) and Schaeffer's (Oct 26, 2018); contents not retrievable. — [Bloomberg](https://www.bloomberg.com/news/articles/2018-10-24/take-two-aims-to-reverse-the-bleeding-with-red-dead-release); [Schaeffer's](https://www.schaeffersresearch.com/content/analysis/2018/10/26/take-two-stock-could-have-gas-in-the-tank)
- Historic Schaeffer's Volatility Index readings (30-day ATM IV proxy) show TTWO's normal range: 54% (86th percentile) in Feb 2018, 34% (12th percentile) in May 2019, 26% (5th percentile) in June 2021. — [Schaeffer's Jun 2021](https://www.schaeffersresearch.com/content/news/2021/06/03/ttwo-scores-analyst-bull-note-on-growth-prospects); [Schaeffer's May 2019](https://www.schaeffersresearch.com/content/analysis/2019/05/31/this-video-game-stock-beat-the-may-sell-off); [Schaeffer's Feb 2018](https://www.schaeffersresearch.com/content/news/2018/02/01/take-two-stock-scores-bull-note-new-high-ahead-of-earnings)
- GTA VI delay reactions: the stock dropped on the Nov 2025 delay (to Nov 19, 2026) and Schaeffer's covered both that and the May 2024 guidance/delay reaction (stock higher despite the delay). The game was originally slated for 2025, then May 26, 2026, then Nov 19, 2026. — [Schaeffer's, Nov 7, 2025](https://www.schaeffersresearch.com/content/news/2025/11/07/software-stock-drops-on-delay-in-grand-theft-auto-release); [Schaeffer's, May 17, 2024](https://www.schaeffersresearch.com/content/news/2024/05/17/video-game-stock-higher-despite-gta-delay); [Finviz](https://finviz.com/news/223170/software-stock-drops-after-another-grand-theft-auto-delay)
- IV level progression through 2026 (the only "IV history" available): ~34-36% (undated, earlier 2026) -> 44.5% 30-day IV on Jul 2 -> 51.7% ATM on Oct 14 -> 70.8% on Nov 3 -> 74.1% for the launch-spanning weekly on ~Nov 13. — [Nasdaq](https://www.nasdaq.com/articles/december-2026-options-now-available-take-two-interactive-software-ttwo); [ApexVol](https://apexvol.com/options/ttwo); [OptionsAnalysisSuite](https://www.optionsanalysissuite.com/stocks/ttwo/iv-hv-history); [FlashAlpha](https://flashalpha.com/stock/ttwo/iv); [Market Chameleon](https://marketchameleon.com/Overview/TTWO/OptionChain/)

### Inferences
- MODELED event-variance arithmetic for the June 2027 expiry (total IV 47.8%, 211 days): stripping out a one-day event with standard deviation 6% / 8% / 10% / 12% lowers the 211-day IV by only about 0.7 / 1.2 / 1.8 / 2.7 points. Mechanical "event passes" crush is therefore small for a 7-month option; the weekly options absorb almost all of it. (calc)
- A 5-10 point drop in the June 2027 IV (to ~38-43%) is nonetheless plausible if the launch resolves uncertainty and long-dated IV drifts back toward the 34-36% level cited earlier in 2026 or toward the ~30% realized vol. That is a regime repricing rather than a one-day effect, and it is why the scenario tables include -5 and -10 (and I added -15) point cases. This is my judgment, not a sourced statistic.
- The RDR2 precedent (record launch, stock down afterward and -13% at the following fiscal Q3 report) shows "great launch" and "stock up" are not the same event; both fiscal Q3 (Feb) and Q4 (May) reports are separate vol events that will re-inflate short-dated IV before each.
- The steep front-end term structure (74% weekly vs. ~48% June 2027 backed out) is the normal shape before a known event and will flatten immediately after Nov 19-20.

### Gaps
- No historical IV series for TTWO around the 2018 RDR2 launch, the May 2025 and Nov 2025 GTA VI delays, or earnings dates could be retrieved; "typical IV contraction" is not sourced. Market Chameleon's earnings "IV crush" tables and OptionsAnalysisSuite's IV/HV history would answer this but were blocked.
- TTWO's stock reaction to the GTA V launch (Sept 2013) was not found.
- Exact one-day percentage moves on the May 2025 and Nov 2025 delay announcements were not in the snippets.

---

## 3. Black-Scholes analysis of the June 17, 2027 $270 call bought at $12.50 (ALL MODELED)

### Takeaway
At spot $206, 211 days, r = 4.4%, no dividend, $12.50 implies about 47.8% IV; delta ~0.31, theta about -$0.069/share/day (-$6.9/contract), vega about $0.55 per vol point ($55/contract). Risk-neutral probability of finishing above $270 is ~20% and above the $282.50 breakeven ~16%. If the stock does nothing, the option is worth ~$10.6 by mid-December and ~$6.2 by mid-February at unchanged IV, and ~$6.0 / ~$3.0 with IV 10 points lower.

### Cited Findings
Inputs and assumptions
- Model: Black-Scholes European call, flat volatility (no skew or term structure), continuous compounding, 365-day year, no dividend. Script: `/tmp/claude-0/-home-user-smbstuff/7f65bd08-d200-53bf-b100-4dab665c4724/scratchpad/bs.py` (pure Python, bisection for IV). — (calc)
- Valuation date Nov 18, 2026; expiry Thursday June 17, 2027; 211 calendar days; T = 0.5781 years. — (calc)
- Risk-free rate 4.4%: the most recent Treasury data found were the Sept 28, 2026 26-week bill auction (investment rate 4.441%) and Sept 29, 2026 52-week bill (4.616%); November 2026 daily rates could not be retrieved. Sensitivity run at 4.0% and 4.8%. — [tftc.io Treasury bill auction data](https://www.tftc.io/treasury-bills)
- TTWO pays no dividend (assumption; standard for this company, not re-verified this session).
- American-style exercise is ignored; for a non-dividend stock the early-exercise value of a call is nil, so this is not a material simplification.

Implied volatility and Greeks at $12.50 (per share; multiply by 100 per contract)

| Spot | r | Implied vol | Delta | Theta/day | Vega per 1 vol pt | P(S_T > $270) | P(S_T > $282.50) |
|---|---|---|---|---|---|---|---|
| $204 | 4.4% | 48.9% | 0.309 | -$0.069 | $0.546 | 19.2% | 16.0% |
| **$206** | **4.4%** | **47.8%** | **0.311** | **-$0.069** | **$0.553** | **19.6%** | **16.3%** |
| $208 | 4.4% | 46.7% | 0.313 | -$0.068 | $0.561 | 20.0% | 16.6% |
| $206 | 4.0% | 48.0% | 0.310 | -$0.069 | $0.553 | 19.5% | 16.2% |
| $206 | 4.8% | 47.6% | 0.312 | -$0.069 | $0.554 | 19.7% | 16.4% |

- Gamma at base case: 0.0047 per $1. Forward price to expiry: $211.31. $270 is 31.1% above $206; the $282.50 breakeven is 37.1% above. — (calc)
- For reference, the same call would be worth $5.95 at 35% IV, $8.37 at 40%, $10.98 at 45%, $13.74 at 50% (spot $206, today). — (calc)
- The probabilities are risk-neutral N(d2) values, i.e., what the option price implies under the model, not forecasts.

Immediate sensitivity (spot $206, today): value $12.50 at 47.8% IV; $9.80 at 42.8%; $7.27 at 37.8%. — (calc)

Post-launch snapshot, Friday Nov 20, 2026 (209 days left)

| Stock move | Spot | IV unchanged (47.8%) | IV -5 (42.8%) | IV -10 (37.8%) |
|---|---|---|---|---|
| -15% | $175.1 | $4.99 | $3.41 | $2.11 |
| -10% | $185.4 | $6.97 | $5.03 | $3.33 |
| -5% | $195.7 | $9.42 | $7.11 | $5.00 |
| 0% | $206.0 | $12.36 | $9.68 | $7.17 |
| +5% | $216.3 | $15.80 | $12.79 | $9.90 |
| +10% | $226.6 | $19.74 | $16.44 | $13.22 |
| +15% | $236.9 | $24.19 | $20.65 | $17.14 |

Scenario table: estimated option value per share (cost basis $12.50)

Mid-December 2026 (Dec 15, 2026; 184 days left)

| IV | $180 | $200 | $220 | $240 | $260 | $280 | $300 |
|---|---|---|---|---|---|---|---|
| Unchanged 47.8% | 4.74 | 8.98 | 15.12 | 23.24 | 33.30 | 45.15 | 58.58 |
| -5 pts (42.8%) | 3.24 | 6.77 | 12.25 | 19.87 | 29.64 | 41.41 | 54.94 |
| -10 pts (37.8%) | 2.00 | 4.77 | 9.50 | 16.53 | 25.97 | 37.67 | 51.37 |
| -15 pts (32.8%) | 1.05 | 3.02 | 6.90 | 13.25 | 22.29 | 33.96 | 47.90 |

Mid-February 2027, after the fiscal Q3 report (Feb 15, 2027; 122 days left)

| IV | $180 | $200 | $220 | $240 | $260 | $280 | $300 |
|---|---|---|---|---|---|---|---|
| Unchanged 47.8% | 2.13 | 4.95 | 9.69 | 16.67 | 25.97 | 37.48 | 50.93 |
| -5 pts (42.8%) | 1.31 | 3.50 | 7.57 | 14.00 | 22.97 | 34.41 | 48.03 |
| -10 pts (37.8%) | 0.70 | 2.25 | 5.58 | 11.37 | 19.97 | 31.36 | 45.20 |
| -15 pts (32.8%) | 0.30 | 1.26 | 3.79 | 8.82 | 16.98 | 28.33 | 42.47 |

After the fiscal Q4 report (May 21, 2027; 27 days left). Note: the prior-year Q4 report was May 21, so "mid-May" (e.g., May 14) may fall before the report; I used May 21 so the table is genuinely post-report.

| IV | $180 | $200 | $220 | $240 | $260 | $280 | $300 |
|---|---|---|---|---|---|---|---|
| Unchanged 47.8% | 0.01 | 0.12 | 0.82 | 3.43 | 9.63 | 20.32 | 35.04 |
| -5 pts (42.8%) | 0.00 | 0.05 | 0.48 | 2.54 | 8.25 | 18.91 | 34.00 |
| -10 pts (37.8%) | 0.00 | 0.01 | 0.24 | 1.74 | 6.88 | 17.52 | 33.06 |
| -15 pts (32.8%) | 0.00 | 0.00 | 0.09 | 1.07 | 5.54 | 16.15 | 32.25 |

Derived readings from the same model
- Stock price at which the option is still worth the $12.50 paid: mid-Dec $212 (IV unchanged) / $221 (-5) / $229 (-10); mid-Feb $229 / $236 / $243; May 21 $266 / $269 / $272. — (calc)
- Value if the stock sits at $206: mid-Dec $10.62 / $8.20 / $5.96; mid-Feb $6.15 / $4.50 / $3.03; May 21 $0.22 / $0.10 / $0.04 (IV unchanged / -5 / -10). — (calc)
- At expiry the call is worth max(S - 270, 0): zero at or below $270, a 100% loss; $10 at $280 (-20% on premium); $30 at $300 (+140%); $50 at $320 (+300%). — (calc)

### Inferences
- A 10-point IV decline costs about $5.2 per share today (roughly 42% of the premium), equivalent to about a 9% drop in the stock at unchanged IV. The position is as much a volatility position as a directional one in the first weeks.
- Theta of ~$0.07/day is modest now but the option is far out of the money, so decay accelerates in percentage terms: a flat stock loses ~15% of premium by mid-December and ~51% by mid-February even with no IV change.
- By the post-Q4 date the option is nearly binary: it has meaningful value only if the stock is already at or above roughly $250-260.
- With spot at the Nov 17 close of $203.93 instead of $206, the implied vol backed out is about a point higher (~49%); the conclusions do not change.

### Gaps
- No quoted market IV for this contract was available to check the 47.8% back-solve, and the true surface has skew (far-OTM calls often trade at a different IV than ATM) and term structure, so alternative strikes/expiries priced at the same flat IV are approximations.
- Risk-free rate is from late-September 2026 bill auctions; November data unavailable. The sensitivity (0.2 vol points per 40 bp) is negligible.

---

## 4. Next two earnings reports

### Takeaway
Based on prior-year dates, fiscal Q3 2027 (quarter ending Dec 31, 2026, the first to include GTA VI) should be reported in early February 2027 and fiscal Q4 2027 with initial fiscal 2028 guidance around the third week of May 2027; neither date has been announced in anything I found. Both fall before the June 17, 2027 expiry.

### Cited Findings
- Fiscal Q3 2026 results were reported after the close on Tuesday February 3, 2026 (date announced in early January 2026; call at 4:30 pm ET). — [Nasdaq press release](https://www.nasdaq.com/press-release/take-two-interactive-software-inc-report-third-quarter-fiscal-year-2026-results); [Business Wire](https://www.businesswire.com/news/home/20260106677069/en/)
- Fiscal Q4 and full-year 2026 results were reported after the close on Thursday May 21, 2026 (date announced April 23, 2026). — [Business Wire](https://secure.businesswire.com/news/home/20260423775049/en/Take-Two-Interactive-Software-Inc.-to-Report-Fourth-Quarter-and-Fiscal-Year-2026-Results-on-Thursday-May-21-2026); [Motley Fool transcript](https://www.fool.com/earnings/call-transcripts/2026/05/21/take-two-ttwo-q4-2026-earnings-transcript/)
- Fiscal Q2 2027 results were reported November 9, 2026; fiscal Q3 2027 net bookings guidance is $3.35-3.50B and FY27 net bookings guidance is $8.0-8.2B. — [Seeking Alpha PR](https://seekingalpha.com/pr/20719548); [24/7 Wall St](https://247wallst.com/cards/take-two-interactive-q2-2027-earnings-ttwo-01m712jtt7dtqmd3g0kxygyrkz)

### Inferences
- Expected windows: fiscal Q3 2027 around Feb 2-9, 2027 (announcement of the date likely in early January 2027); fiscal Q4 2027 / FY28 guidance around May 13-20, 2027 (date likely announced in late April). These are estimates from the pattern, not company-confirmed dates.
- If the Q4 report lands around May 20, 2027, the June 17 call would have about 28 calendar days (about 19 trading days) left afterward, so the FY28 guidance reaction is captured but there is little time for a slower re-rating.
- The February report carries the first hard GTA VI sell-through and net bookings numbers versus the $3.35-3.50B guide; per the RDR2 precedent (stock -13% on the Feb 2019 report despite 23 million units), it is a two-sided event.

### Gaps
- Fiscal 2025 dates (which I recall as roughly Feb 6 and May 15, 2025) were not confirmed by any source found this session; only fiscal 2026 dates are sourced.
- The company's IR calendar (ir.take2games.com) could not be opened to check for an already-announced Q3 date.

---

## 5. Alternative structures for the same bullish view (ALL PRICES MODELED at flat 47.8% IV, spot $206, r 4.4%)

### Takeaway
No market quotes were obtainable, so all alternatives are modeled at the same flat IV as the $270 call. Closer strikes and a call spread roughly halve the required stock move to break even (to +17% to +26% instead of +37%) at the cost of more premium or a capped payoff; the January 2028 $270 call roughly doubles the premium to buy seven more months and a slower decay rate.

### Cited Findings
Model prices and Greeks, per share (calc; same script and inputs as section 3)

| Structure | Est. cost | Delta | Theta/day | Vega/pt | Breakeven at expiry | Move needed from $206 | Risk-neutral P(ITM) | Max loss | Max gain |
|---|---|---|---|---|---|---|---|---|---|
| Jun-2027 $270 call (held) | $12.50 | 0.31 | -0.069 | 0.55 | $282.50 | +37.1% | 19.6% | $12.50 | Unlimited |
| Jun-2027 $250 call | $16.92 | 0.39 | -0.076 | 0.60 | $266.92 | +29.6% | 26.0% | $16.92 | Unlimited |
| Jun-2027 $240 call | $19.63 | 0.43 | -0.078 | 0.62 | $259.63 | +26.0% | 29.7% | $19.63 | Unlimited |
| Jun-2027 $230 call | $22.73 | 0.48 | -0.080 | 0.62 | $252.73 | +22.7% | 33.9% | $22.73 | Unlimited |
| Jun-2027 $230/$270 call debit spread | $10.23 | ~0.17 net | ~-0.011 net | ~0.07 net | $240.23 | +16.6% | n/a | $10.23 | $29.77 at >= $270 (2.9x debit) |
| Jun-2027 $240/$270 call debit spread | $7.13 | ~0.12 net | ~-0.009 net | ~0.06 net | $247.13 | +20.0% | n/a | $7.13 | $22.87 at >= $270 (3.2x debit) |
| Jan-21-2028 $270 call (429 days) at 47.8% IV | $26.10 | 0.44 | -0.057 | 0.88 | $296.10 | +43.7% | 24.8% | $26.10 | Unlimited |
| Same LEAP at 44.8% IV | $23.47 | 0.42 | -0.053 | 0.87 | $293.47 | +42.5% | 24.4% | $23.47 | Unlimited |
| Same LEAP at 41.8% IV | $20.87 | 0.40 | -0.049 | 0.86 | $290.87 | +41.2% | 23.9% | $20.87 | Unlimited |

- IV sensitivity of the closer strikes: $230 call $20.86 / $22.73 / $24.60 and $240 call $17.79 / $19.63 / $21.48 at IV 44.8% / 47.8% / 50.8%. — (calc)
- January 21, 2028 is the third Friday of January 2028 (standard LEAP expiry); 429 days from Nov 18, 2026. — (calc)

Profit/loss per share at June 17, 2027 expiry (calc)

| Stock at expiry | Long $270 call | Long $230 call | $230/$270 spread | Long $240 call |
|---|---|---|---|---|
| $200 | -12.50 | -22.73 | -10.23 | -19.63 |
| $220 | -12.50 | -22.73 | -10.23 | -19.63 |
| $240 | -12.50 | -12.73 | -0.23 | -19.63 |
| $250 | -12.50 | -2.73 | +9.77 | -9.63 |
| $260 | -12.50 | +7.27 | +19.77 | +0.37 |
| $270 | -12.50 | +17.27 | +29.77 | +10.37 |
| $282.50 | 0.00 | +29.77 | +29.77 | +22.87 |
| $300 | +17.50 | +47.27 | +29.77 | +40.37 |
| $320 | +37.50 | +67.27 | +29.77 | +60.37 |
| $350 | +67.50 | +97.27 | +29.77 | +90.37 |

$230/$270 spread value before expiry (IV unchanged / IV -10 pts), per share (calc)

| Date | $180 | $200 | $220 | $240 | $260 | $280 | $300 |
|---|---|---|---|---|---|---|---|
| Dec 15, 2026, IV unch. | 5.66 | 8.84 | 12.44 | 16.16 | 19.78 | 23.13 | 26.10 |
| Dec 15, 2026, IV -10 | 4.11 | 7.56 | 11.85 | 16.51 | 21.08 | 25.20 | 28.69 |
| Feb 15, 2027, IV unch. | 4.15 | 7.50 | 11.66 | 16.19 | 20.65 | 24.72 | 28.22 |
| Feb 15, 2027, IV -10 | 2.60 | 5.92 | 10.70 | 16.29 | 21.89 | 26.85 | 30.84 |
| May 21, 2027, IV unch. | 0.31 | 1.99 | 6.77 | 14.85 | 23.93 | 31.31 | 35.95 |
| May 21, 2027, IV -10 | 0.06 | 0.93 | 5.07 | 14.19 | 25.20 | 33.49 | 37.73 |

- Real-market anchor for how expensive upside calls were earlier in 2026: with the stock at $251.61, the December 2026 $270 call was bid $33.50 (undated Nasdaq article). — [Nasdaq](https://www.nasdaq.com/articles/december-2026-options-now-available-take-two-interactive-software-ttwo)

### Inferences
Trade-offs (descriptive, not a recommendation)
- **Outright $270 call (held):** lowest cash outlay of the single-leg choices and the most leverage only in a very large rally (profit as a multiple of premium at $320: 3.0x for the $270 call, 2.96x for the $230 call, 2.9x capped for the spread; at $350: 5.4x vs. 4.3x vs. 2.9x; below about $320 the alternatives return more per dollar risked), but needs +37% by June 17 to break even, has the lowest probability of any payoff (~20% risk-neutral), and is the most exposed to IV contraction in percentage terms (-42% of premium for -10 vol points).
- **$230 or $240 call:** costs 57-82% more, breakeven drops to $253-260 (+23% to +26%), delta 0.43-0.48 so it responds more to a moderate rally, and it retains value in the "stock recovers to $240-260" outcomes where the $270 call expires worthless. Larger dollars at risk; similar vega in dollars but smaller as a share of premium (-10 vol points is about -27% of the $230 call's value versus -42% for the $270).
- **$230/$270 debit spread:** cheaper than the $270 call alone in this model ($10.23 vs. $12.50), breakeven $240 (+17%), and nearly vega-neutral and theta-light because the short $270 call offsets the long leg (a 10-point IV drop changes its value by well under $2 at most stock prices and helps it when the stock is above ~$240). The cost is a hard cap: max value $40, so nothing extra is earned above $270; above about $312 at expiry the outright $270 call makes more. It suits a "re-rating back to the $250-270 area" view rather than a "blowout to $320+" view. Requires spread-trading approval and has two bid/ask spreads.
- **January 2028 $270 call:** about twice the premium ($21-26 modeled) for 218 extra days; lower theta (-$0.05 to -0.06/day vs. -$0.07) and it spans the fiscal Q1-Q3 2028 reports and the first holiday season of GTA Online's successor, but vega is ~60% larger in dollars ($0.87/pt), so it is more exposed to a long-dated IV decline, and the expiry breakeven is higher ($291-296). LEAP IV is typically lower than 7-month IV when the term structure is inverted by an event, which is why I show 41.8-47.8%.
- All modeled prices assume the same flat IV. In practice the surface is unknown here; if out-of-the-money call IV is lower than ATM IV, the closer strikes would cost more than shown and the spread debit would be larger, and vice versa.

### Gaps
- No live bid/ask, IV, or open interest for any of the alternative contracts (June 2027 $230/$240/$250, January 2028 $270); whether a January 2028 $270 strike is listed and liquid was not verified.
- Bid/ask spreads on long-dated OTM TTWO options (which affect entry/exit cost materially) are unknown.

---

## 6. TTWO historical realized volatility and frequency of a 30%+ gain over 7 months

### Takeaway
Realized vol has run around 29-33% on the available 2026 readings, far below the ~48% implied by the option. I could not download price history, so the empirical frequency of 30%+ gains in rolling 7-month windows is not computed; calendar-year returns show 30%+ years in 5 of the 11 years 2015-2025, and a lognormal model at 30-40% vol puts a 30%+ gain in 211 days at roughly 10-23% depending on the drift assumed.

### Cited Findings
Realized volatility (OBSERVED)
- 20-day realized vol 28.8% as of Oct 14, 2026. — [OptionsAnalysisSuite](https://www.optionsanalysissuite.com/stocks/ttwo/iv-hv-history)
- 20-day historical vol 31.5% as of Nov 3, 2026. — [FlashAlpha](https://flashalpha.com/stock/ttwo/iv)
- 180-day close-to-close historical vol 33.2% as of Apr 21, 2026; 10-day Parkinson vol 20.9% as of Jan 20, 2026. — [AlphaQuery 180-day HV](https://www.alphaquery.com/stock/TTWO/volatility-option-statistics/180-day/historical-volatility); [AlphaQuery Parkinson](https://www.alphaquery.com/stock/TTWO/volatility-option-statistics/10-day/parkinson-historical-volatility)
- Trailing-12-month realized vol ~30% (undated, earlier 2026). — [Nasdaq](https://www.nasdaq.com/articles/december-2026-options-now-available-take-two-interactive-software-ttwo)
- Fintel shows 30-day historical vol 55.91 (undated; inconsistent with the others, possibly a different date or method). — [Fintel](https://fintel.io/svd/us/ttwo)

Calendar-year price returns (OBSERVED)
- 2015 +24.3%, 2016 +41.5%, 2017 +122.7% ($49.29 to $109.78), 2018 -6.2%, 2019 +18.9%, 2020 +69.7%, 2021 -14.5%, 2022 -41.4% ($177.72 to $104.13), 2023 +54.6%, 2024 +14.4%, 2025 +39.1% ($184.08 to $256.03). — [ChartRow TTWO returns by year](https://chartrow.com/quote/ttwo/returns)
- Compound annual return since 1998 about 14.4%. — [ChartRow](https://chartrow.com/quote/ttwo/returns)
- 2025 closed at $256.03, so at ~$204-206 the stock is down roughly 20% year to date in 2026. — [ChartRow](https://chartrow.com/quote/ttwo/returns); [Yahoo Finance quote](https://finance.yahoo.com/quote/TTWO/)

MODELED real-world probability of a gain over 211 days (lognormal, constant vol, annual drift mu; calc)

| Drift mu | Vol | P(gain >= 30%) | P(S > $270, +31.1%) | P(S > $282.50, +37.1%) |
|---|---|---|---|---|
| 0% | 30% | 10.3% | 9.7% | 6.7% |
| 0% | 35% | 13.2% | 12.5% | 9.3% |
| 0% | 40% | 15.5% | 14.9% | 11.7% |
| 8% | 30% | 14.4% | 13.6% | 9.8% |
| 8% | 35% | 17.2% | 16.5% | 12.6% |
| 8% | 40% | 19.4% | 18.7% | 15.0% |
| 14.4% | 30% | 18.4% | 17.5% | 12.8% |
| 14.4% | 35% | 21.0% | 20.1% | 15.7% |
| 14.4% | 40% | 22.9% | 22.1% | 18.0% |
| 14.4% | 45% | 24.4% | 23.6% | 19.7% |

### Inferences
- Five of eleven calendar years 2015-2025 (2016, 2017, 2020, 2023, 2025) had 30%+ price gains over 12 months; a 7-month window is shorter, so the per-window frequency should be lower than 5/11. This is a coarse proxy, not the rolling-window statistic requested.
- If future realized vol looks like the recent ~30% rather than the ~48% implied, the modeled chance of clearing the $282.50 breakeven is roughly 7-13% (depending on drift) versus the ~16% the option price implies; the option is "expensive" relative to history on that basis. The counter-argument is that the launch and the two following reports are not ordinary periods, and realized vol around them may exceed the trailing figures (the stock already moved +8.3%, -6.3% and -4.5% on three days between Nov 10 and Nov 17).
- At $270 the stock would be about 5% above its end-2025 level of $256.03, i.e., the strike requires recovering the entire 2026 year-to-date decline and a little more, not reaching uncharted territory. Whether $270 exceeds the all-time high was not verified.

### Gaps
- Daily or monthly price history could not be downloaded (Yahoo, Stooq, Nasdaq blocked), so the empirical share of rolling 7-month (about 147-trading-day) windows with a 30%+ gain, and long-run realized vol by year, were not computed. This is a straightforward calculation once price data is accessible.
- 52-week high/low and the all-time high as of November 2026 were not confirmed.
- Lognormal probabilities ignore fat tails and event jumps; they are illustrative only.
