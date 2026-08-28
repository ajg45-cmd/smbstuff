# Drop exported sessions here

One CSV per symbol per session, named `SYMBOL_YYYYMMDD.csv`, written by
`gr8script/export_bars.py`.

Committing a handful here is the simplest way to hand me real data — I can read
this repo, so anything committed to `data/samples/` I can run the study against
immediately. Keep it to a sample; bulk history belongs outside git (everything
else under `data/` is ignored).

## Required columns

`timestamp, open, high, low, close, volume`

Timestamps in US/Eastern, one row per minute, **including premarket** — the
touch tolerance and several enhancers depend on the premarket rows being there.

## Strongly wanted

`platform_vwap` — Gr8Trade's own session VWAP. With it, every VWAP touch in the
study is measured against the line that was actually on your screen, and
`run_study.py` reports how far the computed VWAP sits from it. Without it the
study computes its own and the reconciliation is skipped, unverified.

Also useful, not required: `symbol, cum_volume, bid, ask, session`.

## Then

```
python3 scripts/run_study.py data/samples --out results
```
