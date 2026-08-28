"""Synthetic session builder shared by the contract tests.

Hand-built sessions, not market data. They exist to pin the mechanics down:
that the zigzag does not flip inside a bar, that a VWAP touch is measured
against the concurrent VWAP rather than the bar's closing value, that entries
never precede their signal. A real edge is not testable here and no test in
this repo claims otherwise.
"""
import os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from midday_reset import features as F  # noqa: E402


def build(path_fn, day="2024-03-05", seed=3, noise=0.02):
    """`path_fn(minute_of_day) -> (price, volume_per_minute)`."""
    idx = pd.date_range(f"{day} 04:00", f"{day} 15:59", freq="1min", tz="US/Eastern")
    rows = [path_fn(t.hour * 60 + t.minute) for t in idx]
    c = np.array([r[0] for r in rows], dtype=float)
    v = np.array([r[1] for r in rows], dtype=float)
    c = c + np.random.default_rng(seed).normal(0, noise, len(c))
    b1 = pd.DataFrame({"open": c, "close": c, "high": c + 0.04,
                       "low": c - 0.04, "volume": v}, index=idx)
    b15 = F.rth(b1).resample("15min").agg(
        {"open": "first", "high": "max", "low": "min",
         "close": "last", "volume": "sum"}).dropna()
    return b1, b15


def flat_baseline(b1, level=5000.0):
    """A featureless prior-day volume curve, so pvr_expected == 1.

    With a flat baseline the normalized ratio equals the raw one, which is what
    makes the normalization visible in a test: change the baseline shape and
    npvr must move while pvr_raw does not.
    """
    hist = b1.copy()
    hist.index = hist.index - pd.Timedelta(days=1)
    hist["volume"] = level
    return F.volume_baseline(hist)


def atr15_of(b15):
    return float((b15["high"] - b15["low"]).mean())
