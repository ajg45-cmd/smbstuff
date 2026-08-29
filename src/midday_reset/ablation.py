"""Does adding a filter actually move EV?

Every clean-price-action gate cuts the sample. Stack five filters that each
remove 40% and you keep 8% of the trades -- and the survivors will show a
higher mean almost regardless of whether the filters carry information, because
you have taken the maximum of a smaller, noisier set.

So "EV went up when I added the filter" is not evidence. Three things have to
be reported alongside it, and this module computes all three:

  1. **n at every rung.** A lift that arrives with an 80% sample cut is a
     different claim from one that arrives with a 10% cut.
  2. **The random-subset null.** Would selecting the same NUMBER of trades at
     random have produced the same lift? This is the control that separates a
     real filter from arithmetic.
  3. **The lift after controlling for trend strength.** Momentum filters are
     mechanically correlated with trending -- a name above all its EMAs all
     morning IS a trending name. Without the control you are rediscovering
     "trends trend" and calling it an edge.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

RNG = np.random.default_rng(20260829)


def _mean(df, col):
    s = df[col].dropna()
    return float(s.mean()) if len(s) else np.nan


def random_subset_null(df: pd.DataFrame, outcome: str, n_keep: int,
                       observed: float, n_iter: int = 5000, rng=RNG) -> dict:
    """Would a RANDOM subset of the same size have done as well?

    The honest test of a filter. If a random draw of the same number of trades
    beats the filtered mean 30% of the time, the filter has told you nothing --
    it has just made the sample smaller.
    """
    vals = df[outcome].dropna().to_numpy(float)
    if (vals.size == 0 or not (0 < n_keep < vals.size) or np.isnan(observed)):
        # n_keep == vals.size is a no-op filter: the "random subset" is the
        # whole population, so the comparison is vacuous rather than passing.
        return {"p_random_beats": np.nan, "null_mean": np.nan, "null_p95": np.nan}
    draws = np.array([rng.choice(vals, n_keep, replace=False).mean()
                      for _ in range(n_iter)])
    return {"p_random_beats": float((draws >= observed).mean()),
            "null_mean": float(draws.mean()),
            "null_p95": float(np.quantile(draws, .95))}


def lift_within_strata(df: pd.DataFrame, outcome: str, mask: pd.Series,
                       strata_col: str = "vwap_slope_atr",
                       n_strata: int = 3) -> float:
    """Mean lift from the filter, averaged across trend-strength strata.

    Compares filtered against unfiltered INSIDE each stratum, so a filter that
    merely selects strong trends scores near zero here while one that adds
    something beyond trend strength keeps its lift.
    """
    if strata_col not in df or df[strata_col].isna().all():
        return np.nan
    try:
        bins = pd.qcut(df[strata_col], n_strata, duplicates="drop")
    except ValueError:
        return np.nan
    lifts, weights = [], []
    for _, idx in df.groupby(bins, observed=True).groups.items():
        sub = df.loc[idx]
        kept = sub[mask.reindex(sub.index).fillna(False)]
        if len(kept) < 5 or len(sub) - len(kept) < 5:
            continue
        a, b = _mean(kept, outcome), _mean(sub, outcome)
        if not (np.isnan(a) or np.isnan(b)):
            lifts.append(a - b)
            weights.append(len(sub))
    if not lifts:
        return np.nan
    return float(np.average(lifts, weights=weights))


def _mask(df: pd.DataFrame, spec) -> pd.Series:
    if callable(spec):
        return spec(df).fillna(False)
    col, op, val = spec
    s = df[col]
    m = {">=": s >= val, "<=": s <= val, "==": s == val,
         "!=": s != val, ">": s > val, "<": s < val}[op]
    return m.fillna(False)


def single_filters(df: pd.DataFrame, outcome: str, filters: dict,
                   n_iter: int = 3000) -> pd.DataFrame:
    """Each filter on its own, against the full population."""
    base_n, base_ev = len(df), _mean(df, outcome)
    rows = [{"filter": "(none)", "n": base_n, "kept_pct": 1.0,
             "mean_R": base_ev, "lift": 0.0, "p_random_beats": np.nan,
             "lift_within_trend": 0.0}]
    for name, spec in filters.items():
        try:
            m = _mask(df, spec)
        except KeyError:
            continue
        kept = df[m]
        if kept.empty:
            rows.append({"filter": name, "n": 0, "kept_pct": 0.0,
                         "mean_R": np.nan, "lift": np.nan,
                         "p_random_beats": np.nan, "lift_within_trend": np.nan})
            continue
        ev = _mean(kept, outcome)
        rows.append({
            "filter": name, "n": len(kept), "kept_pct": len(kept) / base_n,
            "mean_R": ev, "lift": ev - base_ev,
            **{k: v for k, v in random_subset_null(df, outcome, len(kept), ev,
                                                   n_iter).items()
               if k == "p_random_beats"},
            "lift_within_trend": lift_within_strata(df, outcome, m),
        })
    return pd.DataFrame(rows)


def filter_ladder(df: pd.DataFrame, outcome: str, order: list,
                  filters: dict, n_iter: int = 3000) -> pd.DataFrame:
    """Cumulative ladder: add one filter at a time, in a PRE-SPECIFIED order.

    Pre-specified matters. Choosing the order by what raises EV most is how a
    ladder becomes a curve-fit, and the resulting sequence will look monotonic
    on any dataset, signal or not.
    """
    base_n, base_ev = len(df), _mean(df, outcome)
    rows = [{"step": "(none)", "n": base_n, "kept_pct": 1.0, "mean_R": base_ev,
             "cum_lift": 0.0, "step_lift": 0.0, "p_random_beats": np.nan}]
    m = pd.Series(True, index=df.index)
    prev_ev = base_ev
    for name in order:
        if name not in filters:
            continue
        try:
            m = m & _mask(df, filters[name])
        except KeyError:
            continue
        kept = df[m]
        ev = _mean(kept, outcome)
        rows.append({
            "step": f"+ {name}", "n": len(kept), "kept_pct": len(kept) / base_n,
            "mean_R": ev, "cum_lift": ev - base_ev, "step_lift": ev - prev_ev,
            "p_random_beats": random_subset_null(
                df, outcome, max(len(kept), 1), ev, n_iter)["p_random_beats"],
        })
        prev_ev = ev
        if len(kept) < 10:
            break
    return pd.DataFrame(rows)


# The gates, as switchable specs. Order here is the PRE-SPECIFIED ladder order:
# structural gates first, momentum next, cleanliness last, so the cleanliness
# claim is tested on top of everything cheaper rather than credited for it.
STANDARD_FILTERS = {
    "out_of_pm_range":   ("beyond_pm_range", "==", True),
    "trend_ok":          lambda d: (d["pct_session_with_trend"] >= 0.60)
                                   & (d["vwap_slope_atr"] > 0),
    "beyond_all_emas":   ("beyond_all_emas", "==", True),
    "emas_upsloping":    ("emas_upsloping", "==", True),
    "upslope_by_1000":   ("upslope_by_1000", "==", True),
    "ema_ribbon":        ("ema_ribbon_aligned", "==", True),
    "liquid_5M":         ("liquid", "==", True),
    "abnormal_open":     ("open_is_abnormal", "==", True),
    "first_of_day":      ("is_first_of_day", "==", True),
    "clean_90pct_ema21": ("clean_90", "==", True),
    "guidance_raised":   ("guidance", "==", "raise"),
}

LADDER_ORDER = ["out_of_pm_range", "trend_ok", "liquid_5M", "first_of_day",
                "beyond_all_emas", "emas_upsloping", "upslope_by_1000",
                "ema_ribbon", "abnormal_open", "clean_90pct_ema21"]


def anchor_comparison(df: pd.DataFrame, outcome: str) -> pd.DataFrame:
    """Session VWAP (09:30) against Day VWAP (premarket included).

    Not just which has the higher mean -- how much they even AGREE. Two anchors
    that select largely different signals are two strategies; two that select
    the same signals are one strategy with a cosmetic difference.
    """
    if "vwap_anchor" not in df:
        return pd.DataFrame()
    rows = []
    for anchor, sub in df.groupby("vwap_anchor"):
        rows.append({"vwap_anchor": anchor, "n": len(sub),
                     "mean_R": _mean(sub, outcome),
                     "median_R": float(sub[outcome].median()),
                     "win_rate": float((sub[outcome] > 0).mean()),
                     "day_symbols": int(sub["day_symbol"].nunique())
                     if "day_symbol" in sub else np.nan})
    out = pd.DataFrame(rows)
    keys = ["symbol", "date", "side", "frame", "bar_time"]
    if all(k in df for k in keys):
        sets = {a: set(map(tuple, s[keys].values))
                for a, s in df.groupby("vwap_anchor")}
        if len(sets) == 2:
            a, b = sets.values()
            inter, union = len(a & b), len(a | b)
            out.attrs["overlap"] = inter / union if union else np.nan
    return out
