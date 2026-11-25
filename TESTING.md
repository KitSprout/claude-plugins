# Testing

How plugins in this repository are tested, how results are recorded, and how every change is compared with what came before. It applies to every plugin with an `evals/` folder. Handoff is the first; debate has no suite yet, so its suite is a later plan.

Rules in short:

1. Every measurement runs under fixed, recorded conditions.
2. A summary of every measurement is committed; raw results stay local.
3. Results are only compared when the suite version and the agent model match.
4. Whether to accept a regression is decided by the repository owner, who merges.

## Layers

| Layer | Needs a model | Runs | What it checks |
|---|---|---|---|
| Static | no | CI on every pull request and every push to `main`; also locally | Hooks, sizes, file formats, grader self-tests (`python3 tools/evals/check_graders.py`, the unit tests, each plugin's `evals/static-checks.sh`) |
| Triggering | yes | local | Whether the skill loads, or stays unloaded (`tool_used` on `Skill`); a case may also grade the reply. Deterministic, no judge |
| Quality | yes | local | A synthetic session, then the skill's output, then graders |

Case kind comes from the case name prefix: `trigger-*` should load the skill, `nearmiss-*` must not, everything else is a quality case.

Unit tests for the scripts: `python3 -m unittest discover -s tools/evals/tests -v`.

## Conditions

Every measurement fixes and records:

| Condition | Value |
|---|---|
| Plugin version and commit | from `plugin.json` and `git rev-parse --short HEAD`; measure a clean tree |
| Suite version | `suite` in the plugin's `evals/suite.json` |
| Agent model | `claude-opus-5-5` and `claude-sonnet-5-5`, one measurement each |
| Judge model | `sonnet`, for every run |
| Claude Code version | recorded from the run |
| Runs per case | 3 |

A Sonnet judge grading Sonnet output is a known limit of this method.

Command, from `plugins/<name>`, once per agent model:

```
claude plugin eval . --runs 3 --ablation none --scaffold --trust-plugin \
  --allow-tools Write Edit Bash -j 4 --judge-model sonnet --no-publish \
  --model <model>
```

The eval command runs from `plugins/<name>` and writes `plugins/<name>/evals/results/<timestamp>/aggregate-result.json`. `summarize.py`, `compare.py` and `check_graders.py` run from the repository root, so give `summarize.py` the result path relative to it.

Git in the eval sandbox: on macOS, plain `git` fails there, because the `/usr/bin/git` shim calls `xcrun`, which cannot write its cache. `PATH` order is not honoured inside the sandbox, `execution.env` accepts only `EVAL_*` keys, and a workspace `.claude/settings.json` is not loaded. So every quality case carries the same `execution.append_system_prompt`, an environment note for the test machine only: run git as `/Library/Developer/CommandLineTools/usr/bin/git`, one command per Bash call (the sandbox denies compound commands that contain git), and do not record the note in any file (agents copied it into handoffs). The note is part of the suite, so it is identical for every version measured. It is a limit: by drawing attention to git it may slightly help graders that depend on git (uncommitted, unpushed, no remote). Each summary says "git via environment note" in its notes.

**Before each full measurement, tell the owner the estimated cost** and wait for a yes. Estimate it by summing `agent_cost_usd` and `judge_cost_usd` over all cases of the previous summary for each model to be run, adding the models together, and scaling if the run count differs. With no previous summary for the suite (for example the first suite-2 run), run a one-run pilot of a few cases with `--max-cost-usd` and estimate from it.

## Graders

- Prefer deterministic graders (`regex`, `tool_used`, `file_exists`) wherever meaning is not needed.
- An `llm` grader judges the file the skill wrote, not the trace: use `focus: {source: file, path: ...}`. The trace judge sees only the first and last 12 messages. A quality case with an `llm` grader therefore names the output path in its prompt (or, for an automatic update, in its history).
- Every `regex` grader has a self-test: `graders/selftest/<grader>.pass.txt` (the pattern must match) and `<grader>.fail.txt` (it must not), using the grader's `match` field (contains by default, `not_contains`, or `count:N`). `python3 tools/evals/check_graders.py` enforces this for every `plugins/*/evals/*/graders/*.md` of `type: regex` and exits 1 on any problem. It does not check baseline files.
- Every new `llm` grader is shown once to fail, on a known-bad output or on the previous plugin version where the gap exists. Note how in the pull request.
- A **trap** is a grader that guards a harmful failure (a leaked secret, a false approval, an overwritten file). Traps are listed in `suite.json`.

## Records

- Raw results (`plugins/<name>/evals/results/`) stay local and gitignored; they contain temporary paths.
- Summarise each measurement and commit the summary:

```
python3 tools/evals/summarize.py RESULT.json --plugin-dir plugins/<name> \
  --model <model> --judge sonnet \
  [--plugin-version V] [--plugin-commit SHA] [--suite N] [--skill-bytes N] \
  [--note TEXT ...] [--label L] --out plugins/<name>/evals/baselines
```

`RESULT.json` is the run's result file. The script writes `DIR/<version>__suite-<n>__<model>__<date>.json` (the date is the run's `startedAt`) and prints the path. Defaults: version from `plugin.json`, commit from `git rev-parse --short HEAD`, suite and traps from `evals/suite.json`, skill size from `skills/*/SKILL.md`. If `--suite` differs from `suite.json`, traps are left empty and a note says so.

