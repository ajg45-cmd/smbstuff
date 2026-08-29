"""V1 entry: momentum VWAP continuation, long and short, with clean-price-action gates.

Decisions from the trader, 2026-08-28 → 08-29:

  Liquidity        5,000,000 shares CUMULATIVE at time of entry.
  Strong open      Movement larger than normal for the name, measured in ATR.
  Gap direction    BOTH. Gap ups and gap downs are eligible; the sign is logged
                   and sliced, never filtered.
  Premarket range  Entry must be OUT of the premarket range -- above PM high for
                   longs, below PM low for shorts. This is now a GATE. (It was
                   recorded as an enhancer on 08-28; the later instruction
                   supersedes it. `beyond_pm_range` is still logged so the
                   gate-vs-enhancer question stays measurable by re-running with
                   `require_pm_break=False`.)
  VWAP            Session (09:30 anchored) vs Day (premarket included) is a
                   TESTED PARAMETER, not a detail. Both are run.
  EMA gate        The entry bar must close beyond ALL of EMA 5 / 9 / 21 on the
                   entry frame, and every EMA must be upsloping, with that
                   upslope established by the first 30 minutes.
  Cleanliness      Persistence of price beyond the 21 EMA on a fast frame -- the
                   "closes above the 21 EMA 90% of the time" idea, measured
                   rather than eyeballed.
  Frames           5-min, 10-min and 15-min, crossed with the exit frame.
  Guidance         Whether the day-1 report RAISED guidance is carried as an
                   event attribute and sliced. It is not derivable from bars.

CONTINUOUS EMAs -- a correctness point, not a preference
--------------------------------------------------------
A 21-period EMA on 15-minute bars needs 21 bars, which is over five hours. At
10:00 a session-only EMA21 has seen two bars and is meaningless. Charting
platforms compute EMAs on a CONTINUOUS multi-session series, so that is what
the study does: EMAs come from prior sessions plus today, then get reindexed
onto today. Computing them per-session would make every early-session EMA gate
a different (and much weaker) test than the one you are running on your screen.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import time
from typing import Optional

import numpy as np
import pandas as pd

from .features import (RTH_OPEN, RTH_CLOSE, OR_END, WINDOW_START, WINDOW_END,
                       TICK, rth, premarket, session_vwap, _mean_vol_per_min,
                       _baseline_vol_per_min)

# --- tunables [T] ------------------------------------------------------------
TOUCH_TOL_ATR = 0.10          # of DAILY atr -- "gets within 0.1 ATR" counts
MIN_CLOSE_POS = 0.50
STOP_BUFFER_ATR = 0.10
MIN_CUM_SHARES = 5_000_000
OPEN_MOVE_MIN_ATR = 0.75
MAX_APPROACH_BARS = 8

EMA_PERIODS = (5, 9, 21)      # the entry-gate ribbon
CLEAN_EMA = 21                # the persistence yardstick
CLEAN_FRAMES = ("2m", "5m")   # fast frames the persistence is measured on
CLEAN_MIN_PCT = 0.90          # "closes beyond it 90% of the time" [T]
UPSLOPE_BY = time(10, 0)      # "proven by the first 30 minutes"
ENTRY_FRAMES = ("5m", "10m", "15m")


def bar_atr(bars: pd.DataFrame, n: int = 14) -> pd.Series:
    prev = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev).abs(),
                    (bars["low"] - prev).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def emas(bars_cont: pd.DataFrame, periods=EMA_PERIODS) -> pd.DataFrame:
    """EMAs on the CONTINUOUS series -- see the module docstring."""
    return pd.DataFrame({p: bars_cont["close"].ewm(span=p, adjust=False).mean()
                         for p in periods})


@dataclass
class SessionCtx:
    """Everything one session needs, built once and reused across sides/frames."""
    symbol: str
    date: object
    bars_1m: pd.DataFrame
    frames: dict                      # "2m"/"5m"/"10m"/"15m" -> today's bars
    cont: dict                        # same keys -> prior sessions + today
    atr_d: float
    baseline: pd.Series
    prev_close: Optional[float] = None
    event: dict = field(default_factory=dict)   # guidance, surprise, ...

    def vwap(self, anchor: str) -> pd.Series:
        return session_vwap(self.bars_1m, anchor=anchor)


def open_move(bars_1m: pd.DataFrame, atr_d: float) -> dict:
    """'Strong open' = moving more than this name normally moves, in ATR."""
    seg = rth(bars_1m)
    seg = seg[seg.index.time < time(10, 30)]
    if seg.empty or not atr_d:
        return {}
    op = float(seg["open"].iloc[0])
    hi, lo = float(seg["high"].max()), float(seg["low"].min())
    return {"open_range_atr": (hi - lo) / atr_d,
            "open_is_abnormal": bool((hi - lo) / atr_d >= OPEN_MOVE_MIN_ATR)}


def clean_persistence(ctx: SessionCtx, as_of, sgn: float) -> dict:
    """Fraction of fast-frame bars that CLOSED beyond the 21 EMA, since 09:30.

    This is the mechanical version of "it closes above the 21 EMA 90% of the
    time" -- a persistence measure rather than a snapshot. A name that has spent
    the whole morning on one side of its 21 EMA is trending cleanly; one that
    keeps crossing it is chopping, whatever it happens to be doing right now.
    """
    out = {}
    for f in CLEAN_FRAMES:
        bars, cont = ctx.frames.get(f), ctx.cont.get(f)
        if bars is None or cont is None or bars.empty:
            out[f"pct_beyond_ema{CLEAN_EMA}_{f}"] = np.nan
            continue
        e = cont["close"].ewm(span=CLEAN_EMA, adjust=False).mean().reindex(bars.index)
        seg = bars[(bars.index.time >= RTH_OPEN) & (bars.index < as_of)]
        if seg.empty:
            out[f"pct_beyond_ema{CLEAN_EMA}_{f}"] = np.nan
            continue
        beyond = sgn * (seg["close"] - e.reindex(seg.index)) > 0
        out[f"pct_beyond_ema{CLEAN_EMA}_{f}"] = float(beyond.mean())
    return out


def ema_state(ctx: SessionCtx, frame: str, as_of, sgn: float) -> dict:
    """The entry-frame EMA gates: beyond all, all sloping, slope proven early."""
    bars, cont = ctx.frames.get(frame), ctx.cont.get(frame)
    if bars is None or cont is None or bars.empty:
        return {}
    e = emas(cont).reindex(bars.index)
    upto = bars[bars.index < as_of]
    if upto.empty or e.loc[upto.index].isna().all().all():
        return {}
    ts = upto.index[-1]
    close = float(upto["close"].iloc[-1])
    row = e.loc[ts]

    beyond_all = bool(all(sgn * (close - float(row[p])) > 0 for p in EMA_PERIODS))
    slopes = e.diff().loc[ts]
    upsloping = bool(all(sgn * float(slopes[p]) > 0 for p in EMA_PERIODS
                         if not pd.isna(slopes[p])))
    # ribbon in order: 5 above 9 above 21 for a long
    ribbon = bool(all(sgn * (float(row[EMA_PERIODS[i]])
                             - float(row[EMA_PERIODS[i + 1]])) > 0
                      for i in range(len(EMA_PERIODS) - 1)))

    early = upto[upto.index.time <= UPSLOPE_BY]
    if len(early):
        es = e.diff().loc[early.index[-1]]
        upslope_early = bool(all(sgn * float(es[p]) > 0 for p in EMA_PERIODS
                                 if not pd.isna(es[p])))
    else:
        upslope_early = False

    return {"beyond_all_emas": beyond_all, "emas_upsloping": upsloping,
            "ema_ribbon_aligned": ribbon, "upslope_by_1000": upslope_early,
            "dist_ema21_atr": (close - float(row[21])) / ctx.atr_d
                              if ctx.atr_d else np.nan}


def _approach_run(bars: pd.DataFrame, sig_idx, sgn: float,
                  max_bars: int = MAX_APPROACH_BARS) -> pd.DataFrame:
    pos = bars.index.get_loc(sig_idx)
    col = "high" if sgn > 0 else "low"
    start = pos
    while start - 1 >= 0 and pos - start < max_bars:
        if sgn * (bars[col].iloc[start - 1] - bars[col].iloc[start]) < 0:
            break
        start -= 1
    return bars.iloc[start:pos]


@dataclass
class Signal:
    signal_id: str; symbol: str; date: object; side: str; frame: str
    vwap_anchor: str
    bar_time: object; signal_index_today: int; is_first_of_day: bool
    bar_open: float; bar_high: float; bar_low: float; bar_close: float
    close_position: float; touch_depth_atr: float; vwap_at_close: float
    wicked_through: bool
    # trend + momentum gates
    pct_session_with_trend: float; vwap_slope_atr: float
    beyond_all_emas: bool; emas_upsloping: bool; ema_ribbon_aligned: bool
    upslope_by_1000: bool; dist_ema21_atr: float
    pct_beyond_ema21_2m: float; pct_beyond_ema21_5m: float; clean_90: bool
    # premarket range
    beyond_pm_range: bool; pm_break_atr: float
    # catalyst / context, logged and sliced, never filtered
    gap_pct: float; gap_direction: str; guidance: str
    open_range_atr: float; open_is_abnormal: bool
    # liquidity
    cum_shares_at_entry: float; cum_dollars_at_entry: float; liquid: bool
    # volume signature
    approach_bars: int; pvr_raw: float; npvr: float; reject_vol_ratio: float
    # entries and risk
    entry_close: float; stop: float; R: float; R_pct: float; R_atr: float
    entry_break: float; break_time: object


def find_signals(ctx: SessionCtx, side: str = "long", frame: str = "15m",
                 vwap_anchor: str = "rth", window=(WINDOW_START, WINDOW_END),
                 touch_tol_atr: float = TOUCH_TOL_ATR,
                 min_close_pos: float = MIN_CLOSE_POS,
                 require_trend: bool = True,
                 require_pm_break: bool = True,
                 require_ema_gate: bool = True) -> list[Signal]:
    """Every qualifying signal in the window, for one side / frame / VWAP anchor.

    Returns all of them, flagged by `signal_index_today`; the traded population
    is `is_first_of_day`. Gates are switchable so the filter ladder can measure
    what each one is worth instead of assuming it.

    The VWAP touch is tested minute by minute against the CONCURRENT VWAP.
    """
    out: list[Signal] = []
    bars = ctx.frames.get(frame)
    if bars is None or bars.empty or not ctx.atr_d or np.isnan(ctx.atr_d):
        return out
    sgn = 1.0 if side == "long" else -1.0
    step = int(frame.rstrip("m"))

    vwap = ctx.vwap(vwap_anchor)
    pm = premarket(ctx.bars_1m)
    pmh = float(pm["high"].max()) if not pm.empty else np.nan
    pml = float(pm["low"].min()) if not pm.empty else np.nan
    pm_edge = pmh if sgn > 0 else pml
    atr_b = bar_atr(bars)
    om = open_move(ctx.bars_1m, ctx.atr_d)
    tol = touch_tol_atr * ctx.atr_d

    sess = rth(ctx.bars_1m)
    if sess.empty:
        return out
    sess_start = sess.index[0]
    gap = ((float(sess["open"].iloc[0]) - ctx.prev_close) / ctx.prev_close
           if ctx.prev_close else np.nan)

    n_found = 0
    in_win = bars[(bars.index.time >= window[0]) & (bars.index.time < window[1])]

    for ts, bar in in_win.iterrows():
        end = ts + pd.Timedelta(minutes=step)
        sub = ctx.bars_1m[(ctx.bars_1m.index >= ts) & (ctx.bars_1m.index < end)]
        if sub.empty:
            continue
        vsub = vwap.reindex(sub.index).ffill()

        extreme = sub["low"] if sgn > 0 else sub["high"]
        penetration = float((sgn * (extreme - vsub)).min())
        if penetration > tol:
            continue

        vwc_src = vwap[vwap.index < end]
        if vwc_src.empty:
            continue
        vwc = float(vwc_src.iloc[-1])
        op, hi, lo, cl = (float(bar["open"]), float(bar["high"]),
                          float(bar["low"]), float(bar["close"]))
        if sgn * (cl - vwc) <= 0:
            continue
        rng = hi - lo
        cpos = ((cl - lo) if sgn > 0 else (hi - cl)) / rng if rng > 0 else np.nan
        if not (cpos >= min_close_pos):
            continue

        # --- out of the premarket range (gate) --------------------------------
        beyond_pm = bool(sgn * (cl - pm_edge) > 0) if not pd.isna(pm_edge) else False
        pm_break_atr = (sgn * (cl - pm_edge) / ctx.atr_d
                        if not pd.isna(pm_edge) and ctx.atr_d else np.nan)
        if require_pm_break and not beyond_pm:
            continue

        # --- momentum: beyond every EMA, all upsloping, proven early ----------
        es = ema_state(ctx, frame, end, sgn)
        if not es:
            continue
        if require_ema_gate and not (es["beyond_all_emas"]
                                     and es["emas_upsloping"]
                                     and es["upslope_by_1000"]):
            continue

        # --- trend state ------------------------------------------------------
        upto = sess[sess.index < end]
        v_up = vwap.reindex(upto.index)
        pct_with = float((sgn * (upto["close"] - v_up) > 0).mean())
        prior = end - pd.Timedelta(minutes=60)
        vp = vwap[vwap.index <= prior]
        slope = (sgn * (vwc - float(vp.iloc[-1])) / ctx.atr_d) if len(vp) else np.nan
        if require_trend and not (pct_with >= 0.60 and (slope or 0) > 0):
            continue

        cp = clean_persistence(ctx, end, sgn)
        clean90 = bool(max([v for v in cp.values() if not pd.isna(v)] or [0])
                       >= CLEAN_MIN_PCT)

        cum = sess[sess.index < end]
        cum_sh, cum_usd = (float(cum["volume"].sum()),
                           float((cum["close"] * cum["volume"]).sum()))

        appr = _approach_run(bars, ts, sgn)
        a_start = appr.index[0] if len(appr) else ts - pd.Timedelta(minutes=step)
        a_vpm = _mean_vol_per_min(ctx.bars_1m, a_start, ts)
        b_vpm = _mean_vol_per_min(ctx.bars_1m, sess_start, a_start)
        pvr_raw = a_vpm / b_vpm if b_vpm > 0 else np.nan
        e_a = _baseline_vol_per_min(ctx.baseline, a_start, ts)
        e_b = _baseline_vol_per_min(ctx.baseline, sess_start, a_start)
        pexp = (e_a / e_b) if (e_b and e_b > 0) else np.nan
        npvr = pvr_raw / pexp if pexp and pexp > 0 else np.nan
        rej_vpm = float(sub["volume"].sum()) / max(len(sub), 1)

        stop = (lo - STOP_BUFFER_ATR * float(atr_b.loc[ts])) if sgn > 0 else \
               (hi + STOP_BUFFER_ATR * float(atr_b.loc[ts]))
        R = sgn * (cl - stop)
        if R <= 0:
            continue
        nxt = ctx.bars_1m[(ctx.bars_1m.index >= end)
                          & (ctx.bars_1m.index.time < RTH_CLOSE)]
        lvl = hi + TICK if sgn > 0 else lo - TICK
        brk = nxt[(nxt["high"] >= lvl) if sgn > 0 else (nxt["low"] <= lvl)]
        bt, eb = (brk.index[0], lvl) if len(brk) else (None, np.nan)

        n_found += 1
        out.append(Signal(
            signal_id=f"{ctx.symbol}_{ctx.date}_{side}_{frame}_{vwap_anchor}_{ts:%H%M}",
            symbol=ctx.symbol, date=ctx.date, side=side, frame=frame,
            vwap_anchor=vwap_anchor, bar_time=ts,
            signal_index_today=n_found, is_first_of_day=(n_found == 1),
            bar_open=op, bar_high=hi, bar_low=lo, bar_close=cl,
            close_position=cpos, touch_depth_atr=-penetration / ctx.atr_d,
            vwap_at_close=vwc, wicked_through=bool(penetration <= 0),
            pct_session_with_trend=pct_with, vwap_slope_atr=slope,
            beyond_all_emas=es["beyond_all_emas"],
            emas_upsloping=es["emas_upsloping"],
            ema_ribbon_aligned=es["ema_ribbon_aligned"],
            upslope_by_1000=es["upslope_by_1000"],
            dist_ema21_atr=es["dist_ema21_atr"],
            pct_beyond_ema21_2m=cp.get("pct_beyond_ema21_2m", np.nan),
            pct_beyond_ema21_5m=cp.get("pct_beyond_ema21_5m", np.nan),
            clean_90=clean90,
            beyond_pm_range=beyond_pm, pm_break_atr=pm_break_atr,
            gap_pct=gap,
            gap_direction=("up" if (gap or 0) > 0 else
                           "down" if (gap or 0) < 0 else "flat"),
            guidance=str(ctx.event.get("guidance", "unknown")),
            open_range_atr=om.get("open_range_atr", np.nan),
            open_is_abnormal=om.get("open_is_abnormal", False),
            cum_shares_at_entry=cum_sh, cum_dollars_at_entry=cum_usd,
            liquid=bool(cum_sh >= MIN_CUM_SHARES),
            approach_bars=len(appr), pvr_raw=pvr_raw, npvr=npvr,
            reject_vol_ratio=rej_vpm / a_vpm if a_vpm > 0 else np.nan,
            entry_close=cl, stop=stop, R=R, R_pct=R / cl,
            R_atr=R / float(atr_b.loc[ts]),
            entry_break=eb, break_time=bt,
        ))
    return out


def to_frame(sigs: list[Signal]) -> pd.DataFrame:
    df = pd.DataFrame([asdict(s) for s in sigs])
    if not df.empty:
        df["day_symbol"] = df["symbol"] + "_" + df["date"].astype(str)
    return df
