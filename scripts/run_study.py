#!/usr/bin/env python3
"""End to end: Gr8Trade exports in, exit leaderboard out.

    python3 scripts/run_study.py data/gr8_export [--out results]

Every number it prints carries its sample size, and the VWAP reconciliation
runs first -- if the study's VWAP is not the line that was on the screen,
nothing downstream is worth reading.
"""
import argparse
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from midday_reset import io_gr8, v1                      # noqa: E402
from midday_reset.features import volume_baseline        # noqa: E402
from midday_reset.exits import (rule_grid, score_trade,  # noqa: E402
                                leaderboard, universe_report)
from midday_reset.features import forward_labels         # noqa: E402

BENCH = "exit_hold_to_close@15m"


def main(directory, out_dir, frames_wanted=("5m", "15m"), sides=("long", "short")):
    sessions = io_gr8.load_dir(directory)
    if not sessions:
        print(f"no usable CSVs in {directory}")
        return 1
    symbols = sorted({s for s, _ in sessions})
    print(f"{len(sessions)} sessions, {len(symbols)} symbols: {', '.join(symbols)}\n")

    atr_by_symbol = {s: io_gr8.daily_atr_from_sessions(sessions, s) for s in symbols}
    rules = rule_grid(frames_wanted)
    rows, recon = [], []

    for (sym, day), b1 in sorted(sessions.items(), key=lambda kv: kv[0][1]):
        atr_series = atr_by_symbol.get(sym, pd.Series(dtype=float))
        atr_d = float(atr_series.get(day, float("nan")))
        if pd.isna(atr_d) or atr_d <= 0:
            continue                                   # needs prior sessions

        r = io_gr8.reconcile_vwap(b1, atr_d)
        recon.append({"symbol": sym, "date": day, **r})

        fr = io_gr8.frames(b1, frames_wanted)
        vw = io_gr8.vwap_for(b1)
        # prior sessions of the same name, for the clock baseline
        hist = pd.concat([d for (s2, d2), d in sessions.items()
                          if s2 == sym and d2 < day] or [b1])
        base = volume_baseline(hist)

        for f, bars in fr.items():
            for side in sides:
                for sig in v1.find_signals(sym, b1, bars, atr_d, base,
                                           side=side, frame=f):
                    entry_time = sig.bar_time + pd.Timedelta(minutes=int(f.rstrip("m")))
                    row = dict(vars(sig))
                    row["day_symbol"] = f"{sym}_{day}"
                    row.update(forward_labels(b1, entry_time, sig.entry_close,
                                              sig.stop, side=side))
                    row.update(score_trade(fr, vw, entry_time, sig.entry_close,
                                           sig.stop, side, rules))
                    rows.append(row)

    rec = pd.DataFrame(recon)
    print("VWAP RECONCILIATION")
    if not rec.empty and "max_diff_cents" in rec:
        print(f"  sessions compared : {rec['max_diff_cents'].notna().sum()}")
        print(f"  median difference : {rec['median_diff_cents'].median():.2f} cents")
        print(f"  worst difference  : {rec['max_diff_cents'].max():.2f} cents")
        if rec["matched"].notna().any() and not rec["matched"].fillna(True).all():
            print("  *** DIVERGES from the platform. Using platform_vwap where")
            print("      present; investigate before trusting any touch. ***")
    else:
        print("  no platform_vwap in the exports -- computed VWAP used, unverified")
    print()

    if not rows:
        print("no signals. Widen the window, relax the trend gate, or check "
              "that premarket rows are present in the exports.")
        return 0

    df = pd.DataFrame(rows)
    os.makedirs(out_dir, exist_ok=True)
    df.to_csv(os.path.join(out_dir, "signals.csv"), index=False)

    first = df[df["is_first_of_day"]]
    print(f"{len(df)} signals over {df['day_symbol'].nunique()} day-symbol "
          f"clusters ({len(first)} first-of-day, the traded population)")
    print(f"  liquid (>= {v1.MIN_CUM_SHARES:,} sh at entry): "
          f"{int(df['liquid'].sum())}")
    for side in sides:
        n = int((df["side"] == side).sum())
        if n:
            m = df.loc[df["side"] == side, "ret_eod_R"].mean()
            print(f"  {side:5s}: n={n:4d}   mean end-of-day {m:+.3f}R")
    print()

    for label, sub in (("ALL SIGNALS", df), ("FIRST OF DAY ONLY", first)):
        if len(sub) < 10:
            continue
        lb = leaderboard(sub, benchmark=BENCH, n_boot=1000)
        lb.to_csv(os.path.join(out_dir, f"leaderboard_{label.split()[0].lower()}.csv"),
                  index=False)
        cols = ["rule", "n", "mean_R", "median_R", "win_rate", "pct_mfe_captured",
                "vs_benchmark_R", "ci95_low", "ci95_high", "top_reason"]
        print(f"{label} — top 10 by mean R")
        print(lb[cols].head(10).to_string(index=False,
                                          float_format=lambda x: f"{x:7.3f}"))
        print(f"  benchmark: {BENCH}   "
              f"(a rule whose ci95_low is above 0 beat it)\n")

    best_rule = "exit_" + leaderboard(df, benchmark=BENCH, n_boot=200).iloc[0]["rule"]
    ur = universe_report(df, best_rule, benchmark=BENCH)
    ur.to_csv(os.path.join(out_dir, "universe.csv"), index=False)
    print(f"UNIVERSE REPORT — {best_rule}")
    print(ur.to_string(index=False, float_format=lambda x: f"{x:7.3f}"))
    print(f"\nwritten to {out_dir}/")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("directory")
    ap.add_argument("--out", default="results")
    a = ap.parse_args()
    raise SystemExit(main(a.directory, a.out))
