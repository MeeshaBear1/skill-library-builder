#!/usr/bin/env python3
"""Skill footprint — the library's context cost, measured in three loading tiers.

Deterministic, stdlib-only, read-only. Progressive disclosure is a skill library's
whole economic argument ("how much context does it take to make that work?"), so it
must be a measured, budgeted number — not an architecture claim. Per skill:

  tier 1  always-loaded — the YAML frontmatter description; rides in EVERY session's
          system prompt whether or not the skill fires
  tier 2  on-invoke     — the SKILL.md body; loads only when the skill triggers
  tier 3  on-demand     — references/, tools/, and other shipped files; load one at
          a time only when the procedure asks for them

Handles plain, folded (>-), and literal (|) YAML description styles — a folded
description measured as its first line silently understates tier 1 by ~98%.

Budgets (defaults; override by flag):
  --desc-budget      1024 bytes per description  (Anthropic hard limit; FAIL over)
  --library-budget  16384 bytes total tier-1     (~4k tokens/session; WARN over)
  --body-budget     32768 bytes per SKILL.md body (~5k words guidance; WARN over)

Usage: python skill_footprint.py [--skills-dir DIR] [--json] [budget flags]
Exit codes: 0 = within budgets, 1 = over-budget findings, 2 = could not scan.
"""

import argparse
import json
import re
import sys
from pathlib import Path

FM_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
# plain: `description: text` · block: `description: >-` / `|` followed by indented lines
DESC_PLAIN_RE = re.compile(r"^description:\s*(?![>|])(.+)$", re.MULTILINE)
DESC_BLOCK_RE = re.compile(r"^description:\s*[>|][+-]?\s*\n((?:[ \t]+\S.*\n?)+)", re.MULTILINE)


def description_bytes(skill_md_text: str) -> int:
    fm = FM_RE.match(skill_md_text)
    if not fm:
        return 0
    block = DESC_BLOCK_RE.search(fm.group(1) + "\n")
    if block:
        return len(" ".join(line.strip() for line in block.group(1).splitlines()).encode("utf-8"))
    plain = DESC_PLAIN_RE.search(fm.group(1))
    return len(plain.group(1).strip().strip('"').encode("utf-8")) if plain else 0


def measure(skill_dir: Path) -> dict:
    md = skill_dir / "SKILL.md"
    text = md.read_text(encoding="utf-8", errors="ignore")
    fm = FM_RE.match(text)
    body = text[fm.end():] if fm else text
    on_demand = sum(
        p.stat().st_size
        for p in skill_dir.rglob("*")
        if p.is_file() and p != md and "holdout" not in p.parts  # sealed corpora are never read
    )
    return {
        "skill": skill_dir.name,
        "always_loaded": description_bytes(text),
        "on_invoke": len(body.encode("utf-8")),
        "on_demand": on_demand,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--skills-dir", default=str(Path.home() / ".claude" / "skills"))
    ap.add_argument("--desc-budget", type=int, default=1024)
    ap.add_argument("--library-budget", type=int, default=16384)
    ap.add_argument("--body-budget", type=int, default=32768)
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    args = ap.parse_args()

    skills_dir = Path(args.skills_dir)
    dirs = sorted(
        (p for p in skills_dir.rglob("SKILL.md") if "holdout" not in p.parts),
        key=lambda p: p.parent.name,
    ) if skills_dir.is_dir() else []
    if not dirs:
        print(f"no skills found under {skills_dir}", file=sys.stderr)
        return 2

    rows = [measure(p.parent) for p in dirs]
    total_always = sum(r["always_loaded"] for r in rows)
    findings = []
    for r in rows:
        if r["always_loaded"] == 0:
            findings.append(f"FAIL {r['skill']}: no parseable description — it cannot trigger")
        elif r["always_loaded"] > args.desc_budget:
            findings.append(f"FAIL {r['skill']}: description {r['always_loaded']}B > {args.desc_budget}B hard limit")
        if r["on_invoke"] > args.body_budget:
            findings.append(f"WARN {r['skill']}: SKILL.md body {r['on_invoke']}B > {args.body_budget}B — split into references/")
    if total_always > args.library_budget:
        findings.append(
            f"WARN library: {total_always}B of descriptions ride in EVERY session (> {args.library_budget}B budget) — prune or tighten"
        )

    report = {
        "skills_dir": str(skills_dir),
        "totals": {
            "always_loaded": total_always,
            "on_invoke": sum(r["on_invoke"] for r in rows),
            "on_demand": sum(r["on_demand"] for r in rows),
            "approx_tokens_per_session": total_always // 4,
        },
        "budgets": {"desc": args.desc_budget, "library": args.library_budget, "body": args.body_budget},
        "skills": rows,
        "findings": findings,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        w = max(len(r["skill"]) for r in rows)
        print(f"{'skill':<{w}}  {'always':>7}  {'invoke':>7}  {'demand':>8}")
        for r in rows:
            print(f"{r['skill']:<{w}}  {r['always_loaded']:>7}  {r['on_invoke']:>7}  {r['on_demand']:>8}")
        t = report["totals"]
        print(f"\ntier 1 (every session): {t['always_loaded']}B ≈ {t['approx_tokens_per_session']} tokens · "
              f"tier 2 (on invoke): {t['on_invoke']}B · tier 3 (on demand): {t['on_demand']}B")
        for f in findings:
            print(f)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