- A summary has these fields: `format`, `plugin`, `plugin_version`, `plugin_commit`, `suite`, `claude_code`, `model`, `judge`, `runs`, `date`, `partial`, `skill_bytes`, `traps`, `notes`, `label` (only when `--label` was given), and `cases`, where each case has `runs`, `errors`, `agent_cost_usd`, `judge_cost_usd` and `graders` (`passed` and `scored` per grader). `partial` is true when some cases did not complete; a partial summary cannot be a baseline.
- **Never edit an old summary.** Correct it with a new summary, or re-summarise the same result with a `--note` and `--label L`, which writes a new file whose name ends `__L.json` and stores `"label"`.
- Summaries written before this work's first push to this repository name commits from local history that was squashed before publishing; their notes describe what was measured.
- The latest summary for a (suite, agent model) pair is the **baseline** for the next change.
- The 2026-11-18/19 results are suite 1 and are kept with their known defects (see Limits). Suite-1 summaries are history only: never a baseline and never compared.

## Suite versions

Any change to graders, fixtures, case prompts or cases raises `suite` in `evals/suite.json` and adds an entry to its `changes` list (`suite`, `date`, `text`); that list is the change log. The one exception is fixture text that is the plugin's own output, such as the session-start note in handoff's `handoff-auto` history: it follows the plugin version under test, so regenerate it before measuring a version whose hook changed, say so in that summary's notes, and do not raise `suite` for it. Results of different suite versions are never compared. After raising it, re-run the current release as a new baseline (see below).

`suite.json` shape:

```
{"suite": 2, "traps": ["case/grader", ...],
 "changes": [{"suite": 1, "date": "YYYY-MM-DD", "text": "..."}]}
```

Trap names are `<case>/<grader>` and must match grader files.

## Comparing

```
python3 tools/evals/compare.py BASE.json NEW.json
```

It prints a Markdown table (case, grader, before, after, verdict) plus skill bytes and agent cost per run, before and after. Verdicts: `same`, `improved`, `noise`, `regression`, `trap-failed`, `trap-missing`, `new`, `removed`.

| Rule | Verdict |
|---|---|
| A grader's pass rate falls by 0.5 or more | `regression` |
| It falls by less | `noise` (noted) |
| A trap grader fails in any run, regardless of the baseline | `trap-failed`; blocks |
| A trap listed in the new summary has no scored run there (absent, or 0/0) | `trap-missing`; blocks |
| A `nearmiss-*` case fires in any run | `regression` |
| A `trigger-*` case is missing in 2 or more runs | `regression` |
| A grader exists only in the new summary or only in the base | `new` or `removed` (a new grader still gets the trap, `nearmiss-*` and `trigger-*` rules above) |

If run counts differ, rates are compared and the difference is noted.

Exit codes: **2** refused (different suite, different agent model, or a partial summary), **1** blocking (a trap failed or has no scored run), **0** otherwise. A regression that is not a trap exits 0: it has to be read and explained, not ignored.

A missing handoff file fails every grader that reads it, traps included, so when a trap fails, read the case's file-location (or naming) grader first.

Every regression, `trap-failed` or `trap-missing` is explained in the pull request. The repository owner decides whether to accept it. Skill size and cost are compared for information only.

## When something changes

| Change | Do |
|---|---|
| Docs only | Static checks |
| Skill, hooks, `plugin.json` or description | Bump the version in `plugin.json` and commit, then run a full measurement on both agent models, summarise, compare with the latest baseline. Bump and commit first: summaries are never edited, so measuring first records the old version |
| Suite (graders, fixtures, cases) | Raise the suite version, re-run the current release first as a new baseline, then measure the change against it |
| Claude Code or model version | Re-run the current release first as a new baseline |

One exception: a change of a setting's default that leaves the behaviour under each value unchanged may ship without a new measurement, if the results state which value was measured and the static checks cover the changed default; the repository owner approves each such exception. When the suite cannot set the new default (handoff 0.3.0's `auto` off: evals cannot set plugin options), the next baseline of the shipped default may show the graders that need an automatic update, such as `handoff-auto/updated` and `handoff-auto-first`'s file graders, as regressions; explain them in that summary's notes. `nearmiss-read-continue` cannot regress under the off default.

Workflow: work on one branch; open a PR to `main` only when everything is confirmed complete. CI does not check result files; model-free checks may run in CI. Before any push to the public repository, check for personal data and get the owner's OK. Everything in the repository is English, plus `README.zh-TW.md` beside every `README.md`.

## Limits

- Three runs per case is a small sample; a drop of one run in three is noise by this method, not evidence of a regression.
- The judge is Sonnet for all runs, including Sonnet output.
- Handoff size is not in the run results (the traces are not kept), so only skill size is compared.
- Results depend on the Claude Code and model versions; they are recorded but not controlled.
- Suite 1 results (2026-11-18/19) have known defects: git failed in the eval sandbox, the API-key grader read file names only, llm judges read the trace window, and the rescue fixture recorded the API error as a user message. They are kept as history, not as a baseline.
- No CI enforcement of result files; the baselines are for the maintainers' own use.
