"""Load Gr8Trade exports, and reconcile their VWAP against ours.

The reconciliation is the important part. If the study's VWAP is not the line
that was on the screen, every touch is measured against the wrong level and the
result answers a question nobody asked. When the export carries a
`platform_vwap` column, that column wins and ours is only a cross-check.
"""

from __future__ import annotations

import glob
import os

import numpy as np
import pandas as pd

from .features import TZ, rth, session_vwap

REQUIRED = ["timestamp", "open", "high", "low", "close", "volume"]


def load_session_csv(path: str) -> pd.DataFrame:
    """One symbol, one session, 1-minute bars including premarket."""
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"{os.path.basename(path)}: missing columns {missing}")

    ts = pd.to_datetime(df["timestamp"], errors="coerce")
    if ts.isna().any():
        raise ValueError(f"{os.path.basename(path)}: unparseable timestamps")
    ts = ts.dt.tz_localize(TZ) if ts.dt.tz is None else ts.dt.tz_convert(TZ)
    df = df.set_index(ts).sort_index()
    df = df[~df.index.duplicated(keep="last")]

    for c in ["open", "high", "low", "close", "volume", "platform_vwap"]:
        if c in df:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    bad = df[(df["high"] < df["low"])
             | (df["high"] < df[["open", "close"]].max(axis=1))
             | (df["low"] > df[["open", "close"]].min(axis=1))]
    if len(bad):
        raise ValueError(f"{os.path.basename(path)}: {len(bad)} malformed bars")
    return df


def reconcile_vwap(bars_1m: pd.DataFrame, atr_d: float | None = None) -> dict:
    """How far our computed VWAP sits from the platform's.

    Reported in cents and in ATR, because a two-cent gap on a $300 name is
    noise and a two-cent gap on a $6 name is the whole tolerance.
    """
    if "platform_vwap" not in bars_1m or bars_1m["platform_vwap"].isna().all():
        return {"status": "no platform_vwap column -- using computed VWAP",
                "matched": None}
    ours = session_vwap(bars_1m)
    theirs = bars_1m["platform_vwap"].reindex(ours.index).dropna()
    if theirs.empty:
        return {"status": "platform_vwap present but empty in RTH", "matched": None}
    d = (ours.reindex(theirs.index) - theirs).abs()
    out = {
        "status": "compared",
        "n": int(d.size),
        "median_diff_cents": float(d.median() * 100),
        "p95_diff_cents": float(d.quantile(.95) * 100),
        "max_diff_cents": float(d.max() * 100),
    }
    if atr_d:
        out["max_diff_atr"] = float(d.max() / atr_d)
        out["matched"] = bool(d.max() / atr_d < 0.02)
    else:
        out["matched"] = bool(d.max() < 0.02)
    return out


def frames(bars_1m: pd.DataFrame, sizes=("5m", "15m")) -> dict[str, pd.DataFrame]:
    """Resample regular-hours 1-min bars to the study's structure frames."""
    r = rth(bars_1m)
    return {s: r.resample(s.replace("m", "min")).agg(
        {"open": "first", "high": "max", "low": "min",
         "close": "last", "volume": "sum"}).dropna() for s in sizes}


def vwap_for(bars_1m: pd.DataFrame) -> pd.Series:
    """The platform's VWAP when the export carries it, ours otherwise."""
    if "platform_vwap" in bars_1m and bars_1m["platform_vwap"].notna().any():
        return rth(bars_1m)["platform_vwap"].ffill().rename("vwap")
    return session_vwap(bars_1m)


def load_dir(directory: str) -> dict[tuple[str, object], pd.DataFrame]:
    """Every `SYMBOL_YYYYMMDD.csv` in a directory, keyed by (symbol, date)."""
    out: dict[tuple[str, object], pd.DataFrame] = {}
    for p in sorted(glob.glob(os.path.join(directory, "*.csv"))):
        stem = os.path.basename(p).rsplit(".", 1)[0]
        sym = stem.split("_")[0]
        try:
            df = load_session_csv(p)
        except ValueError as e:
            print(f"  skipped {os.path.basename(p)}: {e}")
            continue
        if "symbol" in df and df["symbol"].notna().any():
            sym = str(df["symbol"].iloc[0])
        out[(sym, df.index[0].date())] = df
    return out


def daily_atr_from_sessions(sessions: dict, symbol: str, n: int = 14) -> pd.Series:
    """Build a daily ATR series from the exported 1-min sessions themselves.

    Enough to run the study off nothing but the exports. Replace it with real
    daily bars once they are available -- 14 sessions of intraday-derived
    ranges is a rough ATR, and it is missing overnight gaps by construction.
    """
    rows = []
    for (sym, day), df in sorted(sessions.items(), key=lambda kv: kv[0][1]):
        if sym != symbol:
            continue
        r = rth(df)
        if r.empty:
            continue
        rows.append({"date": day, "high": r["high"].max(),
                     "low": r["low"].min(), "close": r["close"].iloc[-1]})
    if not rows:
        return pd.Series(dtype=float)
    d = pd.DataFrame(rows).set_index("date")
    prev = d["close"].shift(1)
    tr = pd.concat([d["high"] - d["low"], (d["high"] - prev).abs(),
                    (d["low"] - prev).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean().shift(1)
