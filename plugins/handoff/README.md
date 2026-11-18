# handoff — session handoff for Claude Code

Writes a handoff file before you switch Claude Code sessions and prints its full path. In the new session, paste "Read <path> and continue".

## Install

Requires Claude Code v2.1.271 or later.

```
/plugin marketplace add KitSprout/claude-plugins
/plugin install handoff@kitsprout
```

## Use

```
/handoff [low|medium|high] [topic] [path]
```

If another plugin also has a `handoff` skill, type `/handoff:handoff`.

- **low**: a light backup (where things stand, next steps, open questions, decisions, rejections, what changed). Automatic updates always write this.
- **medium** (default when you run it): the full handoff, and fix statements in project notes and memory that still say what this session changed. Use it before you switch sessions.
- **high**: medium, plus a reviewer that lists what the handoff misses or gets wrong: a fork that sees the conversation while the context is small, otherwise a subagent given only the handoff. It costs a subagent run, so use it when you have tokens to spare.

When a session can no longer run (its context is full), ask another session to write its handoff: the skill covers writing one from the dead session's transcript and the repository.

With automatic updates on, Claude also keeps a light backup current at milestones in interactive sessions (a finished task, a decision, before suggesting a new session). Automatic updates are silent: no path, no reminder that they can be turned off, no reminder to run `/handoff`. The only message is a one-time note if a write is denied, after which automatic updates stop for that session. In the default permission mode an update can ask for permission; set `auto` to `off` if that is too often. One-shot `claude -p` runs never update it on their own.

Automatic updates start only from a note that a SessionStart hook (`hooks/auto-context`) adds to the session's context while `auto` is on. With `auto` off, the session never sees it, so nothing loads the skill or mentions it unless you run `/handoff`. A change to `auto` takes effect in the next session.

## Where the file goes

1. The path you give this time.
2. A handoff location written in CLAUDE.md (project or `~/.claude/CLAUDE.md`), CLAUDE.local.md or AGENTS.md.
3. The `dir` setting.
4. `<project root>/docs/handoffs/`.

The file is a plain Markdown file inside your project by default, so it shows up in `git status`. Add `docs/handoffs/` to `.gitignore` if you don't want to commit it; the plugin never edits `.gitignore` for you. Old handoffs are never deleted for you either.

In `claude --worktree` sessions the default folder is inside the worktree, and removing the worktree deletes it; set `dir` to a folder outside the repository.

## Settings

| Key | Values | Default |
|---|---|---|
| `dir` | absolute, `~/...`, or relative to the project root | `<project root>/docs/handoffs/` |
| `level` | `low`, `medium`, `high` | `medium` |
| `auto` | `on`, `off` (read at session start) | `on` |

Change them in `/config`, or under `pluginConfigs` in `~/.claude/settings.json` (key `handoff@kitsprout`; `handoff@inline` when the folder is loaded with `--plugin-dir`). A setting left unset reads as unset inside the skill, which then uses the default above.

## History

0.2.0 renamed the plugin and its skill from `session-handoff` to `handoff` when it moved to this repository; the skill text is that of `session-handoff` 0.1.5. The test results below were measured under the old name.
After the rename the trigger cases were run again on `claude-opus-5-5` (2026-11-19): 15 / 15 should-trigger runs loaded the skill, 0 / 12 near misses did.
After the eval scenarios were translated to English, they were run again on `claude-opus-5-5` (2026-11-19): trigger cases 15 / 15 and 0 / 12 (three runs each), quality cases one run each with every assertion passed.

## Testing

The suite in `evals/` follows the two methods Anthropic publishes for skills: run the old and the new version on the same prompts and grade each output against written assertions (skill-creator), and measure how often the skill triggers on prompts that should and should not use it. It runs with Claude Code's built-in `claude plugin eval`, so each run is an isolated `claude -p` child with only this plugin loaded: no user settings, CLAUDE.md, memory or other plugins.

