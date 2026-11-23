"""First Green Day on the backside of low-float runners -- daily-bar study.

Definitions (all on split-adjusted daily bars):

RUN      peak-day high >= RUN_MULT x the lowest low of the prior BASE_LOOKBACK
         trading days, and peak-day dollar volume >= MIN_DVOL.  The peak must
         stand: no higher high before the giveback below is reached.
RALLY    peak high - base low, in points.
BACKSIDE first day whose low has given back >= GIVEBACK of the rally,
         within MAX_FADE days of the peak.
FGD      first day on/after that with close > open AND close > prior close.
BREAK    first day in the next BREAK_WINDOW sessions that trades above the FGD
         high.  Entry = max(FGD high, that day's open) -- gaps fill at the open.

Daily bars cannot order the high and low inside one session, so "stopped
before target" on the break day itself is unknowable here and is not claimed.
"""
import sys, pathlib, numpy as np, pandas as pd

RUN_MULT, BASE_LOOKBACK, MIN_DVOL = 3.0, 20, 10e6
GIVEBACK, MAX_FADE, BREAK_WINDOW = 0.80, 60, 5


def events(sym, d):
    o, h, l, c, v = (d[k].to_numpy(float) for k in ("open", "high", "low", "close", "volume"))
    n, out, i = len(d), [], BASE_LOOKBACK
    while i < n:
        w0 = i - BASE_LOOKBACK
        b = w0 + int(np.argmin(l[w0:i + 1]))
        base = l[b]
        if l[b] < 0.4 * min(o[b], c[b]):               # bad print in the base bar
            i += 1; continue
        if not (base > 0 and b < i and h[i] >= RUN_MULT * base and h[i] >= h[w0:i + 1].max()
                and c[i] * v[i] >= MIN_DVOL):
            i += 1; continue
        rally, thr = h[i] - base, h[i] - GIVEBACK * (h[i] - base)
        d1 = None
        for j in range(i + 1, min(n, i + 1 + MAX_FADE)):
            if h[j] > h[i]: break                      # higher high: not the peak
            if l[j] <= thr: d1 = j; break
        if d1 is None:
            i += 1; continue
        g = next((j for j in range(d1, min(n, d1 + MAX_FADE)) if c[j] > o[j] and c[j] > c[j - 1]), None)
        if g is None:
            i = d1 + 1; continue
        red = 0
        while g - 1 - red > i and c[g - 1 - red] < c[g - 2 - red]: red += 1
        pc = c[g - 1]
        ev = dict(symbol=sym, peak_date=d.date[i], fgd_date=d.date[g],
                  run_pct=100 * (h[i] / base - 1), run_days=i - b,
                  peak_dvol_m=c[i] * v[i] / 1e6, days_peak_to_fgd=g - i, red_days_before=red,
                  giveback_pct=100 * (h[i] - l[i + 1:g + 1].min()) / rally,
                  # the first green day itself
                  fgd_high_pct=100 * (h[g] / pc - 1), fgd_close_pct=100 * (c[g] / pc - 1),
                  fgd_low_to_high_pct=100 * (h[g] / l[g] - 1),
                  fgd_high_of_rally=100 * (h[g] - pc) / rally, fgd_close_of_rally=100 * (c[g] - pc) / rally,
                  fgd_close_in_range=100 * (c[g] - l[g]) / (h[g] - l[g]) if h[g] > l[g] else np.nan,
                  fgd_relvol=v[g] / max(v[max(i + 1, g - 5):g].mean(), 1) if g > i + 1 else np.nan)
        # the break of the first green day's high
        k = next((j for j in range(g + 1, min(n, g + 1 + BREAK_WINDOW)) if h[j] > h[g]), None)
        if g + 1 < n:
            ev["next_high_pct"] = 100 * (h[g + 1] / c[g] - 1); ev["next_close_pct"] = 100 * (c[g + 1] / c[g] - 1)
        ev["broke_next_day"] = bool(g + 1 < n and h[g + 1] > h[g])
        ev["broke_within_5"] = k is not None
        ev["lost_fgd_low_first"] = bool(l[g + 1:(k if k is not None else min(n, g + 1 + BREAK_WINDOW))].min(initial=np.inf) < l[g])
        if k is not None:
            e = max(h[g], o[k]); ev["break_date"] = d.date[k]
            ev["risk_pct"] = 100 * (e / l[g] - 1)                     # entry down to FGD low
            for N in (1, 3, 5, 10):
                seg = slice(k, min(n, k + N))
                ev[f"mfe{N}_pct"] = 100 * (h[seg].max() / e - 1)
                ev[f"close{N}_pct"] = 100 * (c[seg][-1] / e - 1)
            ev["mfe5_of_rally"] = 100 * (h[k:min(n, k + 5)].max() - e) / rally
            ev["mfe5_R"] = (h[k:min(n, k + 5)].max() - e) / (e - l[g]) if e > l[g] else np.nan
            ev["below_fgd_low_in_5"] = bool(l[k:min(n, k + 5)].min() < l[g])
            ev["break_day_close_green"] = bool(c[k] > e)
        out.append(ev)
        i = g + 1
    return out


def main(bars_dir, out_csv):
    rows = []
    for f in sorted(pathlib.Path(bars_dir).glob("*.csv")):
        d = pd.read_csv(f)
        d = d[(d.volume > 0) & (d.low > 0)].reset_index(drop=True)
        if len(d) > BASE_LOOKBACK + 5: rows += events(f.stem, d)
    df = pd.DataFrame(rows).sort_values("peak_date").reset_index(drop=True)
    df.to_csv(out_csv, index=False)
    print(len(df), "events,", df.symbol.nunique(), "symbols ->", out_csv)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
