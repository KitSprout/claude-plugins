---
name: debate
description: Run a subagent debate or multi-reviewer challenge on a design, plan, specification or decision, at a preset (low, medium, high, max) with adjustable settings, and bring the result back to the user. Use whenever the user asks subagents to debate, argue, challenge each other, or review and debate something, in any language (for example 「subagent 互相辯論」, 「審閱並互相辯論」), even as a one-line request, or types /debate:debate; when only a rule or another skill calls for a debate, load this skill to propose it, and wait. Not for a single independent review by one subagent.
argument-hint: "[low|medium|high|max] [setting=value ...] <what to debate>"
---

# Debate

Words typed after the command, if any: `$ARGUMENTS`

A debate finds what the author of a design missed and settles disputed points with evidence before the user decides. Its value comes from independent first reports and from checking claims at the source; arguing back and forth adds little by itself. The user decides; the debate prepares the decision.

The user starts a debate by typing the command or by asking for one in words; either is the yes. When only a rule or another skill calls for a debate, propose it with its preset, minutes and tokens, and wait.

## 1. Read the request

- Read the words typed after the command this way:
  - only the first word can be the preset (`low`, `medium`, `high`, `max`);
  - a `key=value` word with a known key (section 3) is a setting wherever it stands; a repeated key takes its last value;
  - an unknown key, a value outside its choices, or an old preset name (`quick`, `standard`, `gate`) as the first word is named in the start line and ignored;
  - the rest is the subject. When it is missing or unclear, take it from the conversation and say how you read it.
- When the user asked in words instead, read their message, not `$ARGUMENTS`: take a preset only when they name it as one (「用 high」, "at low"), and a setting only when they give its value ("two sides", 「一輪」). The rest is the subject or context. State the reading in the start line.
- With no preset named, use `medium`: its time and usage are close to those of the earlier debates that read sources (`references/usage.md`). Never use `max` unless the user names it.
- When one objective check could settle the question (a test, reading the code, counting real data), run it if it is cheap and read-only. If it settles the question, say so and ask whether to still debate; otherwise go on.
- Choose the format (section 2). State in one line: format, preset, the settings that differ from it, expected minutes and tokens (`references/usage.md`). Then start.
- Ask the user not to interrupt the session while the agents run: an interruption stops every background agent.

## 2. Format

| Need | Format | Sides |
|---|---|---|
| Find problems in a design, plan, specification or skill before it is built or installed | review | one reviewer per lens; usual lenses: consistency and usability, necessity and cost, failure in real use |
| Choose between options | option | one advocate per option, plus a challenger for doing less only when no option does less |
| A plan reviewed two or three times and still being patched | option | two: build it as it stands, or change it first |

When the user wants a plan as the outcome, the brief says so and the judge writes the plan as rulings, within a length the brief sets.

## 3. Presets and settings

### Presets

| Preset | Use when | sides (at most) | rounds | debaters | judge | judge-effort |
|---|---|---|---|---|---|---|
| `low` | a small or easily undone choice, a process question, a second opinion on one point | 2 | 1 | `opus` | `opus` | high |
| `medium` | the default; most design decisions and plans | 3 | 2 | `opus` | `opus` | high |
| `high` | the last check before something costly to redo: a build stage, an install on every machine, a data migration | 3 | 2 | `opus` | `fable` | high |
| `max` | only when the user asks for it; not measured | 4 | 2 | `opus` | `fable` | xhigh |

### Settings

Any setting can be changed after the preset, for example `/debate:debate medium rounds=1 <subject>`, `high sides=2`, `low debaters=sonnet`. Effort values appear only after `=`; a bare `low`, `medium`, `high` or `max` is the preset only as the first word.

| Setting | Choices | Time | Usage | Result |
|---|---|---|---|---|
| `sides` | 2, 3, 4 | little change (sides run in parallel) | about one more debater's share per side, plus more reading for round two and the judge (inferred) | one more independent view, the main source of a debate's gain |
| `rounds` | 1, 2 | round 2 takes about as long again (inferred) | nearly as much again with fresh agents, less when the same agents are resumed | round 2: each side checks the others' findings at the source |
| `debaters` | `opus`, `sonnet`, `fable`, `mixed` (sides alternate `opus`, `sonnet`, ...) | `sonnet` is faster | `sonnet` costs less | `sonnet` was less precise in one comparison; `mixed` not measured |
| `debater-effort` | unset (default), low, medium, high, xhigh | higher is slower | higher thinks more | not measured |
| `judge` | `opus`, `fable` | `fable` is slower | `fable` costs more per agent | a model other than the debaters' may side less with them (inferred: shown for judges from other model families, not for two models of one vendor) |
| `judge-effort` | high (default), xhigh, max | higher is slower | higher thinks more | not measured |

- `sides` is a maximum. When the question has more options, name in the start line which options get an advocate.
- Pass `model` on every agent call; nothing inherits from the session. This keeps the debaters off the top tier when the session itself runs on it.
- Set the judge's effort; leave debater effort unset unless the user sets it. Neither effect is measured (`references/usage.md`).
- A preset adopts `sonnet` only when comparisons show it helps time, usage and results together; one blind comparison so far (`references/usage.md`) did not. When the user picks `sonnet` or `mixed`, say so in the start line.

