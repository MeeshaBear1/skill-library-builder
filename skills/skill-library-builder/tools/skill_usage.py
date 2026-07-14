#!/usr/bin/env python3
"""Skill reaper — usage evidence for installed skills, mined from Claude Code transcripts.

Deterministic, stdlib-only, read-only. For each skill in a skills directory, gathers two
usage signals from ~/.claude/projects/**/*.jsonl:

  1. invocations — Skill tool_use blocks with input.skill == <name> (also matches
     plugin-namespaced "plugin:<name>" forms)
  2. file reads — any tool_use whose input references a path under the skill's directory
     (skills consumed via "read X first" instructions never show a Skill invocation)

A skill with zero of both across the full scanned window is a deletion candidate; the
receipt is the scanned session count and date range. Evidence of absence, with the
search space stated — never a guess.

Usage:
  python skill_usage.py [--skills-dir DIR] [--projects-dir DIR] [--json] [--dormant-days N]

Defaults: --skills-dir ~/.claude/skills, --projects-dir ~/.claude/projects, dormant = 90.
Exit codes: 0 = every skill has usage evidence, 1 = deletion candidates exist,
2 = could not scan (no transcripts / no skills).
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SKILL_PATH_RE = re.compile(r"skills[/\\\\]+([A-Za-z0-9_.-]+)")


def iter_tool_uses(line: str):
    """Yield tool_use blocks from one transcript JSONL line (cheaply pre-filtered)."""
    try:
        rec = json.loads(line)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return
    msg = rec.get("message")
    if not isinstance(msg, dict):
        return
    content = msg.get("content")
    if not isinstance(content, list):
        return
    ts = rec.get("timestamp")
    for blk in content:
        if isinstance(blk, dict) and blk.get("type") == "tool_use":
            yield blk, ts


def scan(projects_dir: Path, skill_names: set[str]):
    """One pass over every transcript; returns per-skill evidence + scan receipts."""
    evidence = {
        n: {"invocations": 0, "file_reads": 0, "last_seen": None} for n in skill_names
    }
    sessions = 0
    ts_min = ts_max = None
    files = sorted(projects_dir.glob("*/*.jsonl"))
    for f in files:
        sessions += 1
        try:
            with open(f, encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    # cheap pre-filter: no tool_use or no mention of skills at all
                    if '"tool_use"' not in line:
                        continue
                    if "skill" not in line and "Skill" not in line:
                        continue
                    for blk, ts in iter_tool_uses(line):
                        hits = set()
                        if blk.get("name") == "Skill":
                            arg = (blk.get("input") or {}).get("skill", "")
                            base = arg.split(":")[-1].strip()
                            if base in skill_names:
                                evidence[base]["invocations"] += 1
                                hits.add(base)
                        blob = json.dumps(blk.get("input") or {})
                        for m in SKILL_PATH_RE.finditer(blob):
                            name = m.group(1)
                            if name in skill_names and name not in hits:
                                evidence[name]["file_reads"] += 1
                                hits.add(name)
                        for name in hits:
                            prev = evidence[name]["last_seen"]
                            if ts and (prev is None or ts > prev):
                                evidence[name]["last_seen"] = ts
                        if ts:
                            ts_min = ts if ts_min is None or ts < ts_min else ts_min
                            ts_max = ts if ts_max is None or ts > ts_max else ts_max
        except OSError:
            continue
    return evidence, {"sessions_scanned": sessions, "window_start": ts_min, "window_end": ts_max}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--skills-dir", default=str(Path.home() / ".claude" / "skills"))
    ap.add_argument("--projects-dir", default=str(Path.home() / ".claude" / "projects"))
    ap.add_argument("--dormant-days", type=int, default=90)
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    args = ap.parse_args()

    skills_dir = Path(args.skills_dir)
    projects_dir = Path(args.projects_dir)
    skill_names = {p.name for p in skills_dir.iterdir() if p.is_dir() and (p / "SKILL.md").exists()} if skills_dir.is_dir() else set()
    if not skill_names:
        print(f"no skills found under {skills_dir}", file=sys.stderr)
        return 2
    if not projects_dir.is_dir():
        print(f"no transcripts dir at {projects_dir}", file=sys.stderr)
        return 2

    evidence, receipts = scan(projects_dir, skill_names)
    if receipts["sessions_scanned"] == 0:
        print("no transcripts to scan — no evidence either way", file=sys.stderr)
        return 2

    cutoff = None
    if receipts["window_end"]:
        try:
            end = datetime.fromisoformat(receipts["window_end"].replace("Z", "+00:00"))
            cutoff = (end - timedelta(days=args.dormant_days)).isoformat()
        except ValueError:
            pass

    rows = []
    for name in sorted(skill_names):
        e = evidence[name]
        total = e["invocations"] + e["file_reads"]
        if total == 0:
            status = "never-used"
        elif cutoff and e["last_seen"] and e["last_seen"] < cutoff:
            status = "dormant"
        else:
            status = "active"
        rows.append({"skill": name, **e, "status": status})

    candidates = [r for r in rows if r["status"] != "active"]
    report = {"receipts": receipts, "dormant_days": args.dormant_days, "skills": rows}

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        w = max(len(r["skill"]) for r in rows)
        print(f"scanned {receipts['sessions_scanned']} sessions, "
              f"{receipts['window_start']} .. {receipts['window_end']}\n")
        for r in sorted(rows, key=lambda r: (r["status"] == "active", r["skill"])):
            print(f"{r['skill']:<{w}}  {r['status']:<10}  inv={r['invocations']:<4} "
                  f"reads={r['file_reads']:<4} last={r['last_seen'] or '-'}")
        if candidates:
            print(f"\n{len(candidates)} deletion/review candidate(s): every candidate receipt = "
                  f"0 uses (or none since {args.dormant_days}d cutoff) across the full window above.")
    return 1 if candidates else 0


if __name__ == "__main__":
    sys.exit(main())
