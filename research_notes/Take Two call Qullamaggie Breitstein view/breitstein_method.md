# Lance Breitstein's Trading Methodology (EV, sizing, right side of the V, exits/trailing), with pointers to the TTWO Jun-2027 $270 call trade

**Read this first: source reliability**

- **No web page could be opened in this session.** Every fetch attempt failed at the network level (hosts not on the session allow-list: chatwithtraders.com, traderlion.com, retailtradersrepository.substack.com, threadreaderapp.com, theonelanceb.com, tradezella.com, completetradersedge.com, sozai.app, skillsmp.com). **All web findings below rest on search-result summaries and snippets, not on full-page reads.** Wording shown in quotation marks is the fragment as it appeared in a search summary; it may be truncated and should be checked against the original before being published as a verbatim quote.
- The one source read in full is the local study-notes file (paraphrased notes of the Trillium interview with Jonathan Chariton, itself a summary by "A Retail Trader's Repository"). It is paraphrase, not transcript. Cited below as [Local study notes]; underlying interview: https://www.youtube.com/watch?v=-jGUSk5lJbI ; underlying write-up: https://retailtradersrepository.substack.com/p/lance-breitstein-trillium-interview
- Tiers used below: **[LB-direct]** = his own X post, as surfaced in a search snippet. **[Interview-paraphrase]** = notes of what he said in an interview. **[Secondary]** = third-party write-up or AI-generated summary; treat as interpretation. **[Unverified]** = could not be traced to him.
- The brief's premise that he trails "1-minute to 5-minute to higher timeframes" as a trade matures **was not confirmed**. The sources found point to 2-minute bars as his core intraday chart (see Exits section).

---

## 1. Expected value: the trader's job, rejection of fixed win-rate / R:R targets, trade grading

### Takeaway
He frames the job as estimating the EV of an opportunity at each moment and betting in proportion; win rate and reward-to-risk trade off, so no fixed number of either is required, and stops and profit-taking rules should be whatever maximizes EV. Trade grading (A/B/C) is confirmed in his own account, but the specific multi-variable scorecards circulating online are third-party reconstructions.

