"""Contract test for the exit lab: score every rule on the same trades.

Six hand-built sessions with different post-entry behavior -- runners, faders,
and one that stops out -- so the leaderboard has something to separate. These
are synthetic: the ranking below demonstrates that the machinery works. It is
NOT evidence about any exit rule.

Run: python3 tests/test_exit_lab.py
"""
import numpy as np
import pandas as pd
from synth import build, flat_baseline, F
from midday_reset import v1
from test_vwap_rejection import make_ctx  # noqa: F401  (shared ctx builder)
from midday_reset.exits import rule_grid, score_trade, leaderboard, universe_report

ATR_D = 3.0
BENCH = "exit_hold_to_close@15m"


def path_factory(after):
    """Identical setup, different continuation -- `after` is the post-entry drift."""
    def path(m):
        if m < 570: return 100 + 1.5 * (m - 240) / 330, 900
        if m < 615: return 101.5 + 4.0 * (m - 570) / 45, 14000
        if m < 652: return 105.5 - 2.3 * (m - 615) / 37, 3000
        if m < 660: return 103.2 + 1.4 * (m - 652) / 8, 11000
        if m < 680: return 104.6 + 1.9 * (m - 660) / 20, 9000
        if m < 697: return 106.5 - 2.6 * (m - 680) / 17, 2800
        if m < 705: return 103.9 + 1.5 * (m - 697) / 8, 10000
        return 105.4 + after * (m - 705) / 255, 5000
    return path


def frames(b1):
    return {f: F.rth(b1).resample(f.replace("m", "min")).agg(
                {"open": "first", "high": "max", "low": "min",
                 "close": "last", "volume": "sum"}).dropna()
            for f in ("2m", "5m", "10m", "15m")}


if __name__ == "__main__":
    rules = rule_grid(("5m", "10m", "15m"))
    rows = []
    for i, after in enumerate([6.0, 4.0, 2.0, 0.0, -2.5, -5.0]):
        day = f"2024-03-{5 + i:02d}"
        b1, _ = build(path_factory(after), day=day, seed=10 + i)
        fr = frames(b1)
        base = flat_baseline(b1)
        vw = F.session_vwap(b1)

        cont = {k: v for k, v in fr.items()}
        ctx = v1.SessionCtx(symbol=f"SYN{i}", date=b1.index[0].date(),
                            bars_1m=b1, frames=fr, cont=cont, atr_d=ATR_D,
                            baseline=base, event={"guidance": "raise"})
        for f in fr:
            sigs = v1.find_signals(ctx, side="long", frame=f,
                                   require_trend=False, require_pm_break=False,
                                   require_ema_gate=False)
            for s in sigs:
                entry_time = s.bar_time + pd.Timedelta(minutes=int(f.rstrip("m")))
                row = dict(vars(s))
                row["day_symbol"] = f"SYN{i}_{day}"
                row.update(F.forward_labels(b1, entry_time, s.entry_close,
                                            s.stop, side=s.side))
                row.update(score_trade(fr, vw, entry_time, s.entry_close,
                                       s.stop, s.side, rules))
                rows.append(row)

    df = pd.DataFrame(rows)
    print(f"{len(df)} trades from {df.day_symbol.nunique()} day-symbol clusters, "
          f"{len([c for c in df if c.startswith('exit_')])} exit rules scored\n")

    lb = leaderboard(df, benchmark=BENCH, n_boot=400)
    show = ["rule", "n", "mean_R", "median_R", "win_rate", "p90_R",
            "pct_mfe_captured", "vs_benchmark_R", "top_reason"]
    print("TOP 12 (synthetic -- mechanism demo, not evidence)")
    print(lb[show].head(12).to_string(index=False, float_format=lambda x: f"{x:7.3f}"))
    print("\nBOTTOM 5")
    print(lb[show].tail(5).to_string(index=False, float_format=lambda x: f"{x:7.3f}"))

    best = "exit_" + lb.iloc[0]["rule"]
    print(f"\nUNIVERSE REPORT for {best}")
    print(universe_report(df, best, benchmark=BENCH, min_n=2)
          .to_string(index=False, float_format=lambda x: f"{x:7.3f}"))

    # --- contract assertions -------------------------------------------------
    assert len(df) >= 6, "expected trades from several sessions"
    assert BENCH in df.columns, "the do-nothing benchmark must always be scored"

    for c in [c for c in df.columns if c.startswith("exit_")]:
        v = df[c].dropna()
        assert (v >= -1.0001).all(), f"{c} lost more than 1R past its stop"

    for t in (1, 2, 3, 4):
        for f in ("5m", "15m"):
            col, why = f"exit_target_{t}R@{f}", f"why_target_{t}R@{f}"
            hit = df[df[why] == "target"][col]
            assert hit.empty or np.allclose(hit, float(t)), \
                f"{col} must realize exactly {t}R when the target is what fired"

    pair = df[["exit_ema9@5m", "exit_ema9@15m"]].dropna()
    print(f"\nema9 on 5m vs 15m, same trades: "
          f"{pair['exit_ema9@5m'].mean():.3f}R vs {pair['exit_ema9@15m'].mean():.3f}R")

    assert lb["ci95_low"].notna().any(), "clustered intervals must compute"
    assert (lb.loc[lb["rule"] == BENCH.replace("exit_", ""),
                   "vs_benchmark_R"].abs() < 1e-9).all(), \
        "the benchmark must score zero against itself"
    print("\nOK - all assertions passed")
