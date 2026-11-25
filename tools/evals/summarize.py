"""Turn one `claude plugin eval` result file into a small summary JSON.

Usage:
  python3 tools/evals/summarize.py RESULT.json --plugin-dir plugins/handoff \\
      --model M --judge sonnet [--plugin-version V] [--plugin-commit SHA] \\
      [--suite N] [--skill-bytes N] [--note TEXT ...] [--label L] --out DIR

Writes DIR/<version>__suite-<n>__<model>__<date>.json (date from the result's
startedAt; with --label, the name ends __<label>.json and the summary stores
"label") and prints the path. Refuses to overwrite an existing summary.
Only the `with` arm is summarised; no local paths reach the output.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def _need(obj, key, path):
    if not isinstance(obj, dict) or key not in obj or obj[key] is None:
        raise SystemExit("result is missing required field: %s" % path)
    return obj[key]


def _need_list(obj, key, path):
    v = _need(obj, key, path)
    if not isinstance(v, list):
        raise SystemExit("result field is not a list: %s" % path)
    return v


def summarize(result, *, plugin, plugin_version, plugin_commit, suite, traps,
              model, judge, date, skill_bytes, notes):
    claude_code = _need(result, "claudeVersion", "claudeVersion")
    partial = _need(result, "partial", "partial")
    cfg = result.get("suite")
    if isinstance(cfg, dict) and cfg.get("judgeModel") not in (None, judge):
        raise SystemExit("judge mismatch: result used %r but --judge is %r"
                         % (cfg["judgeModel"], judge))
    cases_in = _need_list(result, "cases", "cases")
    cases = {}
    for i, case in enumerate(cases_in):
        cp = "cases[%d]" % i
        name = _need(case, "name", cp + ".name")
        arms = _need(case, "arms", cp + ".arms")
        runs = _need_list(arms, "with", cp + ".arms.with")
        case_graders = _need_list(case, "graders", cp + ".graders")
        graders = {}
        errors = 0
        agent = judge_cost = 0.0
        for j, run in enumerate(runs):
            rp = "%s.arms.with[%d]" % (cp, j)
            cost = _need(run, "costUsd", rp + ".costUsd")
            jcost = _need(run, "judgeCostUsd", rp + ".judgeCostUsd")
            agent += cost - jcost
            judge_cost += jcost
            if run.get("error"):
                errors += 1
                for k, g in enumerate(case_graders):
                    gn = _need(g, "name", "%s.graders[%d].name" % (cp, k))
                    e = graders.setdefault(gn, {"passed": 0, "scored": 0})
                    e["scored"] += 1
                continue
            for k, g in enumerate(_need_list(run, "graders", rp + ".graders")):
                gp = "%s.graders[%d]" % (rp, k)
                gn = _need(g, "name", gp + ".name")
                if _need(g, "scored", gp + ".scored"):
                    e = graders.setdefault(gn, {"passed": 0, "scored": 0})
                    e["scored"] += 1
                    e["passed"] += 1 if _need(g, "passed", gp + ".passed") else 0
        cases[name] = {"runs": len(runs), "errors": errors,
                       "agent_cost_usd": round(agent, 3),
                       "judge_cost_usd": round(judge_cost, 3),
                       "graders": graders}
    return {
        "format": 1, "plugin": plugin, "plugin_version": plugin_version,
        "plugin_commit": plugin_commit, "suite": suite,
        "claude_code": claude_code, "model": model, "judge": judge,
        "runs": max((c["runs"] for c in cases.values()), default=0),
        "date": date, "partial": bool(partial), "skill_bytes": skill_bytes,
        "traps": list(traps), "notes": list(notes), "cases": cases,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("result")
    ap.add_argument("--plugin-dir", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--judge", required=True)
    ap.add_argument("--plugin-version")
    ap.add_argument("--plugin-commit")
    ap.add_argument("--suite", type=int)
    ap.add_argument("--skill-bytes", type=int)
    ap.add_argument("--note", action="append", default=[])
    ap.add_argument("--label")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)

    pdir = Path(a.plugin_dir)
    result = json.loads(Path(a.result).read_text())
    version = a.plugin_version
    if version is None:
        version = json.loads((pdir / ".claude-plugin" / "plugin.json").read_text())["version"]
    commit = a.plugin_commit
    if commit is None:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    sj = json.loads((pdir / "evals" / "suite.json").read_text())
    suite = a.suite if a.suite is not None else sj["suite"]
    notes = list(a.note)
    if suite == sj["suite"]:
        traps = sj.get("traps", [])
    else:
        traps = []
        notes.append("traps not defined for suite %d" % suite)
    sb = a.skill_bytes
    if sb is None:
        sb = sum(p.stat().st_size for p in sorted(pdir.glob("skills/*/SKILL.md")))
    started = _need(result, "startedAt", "startedAt")
    date = str(started)[:10]
    out = summarize(result, plugin=pdir.resolve().name, plugin_version=version,
                    plugin_commit=commit, suite=suite, traps=traps,
                    model=a.model, judge=a.judge, date=date,
                    skill_bytes=sb, notes=notes)
    name = "%s__suite-%d__%s__%s" % (version, suite, a.model, date)
    if a.label is not None:
        if not a.label or not all(c.isalnum() or c in "-_." for c in a.label):
            raise SystemExit("--label must be non-empty and hold only letters, digits, '-', '_' and '.'")
        out["label"] = a.label
        name += "__" + a.label
    path = Path(a.out) / (name + ".json")
    if path.exists():
        raise SystemExit("refusing to overwrite existing summary: %s" % path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(path)


if __name__ == "__main__":
    main()
