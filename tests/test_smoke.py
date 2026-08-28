"""End-to-end smoke test on a hand-built session.

Not a market test -- a contract test. It asserts that the pipeline detects the
leg structure, resets against a level, measures the volume dry-up, triggers,
and produces a labelled trade. Run: python3 tests/test_smoke.py
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from midday_reset import features as F

def synth_session(day="2024-03-05"):
    idx = pd.date_range(f"{day} 04:00", f"{day} 15:59", freq="1min", tz="US/Eastern")
    n = len(idx)
    price = np.full(n, 100.0)
    vol = np.full(n, 3000.0)
    t = pd.Series(idx.time, index=range(n))
    for i, ts in enumerate(idx):
        m = ts.hour*60 + ts.minute
        if m < 570:                      # premarket: drift to 101.5 (PMH ~101.5)
            price[i] = 100 + 1.5*(m-240)/330; vol[i] = 800
        elif m < 630:                    # 9:30-10:30 impulse 101.5 -> 106
            price[i] = 101.5 + 4.5*(m-570)/60; vol[i] = 12000
        elif m < 675:                    # 10:30-11:15 pullback 106 -> 103.6, DRY
            price[i] = 106 - 2.4*(m-630)/45; vol[i] = 2200
        elif m < 690:                    # 11:15-11:30 resumption, expansion
            price[i] = 103.6 + 3.0*(m-675)/15; vol[i] = 16000
        else:
            price[i] = 106.6 + 2.0*(m-690)/270; vol[i] = 6000
    noise = np.random.default_rng(1).normal(0, 0.03, n)
    close = price + noise
    df = pd.DataFrame({"open": close, "close": close,
                       "high": close+0.05, "low": close-0.05,
                       "volume": vol}, index=idx)
    return df

b1 = synth_session()
r = F.rth(b1)
b15 = r.resample("15min").agg({"open":"first","high":"max","low":"min",
                               "close":"last","volume":"sum"}).dropna()
daily = pd.DataFrame({"open":[99,100],"high":[101,107],"low":[98,99],
                      "close":[100,106],"volume":[5e6,3e7]},
                     index=pd.to_datetime(["2024-03-04","2024-03-05"]))
atr_d = float(F.atr(daily, n=2).iloc[-1])
atr15 = float((b15["high"]-b15["low"]).mean())
print(f"atr_d={atr_d:.2f} atr15={atr15:.2f}")

# baseline built from a flat prior session -> pvr_expected ~ 1
hist = synth_session("2024-03-04")
hist.index = hist.index - pd.Timedelta(days=1)
hist["volume"] = 5000.0
base = F.volume_baseline(hist)

vw = F.session_vwap(b1)
pmh = float(F.premarket(b1)["high"].max())
print("PMH", round(pmh,2), "cleared:", F.pmh_cleared_and_held(b15, pmh))
print("open_strength:", {k: (round(v,3) if isinstance(v,float) else v)
                         for k,v in F.open_strength(b1, vw, pmh, atr_d).items()})
sw = F.swing_points(b15, F.ZIGZAG_ATR_MULT*atr15)
print("swings:", [(s.kind, str(s.idx.time()), round(s.price,2)) for s in sw])

c = F.find_candidate("TEST", b1, b15, atr_d, atr15, base,
                     levels_extra={"ORH": 103.71, "PDH": 101.0})
if c is None:
    print("NO CANDIDATE")
else:
    for k, v in vars(c).items():
        print(f"  {k:24s} {round(v,4) if isinstance(v,float) else v}")
    lab = F.forward_labels(b1, c.trigger_time, c.entry, c.stop)
    print("labels:", {k:(round(v,2) if isinstance(v,float) else v) for k,v in lab.items()})
    print("exit EMA9(15m):", round(F.exit_ema9(b15, c.trigger_time, c.entry, c.stop),3))
    print("exit 2R       :", round(F.exit_fixed_target(b1, c.trigger_time, c.entry, c.stop, 2.0),3))

    # --- contract assertions --------------------------------------------------
    assert c is not None, "expected a candidate on the synthetic session"
    assert [s.kind for s in sw] == ["L", "H", "L"], "zigzag must not flip intrabar"
    assert len({s.idx for s in sw}) == 3, "swings must sit on distinct bars"
    assert 0.20 <= c.depth <= 0.70
    assert c.npvr < 0.5, "the pullback was built dry; npvr must reflect it"
    assert c.trigger_vol_ratio >= F.TRIGGER_VOL_MULT
    assert c.entry > c.stop and c.R_pct <= F.MAX_R_PCT
    assert c.trigger_time > c.L2_time, "no entry before the pullback low"
    assert lab["mfe_60"] > 0 and lab["hit_1R_before_stop"] is True
    print("\nOK - all assertions passed")
