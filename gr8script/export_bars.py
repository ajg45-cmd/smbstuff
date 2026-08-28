"""Gr8Script — 1-minute bar recorder, for the VWAP continuation exit study.

Runs INSIDE Gr8Trade and writes one CSV per symbol per session. Those CSVs are
the input to the study; nothing else is needed to get a first answer.

WHY EXPORT FROM THE PLATFORM RATHER THAN BUY BARS
-------------------------------------------------
Because it captures the VWAP *you were actually looking at*. Session VWAP
differs between vendors on two choices — whether it starts at 9:30 or includes
premarket, and which venues' prints are counted. Recording Gr8Trade's own VWAP
alongside the bars means every touch in the study is measured against the line
that was on your screen, and the whole class of "the backtest disagrees with
what I saw" problems disappears.

  ┌──────────────────────────────────────────────────────────────┐
  │  ADAPTER — the only part I could not verify.                  │
  │  I do not have Gr8Script API docs, so `fetch_bars()` and      │
  │  `current_vwap()` below are written from the constructs in    │
  │  your EMA9 hot key (md.L1, md.stat, service.add_time_trigger, │
  │  service.write_file). Point me at the real calls and I will   │
  │  correct them — everything outside this block is independent  │
  │  of how they are spelled.                                     │
  └──────────────────────────────────────────────────────────────┘

Two modes:
  RECORD_LIVE   append each minute as it closes. Certain to work, but only
                collects data going forward — start it today.
  DUMP_HISTORY  pull N sessions at startup. Much faster to a first result, but
                depends on the historical accessor your EMA9 script already
                uses for its 9x5-min lookback.
"""

# --- configuration -----------------------------------------------------------
OUT_DIR = r"C:\gr8_export"        # must exist; one CSV per symbol per session
RECORD_LIVE = True
DUMP_HISTORY = False              # flip on once the accessor below is correct
HISTORY_SESSIONS = 60

# Watchlist. Keep it to names that were genuinely in play -- for a first pass
# this can simply be what you traded or watched. A clean universe definition is
# not needed to answer the exit question.
SYMBOLS = ["NVDA", "TSLA", "COIN", "AMD", "META"]

HEADER = ("timestamp,symbol,open,high,low,close,volume,"
          "platform_vwap,cum_volume,bid,ask,session")


# ============================== ADAPTER =====================================
def fetch_bars(md, symbol, minutes=1, sessions=1):
    """Historical `minutes`-bars for `symbol`. RETURN NEWEST LAST.

    Your EMA9 hot key already reads 9 x 5-min bars, so this accessor exists --
    I just don't know its name. Likely one of:

        md.get_bars(symbol, interval=60, count=390 * sessions)
        md.bars(symbol, 60, 390 * sessions)
        md.history(symbol, bar_size=60, lookback=390 * sessions)

    Each element must expose .time .open .high .low .close .volume
    (a tuple in that order is fine -- `row()` below handles both).
    """
    raise NotImplementedError("point this at the accessor your EMA9 script uses")


def current_vwap(md):
    """The platform's own session VWAP for this symbol, right now.

    If Gr8Script does not expose VWAP directly, return None -- the study
    computes its own and reports how far apart the two are. Getting the real
    value here is worth more than any other single line in this file.
    """
    for attr in ("vwap", "session_vwap"):
        v = getattr(getattr(md, "stat", md), attr, None)
        if v is not None:
            return float(v)
    return None
# ============================ END ADAPTER ===================================


def _get(bar, name, idx):
    """Bars may be objects or plain tuples; accept either."""
    if hasattr(bar, name):
        return getattr(bar, name)
    return bar[idx]


def session_of(ts):
    """pre / regular / post, by wall clock."""
    hm = ts.hour * 60 + ts.minute
    if hm < 9 * 60 + 30:
        return "pre"
    if hm < 16 * 60:
        return "regular"
    return "post"


def row(bar, symbol, vwap, cum_vol, bid, ask):
    ts = _get(bar, "time", 0)
    return ",".join(str(x) for x in (
        ts, symbol,
        _get(bar, "open", 1), _get(bar, "high", 2),
        _get(bar, "low", 3), _get(bar, "close", 4), _get(bar, "volume", 5),
        "" if vwap is None else round(float(vwap), 4),
        cum_vol,
        "" if bid is None else bid,
        "" if ask is None else ask,
        session_of(ts),
    ))


def path_for(symbol, ts):
    return "%s\\%s_%s.csv" % (OUT_DIR, symbol, ts.strftime("%Y%m%d"))


class Recorder:
    """One instance per symbol. Appends a line as each minute closes."""

    def __init__(self, symbol):
        self.symbol = symbol
        self.cum_vol = 0
        self.started = False

    def start(self, service, md):
        # premarket matters: the touch tolerance and the enhancers both need it,
        # so the recorder starts at 04:00, not at the opening bell.
        service.add_time_trigger(md.market_open_time - 330 * 60 * 1_000_000,
                                 60 * 1_000_000, timer_id=1)
        self.started = True
        service.info("recording %s -> %s" % (self.symbol, OUT_DIR))

    def on_minute(self, service, md):
        try:
            bars = fetch_bars(md, self.symbol, minutes=1, sessions=1)
        except NotImplementedError:
            service.info("ADAPTER: fetch_bars is not wired up yet")
            return
        if not bars:
            return
        bar = bars[-1]
        self.cum_vol += int(_get(bar, "volume", 5))
        bid = getattr(getattr(md, "L1", None), "bid", None)
        ask = getattr(getattr(md, "L1", None), "ask", None)
        line = row(bar, self.symbol, current_vwap(md), self.cum_vol, bid, ask)

        p = path_for(self.symbol, _get(bar, "time", 0))
        # write_file is assumed to append and to create on first write; if it
        # truncates instead, buffer the lines and flush once at 16:00.
        service.write_file(p, line + "\n", append=True)

    def dump_history(self, service, md):
        bars = fetch_bars(md, self.symbol, minutes=1, sessions=HISTORY_SESSIONS)
        if not bars:
            service.info("no history for %s" % self.symbol)
            return
        by_day, cum = {}, {}
        for b in bars:
            ts = _get(b, "time", 0)
            key = ts.strftime("%Y%m%d")
            cum[key] = cum.get(key, 0) + int(_get(b, "volume", 5))
            # no historical VWAP available -- the study computes and reconciles
            by_day.setdefault(key, []).append(
                row(b, self.symbol, None, cum[key], None, None))
        for key, lines in by_day.items():
            service.write_file("%s\\%s_%s.csv" % (OUT_DIR, self.symbol, key),
                               HEADER + "\n" + "\n".join(lines) + "\n")
        service.info("dumped %d sessions for %s" % (len(by_day), self.symbol))


_recorders = {}


def on_start(service, md, symbol):
    r = _recorders.setdefault(symbol, Recorder(symbol))
    service.write_file(path_for(symbol, md.market_open_time), HEADER + "\n")
    if DUMP_HISTORY:
        r.dump_history(service, md)
    if RECORD_LIVE:
        r.start(service, md)


def on_timer(service, md, symbol, timer_id):
    if timer_id == 1 and RECORD_LIVE:
        _recorders[symbol].on_minute(service, md)
