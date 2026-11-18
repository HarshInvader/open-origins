#!/usr/bin/env python3
"""Shared task board for the agent team (SQLite, safe for concurrent agents).

Usage (run from the repo root):
  python3 -I board/board.py list [--all]          open and claimed tasks (or all)
  python3 -I board/board.py show ID               full task text
  python3 -I board/board.py claim AGENT [ID]      claim ID, or the best open task whose
                                                  dependencies are done; first claim wins
  python3 -I board/board.py add --title T --milestone M --body B
                               [--deps 3,4] [--parent ID] [--prio N] [--by AGENT]
  python3 -I board/board.py done ID --agent A --verdict V --path P --summary S
        V is one of: positive, negative, untestable, data, tool, mixed
  python3 -I board/board.py release ID --agent A --why W    give a task back
  python3 -I board/board.py note AGENT "text"     post to the open notes board
  python3 -I board/board.py notes [N]             last N notes (default 30)
  python3 -I board/board.py landed                log of finished work
"""
import argparse, os, sqlite3, sys, time

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "board.db")
VERDICTS = {"positive", "negative", "untestable", "data", "tool", "mixed"}


def con():
    c = sqlite3.connect(DB, timeout=60, isolation_level=None)
    c.execute("PRAGMA journal_mode=WAL")
    c.executescript("""
    CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY, milestone TEXT, title TEXT,
      body TEXT, deps TEXT DEFAULT '', parent INTEGER, prio INTEGER DEFAULT 5,
      status TEXT DEFAULT 'open', owner TEXT, created_by TEXT, created REAL, claimed REAL, finished REAL);
    CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY, ts REAL, agent TEXT, text TEXT);
    CREATE TABLE IF NOT EXISTS landed(id INTEGER PRIMARY KEY, ts REAL, task INTEGER, agent TEXT,
      verdict TEXT, path TEXT, summary TEXT);
    """)
    return c


def deps_done(c, deps):
    ids = [int(x) for x in deps.split(",") if x.strip()]
    if not ids:
        return True
    q = "SELECT COUNT(*) FROM tasks WHERE status='done' AND id IN (%s)" % ",".join("?" * len(ids))
    return c.execute(q, ids).fetchone()[0] == len(ids)


def stamp(t):
    return time.strftime("%m-%d %H:%M", time.localtime(t)) if t else ""


