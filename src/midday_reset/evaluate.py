"""The four Monte Carlo simulations, plus the tests that decide if this is real.

They answer four different questions. Running one and calling it "the Monte
Carlo" is the standard mistake -- see docs/03-study-design.md.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

RNG = np.random.default_rng(20260828)


# ----------------------------------------------------------------------------
# MC-1 -- trade-sequence bootstrap: what does a normal bad stretch look like?
# ----------------------------------------------------------------------------

def block_bootstrap_paths(returns_R, n_paths=10_000, path_len=None,
                          block=8, rng=RNG) -> dict:
    """Block bootstrap of realized R-multiples.

    Blocks, not iid: setup trades cluster by day, theme and regime, and an iid
    bootstrap understates drawdown badly. `block` is the block length in trades.

    Returns the distributions you need to know whether a losing streak is
    normal -- which is worth more to your P&L than the significance test.
    """
    r = np.asarray(pd.Series(returns_R).dropna(), dtype=float)
    if r.size == 0:
        return {}
    path_len = path_len or r.size
    n_blocks = int(np.ceil(path_len / block))

    starts = rng.integers(0, max(r.size - block, 1), size=(n_paths, n_blocks))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]) % r.size
    paths = r[idx].reshape(n_paths, -1)[:, :path_len]

    equity = np.cumsum(paths, axis=1)
    running_max = np.maximum.accumulate(equity, axis=1)
    max_dd = (running_max - equity).max(axis=1)

    losses = paths < 0
    streaks = np.zeros(n_paths, dtype=int)
    cur = np.zeros(n_paths, dtype=int)
    for j in range(paths.shape[1]):
        cur = np.where(losses[:, j], cur + 1, 0)
        streaks = np.maximum(streaks, cur)

    total = equity[:, -1]
    q = lambda a, p: float(np.quantile(a, p))
    return {
        "n_trades_per_path": path_len,
        "mean_R_per_trade": float(r.mean()),
        "total_R": {"p05": q(total, .05), "p25": q(total, .25),
                    "p50": q(total, .50), "p75": q(total, .75),
                    "p95": q(total, .95)},
        "max_drawdown_R": {"p50": q(max_dd, .50), "p90": q(max_dd, .90),
                           "p99": q(max_dd, .99)},
        "longest_losing_streak": {"p50": q(streaks, .50), "p90": q(streaks, .90),
                                  "p99": q(streaks, .99)},
        "p_negative_year": float((total < 0).mean()),
        "_paths": paths,
    }


# ----------------------------------------------------------------------------
# MC-2 -- permutation test: is the signal real?
# ----------------------------------------------------------------------------

def tercile_spread(feature, outcome) -> float:
    """Mean outcome in the bottom feature tercile minus the top tercile.

    Signed for H1: low npvr (drier than the clock explains) should be BETTER,
    so a positive spread supports the hypothesis.
    """
    f, o = np.asarray(feature, float), np.asarray(outcome, float)
    ok = ~(np.isnan(f) | np.isnan(o))
    f, o = f[ok], o[ok]
    if f.size < 30:
        return np.nan
    lo, hi = np.quantile(f, 1 / 3), np.quantile(f, 2 / 3)
    return float(o[f <= lo].mean() - o[f >= hi].mean())


def permutation_test(feature, outcome, n_perm=10_000, stat=tercile_spread,
                     rng=RNG) -> dict:
    """Shuffle the feature across candidates; how often does chance beat you?

    Robust to the fat-tailed, non-normal return distribution in a way a t-test
    is not. This is the honest significance test.
    """
    f, o = np.asarray(feature, float), np.asarray(outcome, float)
    ok = ~(np.isnan(f) | np.isnan(o))
    f, o = f[ok], o[ok]
    observed = stat(f, o)
    null = np.array([stat(rng.permutation(f), o) for _ in range(n_perm)])
    null = null[~np.isnan(null)]
    p = float((np.abs(null) >= abs(observed)).mean()) if null.size else np.nan
    return {"observed": observed, "p_value": p, "n": int(f.size),
            "null_p95": float(np.quantile(null, .95)) if null.size else np.nan}


def residualize(df: pd.DataFrame, target: str, controls: list[str]) -> pd.Series:
    """Strip the confounds out of the feature before testing it.

    npvr is mechanically correlated with pullback depth and duration -- a
    shallow three-bar pullback has low volume by construction. Test H1 on the
    RESIDUAL, or you will discover that shallow pullbacks work and publish it
    to yourself as a volume finding.
    """
    sub = df[[target] + controls].dropna()
    X = np.column_stack([np.ones(len(sub))] + [sub[c].values for c in controls])
    y = sub[target].values
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return pd.Series(y - X @ beta, index=sub.index, name=f"{target}_resid")


# ----------------------------------------------------------------------------
# MC-3 -- random-entry control: is the setup real, or just the population?
# ----------------------------------------------------------------------------

def random_entry_control(real_R, null_sampler, k=20, rng=RNG) -> dict:
    """Compare the setup against matched random entries.

    `null_sampler(i, rng) -> float` must return one pseudo-trade's R using the
    SAME symbol, day and ATR-scaled stop, entered at a random minute in the
    10:30-12:00 window (Null A), or on a random non-earnings day (Null B).

    The control everyone skips and the one most likely to kill the project. If
    the setup does not clearly beat Null A, you have discovered that day-1
    earnings gappers drift up -- not that the reset works.
    """
    real = np.asarray(pd.Series(real_R).dropna(), float)
    null = np.array([null_sampler(i, rng)
                     for i in range(real.size) for _ in range(k)], dtype=float)
    null = null[~np.isnan(null)]
    if real.size == 0 or null.size == 0:
        return {}
    edge = float(real.mean() - null.mean())
    boot = np.array([
        rng.choice(real, real.size, replace=True).mean()
        - rng.choice(null, null.size, replace=True).mean()
        for _ in range(2000)])
    return {
        "real_mean_R": float(real.mean()), "null_mean_R": float(null.mean()),
        "edge_over_null_R": edge,
        "edge_ci95": (float(np.quantile(boot, .025)),
                      float(np.quantile(boot, .975))),
        "p_edge_le_0": float((boot <= 0).mean()),
        "n_real": int(real.size), "n_null": int(null.size),
    }


# ----------------------------------------------------------------------------
# MC-4 -- sizing and risk of ruin: what can you actually bet?
# ----------------------------------------------------------------------------

def risk_of_ruin_sweep(returns_R, risk_fractions=(0.0025, 0.005, 0.01, 0.015,
                                                  0.02, 0.03),
                       n_paths=10_000, path_len=None, block=8,
                       ruin_dd=0.20, rng=RNG) -> pd.DataFrame:
    """Compound each bootstrapped R-path at a range of risk-per-trade sizes.

    The size that maximises the median outcome and the size at which ruin risk
    becomes unacceptable are far apart -- the gap between them is the answer.
    Then check your probe/A/A+ bands (15/30/80% of stop) against this.
    """
    mc = block_bootstrap_paths(returns_R, n_paths, path_len, block, rng)
    if not mc:
        return pd.DataFrame()
    paths = mc["_paths"]
    rows = []
    for f in risk_fractions:
        growth = np.cumprod(1.0 + f * paths, axis=1)
        peak = np.maximum.accumulate(growth, axis=1)
        dd = (peak - growth) / peak
        rows.append({
            "risk_per_trade": f,
            "median_terminal_x": float(np.median(growth[:, -1])),
            "p05_terminal_x": float(np.quantile(growth[:, -1], .05)),
            "p95_terminal_x": float(np.quantile(growth[:, -1], .95)),
            "median_max_dd": float(np.median(dd.max(axis=1))),
            f"p_dd_gt_{int(ruin_dd*100)}pct": float((dd.max(axis=1) > ruin_dd).mean()),
            "p_terminal_below_1": float((growth[:, -1] < 1).mean()),
        })
    return pd.DataFrame(rows)


def half_kelly(returns_R) -> float:
    """Half-Kelly on the R distribution. Full Kelly is not a real-world size."""
    r = np.asarray(pd.Series(returns_R).dropna(), float)
    if r.size == 0 or r.var() == 0:
        return np.nan
    return float(0.5 * r.mean() / r.var())


# ----------------------------------------------------------------------------
# costs -- apply BEFORE quoting any expectancy
# ----------------------------------------------------------------------------

def apply_costs(entry, exit_px, stop, shares, spread, mean_1min_vol, atr15,
                k_impact=0.10, commission_per_share=0.005) -> float:
    """Realized R after spread, impact and commission.

    Many intraday edges live entirely inside this function. Report expectancy
    at 10%, 25% and 50% of one minute's volume -- if it only survives at 10%,
    that is your capacity ceiling and it belongs in the headline.
    """
    R = entry - stop
    if R <= 0:
        return np.nan
    part = shares / mean_1min_vol if mean_1min_vol else 0.0
    impact = k_impact * part * atr15
    fill_in = entry + 0.5 * spread + impact
    fill_out = exit_px - 0.5 * spread - impact
    comm = 2 * commission_per_share
    return (fill_out - fill_in - comm) / R


# ----------------------------------------------------------------------------
# clustering -- required once entries are VWAP touches
# ----------------------------------------------------------------------------

def cluster_bootstrap_paths(df: pd.DataFrame, ret_col: str,
                            cluster_col: str = "day_symbol",
                            n_paths: int = 10_000, rng=RNG) -> dict:
    """Bootstrap by resampling CLUSTERS, not individual trades.

    A trending name touches VWAP three or four times in one session. Those
    signals share a symbol, a day, a catalyst and overlapping forward paths --
    they are one observation wearing four hats. Resampling them individually
    inflates the effective sample size and shrinks every confidence interval by
    roughly sqrt(signals per day), which is how a study convinces itself of an
    edge that is not there.

    Resample whole day-symbol clusters instead. The width of the interval this
    produces is the honest one.
    """
    sub = df[[cluster_col, ret_col]].dropna()
    if sub.empty:
        return {}
    groups = [g[ret_col].to_numpy(float) for _, g in sub.groupby(cluster_col)]
    n_clusters = len(groups)
    means = np.empty(n_paths)
    for i in range(n_paths):
        pick = rng.integers(0, n_clusters, n_clusters)
        means[i] = np.concatenate([groups[j] for j in pick]).mean()
    obs = sub[ret_col].mean()
    naive = sub[ret_col].std(ddof=1) / np.sqrt(len(sub))
    return {
        "mean_R": float(obs),
        "n_signals": int(len(sub)),
        "n_clusters": int(n_clusters),
        "signals_per_cluster": float(len(sub) / n_clusters),
        "ci95_clustered": (float(np.quantile(means, .025)),
                           float(np.quantile(means, .975))),
        "se_clustered": float(means.std(ddof=1)),
        "se_naive_if_treated_as_independent": float(naive),
        "se_understatement_factor": float(means.std(ddof=1) / naive) if naive else np.nan,
    }


def compare_exits(df: pd.DataFrame, exit_cols: list[str],
                  cluster_col: str = "day_symbol") -> pd.DataFrame:
    """Score every candidate exit rule on the SAME entries.

    The point of logging the full forward path instead of one exit: the entry
    and the exit cannot be chosen separately. A trend entry with a modest mean
    and a fat right tail needs an exit that does not cut the tail, so the pair
    is what gets evaluated.
    """
    rows = []
    for c in exit_cols:
        s = df[c].dropna()
        if s.empty:
            continue
        boot = cluster_bootstrap_paths(df, c, cluster_col, n_paths=2000)
        rows.append({
            "exit_rule": c,
            "n": int(s.size),
            "mean_R": float(s.mean()),
            "median_R": float(s.median()),
            "win_rate": float((s > 0).mean()),
            "p90_R": float(s.quantile(.90)),
            "pct_of_mfe_captured": (float(s.mean() / df["mfe_eod"].mean())
                                    if "mfe_eod" in df and df["mfe_eod"].mean() else np.nan),
            "ci95_low": boot.get("ci95_clustered", (np.nan, np.nan))[0],
            "ci95_high": boot.get("ci95_clustered", (np.nan, np.nan))[1],
        })
    return pd.DataFrame(rows).sort_values("mean_R", ascending=False)
