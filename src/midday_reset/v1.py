"""V1 entry: the 15-min (or 5-min) VWAP continuation, long and short.

Decisions recorded from the trader, 2026-08-28 -- these are answers, not
defaults, and changing one is a deliberate act:

  Liquidity      5,000,000 shares CUMULATIVE at time of entry (not day total).
                 Dollar volume logged alongside so the filter can be swapped.
  Strong open    Defined relative to the name's own norm: first-hour movement
                 larger than usual, measured in ATR, not an absolute percent.
  Premarket high An ENHANCER, not a gate. Logged, never filtered on.
  VWAP touch     Wick through and hold, OR come within 0.10 x daily ATR. It does
                 not have to print the line exactly.
  Window         10:30-12:00 hard for now; widen once there is a result.
  Which signal   The second leg of the FIRST directional program -- so the first
                 qualifying rejection of the day. Later ones are logged and kept
                 in their own bucket, never pooled with the first.
  Direction      Long AND short. Mirrored logic, separate populations, never
                 pooled in a result.
  Concurrency    Multiple positions allowed; still clustered by day for stats.
  Bar frames     5-min and 15-min both, as a crossed axis with the exit frame.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import time
from typing import Optional

import numpy as np
import pandas as pd

from .features import (RTH_OPEN, RTH_CLOSE, OR_END, WINDOW_START, WINDOW_END,
                       TICK, rth, premarket, session_vwap, _mean_vol_per_min,
                       _baseline_vol_per_min, swing_points, ZIGZAG_ATR_MULT)

# --- tunables [T] ------------------------------------------------------------
TOUCH_TOL_ATR = 0.10          # of DAILY atr -- "gets within 0.1 ATR" counts
MIN_CLOSE_POS = 0.50          # closes in the direction of the trend
STOP_BUFFER_ATR = 0.10        # of the bar-frame atr, beyond the signal bar
MIN_CUM_SHARES = 5_000_000    # cumulative at entry
OPEN_MOVE_MIN_ATR = 0.75      # first-hour range vs the name's own ATR
MAX_APPROACH_BARS = 8


def bar_atr(bars: pd.DataFrame, n: int = 14) -> pd.Series:
    prev = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev).abs(),
                    (bars["low"] - prev).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def open_move(bars_1m: pd.DataFrame, atr_d: float) -> dict:
    """'Strong open' = moving more than this name normally moves.

    Relative to its own ATR, not an absolute percent -- a 2% first hour is
    unremarkable in one name and extraordinary in another.
    """
    seg = rth(bars_1m)
    seg = seg[seg.index.time < time(10, 30)]
    if seg.empty or not atr_d:
        return {}
    op = float(seg["open"].iloc[0])
    hi, lo = float(seg["high"].max()), float(seg["low"].min())
    return {
        "open_range_atr": (hi - lo) / atr_d,
        "open_up_atr": (hi - op) / atr_d,
        "open_down_atr": (op - lo) / atr_d,
        "open_close_atr": (float(seg["close"].iloc[-1]) - op) / atr_d,
        "open_is_abnormal": bool((hi - lo) / atr_d >= OPEN_MOVE_MIN_ATR),
    }


def _approach_run(bars: pd.DataFrame, sig_idx, sgn: float,
                  max_bars: int = MAX_APPROACH_BARS) -> pd.DataFrame:
    """The run of bars moving against the trend immediately before the signal.

    Replaces the zigzag pullback as the interval over which volume dry-up is
    measured: no reversal threshold to tune before the study can start.
    """
    pos = bars.index.get_loc(sig_idx)
    col = "high" if sgn > 0 else "low"
    start = pos
    while start - 1 >= 0 and pos - start < max_bars:
        prev, cur = bars[col].iloc[start - 1], bars[col].iloc[start]
        if sgn * (prev - cur) < 0:
            break
        start -= 1
    return bars.iloc[start:pos]


@dataclass
class Signal:
    signal_id: str; symbol: str; date: object; side: str; frame: str
    bar_time: object; signal_index_today: int; is_first_of_day: bool
    # the bar
    bar_open: float; bar_high: float; bar_low: float; bar_close: float
    close_position: float; touch_depth_atr: float; vwap_at_close: float
    wicked_through: bool
    # trend context
    pct_session_with_trend: float; vwap_slope_atr: float
    above_ema9: bool; new_extreme_last_90m: bool; trend_ok: bool
    # enhancers (logged, never gates)
    beyond_pmh: bool; beyond_orh: bool
    open_range_atr: float; open_is_abnormal: bool
    leg_index: int
    # liquidity, point-in-time
    cum_shares_at_entry: float; cum_dollars_at_entry: float; liquid: bool
    # volume signature (kept simple: the RVOL normalization is a later upgrade)
    approach_bars: int; pvr_raw: float; pvr_expected: float; npvr: float
    reject_vol_ratio: float
    # entries and risk
    entry_close: float; stop: float; R: float; R_pct: float; R_atr: float
    entry_break: float; break_time: object; R_break: float


def find_signals(symbol: str, bars_1m: pd.DataFrame, bars: pd.DataFrame,
                 atr_d: float, baseline: pd.Series, side: str = "long",
                 frame: str = "15m", window=(WINDOW_START, WINDOW_END),
                 touch_tol_atr: float = TOUCH_TOL_ATR,
                 min_close_pos: float = MIN_CLOSE_POS,
                 require_trend: bool = True) -> list[Signal]:
    """Every VWAP continuation signal in the window, for one side, one frame.

    Returns ALL of them, flagged by `signal_index_today`. The traded population
    is `is_first_of_day` -- the second leg of the first directional program --
    but the rest are kept so that choice can be checked rather than assumed.

    The touch is tested minute by minute against the CONCURRENT VWAP. Testing a
    low made at 11:03 against the line as it stood at 11:15 is the single
    easiest way to manufacture signals that never existed.
    """
    out: list[Signal] = []
    if bars.empty or bars_1m.empty or not atr_d or np.isnan(atr_d):
        return out
    sgn = 1.0 if side == "long" else -1.0
    step = int(frame.rstrip("m"))
    day = bars.index[0].date()

    vwap = session_vwap(bars_1m)
    pm = premarket(bars_1m)
    pmh = float(pm["high"].max()) if not pm.empty else np.nan
    pml = float(pm["low"].min()) if not pm.empty else np.nan
    atr_b = bar_atr(bars)
    swings = swing_points(bars, ZIGZAG_ATR_MULT * float(atr_b.median()))
    om = open_move(bars_1m, atr_d)
    tol = touch_tol_atr * atr_d

    sess = rth(bars_1m)
    if sess.empty:
        return out
    sess_start = sess.index[0]
    or_seg = sess[sess.index.time < OR_END]
    orh = float(or_seg["high"].max()) if not or_seg.empty else np.nan
    orl = float(or_seg["low"].min()) if not or_seg.empty else np.nan

    n_found = 0
    in_win = bars[(bars.index.time >= window[0]) & (bars.index.time < window[1])]

    for ts, bar in in_win.iterrows():
        end = ts + pd.Timedelta(minutes=step)
        sub = bars_1m[(bars_1m.index >= ts) & (bars_1m.index < end)]
        if sub.empty:
            continue
        vsub = vwap.reindex(sub.index).ffill()

        # against-trend extreme of each minute, relative to the concurrent vwap
        extreme = sub["low"] if sgn > 0 else sub["high"]
        penetration = float((sgn * (extreme - vsub)).min())
        if penetration > tol:                       # never got near the line
            continue

        vwc = float(vwap.asof(min(end, vwap.index[-1])))
        op, hi, lo, cl = (float(bar["open"]), float(bar["high"]),
                          float(bar["low"]), float(bar["close"]))
        if sgn * (cl - vwc) <= 0:                   # must close back on side
            continue
        rng = hi - lo
        cpos = ((cl - lo) if sgn > 0 else (hi - cl)) / rng if rng > 0 else np.nan
        if not (cpos >= min_close_pos):
            continue

        # --- trend state, using only data up to this bar's close --------------
        upto = sess[sess.index < end]
        v_up = vwap.reindex(upto.index)
        pct_with = float((sgn * (upto["close"] - v_up) > 0).mean())
        prior = end - pd.Timedelta(minutes=60)
        vprior = float(vwap.asof(prior)) if prior >= sess_start else np.nan
        slope = (sgn * (vwc - vprior) / atr_d) if not pd.isna(vprior) else np.nan
        b_upto = bars[bars.index < end]
        ema9 = b_upto["close"].ewm(span=9, adjust=False).mean()
        above_ema = bool(len(b_upto) and
                         sgn * (float(b_upto["close"].iloc[-1])
                                - float(ema9.iloc[-1])) > 0)
        late = upto[upto.index.time >= time(9, 45)]
        ext_t = (late["high"].idxmax() if sgn > 0 else late["low"].idxmin()) \
            if not late.empty else None
        new_ext = bool(ext_t is not None and ext_t >= end - pd.Timedelta(minutes=90))
        trend_ok = bool(pct_with >= 0.60 and (slope or 0) > 0 and above_ema)
        if require_trend and not trend_ok:
            continue

        # --- liquidity, point-in-time ----------------------------------------
        cum = sess[sess.index < end]
        cum_sh = float(cum["volume"].sum())
        cum_usd = float((cum["close"] * cum["volume"]).sum())

        # --- volume over the approach ----------------------------------------
        appr = _approach_run(bars, ts, sgn)
        a_start = appr.index[0] if len(appr) else ts - pd.Timedelta(minutes=step)
        a_vpm = _mean_vol_per_min(bars_1m, a_start, ts)
        b_vpm = _mean_vol_per_min(bars_1m, sess_start, a_start)
        pvr_raw = a_vpm / b_vpm if b_vpm > 0 else np.nan
        e_a = _baseline_vol_per_min(baseline, a_start, ts)
        e_b = _baseline_vol_per_min(baseline, sess_start, a_start)
        pvr_exp = (e_a / e_b) if (e_b and e_b > 0) else np.nan
        npvr = pvr_raw / pvr_exp if pvr_exp and pvr_exp > 0 else np.nan
        rej_vpm = float(sub["volume"].sum()) / max(len(sub), 1)

        # --- entries and risk -------------------------------------------------
        stop = (lo - STOP_BUFFER_ATR * float(atr_b.loc[ts])) if sgn > 0 else \
               (hi + STOP_BUFFER_ATR * float(atr_b.loc[ts]))
        R = sgn * (cl - stop)
        if R <= 0:
            continue
        nxt = bars_1m[(bars_1m.index >= end) & (bars_1m.index.time < RTH_CLOSE)]
        lvl = hi + TICK if sgn > 0 else lo - TICK
        brk = nxt[(nxt["high"] >= lvl) if sgn > 0 else (nxt["low"] <= lvl)]
        bt, eb = (brk.index[0], lvl) if len(brk) else (None, np.nan)

        prior_h = [s for s in swings if s.kind == "H" and s.idx < ts]
        prior_l = [s for s in swings if s.kind == "L" and s.idx < ts]

        n_found += 1
        out.append(Signal(
            signal_id=f"{symbol}_{day}_{side}_{frame}_{ts:%H%M}",
            symbol=symbol, date=day, side=side, frame=frame, bar_time=ts,
            signal_index_today=n_found, is_first_of_day=(n_found == 1),
            bar_open=op, bar_high=hi, bar_low=lo, bar_close=cl,
            close_position=cpos, touch_depth_atr=-penetration / atr_d,
            vwap_at_close=vwc, wicked_through=bool(penetration <= 0),
            pct_session_with_trend=pct_with, vwap_slope_atr=slope,
            above_ema9=above_ema, new_extreme_last_90m=new_ext, trend_ok=trend_ok,
            beyond_pmh=bool(sgn * (cl - (pmh if sgn > 0 else pml)) > 0)
                       if not pd.isna(pmh) else False,
            beyond_orh=bool(sgn * (cl - (orh if sgn > 0 else orl)) > 0)
                       if not pd.isna(orh) else False,
            open_range_atr=om.get("open_range_atr", np.nan),
            open_is_abnormal=om.get("open_is_abnormal", False),
            leg_index=len(prior_h) if sgn > 0 else len(prior_l),
            cum_shares_at_entry=cum_sh, cum_dollars_at_entry=cum_usd,
            liquid=bool(cum_sh >= MIN_CUM_SHARES),
            approach_bars=len(appr), pvr_raw=pvr_raw, pvr_expected=pvr_exp,
            npvr=npvr,
            reject_vol_ratio=rej_vpm / a_vpm if a_vpm > 0 else np.nan,
            entry_close=cl, stop=stop, R=R, R_pct=R / cl,
            R_atr=R / float(atr_b.loc[ts]),
            entry_break=eb, break_time=bt,
            R_break=sgn * (eb - stop) if not pd.isna(eb) else np.nan,
        ))
    return out


def to_frame(sigs: list[Signal]) -> pd.DataFrame:
    df = pd.DataFrame([asdict(s) for s in sigs])
    if not df.empty:
        df["day_symbol"] = df["symbol"] + "_" + df["date"].astype(str)
    return df
