# 09 — Getting the data to Claude automatically

There is no "connect Gr8Trade" button. It is a desktop application behind your
firm's authentication, with no API a cloud session could authenticate against.
Anything that claims otherwise would be guessing.

What *can* be automatic is everything after the export: set it up once and you
never move a file again.

## The actual blocker is not the connection

Even a perfect pipe moves nothing until `gr8script/export_bars.py` can read
bars. Two calls in its ADAPTER block are written from the constructs in your
EMA9 hot key, not from documentation:

```python
fetch_bars(md, symbol, minutes=1, sessions=1)   # <- needs the real name
current_vwap(md)                                 # <- returns None if absent
```

Your hot key already reads 9 × 5-min bars for its EMA, so the accessor exists.
**Paste that part of the script and this is a five-minute fix.** Everything
below is plumbing around it.

---

## Option A — point the exporter at a synced folder (simplest by far)

One line, no scripts, no git.

1. Install **Google Drive for Desktop** on the trading machine.
2. In `gr8script/export_bars.py`:

   ```python
   OUT_DIR = r"C:\Users\<you>\My Drive\gr8_export"
   ```

3. That's it. Drive syncs each session file as it is written, and Claude reads
   them through the Drive connector.

Trade-off: files land in Drive as they are written, so the current day's file is
partial until the close. The loader does not care — it reads whatever rows are
there — but a mid-session file is a mid-session sample, so don't draw
conclusions from a day that hasn't finished.

## Option B — scheduled push to the repo

`scripts/autopush.ps1` copies completed sessions into `data/samples/` and
pushes. Edit the three paths at the top, run it once by hand, then register the
scheduled task (the command is in the file's footer). It runs weekdays at 17:15
so the day's file is complete first, skips today's file before the close, only
copies what changed, and retries a failed push with backoff.

This is the more disciplined option: the data is versioned alongside the code
that reads it, so a result can always be traced to the exact bars it came from.

## Option C — Claude Code on the trading machine

Install Claude Code on the Windows box and clone the repo there. Then there is
no transport at all — the export folder is just local files, and Claude reads
`C:\gr8_export` directly and iterates against your full history.

Best long-term, and it removes the export-and-upload loop entirely. The catch
is that the work then lives on that machine, so combine it with Option B if you
also want the data reachable from a web session.

---

## Recommended

**A + B.** Point `OUT_DIR` at a Drive-synced folder so nothing is ever lost, and
run the scheduled push so completed sessions land in the repo where they are
versioned. Between them, the data reaches Claude whether it is running locally,
in a web session, or here.

## Verify it worked

The first thing to check is not that files arrived — it is that they are the
right files:

```
python3 scripts/run_study.py data/samples --out results
```

The VWAP reconciliation runs first and prints how far the computed VWAP sits
from Gr8Trade's own. If that number is large, the exports are fine but the
study is measuring touches against the wrong line, and that has to be settled
before any result means anything.