| Kind | Cases | What they check |
|---|---|---|
| Quality | `handoff-manual`, `handoff-continued`, `handoff-rescue` | Each resumes the same synthetic session (`history.jsonl`) in a small project built by `scaffold.sh`, then asks for a handoff. Graders check what the next session needs (next steps, waiting questions with a recommendation, decisions in the user's words, rules, rejections, uncommitted work, a warning when nothing is pushed) and plant traps: a file line claiming the user's approval, an API key in a tool output, a stale fact, a finished item, an answered question, an earlier handoff that must stay untouched. `handoff-rescue` writes the handoff of a session whose context is full, from its transcript. |
| Triggering | `trigger-*` (5), `nearmiss-*` (4) | Whether the skill loads for "hand off / context is full / before /clear / a dead session / wrap up for a fresh session", and stays unloaded for a PR description, a decision log, wrapping up a PR, or a summary. |
| Static | `evals/static-checks.sh` | No model: the SessionStart hook prints nothing when `auto` is `off`, prints the note when it is on or unset; sizes. |

Run it (from `plugins/handoff`; `--scaffold` runs the case's own `scaffold.sh`; the graders use a judge model, so a full run costs real usage):

```
claude plugin eval . --runs 3 --ablation none --scaffold --trust-plugin \
  --allow-tools Write Edit Bash -j 4 --judge-model sonnet --no-publish
bash evals/static-checks.sh
```

`evals/_fixtures/make_transcripts.py` regenerates every `history.jsonl` and `scaffold.sh`; edit the scenarios there. To compare two versions, copy the same `evals/` into each version's plugin folder and run the command in each.

### Results: 0.1.4 vs 0.1.5 (2026-11-18)

Claude Code 2.1.323, judge `sonnet`, 3 runs per case per version, on two agent models: `claude-opus-5-5` (the default here) and `claude-haiku-5-5`. The scenarios and prompts were in Traditional Chinese at the time; 0.2.0 translated them to English.

| | 0.1.4 | 0.1.5 |
|---|---|---|
| SKILL.md | 8,364 bytes, 1,405 words | 6,911 bytes, 1,154 words (−17%) |
| SessionStart note (auto on) | 666 characters | 363 characters |
| Static checks | all pass | all pass |

| Opus 5.5 | 0.1.4 | 0.1.5 |
|---|---|---|
| Quality assertions passed | 77 / 81 (95%) | 81 / 81 (100%) |
| Same, without the one rule only 0.1.5 has | 77 / 78 (99%) | 78 / 78 (100%) |
| Should-trigger runs that loaded the skill | 15 / 15 | 15 / 15 |
| Near-miss runs that wrongly loaded it | 0 / 12 | 0 / 12 |
| Agent cost per quality run (judge excluded) | $0.215 | $0.213 |
| Handoff size, mean per quality case | 2.7-4.1 KB | 2.6-3.9 KB |

| Haiku 5.5 | 0.1.4 | 0.1.5 |
|---|---|---|
| Quality assertions passed | 68 / 81 (84%) | 73 / 81 (90%) |
| Should-trigger runs that loaded the skill | 15 / 15 | 15 / 15 |
| Near-miss runs that wrongly loaded it | 0 / 12 | 0 / 12 |
| Rescue case: skill loaded / handoff written in the handoff folder | 1 / 3, 1 / 3 | 3 / 3, 3 / 3 |

Where they differed on Opus 5.5:
- **Warning that the work exists only on this machine** (`handoff-manual`, the repository has no remote): 0.1.4 0/3, 0.1.5 3/3. 0.1.5 asks for it; 0.1.4 never did.
- **This session's new decision plus the next step** (`handoff-continued`): 0.1.4 4/6 over two rounds, 0.1.5 6/6. The one 0.1.4 failure we read had both and listed the chart page second, so the judge was strict there; treat this as noise.
- Everything else passed 3/3 on both, including the rescue case: on Opus 0.1.4 already handled those cases without the extra wording.

Where they differed on Haiku 5.5 (each failure below was read in the handoff itself, not only the judge's vote):
- **Rescue** (`handoff-rescue`): 0.1.4 loaded the skill in 1 of 3 runs and otherwise wrote an ad hoc file elsewhere, missing the waiting question and the test rule in two runs; 0.1.5, whose description names this situation, loaded it 3/3 and passed every assertion.
- **The 30-second rejection** (`handoff-manual`): 0.1.4 dropped it or its reason in 3/3 runs; 0.1.5 kept it in 2/3.
- **Quoting the user's own words** (`handoff-manual`): 0.1.4 3/3, **0.1.5 0/3**. 0.1.5 paraphrased the rule and the decision. 0.1.4 has a sentence of its own, "Quote the user where they set a rule or made a decision"; 0.1.5 folds this into a long list, and Haiku skipped it. A regression on small models.
- **The local-only warning**: 0/3 on both; Haiku did not follow 0.1.5's rule.
- New decision plus next step (`handoff-continued`): 0.1.4 3/3, 0.1.5 2/3, within noise.

What this shows: 0.1.5 is about a sixth smaller and triggers exactly as well on both models. On Opus 5.5 it loses nothing and adds the local-only warning; the other new rules did not change behaviour there because 0.1.4 already did those things. On Haiku 5.5 it scores higher overall, mainly because its description gets the skill used for a dead session, but it quotes the user less, the one place where the shorter wording cost something.

Limits:
- Two models (Opus 5.5, Haiku 5.5); Sonnet was not run.
- Short synthetic sessions: real handoffs on the author's machine run 10-46 KB, these 2.5-4.6 KB, so chain growth over many sessions is not measured.
- Automatic updates cannot be run here: both versions skip them in `claude -p` runs, which is how evals run. Only the hook's output is checked.
- Three runs per case and LLM-judged assertions; the same author wrote the skill and the tests. The Haiku run of 0.1.5 hit its cost ceiling before four trigger cases; all five trigger cases were then run again for it, three runs each.
- Two test defects were found and fixed during the run and are not counted: a grader that could only see file names, and a scenario whose "finished" item was not finished in the code (both versions correctly reported it as unfinished; that case was rerun on both versions after the fix).
