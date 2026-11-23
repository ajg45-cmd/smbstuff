# 10 — First green day on the backside of low-float runners

Side study, separate from the midday-reset exit work. Daily bars only.

- Code: `src/first_green_day/` (`fetch.py` → `study.py` → `summarize.py`); definitions are in the `study.py` docstring.
- Every event: `results/fgd_events.csv` (623 events, 260 symbols, 2019–2026).

```
cd src/first_green_day
python3 fetch.py ../../data/fgd/bars
python3 study.py ../../data/fgd/bars ../../results/fgd_events.csv
python3 summarize.py ../../results/fgd_events.csv
```

## What this sample is and is not

- The symbol list (`seed_tickers.py`) was written from memory, not a screener.
  The detector decides objectively whether each name ran, but the names checked
  skew famous.
- 119 of 436 seed names are delisted and missing from Yahoo. Names that went to
  zero are the ones missing, so bounce numbers here are flattered.
- Float is **not** verified. No float data source was reachable.
- Daily bars cannot order the high and low within a session, so nothing here
  says whether a stop or a target was hit first on the break day.

## Headline (medians)

| | |
|---|---|
| First green day: high vs prior close | +13.7% (4.9% of the rally) |
| First green day: close vs prior close | +6.8% (2.5% of the rally) |
| Close location in the day's range | 67% |
| Breaks its high next day / within 5 days | 42% / 65% |
| After the break, best price within 1 / 5 / 10 days | +4.8% / +11.6% / +15.5% |
| After the break, close 1 / 5 / 10 days later | −1.9% / −7.9% / −12.9% |
| Break day closes above entry | 34% |
| Trades below the first green day's low within 5 days | 48% |