def main():
    p = argparse.ArgumentParser()
    s = p.add_subparsers(dest="cmd", required=True)
    a = s.add_parser("list"); a.add_argument("--all", action="store_true")
    a = s.add_parser("show"); a.add_argument("id", type=int)
    a = s.add_parser("claim"); a.add_argument("agent"); a.add_argument("id", type=int, nargs="?")
    a = s.add_parser("add")
    for f in ("title", "milestone", "body"):
        a.add_argument("--" + f, required=True)
    a.add_argument("--deps", default=""); a.add_argument("--parent", type=int)
    a.add_argument("--prio", type=int, default=5); a.add_argument("--by", default="lead")
    a = s.add_parser("done"); a.add_argument("id", type=int)
    for f in ("agent", "verdict", "path", "summary"):
        a.add_argument("--" + f, required=True)
    a = s.add_parser("release"); a.add_argument("id", type=int)
    a.add_argument("--agent", required=True); a.add_argument("--why", required=True)
    a = s.add_parser("note"); a.add_argument("agent"); a.add_argument("text")
    a = s.add_parser("notes"); a.add_argument("n", type=int, nargs="?", default=30)
    s.add_parser("landed")
    x = p.parse_args()
    c = con(); now = time.time()

    if x.cmd == "list":
        q = "SELECT id,milestone,prio,status,owner,deps,title FROM tasks"
        if not x.all:
            q += " WHERE status!='done'"
        for r in c.execute(q + " ORDER BY prio,id"):
            ready = "" if r[3] != "open" else (" READY" if deps_done(c, r[5]) else " blocked by " + r[5])
            print(f"#{r[0]} [{r[1]}] p{r[2]} {r[3]}{ready} {r[4] or ''} | {r[6]}")
    elif x.cmd == "show":
        r = c.execute("SELECT * FROM tasks WHERE id=?", (x.id,)).fetchone()
        if not r:
            sys.exit("no such task")
        print(f"#{r[0]} [{r[1]}] {r[2]}\nstatus {r[7]} owner {r[8]} deps '{r[4]}' parent {r[5]} prio {r[6]} by {r[9]}\n\n{r[3]}")
        for l in c.execute("SELECT agent,verdict,path,summary FROM landed WHERE task=?", (x.id,)):
            print(f"\nLANDED by {l[0]}: {l[1]} {l[2]}\n{l[3]}")
    elif x.cmd == "claim":
        c.execute("BEGIN IMMEDIATE")
        if x.id:
            rows = c.execute("SELECT id,deps FROM tasks WHERE id=? AND status='open'", (x.id,)).fetchall()
        else:
            rows = c.execute("SELECT id,deps FROM tasks WHERE status='open' ORDER BY prio,id").fetchall()
        pick = next((r[0] for r in rows if deps_done(c, r[1])), None)
        if pick is None:
            c.execute("ROLLBACK"); print("NOTHING: no open task with finished dependencies"); return
        c.execute("UPDATE tasks SET status='claimed',owner=?,claimed=? WHERE id=?", (x.agent, now, pick))
        c.execute("COMMIT"); print(f"CLAIMED #{pick} for {x.agent}. Read it with: show {pick}")
    elif x.cmd == "add":
        cur = c.execute("INSERT INTO tasks(milestone,title,body,deps,parent,prio,created_by,created) VALUES(?,?,?,?,?,?,?,?)",
                        (x.milestone, x.title, x.body, x.deps, x.parent, x.prio, x.by, now))
        print(f"ADDED #{cur.lastrowid}")
    elif x.cmd == "done":
        if x.verdict not in VERDICTS:
            sys.exit("verdict must be one of " + ", ".join(sorted(VERDICTS)))
        c.execute("BEGIN IMMEDIATE")
        n = c.execute("UPDATE tasks SET status='done',finished=? WHERE id=? AND owner=? AND status='claimed'",
                      (now, x.id, x.agent)).rowcount
        if not n:
            c.execute("ROLLBACK"); sys.exit("not your claimed task")
        c.execute("INSERT INTO landed(ts,task,agent,verdict,path,summary) VALUES(?,?,?,?,?,?)",
                  (now, x.id, x.agent, x.verdict, x.path, x.summary))
        c.execute("COMMIT"); print(f"LANDED #{x.id}")
    elif x.cmd == "release":
        n = c.execute("UPDATE tasks SET status='open',owner=NULL WHERE id=? AND owner=? AND status='claimed'",
                      (x.id, x.agent)).rowcount
        if n:
            c.execute("INSERT INTO notes(ts,agent,text) VALUES(?,?,?)", (now, x.agent, f"released #{x.id}: {x.why}"))
        print("RELEASED" if n else "not your claimed task")
    elif x.cmd == "note":
        c.execute("INSERT INTO notes(ts,agent,text) VALUES(?,?,?)", (now, x.agent, x.text)); print("NOTED")
    elif x.cmd == "notes":
        for r in reversed(c.execute("SELECT ts,agent,text FROM notes ORDER BY id DESC LIMIT ?", (x.n,)).fetchall()):
            print(f"{stamp(r[0])} {r[1]}: {r[2]}")
    elif x.cmd == "landed":
        for r in c.execute("SELECT ts,task,agent,verdict,path,summary FROM landed ORDER BY id"):
            print(f"{stamp(r[0])} #{r[1]} {r[2]} {r[3]} {r[4]}\n    {r[5]}")


if __name__ == "__main__":
    main()
