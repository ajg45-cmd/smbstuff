"""The exit lab -- the primary study.

The question is not whether the VWAP continuation is a good entry. It is:
**given the entry, which exit logic keeps a trend trader in the trend, and in
which universe does that advantage hold up?**

That reframing is worth a lot statistically. Comparing exits on the SAME trades
is a paired design: the entry noise that swamps an absolute-EV study cancels in
the difference between two rules on the same trade. Paired differences resolve
an effect roughly an order of magnitude smaller than two independent samples of
the same size.

One caveat that has to stay in view: exit rankings are conditional on the entry
having positive expectancy. If entry EV <= 0 the optimal exit degenerates to
"exit immediately," and a leaderboard of trailing rules is measuring nothing.
So establish entry EV > 0 first -- it comes free from the same dataset, and it
is a low bar, not the whole study.

Within-bar ordering is deliberately pessimistic: adverse levels are assumed hit
before favorable ones, because on a 5- or 15-min bar you cannot know the order
and the optimistic assumption is how backtests manufacture edge.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import time
from typing import Optional

import numpy as np
import pandas as pd

from .features import RTH_CLOSE
from .v1 import bar_atr


@dataclass
class ExitResult:
    R: float
    exit_time: object
    exit_price: float
    reason: str


def run_exit(bars: pd.DataFrame, entry_time, entry: float, stop: float,
             side: str = "long", *,
             vwap: Optional[pd.Series] = None,
             ema_span: Optional[int] = None, ema_buffer_atr: float = 0.0,
             vwap_exit: bool = False, vwap_buffer_atr: float = 0.0,
             trail_bars: Optional[int] = None,
             chandelier_atr: Optional[float] = None,
             target_R: Optional[float] = None,
             breakeven_at_R: Optional[float] = None,
             time_stop: Optional[time] = None) -> ExitResult:
    """Walk `bars` from the entry and apply one exit rule.

    Every rule shares this engine so the comparison is apples to apples: the
    only thing that differs between two rows of the leaderboard is the rule.
    """
    sgn = 1.0 if side == "long" else -1.0
    R = sgn * (entry - stop)
    if R <= 0 or bars.empty:
        return ExitResult(np.nan, None, np.nan, "invalid")

    fwd = bars[(bars.index > entry_time) & (bars.index.time < RTH_CLOSE)]
    if fwd.empty:
        return ExitResult(np.nan, None, np.nan, "no_bars")

    atr = bar_atr(bars).reindex(fwd.index).ffill()
    ema = (bars["close"].ewm(span=ema_span, adjust=False).mean().reindex(fwd.index)
           if ema_span else None)

    cur_stop = stop
    run_ext = entry                       # running favorable extreme
    lows, highs = [], []

    for i, (ts, row) in enumerate(fwd.iterrows()):
        hi, lo, cl, op = (float(row["high"]), float(row["low"]),
                          float(row["close"]), float(row["open"]))
        a = float(atr.loc[ts]) if not pd.isna(atr.loc[ts]) else 0.0

        # 1. a clock stop fires before anything the bar does
        if time_stop is not None and ts.time() >= time_stop:
            return ExitResult(sgn * (op - entry) / R, ts, op, "time")

        # 2. adverse first -- assume the worst intrabar sequence
        hit_stop = (lo <= cur_stop) if sgn > 0 else (hi >= cur_stop)
        if hit_stop:
            reason = "stop" if cur_stop == stop else "trail"
            return ExitResult(sgn * (cur_stop - entry) / R, ts, cur_stop, reason)

        # 3. then the target
        if target_R is not None:
            tgt = entry + sgn * target_R * R
            if (hi >= tgt) if sgn > 0 else (lo <= tgt):
                return ExitResult(float(target_R), ts, tgt, "target")

        # 4. close-based signals, evaluated at the close
        if ema is not None:
            line = float(ema.loc[ts]) - sgn * ema_buffer_atr * a
            if sgn * (cl - line) < 0:
                return ExitResult(sgn * (cl - entry) / R, ts, cl, "ema")
        if vwap_exit and vwap is not None:
            line = float(vwap.asof(ts)) - sgn * vwap_buffer_atr * a
            if sgn * (cl - line) < 0:
                return ExitResult(sgn * (cl - entry) / R, ts, cl, "vwap")

        # 5. update trailing levels AFTER the bar closes, so a level computed
        #    from this bar can only bind from the next one
        lows.append(lo); highs.append(hi)
        run_ext = max(run_ext, hi) if sgn > 0 else min(run_ext, lo)

        if breakeven_at_R is not None and sgn * (run_ext - entry) / R >= breakeven_at_R:
            cur_stop = max(cur_stop, entry) if sgn > 0 else min(cur_stop, entry)
        if trail_bars is not None and len(lows) >= trail_bars:
            lvl = (min(lows[-trail_bars:]) if sgn > 0 else max(highs[-trail_bars:]))
            cur_stop = max(cur_stop, lvl) if sgn > 0 else min(cur_stop, lvl)
        if chandelier_atr is not None and a > 0:
            lvl = run_ext - sgn * chandelier_atr * a
            cur_stop = max(cur_stop, lvl) if sgn > 0 else min(cur_stop, lvl)

    last = fwd.iloc[-1]
    return ExitResult(sgn * (float(last["close"]) - entry) / R,
                      fwd.index[-1], float(last["close"]), "eod")


# ----------------------------------------------------------------------------
# the rule set
# ----------------------------------------------------------------------------

def rule_grid(frames=("5m", "15m")) -> list[dict]:
    """Every exit rule to score, across both bar frames.

    Deliberately includes the do-nothing benchmark. Traders almost never check
    it, and a trailing rule that cannot beat "initial stop, hold to the close"
    is costing money to feel busy.
    """
    rules: list[dict] = []
    for f in frames:
        add = lambda name, **kw: rules.append({"name": name, "frame": f, **kw})

        add("hold_to_close")                                   # the benchmark
        for span in (5, 9, 21):
            add(f"ema{span}", ema_span=span)
        for buf in (0.25, 0.5, 1.0):                           # the v2 idea
            add(f"ema9_atr{buf}", ema_span=9, ema_buffer_atr=buf)
        add("vwap_loss", vwap_exit=True)
        add("vwap_loss_atr0.5", vwap_exit=True, vwap_buffer_atr=0.5)
        for n in (1, 2, 3):
            add(f"trail_{n}bar", trail_bars=n)
        for k in (1.5, 2.0, 3.0):
            add(f"chandelier_{k}atr", chandelier_atr=k)
        for t in (1, 2, 3, 4):
            add(f"target_{t}R", target_R=float(t))
        for t in (time(12, 30), time(13, 30), time(15, 30)):
            add(f"time_{t:%H%M}", time_stop=t)
        add("be1R_then_ema9", ema_span=9, breakeven_at_R=1.0)
        add("be1R_then_trail2", trail_bars=2, breakeven_at_R=1.0)
        add("ema9_be1R_atr0.5", ema_span=9, ema_buffer_atr=0.5, breakeven_at_R=1.0)
    return rules


def score_trade(frames: dict[str, pd.DataFrame], vwap: pd.Series,
                entry_time, entry: float, stop: float, side: str,
                rules: Optional[list[dict]] = None) -> dict:
    """Realized R for every rule on ONE trade. Keys are `rule@frame`."""
    rules = rules or rule_grid(tuple(frames))
    out: dict = {}
    for spec in rules:
        spec = dict(spec)
        name, f = spec.pop("name"), spec.pop("frame")
        bars = frames.get(f)
        if bars is None:
            continue
        res = run_exit(bars, entry_time, entry, stop, side, vwap=vwap, **spec)
        out[f"exit_{name}@{f}"] = res.R
        out[f"why_{name}@{f}"] = res.reason
    return out


def leaderboard(df: pd.DataFrame, cluster_col: str = "day_symbol",
                benchmark: str = "exit_hold_to_close@15m",
                n_boot: int = 2000, rng=None) -> pd.DataFrame:
    """Rank exit rules by EV, with PAIRED differences against the benchmark.

    Paired, because the rules are scored on identical trades. Clustered on the
    day, because several signals in one name on one day share a catalyst and
    overlapping forward paths -- they are one observation wearing several hats,
    and treating them as independent shrinks every interval by roughly the
    square root of the signals per day.
    """
    rng = rng or np.random.default_rng(20260828)
    cols = [c for c in df.columns if c.startswith("exit_")]
    if benchmark not in df.columns:
        benchmark = cols[0]

    groups = list(df.groupby(cluster_col).indices.values())
    n_g = len(groups)
    picks = [rng.integers(0, n_g, n_g) for _ in range(n_boot)]

    rows = []
    for c in cols:
        s = df[c]
        d = (s - df[benchmark]).dropna()
        if s.dropna().empty:
            continue
        diffs = np.empty(n_boot)
        dv = (s - df[benchmark]).to_numpy(float)
        for b, pick in enumerate(picks):
            idx = np.concatenate([groups[j] for j in pick])
            vals = dv[idx]
            vals = vals[~np.isnan(vals)]
            diffs[b] = vals.mean() if vals.size else np.nan
        why = df.get(c.replace("exit_", "why_"))
        rows.append({
            "rule": c.replace("exit_", ""),
            "n": int(s.notna().sum()),
            "mean_R": float(s.mean()),
            "median_R": float(s.median()),
            "win_rate": float((s > 0).mean()),
            "p90_R": float(s.quantile(.90)),
            "pct_mfe_captured": (float(s.mean() / df["mfe_eod"].mean())
                                 if "mfe_eod" in df and df["mfe_eod"].mean() > 0
                                 else np.nan),
            "vs_benchmark_R": float(d.mean()) if len(d) else np.nan,
            "ci95_low": float(np.nanquantile(diffs, .025)),
            "ci95_high": float(np.nanquantile(diffs, .975)),
            "p_worse_than_bench": float(np.nanmean(diffs <= 0)),
            "top_reason": (why.mode().iloc[0] if why is not None
                           and not why.mode().empty else ""),
        })
    lb = pd.DataFrame(rows).sort_values("mean_R", ascending=False)
    return lb.reset_index(drop=True)


def universe_slices(df: pd.DataFrame) -> dict[str, pd.Series]:
    """'In what universe does it prove significant' -- the slices to check.

    A rule that wins overall but only in one slice has not been shown to work;
    it has been shown where to look next. Require the winner to hold in most of
    these, then re-check it out of sample.
    """
    def split(col, name_lo, name_hi, out):
        """Tercile split, skipped when the terciles are degenerate.

        If a column is constant (or nearly so) both masks come back True for
        every row and the report shows two identical slices that look like
        agreement. That is worse than no slice at all.
        """
        if col not in df:
            return
        lo, hi = df[col].quantile(1 / 3), df[col].quantile(2 / 3)
        if pd.isna(lo) or pd.isna(hi) or lo >= hi:
            return
        out[name_lo] = df[col] <= lo
        out[name_hi] = df[col] >= hi

    s: dict[str, pd.Series] = {"all": pd.Series(True, index=df.index)}
    if "side" in df:
        s["long"] = df["side"] == "long"
        s["short"] = df["side"] == "short"
    if "frame" in df:
        for f in df["frame"].dropna().unique():
            s[f"entry_{f}"] = df["frame"] == f
    if "is_first_of_day" in df:
        s["first_signal"] = df["is_first_of_day"]
        s["later_signals"] = ~df["is_first_of_day"]
    if "liquid" in df:
        s["liquid_5M+"] = df["liquid"]
    if "open_is_abnormal" in df:
        s["abnormal_open"] = df["open_is_abnormal"]
    if "beyond_pmh" in df:
        s["beyond_pmh"] = df["beyond_pmh"]
    split("npvr", "dry_approach", "wet_approach", s)
    split("vwap_slope_atr", "weak_trend", "strong_trend", s)
    split("R_pct", "tight_risk", "wide_risk", s)
    # a slice that is everybody, or nobody, tells you nothing
    return {k: m for k, m in s.items()
            if k == "all" or 0 < int(m.sum()) < len(df)}


def universe_report(df: pd.DataFrame, rule_col: str,
                    benchmark: str = "exit_hold_to_close@15m",
                    min_n: int = 30) -> pd.DataFrame:
    """One rule's paired edge over the benchmark, slice by slice."""
    rows = []
    for name, mask in universe_slices(df).items():
        sub = df[mask]
        if len(sub) < min_n or rule_col not in sub:
            rows.append({"universe": name, "n": len(sub), "mean_R": np.nan,
                         "vs_benchmark_R": np.nan, "note": "too few"})
            continue
        d = (sub[rule_col] - sub[benchmark]).dropna()
        rows.append({
            "universe": name, "n": len(sub),
            "mean_R": float(sub[rule_col].mean()),
            "vs_benchmark_R": float(d.mean()) if len(d) else np.nan,
            "win_rate": float((sub[rule_col] > 0).mean()),
            "note": "",
        })
    return pd.DataFrame(rows)
