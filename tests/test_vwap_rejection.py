"""Contract test for the v1 entry: momentum VWAP continuation.

Covers both sides, all three entry frames, both VWAP anchors, and the gates
added on 08-29 (out of premarket range, beyond all EMAs, EMAs upsloping and
proven by 10:00, and the 21-EMA persistence measure).

Run: python3 tests/test_vwap_rejection.py
"""
import numpy as np
import pandas as pd
from synth import build, flat_baseline, F
from midday_reset import v1

ATR_D = 3.0


def path_at(base):
    """One session, starting from `base`. Ends about 9 higher than it started."""
    def path(m):
        if m < 570: return base + 1.5 * (m - 240) / 330, 900
        if m < 615: return base + 1.5 + 4.0 * (m - 570) / 45, 14000
        if m < 652: return base + 5.5 - 2.3 * (m - 615) / 37, 3000
        if m < 660: return base + 3.2 + 1.4 * (m - 652) / 8, 11000
        if m < 680: return base + 4.6 + 1.9 * (m - 660) / 20, 9000
        if m < 697: return base + 6.5 - 2.6 * (m - 680) / 17, 2800
        if m < 705: return base + 3.9 + 1.5 * (m - 697) / 8, 10000
        return base + 5.4 + 3.6 * (m - 705) / 255, 5000
    return path


def make_ctx(days=6):
    """Several CHAINED sessions, so the continuous EMA21 is real.

    Chained matters: repeating an identical session leaves a large overnight
    gap down every morning, which drags the continuous EMA21 above price and
    fails the long-side EMA gate for reasons that have nothing to do with the
    gate. Each day here starts near where the previous one closed.
    """
    b1s = [build(path_at(100 + 9 * i), day=f"2024-03-{4+i:02d}", seed=20 + i)[0]
           for i in range(days)]
    one = pd.concat([F.rth(b) for b in b1s]).sort_index()
    frames_all = {f: one.resample(f.replace("m", "min")).agg(
        {"open": "first", "high": "max", "low": "min",
         "close": "last", "volume": "sum"}).dropna()
        for f in ("2m", "5m", "10m", "15m")}
    last = b1s[-1]
    day = F.rth(last).index[0].date()
    return v1.SessionCtx(
        symbol="TEST", date=day, bars_1m=last,
        frames={f: c[c.index.date == day] for f, c in frames_all.items()},
        cont={f: c[c.index.date <= day] for f, c in frames_all.items()},
        atr_d=ATR_D, baseline=flat_baseline(last),
        prev_close=float(F.rth(b1s[-2])["close"].iloc[-1]),
        event={"guidance": "raise"})


if __name__ == "__main__":
    ctx = make_ctx()
    got = []
    for f in v1.ENTRY_FRAMES:
        for side in ("long", "short"):
            for anchor in ("rth", "day"):
                sigs = v1.find_signals(ctx, side=side, frame=f,
                                       vwap_anchor=anchor,
                                       require_trend=False,
                                       require_pm_break=False,
                                       require_ema_gate=False)
                got += sigs
                print(f"{side:5s} {f:>3s} {anchor:>3s}: {len(sigs)}")

    df = v1.to_frame(got)
    print()
    if not df.empty:
        print(df[["signal_id", "is_first_of_day", "beyond_pm_range",
                  "beyond_all_emas", "emas_upsloping", "upslope_by_1000",
                  "ema_ribbon_aligned", "pct_beyond_ema21_2m",
                  "pct_beyond_ema21_5m", "clean_90", "gap_pct", "guidance"]]
              .to_string(index=False, float_format=lambda x: f"{x:.3f}"))

    assert got, "expected signals"

    # The two anchors are different lines. On a gap up with real premarket
    # volume the day-anchored VWAP is dragged toward the premarket average and
    # sits well below price, so pullbacks reach it far less often than they
    # reach the 09:30-anchored line. Expect DIFFERENT signal sets -- and
    # sometimes for `day` to select none at all.
    keys = lambda a: {(s.frame, s.side, s.bar_time) for s in got
                      if s.vwap_anchor == a}
    assert keys("rth") != keys("day"), \
        "rth and day anchors selected identical signals -- anchor not applied"
    print(f"\nanchor selection: rth={len(keys('rth'))} day={len(keys('day'))}")

    for s in got:
        assert s.R > 0 and s.entry_close > s.stop if s.side == "long" \
            else s.stop > s.entry_close
        assert s.close_position >= v1.MIN_CLOSE_POS
        assert s.touch_depth_atr >= -v1.TOUCH_TOL_ATR - 1e-9
        assert 0.0 <= s.pct_beyond_ema21_5m <= 1.0 or np.isnan(s.pct_beyond_ema21_5m)
        assert s.guidance == "raise", "event attributes must reach the signal"
        assert not np.isnan(s.gap_pct), "prev_close was supplied, so gap must compute"
        if s.break_time is not None:
            assert s.break_time > s.bar_time, "no entry before its own signal"

    # gates must actually gate
    gated = v1.find_signals(ctx, side="long", frame="15m", vwap_anchor="rth",
                            require_trend=True, require_pm_break=True,
                            require_ema_gate=True)
    ungated = [s for s in got
               if s.side == "long" and s.frame == "15m" and s.vwap_anchor == "rth"]
    assert len(gated) <= len(ungated), "gates cannot add signals"
    for s in gated:
        assert s.beyond_pm_range and s.beyond_all_emas and s.emas_upsloping
    print(f"\ngated {len(gated)} of {len(ungated)} on long/15m/rth")
    print("OK - all assertions passed")
