"""Summary tables for the first-green-day study.  Medians lead: the means are
dragged by a handful of 100%+ days and are shown only for contrast."""
import sys, pandas as pd, numpy as np
df = pd.read_csv(sys.argv[1]); br = df[df.broke_within_5]
pd.set_option("display.width", 220, "display.max_columns", 30)

def fgd(g):
    return pd.Series({"n": len(g),
        "high% med": g.fgd_high_pct.median(), "high% mean": g.fgd_high_pct.mean(),
        "close% med": g.fgd_close_pct.median(), "close% mean": g.fgd_close_pct.mean(),
        "high %rally": g.fgd_high_of_rally.median(), "close %rally": g.fgd_close_of_rally.median(),
        "close in range": g.fgd_close_in_range.median(),
        "kept of lift": (g.fgd_close_pct / g.fgd_high_pct).median() * 100,
        "next-day break%": g.broke_next_day.mean() * 100, "break in 5d%": g.broke_within_5.mean() * 100})

def brk(g):
    return pd.Series({"n": len(g), "risk% med": g.risk_pct.median(),
        "mfe d1": g.mfe1_pct.median(), "mfe 3d": g.mfe3_pct.median(), "mfe 5d": g.mfe5_pct.median(), "mfe 10d": g.mfe10_pct.median(),
        "close d1": g.close1_pct.median(), "close 5d": g.close5_pct.median(), "close 10d": g.close10_pct.median(),
        "d1 closes>entry%": g.break_day_close_green.mean() * 100, "5d close>entry%": (g.close5_pct > 0).mean() * 100,
        "mfe5 %rally": g.mfe5_of_rally.median(), "mfe5 R": g.mfe5_R.median(),
        ">=1R in 5d%": (g.mfe5_R >= 1).mean() * 100, ">=2R in 5d%": (g.mfe5_R >= 2).mean() * 100,
        "under FGD low 5d%": g.below_fgd_low_in_5.mean() * 100})

cuts = {"red days before": (df.red_days_before, [-1, 1, 2, 3, 5, 99], ["0-1", "2", "3", "4-5", "6+"]),
        "days peak->FGD": (df.days_peak_to_fgd, [0, 3, 7, 15, 99], ["1-3", "4-7", "8-15", "16+"]),
        "giveback of rally": (df.giveback_pct, [0, 85, 90, 95, 999], ["80-85%", "85-90%", "90-95%", "95%+"]),
        "run size": (df.run_pct, [0, 300, 500, 1000, 1e9], ["200-300%", "300-500%", "500-1000%", "1000%+"])}
print("ALL EVENTS\n", fgd(df).round(1).to_string(), "\n\nAFTER THE BREAK OF FGD HIGH\n", brk(br).round(1).to_string())
for name, (col, bins, labels) in cuts.items():
    k = pd.cut(col, bins, labels=labels)
    print(f"\n=== by {name}: the first green day ===\n", df.groupby(k, observed=True).apply(fgd).round(1).to_string())
    print(f"--- by {name}: after the break ---\n", br.groupby(k[br.index], observed=True).apply(brk).round(1).to_string())
