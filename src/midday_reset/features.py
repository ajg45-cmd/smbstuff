"""Reference implementation of the Midday Reset Continuation setup.

Written to be read as much as run. Where `docs/01-setup-definition.md` is
ambiguous, this module is the tiebreaker -- that is the point of having it.

Input contract
--------------
`bars_1m`  : DataFrame indexed by tz-aware US/Eastern DatetimeIndex (bar OPEN),
             columns ['open','high','low','close','volume'], INCLUDING
             pre/post-market rows. One symbol, one session, or many sessions.
`bars_15m` : same, resampled to 15 minutes, regular session only.
`daily`    : DataFrame indexed by date with ['open','high','low','close','volume'].

Nothing here reads a row later than the timestamp it claims to be known at.
That invariant is the whole reason the functions take explicit `as_of` cutoffs
instead of slicing lazily.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import time
from typing import Optional

import numpy as np
import pandas as pd

TZ = "US/Eastern"
RTH_OPEN = time(9, 30)
RTH_CLOSE = time(16, 0)
OR_END = time(10, 0)
OPEN_EVAL_END = time(10, 30)
WINDOW_START = time(10, 30)
WINDOW_END = time(12, 0)

# --- tunables [T] -- every one of these is swept in the sensitivity analysis ---
ZIGZAG_ATR_MULT = 0.75
MIN_IMPULSE_ATR = 1.00
DEPTH_MIN, DEPTH_MAX = 0.20, 0.70
DUR_MIN_BARS, DUR_MAX_BARS = 2, 6
LEVEL_TOL_ATR = 0.35
TRIGGER_VOL_MULT = 1.5
STOP_BUFFER_ATR = 0.10
MAX_R_PCT = 0.025
MIN_OPEN_STRENGTH = 0.60
TICK = 0.01


# ----------------------------------------------------------------------------
# primitives
# ----------------------------------------------------------------------------

def rth(bars: pd.DataFrame) -> pd.DataFrame:
    """Regular trading hours only."""
    t = bars.index.time
    return bars[(t >= RTH_OPEN) & (t < RTH_CLOSE)]


def premarket(bars: pd.DataFrame) -> pd.DataFrame:
    return bars[bars.index.time < RTH_OPEN]


def atr(daily: pd.DataFrame, n: int = 14) -> pd.Series:
    """Wilder ATR on daily bars. Shifted so it is known at the open."""
    prev_close = daily["close"].shift(1)
    tr = pd.concat([
        daily["high"] - daily["low"],
        (daily["high"] - prev_close).abs(),
        (daily["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean().shift(1)


def session_vwap(bars_1m: pd.DataFrame) -> pd.Series:
    """Session VWAP from 9:30, on typical price. Returns a series aligned to RTH."""
    r = rth(bars_1m)
    tp = (r["high"] + r["low"] + r["close"]) / 3.0
    pv = (tp * r["volume"]).cumsum()
    vv = r["volume"].cumsum().replace(0, np.nan)
    return (pv / vv).rename("vwap")


def volume_baseline(hist_1m: pd.DataFrame, lookback_sessions: int = 20) -> pd.Series:
    """Median volume per minute-of-day over the trailing N sessions.

    This is what turns a raw volume ratio into a meaningful one. Without it you
    are measuring the lunchtime volume trough, which happens on every stock
    every day and tells you nothing. See docs/02 section 4.

    Returns a Series indexed by `datetime.time`.
    """
    r = rth(hist_1m)
    sessions = sorted(set(r.index.date))[-lookback_sessions:]
    r = r[np.isin(r.index.date, sessions)]
    if r.empty:
        return pd.Series(dtype=float)
    return r.groupby(r.index.time)["volume"].median()


def _mean_vol_per_min(bars_1m: pd.DataFrame, start, end) -> float:
    seg = bars_1m[(bars_1m.index >= start) & (bars_1m.index < end)]
    minutes = max(len(seg), 1)
    return float(seg["volume"].sum()) / minutes


def _baseline_vol_per_min(baseline: pd.Series, start, end) -> float:
    """Expected vol/min over a clock interval, from the intraday curve alone."""
    if baseline.empty:
        return np.nan
    times = pd.date_range(start, end, freq="1min", inclusive="left").time
    vals = [baseline.get(t, np.nan) for t in times]
    vals = [v for v in vals if not pd.isna(v)]
    return float(np.mean(vals)) if vals else np.nan


# ----------------------------------------------------------------------------
# swing / leg detection
# ----------------------------------------------------------------------------

@dataclass
class Swing:
    idx: pd.Timestamp
    price: float
    kind: str  # 'H' or 'L'


def swing_points(bars: pd.DataFrame, threshold: float) -> list[Swing]:
    """ATR-scaled zigzag. `threshold` is an absolute price move, not a percent.

    A swing is only *confirmed* once price reverses by `threshold` from the
    extreme, so nothing here is visible before it would have been in real time.

    A bar that extends the current extreme can never also confirm the reversal
    off it -- without that rule a single wide 15-min bar prints a swing high and
    a swing low at the same timestamp, and the leg structure becomes nonsense.
    """
    if len(bars) < 3 or threshold <= 0:
        return []

    closes = bars["close"].to_numpy(dtype=float)
    moved = np.abs(closes - closes[0]) >= threshold
    if not moved.any():
        return []

    k = int(np.argmax(moved))
    direction = 1 if closes[k] > closes[0] else -1
    head = bars.iloc[: k + 1]
    hi_i, hi_p = head["high"].idxmax(), float(head["high"].max())
    lo_i, lo_p = head["low"].idxmin(), float(head["low"].min())

    # seed with the anchor so the sequence reads L,H,L,... (or H,L,H,...);
    # without it the leg that started at the open is invisible.
    swings: list[Swing] = [Swing(lo_i, lo_p, "L") if direction == 1
                           else Swing(hi_i, hi_p, "H")]

    for ts, row in bars.iloc[k + 1:].iterrows():
        h, l = float(row["high"]), float(row["low"])
        if direction == 1:
            if h > hi_p:
                hi_i, hi_p = ts, h
            elif (hi_p - l) >= threshold:
                swings.append(Swing(hi_i, hi_p, "H"))
                direction, lo_i, lo_p = -1, ts, l
        else:
            if l < lo_p:
                lo_i, lo_p = ts, l
            elif (h - lo_p) >= threshold:
                swings.append(Swing(lo_i, lo_p, "L"))
                direction, hi_i, hi_p = 1, ts, h

    return swings


def overlap_ratio(bars: pd.DataFrame) -> float:
    """Mean bar-to-bar overlap across a leg. High = orderly drift, low = impulsive.

    The most promising computable proxy for what the eye calls 'clean'.
    """
    if len(bars) < 2:
        return np.nan
    ov = []
    for i in range(1, len(bars)):
        a, b = bars.iloc[i - 1], bars.iloc[i]
        inter = min(a["high"], b["high"]) - max(a["low"], b["low"])
        union = max(a["high"], b["high"]) - min(a["low"], b["low"])
        if union > 0:
            ov.append(max(inter, 0.0) / union)
    return float(np.mean(ov)) if ov else np.nan


# ----------------------------------------------------------------------------
# stage 2 -- open quality
# ----------------------------------------------------------------------------

def open_strength(bars_1m: pd.DataFrame, vwap: pd.Series, pmh: float,
                  atr_d: float) -> dict:
    """Everything measurable at 10:30 using only 9:30-10:30. Known-as-of 10:30."""
    day = bars_1m.index[0].date()
    seg = rth(bars_1m)
    seg = seg[seg.index.time < OPEN_EVAL_END]
    if seg.empty:
        return {}

    v = vwap.reindex(seg.index)
    pct_above_vwap = float((seg["close"] > v).mean())

    hi, lo = float(seg["high"].max()), float(seg["low"].min())
    close_1030 = float(seg["close"].iloc[-1])
    rng = hi - lo
    range_position = (close_1030 - lo) / rng if rng > 0 else np.nan

    pmh_clear_atr = (hi - pmh) / atr_d if (atr_d and not np.isnan(pmh)) else np.nan

    tail = seg[seg.index.time >= time(9, 45)]
    if len(tail) > 1:
        anchor = float(tail["close"].iloc[0])
        mfe = max(float(tail["high"].max()) - anchor, 0.0)
        mae = max(anchor - float(tail["low"].min()), 0.0)
        trend_quality = mfe / (mfe + mae) if (mfe + mae) > 0 else np.nan
    else:
        trend_quality = np.nan

    parts = [pct_above_vwap, range_position, pmh_clear_atr, trend_quality]
    parts = [np.nan if p is None else p for p in parts]
    clipped = [np.clip(p, 0, 1) for p in parts if not pd.isna(p)]
    score = float(np.mean(clipped)) if clipped else np.nan

    or_seg = seg[seg.index.time < OR_END]
    return {
        "date": day,
        "pct_above_vwap": pct_above_vwap,
        "range_position_1030": range_position,
        "pmh_clear_atr": pmh_clear_atr,
        "trend_quality": trend_quality,
        "open_strength": score,
        "or_high": float(or_seg["high"].max()) if not or_seg.empty else np.nan,
        "or_low": float(or_seg["low"].min()) if not or_seg.empty else np.nan,
        "high_0930_1030": hi,
        "close_1030": close_1030,
    }


def pmh_cleared_and_held(bars_15m: pd.DataFrame, pmh: float) -> bool:
    """Hard gate: a 15-min bar CLOSED above the premarket high before noon."""
    seg = bars_15m[bars_15m.index.time < WINDOW_END]
    return bool((seg["close"] > pmh).any())


# ----------------------------------------------------------------------------
# stages 3-5 -- the setup itself
# ----------------------------------------------------------------------------

def reset_levels(levels: dict[str, float], price: float, tol: float) -> tuple[list, int]:
    """Which reference levels the pullback low reset against, within tolerance."""
    hits = [k for k, v in levels.items()
            if v is not None and not pd.isna(v) and abs(price - v) <= tol]
    return hits, len(hits)


@dataclass
class Candidate:
    candidate_id: str
    symbol: str
    date: object
    # structure
    L0_time: object; L0: float
    H1_time: object; H1: float
    L2_time: object; L2: float
    leg_index: int
    depth: float
    depth_atr: float
    duration_bars: int
    overlap_ratio: float
    max_pb_bar_range_atr: float
    # levels
    reset_level_type: str
    level_confluence: int
    vwap_distance_atr: float
    # volume (the core)
    pvr_raw: float
    pvr_expected: float
    npvr: float
    trigger_vol_ratio: float
    spring_ratio: float
    dollar_vol_at_trigger: float
    # trigger / risk
    trigger_time: object
    trigger_bucket: str
    entry: float
    stop: float
    R: float
    R_pct: float
    R_atr: float


def find_candidate(symbol: str, bars_1m: pd.DataFrame, bars_15m: pd.DataFrame,
                   atr_d: float, atr_15: float, baseline: pd.Series,
                   levels_extra: Optional[dict] = None) -> Optional[Candidate]:
    """Scan one session for a Midday Reset Continuation candidate.

    Returns the FIRST valid trigger in the 10:30-12:00 window, or None.
    Everything used is available at or before the trigger timestamp.
    """
    if bars_15m.empty or bars_1m.empty or not atr_15 or np.isnan(atr_15):
        return None

    day = bars_15m.index[0].date()
    vwap = session_vwap(bars_1m)
    pm = premarket(bars_1m)
    pmh = float(pm["high"].max()) if not pm.empty else np.nan
    if np.isnan(pmh) or not pmh_cleared_and_held(bars_15m, pmh):
        return None

    swings = swing_points(bars_15m, ZIGZAG_ATR_MULT * atr_15)
    if len(swings) < 2:
        return None

    # walk confirmed L -> H -> L triples, take the first whose L2 lands in window
    for i in range(len(swings) - 2):
        a, b, c = swings[i], swings[i + 1], swings[i + 2]
        if (a.kind, b.kind, c.kind) != ("L", "H", "L"):
            continue
        if not (WINDOW_START <= c.idx.time() < WINDOW_END):
            continue
        if c.price <= a.price:                       # higher-low structure broken
            continue
        if (b.price - a.price) < MIN_IMPULSE_ATR * atr_15:
            continue

        depth = (b.price - c.price) / (b.price - a.price)
        if not (DEPTH_MIN <= depth <= DEPTH_MAX):
            continue

        pb = bars_15m[(bars_15m.index >= b.idx) & (bars_15m.index <= c.idx)]
        dur = len(pb) - 1
        if not (DUR_MIN_BARS <= dur <= DUR_MAX_BARS):
            continue

        # --- levels -----------------------------------------------------------
        vwap_at_L2 = float(vwap.asof(c.idx))
        levels = {"VWAP": vwap_at_L2, "PMH": pmh}
        if levels_extra:
            levels.update(levels_extra)
        hits, confluence = reset_levels(levels, c.price, LEVEL_TOL_ATR * atr_15)
        if not hits:
            continue

        # --- volume: the whole point -----------------------------------------
        imp_start, imp_end = a.idx, b.idx
        pb_start, pb_end = b.idx, c.idx
        imp_vpm = _mean_vol_per_min(bars_1m, imp_start, imp_end)
        pb_vpm = _mean_vol_per_min(bars_1m, pb_start, pb_end)
        if imp_vpm <= 0:
            continue
        pvr_raw = pb_vpm / imp_vpm

        exp_imp = _baseline_vol_per_min(baseline, imp_start, imp_end)
        exp_pb = _baseline_vol_per_min(baseline, pb_start, pb_end)
        pvr_expected = (exp_pb / exp_imp) if (exp_imp and exp_imp > 0) else np.nan
        npvr = pvr_raw / pvr_expected if pvr_expected and pvr_expected > 0 else np.nan

        # --- trigger ----------------------------------------------------------
        # Break of the last DOWN-closing pullback bar's high, not simply the
        # final bar's high: when the swing-low bar reverses intrabar, its own
        # high already contains the resumption and using it inflates the entry
        # (and the stop distance) by the whole recovery. [T] -- the alternative
        # ("high of the final pullback bar") is a variant to sweep.
        down = pb[pb["close"] < pb["open"]]
        h_pb = float(down["high"].iloc[-1]) if not down.empty else float(pb["high"].iloc[-1])
        after = bars_1m[(bars_1m.index > c.idx) & (bars_1m.index.time < WINDOW_END)]
        hit = after[after["high"] >= h_pb + TICK]
        if hit.empty:
            continue
        t_time = hit.index[0]
        t_vol = float(hit["volume"].iloc[0])
        trigger_vol_ratio = t_vol / pb_vpm if pb_vpm > 0 else np.nan
        if not (trigger_vol_ratio >= TRIGGER_VOL_MULT):
            continue

        entry = h_pb + TICK
        stop = c.price - STOP_BUFFER_ATR * atr_15
        R = entry - stop
        if R <= 0 or (R / entry) > MAX_R_PCT:
            continue

        upto = bars_1m[(bars_1m.index <= t_time) & (bars_1m.index.time >= RTH_OPEN)]
        dollar_vol = float((upto["close"] * upto["volume"]).sum())
        leg_index = sum(1 for s in swings[: i + 2] if s.kind == "H")
        pb_ranges = (pb["high"] - pb["low"]) / atr_15
        tb = ("10:30-11:00" if t_time.time() < time(11, 0)
              else "11:00-11:30" if t_time.time() < time(11, 30)
              else "11:30-12:00")

        return Candidate(
            candidate_id=f"{symbol}_{day}_{t_time:%H%M}",
            symbol=symbol, date=day,
            L0_time=a.idx, L0=a.price, H1_time=b.idx, H1=b.price,
            L2_time=c.idx, L2=c.price,
            leg_index=leg_index, depth=depth,
            depth_atr=(b.price - c.price) / atr_15, duration_bars=dur,
            overlap_ratio=overlap_ratio(pb),
            max_pb_bar_range_atr=float(pb_ranges.max()),
            reset_level_type="+".join(sorted(hits)), level_confluence=confluence,
            vwap_distance_atr=(c.price - vwap_at_L2) / atr_15,
            pvr_raw=pvr_raw, pvr_expected=pvr_expected, npvr=npvr,
            trigger_vol_ratio=trigger_vol_ratio,
            spring_ratio=(trigger_vol_ratio / npvr) if npvr and npvr > 0 else np.nan,
            dollar_vol_at_trigger=dollar_vol,
            trigger_time=t_time, trigger_bucket=tb,
            entry=entry, stop=stop, R=R, R_pct=R / entry, R_atr=R / atr_15,
        )
    return None


# ----------------------------------------------------------------------------
# labels -- kept deliberately separate from features
# ----------------------------------------------------------------------------

def forward_labels(bars_1m: pd.DataFrame, entry_time, entry: float,
                   stop: float, next_session_1m: Optional[pd.DataFrame] = None,
                   horizons=(15, 30, 60, 120)) -> dict:
    """MFE/MAE in R at each horizon. NEVER join this to features before modeling."""
    R = entry - stop
    if R <= 0:
        return {}
    fwd = bars_1m[bars_1m.index > entry_time]
    fwd = fwd[fwd.index.time < RTH_CLOSE]
    out: dict = {}

    for h in horizons:
        seg = fwd[fwd.index <= entry_time + pd.Timedelta(minutes=h)]
        if seg.empty:
            out[f"mfe_{h}"] = out[f"mae_{h}"] = np.nan
            continue
        out[f"mfe_{h}"] = (float(seg["high"].max()) - entry) / R
        out[f"mae_{h}"] = (float(seg["low"].min()) - entry) / R

    if not fwd.empty:
        out["mfe_eod"] = (float(fwd["high"].max()) - entry) / R
        out["mae_eod"] = (float(fwd["low"].min()) - entry) / R
        out["ret_eod_R"] = (float(fwd["close"].iloc[-1]) - entry) / R
        out["time_to_mfe"] = int(
            (fwd["high"].idxmax() - entry_time).total_seconds() // 60)
        # did 1R arrive before the stop did?
        up = fwd.index[fwd["high"] >= entry + R]
        dn = fwd.index[fwd["low"] <= stop]
        first_up = up[0] if len(up) else None
        first_dn = dn[0] if len(dn) else None
        out["hit_1R_before_stop"] = bool(
            first_up is not None and (first_dn is None or first_up < first_dn))
        out["stopped"] = bool(first_dn is not None)

    if next_session_1m is not None and not next_session_1m.empty:
        nr = rth(next_session_1m)
        if not nr.empty:
            out["ret_nextopen_R"] = (float(nr["open"].iloc[0]) - entry) / R
            out["ret_nextclose_R"] = (float(nr["close"].iloc[-1]) - entry) / R
    return out


# ----------------------------------------------------------------------------
# exit rules -- score your existing hot key against the alternatives
# ----------------------------------------------------------------------------

def exit_ema9(bars: pd.DataFrame, entry_time, entry: float, stop: float,
              period: int = 9, atr_buffer: float = 0.0,
              atr_val: float = 0.0) -> float:
    """Realized R under 'exit when a bar CLOSES below EMA(period) - buffer'.

    `bars` should be the 5-min or 15-min frame -- this is exactly what the
    Gr8Script EMA9 hot key does today. Pass atr_buffer > 0 to score the v2
    ATR-cushioned variant instead of guessing at it.
    """
    R = entry - stop
    if R <= 0:
        return np.nan
    fwd = bars[bars.index > entry_time]
    fwd = fwd[fwd.index.time < RTH_CLOSE]
    if fwd.empty:
        return np.nan
    ema = fwd["close"].ewm(span=period, adjust=False).mean()
    for ts, row in fwd.iterrows():
        if row["low"] <= stop:                       # hard stop wins ties
            return -1.0
        if row["close"] < ema.loc[ts] - atr_buffer * atr_val:
            return (float(row["close"]) - entry) / R
    return (float(fwd["close"].iloc[-1]) - entry) / R


def exit_fixed_target(bars_1m: pd.DataFrame, entry_time, entry: float,
                      stop: float, target_R: float) -> float:
    R = entry - stop
    fwd = bars_1m[(bars_1m.index > entry_time) & (bars_1m.index.time < RTH_CLOSE)]
    for _, row in fwd.iterrows():
        if row["low"] <= stop:
            return -1.0
        if row["high"] >= entry + target_R * R:
            return target_R
    return (float(fwd["close"].iloc[-1]) - entry) / R if not fwd.empty else np.nan


def to_frame(cands: list[Candidate]) -> pd.DataFrame:
    return pd.DataFrame([asdict(c) for c in cands])
