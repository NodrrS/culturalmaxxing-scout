"""Where runs, their step logs and the human decisions are kept.

Everything is a plain file under scout/runs/, which is never committed:

  runs/YYYY-MM-DD/HHMMSS-find.json            the records of one run
  runs/YYYY-MM-DD/HHMMSS-find.events.jsonl    every step, for the replay
  runs/decisions.jsonl                        what a person decided, one line each

The files about real shops (the registry, the seeds and the hand-judged ground
truth) are read from data/, or from the folder in SCOUT_DATA. Git ignores them.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
from pathlib import Path

HERE = Path(__file__).parent
RUNS = HERE / "runs"
SAMPLE = HERE / "web" / "sample-run.json"
DATA = Path(os.environ.get("SCOUT_DATA") or HERE.parent / "data")
RUN_ID = re.compile(r"^\d{4}-\d{2}-\d{2}/\d{6}-(find|verify)$")


class MissingData(FileNotFoundError):
    """A private data file is not on this machine."""


def private_file(name: str) -> Path:
    path = DATA / name
    if not path.is_file():
        raise MissingData(f"{name} is not in {DATA}. It describes real shops, so it is kept out of the "
                          "repository. See data/README.md.")
    return path


def now() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def new_id(kind: str) -> str:
    return f"{dt.date.today().isoformat()}/{dt.datetime.now().strftime('%H%M%S')}-{kind}"


def _path(run_id: str, suffix: str) -> Path:
    if not RUN_ID.match(run_id):
        raise ValueError(f"not a run id: {run_id!r}")
    return RUNS / f"{run_id}{suffix}"


class Recorder:
    """Keeps the step log of one run, and passes each step on (to the screen or the terminal)."""

    def __init__(self, run_id: str, then=None):
        self.path = _path(run_id, ".events.jsonl")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.then = then

    def __call__(self, event: dict) -> None:
        event = dict(event, at=now())
        with self.path.open("a") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
        if self.then:
            self.then(event)


def save(run_id: str, data: dict) -> Path:
    path = _path(run_id, ".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(data, id=run_id), ensure_ascii=False, indent=2))
    return path


def decisions(run_id: str) -> dict[str, dict]:
    """The latest decision per shop for one run."""
    path = RUNS / "decisions.jsonl"
    latest: dict[str, dict] = {}
    if path.exists():
        for line in path.read_text().splitlines():
            if line.strip():
                d = json.loads(line)
                if d.get("run") == run_id:
                    latest[d["shop"]] = d
    return latest


def decide(run_id: str, shop: str, decision: str, note: str = "") -> dict:
    if decision not in ("approve_outreach", "visit", "reject"):
        raise ValueError(f"not a decision: {decision!r}")
    entry = {"at": now(), "run": run_id, "shop": shop, "decision": decision, "note": note[:500]}
    RUNS.mkdir(parents=True, exist_ok=True)
    with (RUNS / "decisions.jsonl").open("a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def load(run_id: str) -> dict:
    """A run with its steps and decisions. 'sample' is the invented run shipped with the screen."""
    if run_id == "sample":
        run = json.loads(SAMPLE.read_text())
        return dict(run, id="sample", decisions=decisions("sample"))
    run = json.loads(_path(run_id, ".json").read_text())
    log = _path(run_id, ".events.jsonl")
    events = [json.loads(line) for line in log.read_text().splitlines() if line.strip()] if log.exists() else []
    return dict(run, id=run_id, events=events, decisions=decisions(run_id))


def list_runs(limit: int = 20) -> list[dict]:
    rows = []
    for path in sorted(RUNS.glob("*/*.json"), reverse=True):
        run_id = f"{path.parent.name}/{path.stem}"
        if not RUN_ID.match(run_id):
            continue
        try:
            run = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        rows.append({"id": run_id, "brief": run.get("brief") or "", "shops": len(run.get("shops") or []),
                     "checked_at": run.get("checked_at")})
        if len(rows) >= limit:
            break
    return rows
