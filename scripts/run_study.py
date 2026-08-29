#!/usr/bin/env python3
"""End to end: Gr8Trade exports in, exit leaderboard and filter ladder out.

    python3 scripts/run_study.py data/samples --out results

Order of business, deliberately:
  1. VWAP reconciliation -- if the study's line is not the one on your screen,
     nothing downstream is worth reading.
  2. Session VWAP vs Day VWAP, including how much the two even agree.
  3. The filter ladder -- does clean price action move EV, or just shrink n?
  4. The exit leaderboard, against the do-nothing benchmark.
  5. The universe report for the winner.
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from midday_reset import io_gr8, v1, ablation                    # noqa: E402
from midday_reset.features import volume_baseline, rth, forward_labels  # noqa: E402
from midday_reset.exits import (rule_grid, score_trade,          # noqa: E402
                                leaderboard, universe_report)

BENCH = "exit_hold_to_close@15m"
ALL_FRAMES = ("2m", "5m", "10m", "15m")
ANCHORS = ("rth", "day")
FMT = lambda x: f"{x:7.3f}"


def load_events(directory):
    """Optional per-event attributes -- guidance is the one being tested."""
    for name in ("events.csv", "_events.csv"):
        p = os.path.join(directory, name)
        if os.path.exists(p):
            ev = pd.read_csv(p)
            ev["date"] = pd.to_datetime(ev["date"]).dt.date
            return {(r["symbol"], r["date"]): r.to_dict()
                    for _, r in ev.iterrows()}
    return {}


def continuous(sessions, symbol):
    """One continuous RTH series per frame, across every session of a symbol.

    EMAs must come from this, not from a single session: a 21-period EMA on
    15-minute bars needs over five hours, so a session-only EMA21 at 10:00 has
    seen two bars and is not the line on your chart.
    """
    parts = [rth(df) for (s, _), df in sorted(sessions.items(), key=lambda kv: kv[0][1])
             if s == symbol]
    if not parts:
        return {}
    one = pd.concat(parts).sort_index()
    one = one[~one.index.duplicated(keep="last")]
    return {f: one.resample(f.replace("m", "min")).agg(
                {"open": "first", "high": "max", "low": "min",
                 "close": "last", "volume": "sum"}).dropna()
            for f in ALL_FRAMES}


def main(directory, out_dir, entry_frames=v1.ENTRY_FRAMES,
         sides=("long", "short"), anchors=ANCHORS):
    sessions = io_gr8.load_dir(directory)
    if not sessions:
        print(f"no usable CSVs in {directory}")
        return 1
    symbols = sorted({s for s, _ in sessions})
    events = load_events(directory)
    print(f"{len(sessions)} sessions, {len(symbols)} symbols: {', '.join(symbols)}")
    print(f"event attributes for {len(events)} symbol-days"
          f"{' (none -- guidance will read unknown)' if not events else ''}\n")

    atr_by = {s: io_gr8.daily_atr_from_sessions(sessions, s) for s in symbols}
    cont_by = {s: continuous(sessions, s) for s in symbols}
    prev_close = {}
    for sym in symbols:
        days = sorted(d for s, d in sessions if s == sym)
        for a, b in zip(days, days[1:]):
            r = rth(sessions[(sym, a)])
            if not r.empty:
                prev_close[(sym, b)] = float(r["close"].iloc[-1])

    rules = rule_grid(entry_frames)
    rows, recon = [], []

    for (sym, day), b1 in sorted(sessions.items(), key=lambda kv: kv[0][1]):
        atr_d = float(atr_by[sym].get(day, float("nan")))
        if pd.isna(atr_d) or atr_d <= 0:
            continue
        recon.append({"symbol": sym, "date": day,
                      **io_gr8.reconcile_vwap(b1, atr_d)})

        today = {f: c[c.index.date == day] for f, c in cont_by[sym].items()}
        cont = {f: c[c.index.date <= day] for f, c in cont_by[sym].items()}
        hist = pd.concat([d for (s2, d2), d in sessions.items()
                          if s2 == sym and d2 < day] or [b1])

        ctx = v1.SessionCtx(symbol=sym, date=day, bars_1m=b1, frames=today,
                            cont=cont, atr_d=atr_d,
                            baseline=volume_baseline(hist),
                            prev_close=prev_close.get((sym, day)),
                            event=events.get((sym, day), {}))

        for f in entry_frames:
            for side in sides:
                for anchor in anchors:
                    for sig in v1.find_signals(ctx, side=side, frame=f,
                                               vwap_anchor=anchor,
                                               require_trend=False,
                                               require_pm_break=False,
                                               require_ema_gate=False):
                        # gates OFF at scan time so the ladder can price each
                        # one; every gate is recorded as a column instead.
                        entry_time = sig.bar_time + pd.Timedelta(
                            minutes=int(f.rstrip("m")))
                        row = dict(vars(sig))
                        row["day_symbol"] = f"{sym}_{day}"
                        row.update(forward_labels(b1, entry_time,
                                                  sig.entry_close, sig.stop,
                                                  side=side))
                        row.update(score_trade(today, ctx.vwap(anchor),
                                               entry_time, sig.entry_close,
                                               sig.stop, side, rules))
                        rows.append(row)

    rec = pd.DataFrame(recon)
    print("1. VWAP RECONCILIATION (computed vs the platform's own)")
    if not rec.empty and "max_diff_cents" in rec and rec["max_diff_cents"].notna().any():
        print(f"   sessions compared {int(rec['max_diff_cents'].notna().sum())}   "
              f"median {rec['median_diff_cents'].median():.2f}c   "
              f"worst {rec['max_diff_cents'].max():.2f}c")
        if not rec["matched"].fillna(True).all():
            print("   *** DIVERGES. platform_vwap is being used; investigate ***")
    else:
        print("   no platform_vwap column -- computed VWAP used, UNVERIFIED")

    if not rows:
        print("\nno signals. Check that premarket rows are present, or widen "
              "the window / relax the trend gate.")
        return 0

    df = pd.DataFrame(rows)
    os.makedirs(out_dir, exist_ok=True)
    df.to_csv(os.path.join(out_dir, "signals.csv"), index=False)
    outcome = BENCH if BENCH in df else "ret_eod_R"

    print(f"\n   {len(df)} signals / {df['day_symbol'].nunique()} day-symbols "
          f"/ {df['is_first_of_day'].sum()} first-of-day")

    print("\n2. SESSION VWAP vs DAY VWAP")
    ac = ablation.anchor_comparison(df, outcome)
    if not ac.empty:
        print(ac.to_string(index=False, float_format=FMT))
        ov = ac.attrs.get("overlap")
        if ov is not None and not np.isnan(ov):
            print(f"   signal overlap: {ov:.0%} — below ~70% these are two "
                  f"different strategies, not one with a cosmetic difference")
        ac.to_csv(os.path.join(out_dir, "vwap_anchor.csv"), index=False)

    print("\n3. FILTER LADDER — does clean price action move EV, or shrink n?")
    for anchor in anchors:
        sub = df[df["vwap_anchor"] == anchor]
        if len(sub) < 20:
            continue
        lad = ablation.filter_ladder(sub, outcome, ablation.LADDER_ORDER,
                                     ablation.STANDARD_FILTERS)
        lad.to_csv(os.path.join(out_dir, f"ladder_{anchor}.csv"), index=False)
        print(f"\n   anchor = {anchor}")
        print(lad.to_string(index=False, float_format=FMT))

    print("\n   each filter alone (lift_within_trend strips out "
          "'trends trend'; p_random_beats is the same-size random control)")
    sf = ablation.single_filters(df, outcome, ablation.STANDARD_FILTERS)
    sf.to_csv(os.path.join(out_dir, "single_filters.csv"), index=False)
    print(sf.to_string(index=False, float_format=FMT))

    print("\n4. EXIT LEADERBOARD (benchmark: %s)" % BENCH)
    for label, sub in (("all signals", df),
                       ("gated + first-of-day", df[
                           df["beyond_pm_range"].fillna(False)
                           & df["beyond_all_emas"].fillna(False)
                           & df["emas_upsloping"].fillna(False)
                           & df["is_first_of_day"]])):
        if len(sub) < 10:
            print(f"\n   {label}: n={len(sub)}, too few to rank")
            continue
        lb = leaderboard(sub, benchmark=BENCH, n_boot=800)
        lb.to_csv(os.path.join(out_dir,
                               f"leaderboard_{label.split()[0]}.csv"), index=False)
        cols = ["rule", "n", "mean_R", "win_rate", "pct_mfe_captured",
                "vs_benchmark_R", "ci95_low", "ci95_high"]
        print(f"\n   {label} (n={len(sub)}) — top 8")
        print(lb[cols].head(8).to_string(index=False, float_format=FMT))

    best = "exit_" + leaderboard(df, benchmark=BENCH, n_boot=200).iloc[0]["rule"]
    ur = universe_report(df, best, benchmark=BENCH)
    ur.to_csv(os.path.join(out_dir, "universe.csv"), index=False)
    print(f"\n5. UNIVERSE REPORT — {best}")
    print(ur.to_string(index=False, float_format=FMT))
    print(f"\nwritten to {out_dir}/")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("directory")
    ap.add_argument("--out", default="results")
    a = ap.parse_args()
    raise SystemExit(main(a.directory, a.out))
