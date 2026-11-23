"""Download split-adjusted daily bars from Yahoo's chart endpoint into CSVs."""
import sys, time, pathlib, requests, pandas as pd
from seed_tickers import SEED
OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
S = requests.Session(); S.headers["User-Agent"] = "fgd-research-script/0.1"
ok = bad = 0
for t in SEED:
    f = OUT / f"{t}.csv"
    if f.exists(): ok += 1; continue
    for attempt in range(4):
        try:
            r = S.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{t}",
                      params={"period1": 1546300800, "period2": 1900000000, "interval": "1d"}, timeout=30)
        except requests.RequestException:
            time.sleep(2 ** attempt); continue
        if r.status_code == 429: time.sleep(5 * (attempt + 1)); continue
        break
    try:
        res = r.json()["chart"]["result"][0]; q = res["indicators"]["quote"][0]
        df = pd.DataFrame({"date": pd.to_datetime(res["timestamp"], unit="s").date, **{k: q[k] for k in ("open","high","low","close","volume")}}).dropna()
        df.to_csv(f, index=False); ok += 1
    except Exception:
        bad += 1; print("no data", t, r.status_code if 'r' in dir() else '')
    time.sleep(0.25)
print("ok", ok, "missing", bad)
