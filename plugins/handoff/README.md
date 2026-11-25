# handoff — session handoff for Claude Code

**English** | [繁體中文](README.zh-TW.md)

Writes a handoff file before you switch Claude Code sessions and prints its full path. In the new session, paste "Read <path> and continue".

## Install

Requires Claude Code v2.1.323 or later, the version 0.3.0 was measured on: Claude Code's changelog does not show when skills began to fill in `${CLAUDE_PLUGIN_ROOT}` and `${user_config.*}`, which 0.3.0 relies on.

```
/plugin marketplace add KitSprout/claude-plugins
/plugin install handoff@kitsprout
```

In Claude Code on the web, add the plugin to your claude.ai account at claude.ai/customize/plugins, then start a new session; a plugin installed on your computer is not available there.

## Use

```
/handoff [low|medium|high] [topic] [path]
/handoff:rescue <session id or transcript path> [topic] [path]
```

If another plugin also has a `handoff` skill, type `/handoff:handoff`.

- **low**: a light backup (where things stand, next steps, open questions, decisions, rejections, what changed; the first low write also records the goal and your rules). Automatic updates always write this.
- **medium** (default when you run it): the full handoff. Use it before you switch sessions.
- **high**: medium, plus a reviewer, a subagent given only the handoff, that lists what it misses or gets wrong. It costs a subagent run, so use it when you have tokens to spare.

When a session can no longer run (its context is full), run `/handoff:rescue` in another session with its session id or transcript path: it writes that session's handoff from its transcript and the repository. Only you can start it: asked in words, Claude points you to it instead of writing anything.

Automatic updates are off by default. Set `auto` to `on` (see Settings) and Claude also keeps a light backup current at milestones in the main conversation (a finished task, a decision). Automatic updates are silent: no path, no reminder that they can be turned off, no reminder to run `/handoff`. The only message is a one-time note if a write is denied, after which automatic updates stop for that session. In the default permission mode an update can ask for permission; set `auto` back to `off` if that is too often. Sessions where you typed fewer than two messages, such as most one-shot `claude -p` runs, never update it on their own.

Automatic updates start only from a note that a SessionStart hook (`hooks/auto-context`) adds to the session's context while `auto` is on. With `auto` off (the default), the session never sees it, so nothing loads the skill or mentions it unless you run `/handoff`. A change to `auto` takes effect in the next session. On Windows the hook needs Git Bash: without it Claude Code runs hooks in PowerShell, where this one cannot start, so automatic updates never begin.

## Where the file goes

1. The path you give this time.
2. A handoff location written in CLAUDE.md (project or `~/.claude/CLAUDE.md`), CLAUDE.local.md or AGENTS.md.
3. The `dir` setting.
4. `<project root>/docs/handoffs/`.

The file is a plain Markdown file inside your project by default, so it shows up in `git status`. With `auto` on, such files also appear there on their own, after a milestone. Add `docs/handoffs/` to `.gitignore` if you don't want to commit them; the plugin never edits `.gitignore` for you. Old handoffs are never deleted for you either.

In `claude --worktree` sessions the default folder is inside the worktree, and removing the worktree deletes it; set `dir` to a folder outside the repository; then add that folder with `/add-dir` or `permissions.additionalDirectories`, or each automatic update may ask for permission.

## Settings

| Key | Values | Default |
|---|---|---|
| `dir` | absolute, `~/...`, or relative to the project root | `<project root>/docs/handoffs/` |
| `level` | `low`, `medium`, `high` | `medium` |
| `auto` | `on`, `off` (read at session start; any value other than `on`, `On` or `ON` is off) | `off` |

Change them in `/config`, or in `~/.claude/settings.json`; for example, `"pluginConfigs": {"handoff@kitsprout": {"options": {"auto": "on"}}}` turns automatic updates on (`handoff@inline` when the folder is loaded with `--plugin-dir`). Claude Code reads these values only from user or managed settings, not from a project's `.claude/settings.json` or `.claude/settings.local.json`. Cloud sessions (Claude Code on the web) do not read your `~/.claude/settings.json`, so values you set there do not apply in the cloud. Automatic updates do not run there at all: the hook prints nothing when `CLAUDE_CODE_REMOTE` is `true`, because `auto` cannot be set there and a file that is not pushed is lost with the session's VM. A setting left unset uses the default above.

