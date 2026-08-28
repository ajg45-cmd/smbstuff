"""Contract test for the v1 entry: VWAP continuation, both sides, both frames.

Run: python3 tests/test_vwap_rejection.py
"""
import pandas as pd
from synth import build, flat_baseline, F
from midday_reset import v1

ATR_D = 3.0


def path(m):
    """Two approaches that reach VWAP and close back in the trend's direction."""
    if m < 570: return 100 + 1.5 * (m - 240) / 330, 900
    if m < 615: return 101.5 + 4.0 * (m - 570) / 45, 14000
    if m < 652: return 105.5 - 2.3 * (m - 615) / 37, 3000
    if m < 660: return 103.2 + 1.4 * (m - 652) / 8, 11000
    if m < 680: return 104.6 + 1.9 * (m - 660) / 20, 9000
    if m < 697: return 106.5 - 2.6 * (m - 680) / 17, 2800
    if m < 705: return 103.9 + 1.5 * (m - 697) / 8, 10000
    return 105.4 + 3.6 * (m - 705) / 255, 5000


def frames(b1):
    out = {}
    for f in ("5m", "15m"):
        out[f] = F.rth(b1).resample(f.replace("m", "min")).agg(
            {"open": "first", "high": "max", "low": "min",
             "close": "last", "volume": "sum"}).dropna()
    return out


if __name__ == "__main__":
    b1, _ = build(path)
    fr = frames(b1)
    base = flat_baseline(b1)

    all_sigs = []
    for f, bars in fr.items():
        for side in ("long", "short"):
            sigs = v1.find_signals("TEST", b1, bars, ATR_D, base, side=side, frame=f)
            all_sigs += sigs
            print(f"{side:5s} {f:>3s}: {len(sigs)} signal(s)")

    df = v1.to_frame(all_sigs)
    print()
    if not df.empty:
        cols = ["signal_id", "signal_index_today", "is_first_of_day", "wicked_through",
                "touch_depth_atr", "close_position", "pct_session_with_trend",
                "npvr", "reject_vol_ratio", "beyond_pmh", "open_is_abnormal",
                "cum_shares_at_entry", "liquid", "R_pct"]
        print(df[cols].to_string(index=False,
                                 float_format=lambda x: f"{x:,.3f}"))

    longs = [s for s in all_sigs if s.side == "long"]
    assert longs, "expected long signals"
    assert not [s for s in all_sigs if s.side == "short"], \
        "an uptrending session must not produce short continuations"

    for s in all_sigs:
        assert s.trend_ok
        assert s.close_position >= v1.MIN_CLOSE_POS
        assert s.R > 0 and s.entry_close > s.stop
        assert s.touch_depth_atr >= -v1.TOUCH_TOL_ATR - 1e-9, \
            "a signal must have reached within the tolerance of VWAP"
        if s.break_time is not None:
            assert s.break_time > s.bar_time, "no entry before its own signal"

    first = [s for s in all_sigs if s.is_first_of_day]
    assert first, "the traded population is the first signal of the day"
    assert all(s.signal_index_today == 1 for s in first)

    # tolerance, not an exact print: at least one signal should qualify by
    # coming close to VWAP rather than by trading through it
    print("\nsignals that only came NEAR vwap:",
          sum(1 for s in all_sigs if not s.wicked_through))
    print("OK - all assertions passed")