### Cited Findings
- [Interview-paraphrase] "At any moment you're estimating the EV of an opportunity and betting based on it." Positive expectancy combines chance of success and risk-to-reward, so "I need a 60% win rate" or "I only take 3:1" is the wrong frame; the two trade off. He built a crude Excel sheet (RANDBETWEEN) with win rate, R:R and size variables to simulate 100-trade outcomes and kill the idea that a single fixed number is required. — [Local study notes / Trillium interview](https://www.youtube.com/watch?v=-jGUSk5lJbI); same point in the summary of [A Retail Trader's Repository](https://retailtradersrepository.substack.com/p/lance-breitstein-trillium-interview)
- [LB-direct, snippet] "Few fallacies worse than 'can't go broke taking profits!' & 'keep a tight stop on your losers'. So pervasive & broadly accepted. Your take-profit rules and stop should be dictated by your system based on maximizing EV. Not a tight stop, but the RIGHT stop." — [X post, Mar 2024](https://x.com/TheOneLanceB/status/1772277268909277312)
- [LB-direct, snippet] Same price, different EV: buying "Point A" (on the way down) "you are fighting the trend. Your probability of success is lower as a result. Your risk is potentially uncapped w no obvious stop"; the same price after the turn is with the trend and has a defined stop at the lows. — [Right side of the V thread via rattibha](https://en.rattibha.com/thread/1508815079541776397); [Thread Reader copy](https://threadreaderapp.com/thread/1546494443511062528.html)
- [Interview-paraphrase] Track rising EV over time, not P&L; a losing trade can still raise EV if the lesson is extracted ("Bobblehead"/EV curve). — [Local study notes / Trillium interview](https://www.youtube.com/watch?v=-jGUSk5lJbI)
- [LB-direct via interview, snippet] He used a notecard to plan A, B and C trades and how much to risk on each. — [Churning and Burning interview, Nov 2026](https://churningandburning.com/2026/11/churning-and-chatting-4-lance-breitstein-the-100-million-market-wizard.html)
- [Secondary] He "grades every idea before the open, then sizes up only when catalyst, level, and tape all align" (the "pocket aces" moments); below A+ gets small size or a pass. — [forex.in.rs playbook](https://www.forex.in.rs/lance-breitstein-insights/) (AI-style summary; wording not reliable)
- [Secondary] He judges capitulation quality by the size and speed of the directional move, its rate of change, and the number of consecutive days in one direction. — [Medium, "Anatomy of a Hundred Million Dollar Edge"](https://medium.com/@wernerotto/the-anatomy-of-a-hundred-million-dollar-edge-decoding-lance-breitsteins-capitulation-strategy-6ab9d059a179)
- [Interview-paraphrase, snippet] Capitulation typically shows an extremely rapid, exponential change in price over time with heavy volume and turnover. — [Chat With Traders 228 transcript summary](https://sozai.app/transcript/ultimate-day-trader-lance-breitstein/)
- [Secondary / Unverified] A community-built "Capitulation Mean Reversion" skill file scores seven variables 0-10 (Size, Speed, News, Days, Liquidations, Sentiment, Asset Class), with 20-25 = B/C+ at small-to-moderate size, under 15 = pass, and 95+ reserved for extreme waterfalls. This is a third-party reconstruction, not his document. — [skillsmp.com](https://skillsmp.com/creators/mahmoud20138/tradecraft/plugins-tradecraft-skills-capitulation-mean-reversion); [mcpmarket.com](https://mcpmarket.com/tools/skills/capitulation-mean-reversion-strategy)
- [Interview-paraphrase] Nuances that decide setup quality in his examples: an in-play stock, a real/fresh catalyst, a good daily chart, big price swings and volume. — [Local study notes / Trillium interview](https://www.youtube.com/watch?v=-jGUSk5lJbI)
- [Secondary, snippet] Core filter: "Never be long a stock steadily holding below VWAP unless it capitulates — and vice versa." Multi-timeframe alignment and trading with the trend are stressed; his biggest losses came when fighting the trend. — [TraderLion, "Simple Setup That Made Millions"](https://traderlion.com/investing-champions/lance-breitsteins-simple-setup-that-made-millions/); [videohighlight summary of the same talk](https://videohighlight.com/v/R215f4fj7V8?mediaType=youtube&language=en&summaryType=default&aiFormatted=false)
- [Interview-paraphrase] Mean reversion: the more legs a move makes in one direction, the more probable a reversal, with bigger reward for less risk. Example: fake-news drop from $50 to $5 with no bankruptcy risk, risk $3-4 for a bounce back toward $50. — [Local study notes / Trillium interview](https://www.youtube.com/watch?v=-jGUSk5lJbI)

### Inferences
- Bearing on TTWO: he would ask for an explicit EV estimate (probability the calls pay, payoff if they do, loss if not), not a verdict from win rate or R:R alone. A far-OTM call is a low-probability, high-payoff structure, which his framework permits in principle only if the probability-weighted payoff is positive.
- Bearing on TTWO: a 10% two-day drop that leaves the stock 22% off its high is modest against his capitulation descriptors (exponential rate of change, heavy turnover, many consecutive legs). On his own variables, the writer should test whether it is a true dislocation or an ordinary pullback.
- "Time of day" and "extension" as named grading variables could not be traced to him in these results; "trend", "catalyst", "in-play", "daily chart" and "VWAP side" could.

### Gaps
- No primary list from him of grading variables with weights. The 7-variable score is third-party.
- No statement found from him specifying time of day as a grading variable.
- The Schwager chapter (Market Wizards: The Next Generation, 2026) was not readable; summaries of it are secondary.

---

## 2. Bet sizing: pocket aces, exponential sizing, base hits, concentration of profit, emotional limits

### Takeaway
Size should rise steeply with setup quality: small or nothing on mediocre trades, very large on rare "pocket aces", because a small number of opportunities produce most of a year's P&L. The cap is psychological and financial survival: never so big that a failure damages your psychology, a rule he says his $2M CAR loss in 2023 taught.

### Cited Findings
- [Interview-paraphrase] "Good, want to be elite: prudent exponential bet sizing — go big on pocket aces, because most of your P&L is ~10 big trades a year (Pareto)." The figure of 10 is a paraphrase from interview notes. — [Local study notes / Trillium interview](https://www.youtube.com/watch?v=-jGUSk5lJbI); [A Retail Trader's Repository](https://retailtradersrepository.substack.com/p/lance-breitstein-trillium-interview)
- [LB-direct, snippet] "As with most trading years, huge chunks of PNL come from an exceptionally small percent of the opps." — [2023 SMB Capital takeaways, X, Jan 2024](https://x.com/TheOneLanceB/status/1745466178934550746)
- [LB-direct, snippet] Every elite trader he knows who excelled that year "did so by making 80%+ of their PNL on a select few opportunities." Applied to elite traders generally, not stated as his own figure. — [2024 SMB Capital takeaways, X, Jan 2025](https://x.com/TheOneLanceB/status/1879922774258401382)
- [LB-direct, snippet] His own H1 2024 P&L by ticker: GME 40%, SMCI 20%, AMC 15%, ARM 10%, NVDA 5%, other semis 5%, all others 5%. — [H1 '24 stats post, X, Jun 28 2024](https://x.com/TheOneLanceB/status/1806759030452621590)
- [LB-direct, snippet] "Exponential bet sizing! Always comes up! Traders made huge progress being able to go big then turn it off." — [X, Jun 2022](https://x.com/TheOneLanceB/status/1532726531541413888)
- [Interview-paraphrase, snippet] Exponential sizing is mathematically optimal if you can tell your setups apart by quality; bet more on higher-EV plays "but not so much that it negatively impacts you emotionally." — [A Retail Trader's Repository](https://retailtradersrepository.substack.com/p/lance-breitstein-trillium-interview); [Chat With Traders 236, "Exponential Bet Sizing" segment at 48:40](https://chatwithtraders.com/236)
- [LB-direct via interview, snippet] He kept a trade from ever being sized so big that, if it failed, it would ruin his psychology. — [Churning and Burning interview, Nov 2026](https://churningandburning.com/2026/11/churning-and-chatting-4-lance-breitstein-the-100-million-market-wizard.html)
- [Secondary, snippet] 2023 Avis Budget (CAR): the stock reversed, then reignited, and he lost $2 million in an hour, his biggest loss; summary lesson, "the setup wasn't wrong; his size was." — [search summary of Market Wizards: The Next Generation coverage](https://www.insta.page/market-wizards-summary); see also [timelessmarkettheory profile](https://timelessmarkettheory.com/traders/lance-breitstein)
- [LB-direct, snippet] "For most intermediate traders, the easiest way to reach the next level and elevate your game is to prudently push size in YOUR version of 'easy money trades' (the free throws / layups)." — [X, Mar 2024](https://twitter.com/TheOneLanceB/status/1774089199341236231)
- [LB-direct, snippet] He says he originated "easy money trades" at SMB; a trader needs a varied set of smaller easy-money trades to get through slow periods; no trade is literally easy; some home runs also qualify. — [X, Aug 2025](https://x.com/TheOneLanceB/status/1951667044291911877)
- [Interview-paraphrase] Bigger base hits create the cushion that lets you parlay into the big opportunities; the largest leaps come from sizing up, not from a new setup. One huge edge gives more P&L with higher variance; the biggest earners recognize pocket aces and go very big. — [Local study notes / Trillium interview](https://www.youtube.com/watch?v=-jGUSk5lJbI)
- [Interview-paraphrase] Once you have edge, outperformance comes from the psychological foundation to go big on high-EV plays and survive when one fails. — [Local study notes / Trillium interview](https://www.youtube.com/watch?v=-jGUSk5lJbI)

### Inferences
- Bearing on TTWO: sizing is a function of grade. If the trade is not an A+ on his variables, his framework says small size; long far-OTM calls cap the loss at premium, which fits "survive when one fails" only if the premium is sized so a 100% loss is tolerable.
- A long-dated lottery-style call is neither a "base hit" nor obviously "pocket aces"; the writer should place it explicitly in one bucket.

### Gaps
- No precise percentage of his own annual profit from his top N trades was found, beyond the H1 2024 ticker split.
- No formula for the "exponential" curve (e.g., size multiples per grade) was found from him.

---

## 3. The right side of the V

### Takeaway
Do not buy a falling stock until it has turned: the same price has far higher EV on the way up than on the way down, because the trend is now with you and the low gives a defined stop. He defines the turn situationally (trendline break, reclaiming VWAP, break of prior bars, moving-average break, exhaustive price/volume) and says the idea applies on every timeframe.

### Cited Findings
- [LB-direct, snippet] "THE 'RIGHT' SIDE OF THE V: such a powerful concept that many traders don't conceptually understand." — [thread via rattibha, Mar 2022](https://en.rattibha.com/thread/1508815079541776397)
- [LB-direct, snippet] "WAYS TO DEFINE CHANGE OF TREND: NOT an exhaustive list & how I'll use is situational, but here are some ideas. Breaking a trendline. Holding new side of VWAP. Break of prior bars. Break of a moving average. Capitulatory exhaustive price move OR exhaustive volume exchange." Search summary adds that he treats a stock that does not go down on bad news as a signal of trend change. — [X, Apr 2022](https://x.com/TheOneLanceB/status/1516798713271767040)
- [LB-direct, snippet] "This concept applies to every single chart and every single decision as a trader. It applies to trailing stops. It applies to system optimization. It applies to selling under resistance." Lesser traders buy higher highs then sell at the higher low; better is to hold the trend, or sell higher highs and buy back higher lows. — [Thread Reader copy, Jul 2022](https://threadreaderapp.com/thread/1546494443511062528.html)
- [LB-direct, snippet] "THE TRADING CONCEPT THAT HELPED ME RISK LESS TO MAKE MORE! The 'right side of the V' is the concept that helped put me on the map." — [X, Nov 2025](https://x.com/TheOneLanceB/status/1989689233481564629)
- [LB-direct, snippet] "CHANNEL FUNDAMENTALS: This is as important as my 'Right Side of the V' concept," used to explain his MSTR/ARKK, Nasdaq futures (Jan 2022) and GME trades. — [X, May 2022](https://x.com/TheOneLanceB/status/1526653469247029250)
- [Interview-paraphrase] "Buying the same price on the way down vs on the way up is orders-of-magnitude different EV." Examples: MARA, AVGO, REV. — [Local study notes / Trillium interview](https://www.youtube.com/watch?v=-jGUSk5lJbI)
- [Secondary, snippet] TraderLion: "The safest reversal entry is never the absolute bottom. Lance Breitstein anchors to key catalyst reference prices, aligns multiple timeframes, and waits for a countertrend pivot to confirm on the right side of the V. Let the turn prove itself first." — [TraderLion on X](https://x.com/TraderLion/status/2113722335706362205)
- [Secondary, snippet] Entry timing uses 2-minute bar highs (video chapter "How Lance times entries using 2-minute bar highs", 54:13). — [videohighlight summary](https://videohighlight.com/v/R215f4fj7V8?mediaType=youtube&language=en&summaryType=default&aiFormatted=false)
- [Secondary / Unverified] Skill-file version: enter after the lowest bar once price trades above the prior bar's high; stop at the low of the move; in extreme waterfalls buy the intra-bar reversal at much smaller size. — [skillsmp.com](https://skillsmp.com/creators/mahmoud20138/tradecraft/plugins-tradecraft-skills-capitulation-mean-reversion)
- [Secondary, snippet] Stop goes below the low of the capitulation move, the point where the idea is invalid. — [TradeZella strategy page](https://www.tradezella.com/strategies/mean-reversion-strategy)
- [Secondary, snippet] Per a research sheet on the Schwager chapter, trading without a stop is permitted only in an extreme capitulation, and he reads four patterns the same way on any bar interval. — [CTE research sheet](https://completetradersedge.com/wp-content/uploads/2026/09/CTE-Research-Sheet-Lance-Breitstein-market-wizards-next-generation.pdf)

### Inferences
- Bearing on TTWO: the entry was made after a two-day, ~10% decline, the day before a known event. The question his rule poses is whether any turn signal (break of a prior bar's high, reclaimed VWAP, trendline break, higher low) existed on the timeframe being traded at the time of purchase. If the stock was still making lower lows, this is the left side of the V by his definition.
- Since he says the concept holds on every timeframe, for a seven-month option the relevant "V" would be on the daily/weekly chart, not the intraday one.

### Gaps
- "Higher low" as his explicit definition of the turn appears only indirectly (the higher-high/higher-low language in the Jul 2022 thread). The clearest direct list is the Apr 2022 post.
- Full thread texts could not be opened.

---

## 4. Exits and trailing

### Takeaway
The best-supported rule is a mechanical trail using the prior bar's low for longs (prior bar's high for shorts), on the 2-minute chart in his intraday trading, with a predetermined exit on most trades and exits governed by EV maximization, not by "take profits" maxims. A progression from 1-minute to 5-minute to higher-timeframe bars as a trade matures, and any rule for giving back open profit, could not be traced to him.

### Cited Findings
- [LB-direct, snippet] Take-profit rules and stops "should be dictated by your system based on maximizing EV. Not a tight stop, but the RIGHT stop"; he calls "can't go broke taking profits" a fallacy. — [X, Mar 2024](https://x.com/TheOneLanceB/status/1772277268909277312)
- [LB-direct, snippet] The right-side-of-the-V premise "applies to trailing stops ... It applies to selling under resistance"; hold the trend, or sell higher highs and buy back higher lows. — [Thread Reader copy, Jul 2022](https://threadreaderapp.com/thread/1546494443511062528.html)
- [Secondary, snippet] Talk summary cites "specific rules, such as trailing stops based on two-minute bar lows", notes exceptions exist, and lists a chapter "Trailing Stops and Trend Lines". — [videohighlight summary of TraderLion talk](https://videohighlight.com/v/R215f4fj7V8?mediaType=youtube&language=en&summaryType=default&aiFormatted=false)
- [Secondary, snippet] On a short: sell trigger was the break of support, initial stop at the prior support level, trailing stop above the high of the prior two-minute bar. He "has a predetermined exit on more than nine out of ten trades" and argues the greatest edge sits in the shortest timeframes. — [trailingstoploss.com profile](https://trailingstoploss.com/traders/lance-breitstein/)
- [Secondary, snippet] He works from a two-minute intraday chart. — [CTE research sheet](https://completetradersedge.com/wp-content/uploads/2026/09/CTE-Research-Sheet-Lance-Breitstein-market-wizards-next-generation.pdf)
- [Secondary, snippet] "For long trades, a common method is trailing the stop below prior bar lows. For short trades, the stop can be trailed above prior bar highs." No timeframe given. — [TradeZella strategy page](https://www.tradezella.com/strategies/mean-reversion-strategy)
- [Secondary / Unverified] Skill file: for longs the stop moves up to the low of each new bar that holds a higher low; it claims this simple trail captured the best trade of his career. Claim not verified. — [skillsmp.com](https://skillsmp.com/creators/mahmoud20138/tradecraft/plugins-tradecraft-skills-capitulation-mean-reversion)
- [Secondary, derivative method] A trader who says he adopted the technique from Breitstein trails at the previous 5-minute bar high on shorts, then moves the remaining stop to the 5-minute 20 EMA or VWAP. This is that trader's adaptation, not Breitstein's stated rule. — [Uncharted Territory Substack](https://unchartedterritoryy.substack.com/p/the-parabolic-short)
- [Secondary, snippet] Summary sequence: "Capitulation low → wait for confirmation → enter on recovery leg → exit into strength." — [Medium, Laurentiu Chisca](https://laurentiuchisca.medium.com/the-simple-setup-that-made-lance-breitstein-millions-trend-capitulation-and-controlled-chaos-ee1ad3429954)
- [Secondary, snippet] Losses are cut when the setup fails, not when a fixed stop is hit: when price loses the level and the tape confirms, he exits on the spot. AI-style source; wording unreliable. — [forex.in.rs playbook](https://www.forex.in.rs/lance-breitstein-insights/)
- [Interview-paraphrase] Bouncy-ball short: successive lower highs against support, then the break, as a defined high-R:R entry; structure defines risk. — [Local study notes / Trillium interview](https://www.youtube.com/watch?v=-jGUSk5lJbI)

### Inferences
- The consistent logic across sources: the trailing reference is the bar structure of the trend being ridden (a long is valid while bars keep making higher lows; a break of the prior bar's low is the right side of the V in reverse). Because he says the concept is timeframe-independent, a longer trade would trail on a longer bar; this is an inference, not a quoted rule.
- His "RIGHT stop" post implies the trail should be tight enough to protect but loose enough not to cut the system's EV; he does not endorse automatic profit-taking, nor unconditional holding.
- Bearing on TTWO: his framework would require a predetermined exit before entry (he is reported to have one on 9 of 10 trades). For an option position that means a defined invalidation on the underlying chart (e.g., the low of the pre-launch selloff) and a pre-chosen trailing reference on a bar interval matched to the intended holding period, plus a plan for what to do if the launch produces a spike (sell into strength versus trail).
- Options add decay and volatility change that a bar-low trail on the stock does not capture; no source shows how he adapts the trail for long options.

### Gaps
- **Not found:** his own statement of which bar interval to trail on as a trade matures, or how the size/quality of the move sets the trailing timeframe. The 1-minute to 5-minute to higher-timeframe ladder in the brief is unconfirmed.
- **Not found:** any rule on scaling out in fractions, or on tolerable give-back of open profit.
- **Not found:** his exit detail on the QLYS, MOR, ARM, GL and TSLA reviews in the Trillium interview (page could not be opened).
- Primary sources to check: his YouTube video on the right side of the V (Nov 2025), the TraderLion talk (video ID R215f4fj7V8), his "Basics of Swing Trading" video, and the Schwager chapter.

---

## 5. Stock selection: broken slot machines, hot themes, in-play stocks, crowded events

### Takeaway
Most of the market is efficient; edge is concentrated in a few "broken slot machine" pockets, usually the year's hot themes and stocks that are in play with a fresh catalyst. No statement from him on "buy the rumor, sell the news" or on trading widely anticipated product launches was found.

### Cited Findings
- [Interview-paraphrase] A normal slot machine loses with certainty over time; certain pockets of the market are wildly inefficient and offer far better EV, the "broken slot machines". A few major themes each year produce the vast majority of gains (Pareto). "Stock selection is everything." 2024 examples: crypto, then semis, then meme/low-float names. — [Local study notes / Trillium interview](https://www.youtube.com/watch?v=-jGUSk5lJbI)
- [LB-direct, snippet] His H1 2024 P&L was concentrated in GME, SMCI, AMC, ARM and NVDA, consistent with theme concentration; he noted "less opportunities on the breaking news front." — [X, Jun 28 2024](https://x.com/TheOneLanceB/status/1806759030452621590)
- [Interview-paraphrase] Setups require an in-play stock with a fresh catalyst, big price swings and volume. — [Local study notes / Trillium interview](https://www.youtube.com/watch?v=-jGUSk5lJbI)
- [LB-direct, snippet] "THE LACK OF CAPITULATIONS AND WHAT TO DO ABOUT IT!? ... stocks haven't really been capitulating and that this makes for one of the trickiest market environments. A slow market, you sit on your hands. But an active market that…" (truncated). — [X, 2026](https://x.com/TheOneLanceB/status/2117619854307971557)
- [LB-direct, snippet] A stock failing to go down on bad news is one of his change-of-trend signals. — [X, Apr 2022](https://x.com/TheOneLanceB/status/1516798713271767040)
- [LB-direct, snippet] "Don't force trades / chase performance! Let opps come to you." — [X, Jun 2022](https://x.com/TheOneLanceB/status/1532726531541413888)
- [Secondary, snippet] He trades actively on days when a theme is driving volatility. — [Medium, "Anatomy of a Hundred Million Dollar Edge"](https://medium.com/@wernerotto/the-anatomy-of-a-hundred-million-dollar-edge-decoding-lance-breitsteins-capitulation-strategy-6ab9d059a179)

### Inferences
- Bearing on TTWO: the writer should ask whether TTWO in mid-November 2026 was a "broken slot machine" (a mispriced, emotionally driven pocket) or an efficiently priced, heavily anticipated event. His framework prizes dislocation and surprise; a launch date known for months is the opposite of breaking news.
- His reaction-to-news signal cuts both ways and is testable after the fact: a stock that cannot rally on good news is a negative tell by the mirror of his own rule (mirror reading is an inference).

### Gaps
- No commentary found from him on "buy the rumor, sell the news", on product-launch trades, or on TTWO/GTA VI specifically.
- No explicit statement found contrasting crowded scheduled events with genuine dislocations, beyond his general preference for capitulation and breaking news.

---

## 6. Options

### Takeaway
He uses options materially (39% of H1 2024 P&L), including selling them, and has said options in newly liquid names can offer better edge than stock; his best 2024 opportunity was an SMCI exhaustion gap expressed through options. His educational material stresses that implied volatility and time decay can make a correct directional call lose money. Nothing was found on him buying long-dated far-OTM calls as a position trade.

### Cited Findings
- [LB-direct, snippet] H1 2024: equities 60% of P&L, options 39%, futures 1%. "Some incredible price action trades, particularly with options." "Selling options were a HUGE amount of my pnl. I'd guess about 20%!" "My biggest misses by far were all the breakout opportunities via options." "The single best opp of the year so far was the SMCI exhaustion gap captured via options." — [X, Jun 28 2024](https://x.com/TheOneLanceB/status/1806759030452621590)
- [Interview-paraphrase] Gamma squeeze / rubber band: a stock stretched far enough snaps back with huge momentum; newly liquid options in smaller names can offer better edge than common stock (example: SMCI). — [Local study notes / Trillium interview](https://www.youtube.com/watch?v=-jGUSk5lJbI)
- [LB podcast, episode description via snippet] An options-basics episode covers calls/puts, strike, premium, expiration and leverage, and explains implied volatility, time decay, "and why direction alone doesn't guarantee an options profit." A 0DTE episode treats time decay and IV as factors that can decide a position in minutes. — [TheOneLanceB Trading Podcast](https://creators.spotify.com/pod/profile/lance-breitstein/)
- [LB-direct, summary only] An early-Nov 2026 post reportedly suggests structuring a front-side position with call options when stocks are overextended and closing weak, with his view depending on implied volatility and the day of the week. Seen only as a search summary without a URL for the specific post; treat as unverified. Nearest surfaced post: — [X](https://x.com/TheOneLanceB/status/2117619854307971557)
- [Secondary, snippet] Exhaustion gap pattern: three consecutive large up-moves on high volume, then a wide gap higher at the open on even higher volume. — [Medium, "Anatomy of a Hundred Million Dollar Edge"](https://medium.com/@wernerotto/the-anatomy-of-a-hundred-million-dollar-edge-decoding-lance-breitsteins-capitulation-strategy-6ab9d059a179)

### Inferences
- His documented options use is tactical: short-dated expressions of exhaustion/capitulation and breakouts, plus premium selling into extremes. That he earned about a fifth of a half-year's P&L from selling options suggests he is alert to when premium is rich.
- Bearing on TTWO: the points he teaches (IV, decay, direction alone not enough) are the ones to test: implied volatility the day before a marquee launch, post-event volatility contraction, and the roughly 30-32% rally needed to reach the $270 strike (roughly 36-38% to the $282.50 breakeven at expiry) from ~$204-208. The arithmetic is the note-taker's; he has not commented on this trade.

### Gaps
- No statement found on buying far-OTM calls, on LEAPS-style options for position trades, or on strike/expiry selection.
- The specific early-Nov 2026 post on calls and IV could not be opened or linked precisely.

---

## 7. Longer-timeframe and event trades

### Takeaway
He now swing trades and has published a "Basics of Swing Trading" video describing two main strategies, but its content could not be read. He states his core concepts apply on every chart and timeframe. No primary material was found on multi-month position trades or on earnings/product-launch event trades.

### Cited Findings
- [LB-direct, snippet] "BASICS OF SWING TRADING: In this video I discuss the pros and cons, biggest pitfalls, and the 2 main strategies I utilize when swing trading." — [X, 2026](https://x.com/TheOneLanceB/status/2059643962554724770)
- [LB podcast description, snippet] "After years of intense intraday trading destroying my health, I switched to swing trading so I could capture big opportunities without being glued to screens all day." Episode covers mistakes made moving from day trading to swing trading. — [TheOneLanceB Trading Podcast](https://creators.spotify.com/pod/profile/lance-breitstein/)
- [LB-direct, snippet] About 10% of his 2024 H1 P&L came from GME overnight trades. — [X, Jun 28 2024](https://x.com/TheOneLanceB/status/1806759030452621590)
- [LB-direct, snippet] The right-side-of-the-V premise "applies to every single chart and every single decision as a trader." — [Thread Reader copy, Jul 2022](https://threadreaderapp.com/thread/1546494443511062528.html)
- [Secondary, snippet] He reads his four patterns the same way on any bar interval. — [CTE research sheet](https://completetradersedge.com/wp-content/uploads/2026/09/CTE-Research-Sheet-Lance-Breitstein-market-wizards-next-generation.pdf)
- [Secondary, snippet] Counterpoint: he is reported to argue the greatest edge sits in the shortest timeframes. — [trailingstoploss.com profile](https://trailingstoploss.com/traders/lance-breitstein/)
- [Secondary, snippet] Multi-day measures matter to him: number of consecutive days in one direction, daily-chart context, multi-timeframe alignment (daily, 15-minute, 5-minute). — [Medium, "Anatomy of a Hundred Million Dollar Edge"](https://medium.com/@wernerotto/the-anatomy-of-a-hundred-million-dollar-edge-decoding-lance-breitsteins-capitulation-strategy-6ab9d059a179); [Medium, Laurentiu Chisca](https://laurentiuchisca.medium.com/the-simple-setup-that-made-lance-breitstein-millions-trend-capitulation-and-controlled-chaos-ee1ad3429954)

### Inferences
- His frameworks are portable to a daily chart by his own statement, so a seven-month trade can be judged with them, but his track record and stated edge are in short-horizon trades; applying his view to a multi-month option hold is extrapolation and should be labelled so.

### Gaps
- The two swing strategies in his 2026 video are unknown here.
- Nothing found on his holding periods for swings, or on trading into scheduled events (earnings, launches).

---

## 8. Review process: Daily Report Card, the "one thing", process over outcome

### Takeaway
He filled in a Daily Report Card every evening, focused on the single improvement that would most move his trading, and stayed on it until fixed. He judges progress by whether EV is rising, not by a trade's P&L, and says knowing a bias is not enough: you need a process that protects you from it.

### Cited Findings
- [Interview-paraphrase] DRC filled "every single evening, no excuses"; it focuses on ONE area and stays there until it improves: "what is the one thing that, if I improved, would most move my trading?" Then pick the next. Make the template your own. — [Local study notes / Trillium interview](https://www.youtube.com/watch?v=-jGUSk5lJbI)
- [LB-direct, snippet] "Consciousness of bad habits is first step to resolve it. DRC helps spot ahead of time." — [X, Jun 2022](https://x.com/TheOneLanceB/status/1532726531541413888)
- [Interview-paraphrase] The biggest mistake is getting frustrated at an error instead of learning; the worst days hold the most to gain; the fastest improvers learn a lesson the first time they see it. — [Local study notes / Trillium interview](https://www.youtube.com/watch?v=-jGUSk5lJbI)
- [Interview-paraphrase] Awareness alone does not remove a bias; build a process that protects you and iterate. FOMO is usually comparison to other traders, not judgment of your own trade. "The Gap and the Gain": measure against where you started. — [Local study notes / Trillium interview](https://www.youtube.com/watch?v=-jGUSk5lJbI)
- [LB-direct, snippet] "Trust the process and focus on getting better every day"; early on he "hesitated on entries, chased moves"; a 2013 breakthrough came from a small playbook of simple, repeatable setups with defined risk. — [15 Years of Trading Advice, X, Dec 2025](https://x.com/TheOneLanceB/status/2006443060159475980)
- [LB-direct, snippet] On reviewing a system's statistics: 448 trades is likely to be statistically significant; no ideal number because it depends on the strategy's variance, "but more always" better. — [X, Apr 2024](https://x.com/TheOneLanceB/status/1777371974739595774)
- [LB-direct, snippet] He declines to hand out trade answers because "everyone needs to put the deep work in to derive what the right answer is for THEM" and "Concepts = Timeless. Markets = Changing." — [X, Oct 2022](https://x.com/TheOneLanceB/status/1577301907265175553)

### Inferences
- Bearing on TTWO: a review in his style would grade the decision at entry (was EV estimated, was the grade honest, was the turn confirmed, was size matched to grade, was the exit predetermined), record it whatever the options later did, and extract one process change. A single trade is one sample of a high-variance structure; his emphasis on sample size argues against judging it by outcome.

### Gaps
- His actual DRC template was not found.
- No direct quote found using the phrase "process over outcome"; the idea is expressed through the EV-over-P&L framing.

---

## Sources attempted but not opened (for the report writer's awareness)
All of the following were found by search but could not be fetched; the session's network settings would need to allow them: chatwithtraders.com (episodes 228, 232/233, 236), traderlion.com, retailtradersrepository.substack.com, threadreaderapp.com, theonelanceb.com, tradezella.com, completetradersedge.com, sozai.app, skillsmp.com. X posts were seen only as search snippets. Jack Schwager's *Market Wizards: The Next Generation* (2026), which reportedly has a Breitstein chapter, was not read; all references to it are via secondary summaries, several of which read as AI-generated.