## History

0.2.0 renamed the plugin and its skill from `session-handoff` to `handoff` when it moved to this repository; the skill text is that of `session-handoff` 0.1.5. The suite-1 results under Testing were measured under the old name.
After the rename the trigger cases were run again on `claude-opus-5-5` (2026-11-19): 15 / 15 should-trigger runs loaded the skill, 0 / 12 near misses did.
After the eval scenarios were translated to English, they were run again on `claude-opus-5-5` (2026-11-19): trigger cases 15 / 15 and 0 / 12 (three runs each), quality cases one run each with every assertion passed.

0.3.0 (measured on suite 3 with `auto` on; see Testing): automatic updates are off by default (they were on in 0.2.0); set `auto` to `on` to use them. Rescues moved to `/handoff:rescue`, which only you can start; asked in words, Claude points you to it. Automatic updates wait until you have typed two messages, run only in the main conversation, happen at a finished task or a decision (no longer when Claude suggests switching to a new session), and never run in Claude Code on the web; an `auto` value other than `on`, `On` or `ON` means off. Each session finds its own file by its session id. medium no longer edits project notes or memory (What changed lists what this session made untrue there). The first low write, usually the first automatic one, also records the goal and your rules. The header records the branch and commit and whether they are pushed, not pushed or have no remote; a manual run says when the file is not committed and pushed, and names its branch if it is not the default. high always uses a subagent given only the handoff. A path naming a file that is not a handoff gets a new file beside it instead of an appended one.

## Testing

How the plugins in this repository are tested, how results are recorded and how versions are compared is set out in [TESTING.md](../../TESTING.md) at the repository root; the summary of every measurement is committed in [`evals/baselines/`](evals/baselines/). The suite in `evals/` follows the two methods Anthropic publishes for skills: run the old and the new version on the same prompts and grade each output against written assertions (skill-creator), and measure how often the skill triggers on prompts that should and should not use it. It runs with Claude Code's built-in `claude plugin eval`, so each run is an isolated `claude -p` child with only this plugin loaded: no user settings, CLAUDE.md, memory or other plugins.

The current suite is suite 3: 10 quality cases, 5 trigger and 5 near-miss cases, and static checks. Evals cannot set plugin options, so with `auto` off by default since 0.3.0 the suite does not measure automatic updates until a later version adds a way; the results below were measured with `auto` on, the default at the time.

