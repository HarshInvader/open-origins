#!/usr/bin/env python3
"""Write board/TASKS.md from the live board, so people outside the team can pick a task.

The live board (board/board.db) stays private: it holds agent notes with local paths. This file
publishes only task ids, titles, descriptions, dependencies and status, plus one line per landed result.
Run from the repo root: python3 -I board/export_tasks.py
"""
import sqlite3, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
db = sqlite3.connect(ROOT / "board" / "board.db")
db.row_factory = sqlite3.Row
tasks = db.execute("SELECT * FROM tasks ORDER BY prio, id").fetchall()
landed = {r["task"]: r for r in db.execute("SELECT * FROM landed ORDER BY ts")}
status = {t["id"]: t["status"] for t in tasks}
name = ROOT.name.replace("-", " ").title()


def ready(t):
    deps = [d.strip() for d in (t["deps"] or "").split(",") if d.strip()]
    return all(status.get(int(d)) == "done" for d in deps)


def block(t):
    deps = (t["deps"] or "").strip()
    waits = f" Waits for #{deps.replace(',', ', #')}." if deps and not ready(t) else ""
    body = " ".join((t["body"] or "").split())
    return f"### #{t['id']} {t['title']}\n\nMilestone {t['milestone']}, priority {t['prio']}.{waits}\n\n{body}\n"


open_ready = [t for t in tasks if t["status"] == "open" and ready(t)]
open_wait = [t for t in tasks if t["status"] == "open" and not ready(t)]
claimed = [t for t in tasks if t["status"] == "claimed"]
done = [t for t in tasks if t["status"] == "done"]

out = [f"# {name}: open tasks\n",
       f"Exported from the team board on {time.strftime('%d %b %Y').lstrip('0')}. "
       f"{len(open_ready)} ready, {len(open_wait)} waiting on earlier tasks, {len(claimed)} in progress, {len(done)} done.\n",
       "To take one, read [CONTRIBUTING.md](../CONTRIBUTING.md) first: open an issue named `Taking #<id>` so nobody duplicates it.\n",
       "## Ready now\n", *map(block, open_ready),
       "## Waiting on earlier tasks\n", *map(block, open_wait),
       "## In progress (do not duplicate)\n",
       *(f"- #{t['id']} {t['title']}\n" for t in claimed),
       "\n## Done\n",
       *(f"- #{t['id']} {t['title']}: **{landed[t['id']]['verdict'] if t['id'] in landed else 'done'}**"
         f"{', `' + landed[t['id']]['path'] + '`' if t['id'] in landed and landed[t['id']]['path'] else ''}\n" for t in done)]
(ROOT / "board" / "TASKS.md").write_text("\n".join(out).replace("\n\n\n", "\n\n"))
print(f"wrote board/TASKS.md: {len(open_ready)} ready, {len(open_wait)} waiting, {len(claimed)} in progress, {len(done)} done")
