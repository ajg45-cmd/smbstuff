"""Write fake Gr8Trade exports so the loader and runner can be exercised.

Synthetic. It proves the pipeline runs end to end and that the VWAP
reconciliation catches a platform whose VWAP includes premarket -- exactly the
divergence that would otherwise silently invalidate every touch.

    python3 tests/make_fake_export.py <out_dir>
"""
import os, sys
import numpy as np
import pandas as pd
from synth import build, F


def path_fn(after, gap):
    def p(m):
        b = 100 + gap
        if m < 570: return b + 1.5 * (m - 240) / 330, 45_000
        if m < 615: return b + 1.5 + 4.0 * (m - 570) / 45, 700_000
        if m < 652: return b + 5.5 - 2.3 * (m - 615) / 37, 150_000
        if m < 660: return b + 3.2 + 1.4 * (m - 652) / 8, 550_000
        if m < 680: return b + 4.6 + 1.9 * (m - 660) / 20, 450_000
        if m < 697: return b + 6.5 - 2.6 * (m - 680) / 17, 140_000
        if m < 705: return b + 3.9 + 1.5 * (m - 697) / 8, 500_000
        return b + 5.4 + after * (m - 705) / 255, 250_000
    return p


def write(out_dir, symbol, day, b1, vwap_includes_premarket):
    df = b1.copy()
    if vwap_includes_premarket:
        # the divergent case: VWAP anchored at 04:00 rather than 09:30
        tp = (df["high"] + df["low"] + df["close"]) / 3
        pv = (tp * df["volume"]).cumsum() / df["volume"].cumsum()
        df["platform_vwap"] = pv
    else:
        df["platform_vwap"] = F.session_vwap(b1).reindex(df.index)
    df["symbol"] = symbol
    df["cum_volume"] = F.rth(df)["volume"].cumsum().reindex(df.index).fillna(0)
    df["bid"] = (df["close"] - 0.01).round(2)
    df["ask"] = (df["close"] + 0.01).round(2)
    hm = df.index.hour * 60 + df.index.minute
    df["session"] = np.where(hm < 570, "pre", np.where(hm < 960, "regular", "post"))
    df = df.reset_index().rename(columns={"index": "timestamp"})
    df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    cols = ["timestamp", "symbol", "open", "high", "low", "close", "volume",
            "platform_vwap", "cum_volume", "bid", "ask", "session"]
    df[cols].to_csv(os.path.join(out_dir, f"{symbol}_{day.replace('-','')}.csv"),
                    index=False)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "data/fake_export"
    os.makedirs(out, exist_ok=True)
    rng = np.random.default_rng(7)
    n, ev_rows = 0, []
    for sym, diverge in (("AAA", False), ("BBB", True)):
        for i in range(16):
            day = f"2024-03-{4 + i:02d}"
            # guidance is made GENUINELY predictive here, so the ladder can be
            # checked for detecting a real effect -- while the other gates stay
            # uninformative, so it can be checked for NOT crediting those.
            raised = bool(rng.random() < 0.5)
            after = float(rng.choice([7, 5, 4] if raised else [1, 0, -3]))
            gap = float(rng.uniform(-2, 4))
            b1, _ = build(path_fn(after, gap=gap), day=day,
                          seed=100 + i, noise=0.03)
            write(out, sym, day, b1, diverge)
            ev_rows.append({"symbol": sym, "date": day,
                            "guidance": "raise" if raised else "maintain",
                            "surprise_pct": round(float(rng.uniform(0, 20)), 1),
                            "notes": ""})
            n += 1
    pd.DataFrame(ev_rows).to_csv(os.path.join(out, "events.csv"), index=False)
    print(f"wrote {n} session files + events.csv to {out}/\n"
          f"  BBB's platform VWAP deliberately includes premarket\n"
          f"  guidance=raise is deliberately predictive; the other gates are not")