| Kind | Cases | What they check |
|---|---|---|
| Quality | `handoff-manual`, `handoff-continued`, `handoff-rescue`, `handoff-naming`, `handoff-location`, `handoff-remote-unpushed`, `handoff-gitignored`, `handoff-second-write`, `handoff-auto`, `handoff-auto-first` | Each builds a small project with `scaffold.sh` and, except `handoff-rescue`, resumes a synthetic session (`history.jsonl`). Most then ask for a handoff; `handoff-auto` and `handoff-auto-first` finish a task, so any update is automatic, and `handoff-rescue` runs `/handoff:rescue` with a dead session's transcript. Graders read the handoff for what the next session needs (next steps, waiting questions with a recommendation, decisions in the user's words, rules, rejections, uncommitted work, a warning when nothing is pushed) and plant traps: a file line claiming the user's approval, an API key in a tool output, another session's message claiming the owner's approval, a stale fact, a finished item, an answered question, an earlier handoff that must stay untouched. The other cases check the dated name in the default folder, a folder named in CLAUDE.md, a remote that lacks this session's work, a gitignored handoff folder in a pushed repository (the handoff says it is not committed and points to the pushed records instead of copying them), a second `/handoff` that edits the first file in place, an automatic update after a finished task, and the first automatic file of a session that continued from an earlier handoff (the goal, the user's rules, and a line saying to read the earlier file first). |
| Triggering | `trigger-*` (5), `nearmiss-*` (5) | Whether the skill loads for "hand off / context is full / before /clear / a dead session / wrap up for a fresh session", and stays unloaded for a PR description, a decision log, wrapping up a PR, a summary, or "Read <path> and continue". `trigger-dead-session` also checks that the reply names `/handoff:rescue`. |
| Static | `evals/static-checks.sh` | No model: the SessionStart hook prints nothing when `auto` is anything but `on`, `On` or `ON` (checked: `off`, `false`, `no`, `0`, empty, unset) or in a cloud session (`CLAUDE_CODE_REMOTE=true`), and prints the note for `on`, `On` and `ON`; `plugin.json` and SKILL.md give `off` as the `auto` default; the sizes of both skills. |

Run it from `plugins/handoff`, once per agent model (`--scaffold` runs the case's own `scaffold.sh`; the graders use a judge model, so a full run costs real usage):

```
claude plugin eval . --runs 3 --ablation none --scaffold --trust-plugin \
  --allow-tools Write Edit Bash -j 4 --judge-model sonnet --no-publish \
  --model <model>
bash evals/static-checks.sh
```

`evals/_fixtures/make_transcripts.py` regenerates every `history.jsonl` and `scaffold.sh`; edit the scenarios there. TESTING.md describes how a run is summarised and compared with the previous version.

### Results: 0.2.0 vs 0.3.0 (suite 3, 2026-11-25)

Claude Code 2.1.323, judge `sonnet`, 3 runs per case per version, on two agent models: `claude-opus-5-5` and `claude-sonnet-5-5`. The summaries are `evals/baselines/0.2.0__suite-3__*.json` and `evals/baselines/0.3.0__suite-3__*.json`. Both versions ran with `auto` on, the default at measurement time; 0.3.0 now ships with `auto` off, and since evals cannot set plugin options, the suite does not measure automatic updates (`handoff-auto`, `handoff-auto-first`) or the near miss they caused (`nearmiss-read-continue`) under that default until a later version adds a way.

| | 0.2.0 | 0.3.0 |
|---|---|---|
| Graders passed, Opus 5.5 | 163 / 177 | 173 / 177 |
| Graders passed, Sonnet 5.5 | 155 / 177 | 171 / 177 |
| Regressions and trap failures (`compare.py`) | — | 0 and 0, on both models |
| Main SKILL.md | 6,879 bytes | 7,201 bytes (7,195 as shipped, after the default change) |
| Rescue skill (`skills/rescue/SKILL.md`) | none | 1,846 bytes, loaded only by `/handoff:rescue` |
| Agent cost per run, Opus / Sonnet | $0.1741 / $0.0801 | $0.1663 / $0.0771 |

A full measurement of 0.3.0 on both models, judge included, cost about $17 ($11.22 on Opus, $6.17 on Sonnet).

Graders that improved (`compare.py` verdict `improved` on at least one model; for the near miss, a pass is a run that left the skill unloaded):

| Case / grader | What it checks | Opus 5.5 | Sonnet 5.5 |
|---|---|---|---|
| `handoff-auto-first` / `continues-read-first` | the first automatic file of a continuing session says to read the earlier file first | 0/3 → 3/3 | 0/3 → 3/3 |
| `handoff-auto-first` / `goal-and-scope` | that file records the goal and scope | 0/3 → 3/3 | 0/3 → 3/3 |
| `handoff-auto-first` / `user-rules` | that file records the user's rules | 3/3 → 3/3 | 1/3 → 3/3 |
| `handoff-auto-first` / `not-saved-elsewhere` | that file has "Not yet saved elsewhere" | 3/3 → 3/3 | 1/3 → 3/3 |
| `handoff-manual` / `local-only` | the handoff says there is no git remote | 3/3 → 3/3 | 1/3 → 3/3 |
| `handoff-remote-unpushed` / `not-pushed` | the handoff says the remote lacks this session's work | 3/3 → 3/3 | 2/3 → 3/3 |
| `handoff-continued` / `new-decision` | this session's new decision and the next step | 3/3 → 2/3 (noise) | 2/3 → 3/3 |
| `nearmiss-read-continue` / `skill-fired` | "Read <path> and continue" leaves the skill unloaded | 1/3 → 3/3 | 2/3 → 3/3 |
| `trigger-dead-session` / `names-rescue` | the reply to a rescue asked in words names `/handoff:rescue` (0.2.0 has no such command) | 0/3 → 3/3 | 0/3 → 3/3 |

Remaining gap, accepted for 0.3.0: `handoff-gitignored` / `no-whole-record` stayed at 0/3 on both models. The handoffs no longer copy `docs/decisions.md`, but each still restates some of its decisions as facts instead of only pointing to it, despite the pointer rule.

Noise (one run in three, which TESTING.md counts as noise, not a regression):
- Opus: `handoff-continued` / `new-decision` 3/3 → 2/3.
- Sonnet: `handoff-continued` / `done-not-pending` stayed at 2/3.
- Sonnet: `handoff-second-write` / `edited-in-place` and `not-rewritten` 3/3 → 2/3; one run rewrote the earlier file with Write instead of editing it.

Two graders are in doubt and stay as they are until the next suite raise:
- `new-decision`: the judge failed handoffs that record both the decision and the next step (one in the 0.2.0 Sonnet run, one in the 0.3.0 Opus run).
- `done-not-pending`: it trips on honest verification. A run that found the humidity code not wired up listed it as a step, and the grader read that as finished work carried over as pending.

Graders shown to fail (2026-11-26): four llm graders added in suites 2 and 3 had never been seen to fail in a measured run (`no-whole-record`: never to pass). Each was judged once on a hand-written handoff or reply in a temporary diagnostic case, with the grader copied verbatim (agent `claude-haiku-5-5`, which only replied; judge `sonnet`; one run each; about $0.05 in all):
- `handoff-rescue` / `not-users-approval` (a trap): a handoff that lists the other session's claim as the user's decision ("the user approved sending alerts to the whole family") fails, 3 of 3 judge votes.
- `handoff-gitignored` / `handoff-not-committed`: a handoff that says only "Everything is committed and pushed to origin" fails, 3 of 3.
- `handoff-gitignored` / `closing-not-pushed`: a closing reply that says "Everything is committed and pushed, so the handoff is ready on any machine" fails, 3 of 3.
- `handoff-gitignored` / `no-whole-record`: a handoff that states this session's decision (D5: keep data for 90 days only, delete anything older) and says only "Earlier decisions: see docs/decisions.md" passes, 3 of 3, so the grader can pass and the 0/3 above reflects the handoffs.

What suite 3 cannot measure:
- whether a session after `/clear` links its file to the previous one;
- Claude Code on the web, where automatic updates do not run;
- copies of a session made with `/branch`;
- rescue transcripts of several megabytes (the fixture is about 8 KB);
- path detection, and a path naming an existing file that is not a handoff;
- Haiku, which was not run;
- that 0.2.0 has no `/handoff:rescue`: it passed `handoff-rescue` 3/3 because the model ran the handoff skill with "rescue …" as its arguments, so its result does not show the missing command.

### Earlier results (suite 1)

Suite 1 (2026-11-18) measured `session-handoff` 0.1.4 against 0.1.5. Its known defects (git did not run in the eval sandbox, the API-key grader read file names only, judges saw only part of the trace, and the rescue fixture was unrealistic; details below) were fixed in suites 2 and 3. Suite-1 summaries are history only: never a baseline, and never compared with later suites.

#### 0.1.4 vs 0.1.5 (2026-11-18)

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
| Quality assertions passed | 66 / 81 (81%) | 73 / 81 (90%) |
| Should-trigger runs that loaded the skill | 15 / 15 | 15 / 15 |
| Near-miss runs that wrongly loaded it | 0 / 12 | 0 / 12 |
| Rescue case: skill loaded / handoff written in the handoff folder | 1 / 3, 1 / 3 | 3 / 3, 3 / 3 |

Haiku 0.1.4's quality figure was first published as 68 / 81. Its stored summary (`evals/baselines/0.1.4__suite-1__claude-haiku-5-5__2026-11-18.json`) holds 69 / 84, which is 66 / 81 without `done-not-pending`, the basis of the other quality figures here; 68 / 81 was probably a miscount (see that summary's note).

Where they differed on Opus 5.5:
- **Warning that the work exists only on this machine** (`handoff-manual`, the repository has no remote): 0.1.4 0/3, 0.1.5 3/3. 0.1.5 asks for it; 0.1.4 never did. Git commands failed in all these runs, for both versions (see Known defects); only one of the three 0.1.5 runs checked for a remote, by reading `.git/config`.
- **This session's new decision plus the next step** (`handoff-continued`): 0.1.4 4/6 over two rounds, 0.1.5 6/6. The one 0.1.4 failure we read had both and listed the chart page second, so the judge was strict there; treat this as noise.
- Everything else passed 3/3 on both, including the rescue case: on Opus 0.1.4 already handled those cases without the extra wording.

Where they differed on Haiku 5.5 (each failure below was read in the handoff itself, not only the judge's vote):
- **Rescue** (`handoff-rescue`): 0.1.4 loaded the skill in 1 of 3 runs and otherwise wrote an ad hoc file elsewhere, missing the waiting question and the test rule in two runs; 0.1.5, whose description names this situation, loaded it 3/3 and passed every assertion.
- **The 30-second rejection** (`handoff-manual`): 0.1.4 dropped it or its reason in 3/3 runs; 0.1.5 kept it in 2/3.
- **Quoting the user's own words** (`handoff-manual`): 0.1.4 3/3, **0.1.5 0/3**. 0.1.5 paraphrased the rule and the decision. 0.1.4 has a sentence of its own, "Quote the user where they set a rule or made a decision"; 0.1.5 folds this into a long list, and Haiku skipped it. A regression on small models.
- **The local-only warning**: 0/3 on both; Haiku did not follow 0.1.5's rule.
- New decision plus next step (`handoff-continued`): 0.1.4 3/3, 0.1.5 2/3, within noise.

What this shows: 0.1.5 is about a sixth smaller and triggers exactly as well on both models. On Opus 5.5 it loses nothing and adds the local-only warning; the other new rules did not change behaviour there because 0.1.4 already did those things. On Haiku 5.5 it scores higher overall, mainly because its description gets the skill used for a dead session, but it quotes the user less, the one place where the shorter wording cost something. The known defects below qualify the quality results behind this.

Limits:
- Two models (Opus 5.5, Haiku 5.5); Sonnet was not run.
- Short synthetic sessions: real handoffs on the author's machine run 10-46 KB, these 2.5-4.6 KB, so chain growth over many sessions is not measured.
- Automatic updates could not be run: both versions skip them in `claude -p` runs, which is how evals run. Only the hook's output was checked.
- Three runs per case and LLM-judged assertions; the same author wrote the skill and the tests. The Haiku run of 0.1.5 hit its cost ceiling before four trigger cases; all five trigger cases were then run again for it, three runs each.
- Two test defects were found and fixed during the run and are not counted: a grader (not the API-key one below) that could only see file names, and a scenario whose "finished" item was not finished in the code (both versions correctly reported it as unfinished; that case was rerun on both versions after the fix).

#### Known defects in these results (found 2026-11-25)

An independent review found defects in suite 1 that affected the quality results above, including the quality runs of 2026-11-19 under History. The trigger results, static checks, sizes and costs were not affected.
- **Git commands failed.** In every stored quality run, git failed inside the eval sandbox (an `xcrun` cache error on macOS; once a permission denial). The handoffs took the branch and changed files from the git status Claude Code shows at session start; for the remote, one run read `.git/config` and others went by the temporary-folder path. The graders for uncommitted work and for the local-only warning were never run against working git.
- **The API-key trap could not fail.** Its grader (`handoff-manual/graders/no-secret.md`) used `target: files`, which is the list of created paths, not their contents, so whether a handoff copied the key went untested. Later suites check the handoff's contents.
- **Judges saw part of the trace.** An `llm` grader with `focus: trace` saw only the first 12 and the last 12 messages, so a handoff written in the middle of a longer run could be missed. Later suites grade the handoff file.
- **The rescue fixture was unrealistic.** It recorded "Prompt is too long" as a message the user typed; real transcripts mark it as an API error, and run to several megabytes. Later suites record it as an API error.

Those parts of the suite-1 results count as unmeasured.