### When a model is refused or fails

- The judge's `fable` call is refused, errors, or fails partway: rerun it once with the same inputs on `opus` at effort xhigh (high if xhigh is refused); if `opus` is refused too, stop and ask. Say so in the result. Check the allowance beforehand only where the platform shows it.
- A `fable` debater the user set is refused: rerun it on `opus` and say so.
- `opus` is refused for the debaters: if the session is not on the top tier, omit `model` and say so; if it is, stop and ask.

## 4. The brief

Write one brief file from `references/brief-template.md`. It decides the quality of the run, so check before launch:

- the user's aim and measures in their own words, each with its source (a judge that is not told the aim invents one; one past debate had to be run again for this reason);
- decisions in force quoted at their source, each marked fixed or open to challenge (a brief once overstated a decision, and only the judge caught it);
- every number, limit and premise with its source, or marked "no source";
- scenarios from real use that every position must handle;
- no recommendation or reasoning of the author's in round one; it enters round two as one more position to check;
- the rules for agents written out in the brief: read-only except their own report file, the commands that would prompt the user (skip and report), tools that are missing. Do not point at per-machine files that may not exist, and do not copy permission settings into the brief.

If the subject so far lives only in the conversation, write it to `subject.md` beside the brief. For a large question, one subagent re-examining the requirements before launch has overturned a premise early.

## 5. Running it

Each agent's prompt holds the brief's path, its role and lens or position, the round, its report path, its length limit, "do not read the other reports in this folder until round two gives them to you", and "return only the report's summary". Keep each debater's agent id from its launch result; round two resumes it by that id.

1. **Round one.** All debaters at once, each blind to the others.
2. **Round two** (when `rounds=2`). Resume each debater with the paths of the others' reports; when one cannot be resumed, give a fresh agent its predecessor's report as its own position. For each of the others' findings it checks the source and says agree, partly agree or disagree, with the evidence, stating a rejected point in its strongest form first; then it keeps, changes or withdraws its own. The aim is to verify, not to persuade or agree.
3. **Judge.** A fresh agent that took no part, given the paths of the brief, the subject and every report.

- Every report names the source of each claim or marks it inferred. Unsourced findings are dropped. A failed command is missing evidence, not evidence against.
- When agents stop (an interruption, an error, nothing returned): check which report files exist and rerun each missing one once, asking the user first where the platform requires a yes to relaunch. If one is still missing, name the missing role in the result.

## 6. The judge

The judge:
- verifies at the source every fact a ruling rests on, especially where the debaters disagree;
- rules on each distinct finding on its merits, never by counting sides;
- uses FIX (which text changes, and how), AUTHOR'S POINT (a gap the author closes without a new decision), USER'S QUESTION (one sentence, its options, a recommendation), DEFER (with its trigger) and REJECT (why); in an option debate it also gives a verdict with its confidence;
- calls a point refuted only with an argument or a check that can be repeated;
- before cutting a part, states the strongest case for keeping it; never softens a ruling to spare the subject;
- marks anything it adds that nobody debated as "judge's addition, not debated";
- lists objections still unresolved, numbers still without a source, conflicts with the user's earlier decisions, and what it could not check. Finding no defect is not proof there is none.

## 7. After the judge

1. Check the citations the verdict rests on yourself, at the source, and say how many held.
2. Record unresolved objections where the topic's pending work is kept; with no such place, keep them in the debate folder and name it. Either way, list them in the result.
3. Report to the user: the answer first, short. Ask first, and alone, the decision that unblocks the others; plain words, one example for each option, no internal ids. Rulings that follow from earlier decisions are told, not asked. Label the judge's additions as not debated.
4. Give each role's model as its transcript records it (a fallback or a switch can differ from what was requested), and the measured time and usage (section 8).
5. When the rulings are applied, the result is not reviewed yet: a debate approves its rulings, not the text written afterwards. List for the user every change that goes beyond the rulings, and suggest a `low` check of the applied result before it is delivered or installed. Apply that check's rulings as ruled and list them; any further change goes to the user. If the user declines the check, deliver and say the result was not reviewed.

## 8. Time and usage

- Units: minutes from the first launch to the judge's report; tokens as new (input, cache write, output) and cache reads, kept apart. Prices change; token counts do not.
- The token figure in an agent's completion notice is not its total usage. Sum usage from the agents' transcripts where the session can read them (`references/usage.md`); otherwise give the notice's figure and say what it is.
- Usage follows how much source each agent reads and how long it thinks, not the length of its report. Before launch, give an expected range from the measurements in `references/usage.md`; for a shape no past run matches, say "not measured" and name the nearest run. Add each finished run there.

## 9. Files

One folder per debate beside the topic's notes; when there are none, the session's scratch folder, named in the start line. Debate folders can hold quotes from private material, so keep them out of anything published unless the user says otherwise. Files: `brief.md`, `subject.md` when needed, one report per agent and round (`<lens or side>-<round>.md`), `judge.md`, and `evidence/` for command output that a claim rests on.

The research these rules draw on is listed in `references/sources.md`; it is for maintaining this skill, not for running a debate.
