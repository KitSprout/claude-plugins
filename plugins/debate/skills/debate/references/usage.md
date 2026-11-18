# Measuring a debate's usage, and past measurements

## How to measure

Claude Code keeps each subagent's transcript as JSONL in the session's project folder: `<config dir>/projects/<project>/<session id>/subagents/agent-<id>.jsonl`, with `agent-<id>.meta.json` beside it naming the agent's description. Agents run by a workflow sit under `subagents/workflows/<run id>/`. Count each assistant message once (by `message.id`):

```
jq -rs '[.[] | select(.type=="assistant" and .message.usage != null)] | unique_by(.message.id)
  | map(.message.usage) | [ (map((.input_tokens//0)+(.cache_creation_input_tokens//0)+(.output_tokens//0))|add),
                           (map(.cache_read_input_tokens//0)|add) ] | @tsv' agent-<id>.jsonl
```

The first number is new tokens, the second cache reads. `message.model` in the same records shows which model actually ran. Minutes run from the first launch to the judge's report file.

## Past measurements

One machine, November 2026, the models of that time. Debater and judge effort were unset unless noted. A guide for the start line, not a promise; add each finished run.

| Run | Shape | Minutes | New tokens | Cache reads |
|---|---|---|---|---|
| three text-only debates | 2-3 sides, 1 round, judge; no source reading | not recorded | 0.13-0.32M | 0.4-4.1M |
| an option debate on a command design | 2 sides x 2 rounds (resumed), `opus` judge, reading sources | 36 | 1.44M | 23.6M |
| three option debates on record formats and storage | 3 sides x 2 rounds (fresh round-two agents), `opus` judge, reading sources and running checks | about 60 (one recorded: 58) | 1.66-2.51M | 27.8-61.5M |
| an option debate on a build plan | 2 sides x 2 rounds, every role on `fable`, the judge wrote a plan and an 80-row register | judge alone 51 | 3.34M | 97.5M |
| review of this skill's first draft, preset `high` (then called gate) | 3 sides x 2 rounds (two resumed, one fresh), `opus` debaters at effort high, `fable` judge at effort high, word limits in the brief | 72, including one reviewer rerun after an interruption; judge 7 | 1.04M | 12.6M |
| check of this skill's rewrite, preset `low` | 2 sides x 1 round, `opus` reviewers (effort unset) reading the earlier debate's reports, diffs and docs, `opus` judge at effort high | 23 (reviewers 17 each, judge 5) | 0.91M | 15.3M |
| second check of this skill, preset `low` | 2 sides x 1 round, `opus` reviewers (effort unset) limited to one diff, reports capped at 800 words, `opus` judge at effort high | 6 (reviewers 2-3, judge 3) | 0.34M | 3.7M |

## Comparisons

| Date | What | Result |
|---|---|---|
| 2026-11-17 | Round one of the skill review run twice on the same brief: three `opus` reviewers and three `sonnet` reviewers, both at effort high; a `fable` evaluator compared the two sets blind | Time: `sonnet` 3.3 min, `opus` 4.6 min (slowest reviewer). Usage: `sonnet` 0.39M new and 2.7M cache reads, `opus` 0.45M and 5.3M. Results: of nine serious problems, six were found by both sets, one only by `sonnet`, two only by `opus`; `opus` had no wrong claim, exact numbers and deeper replays of past debates; `sonnet` had more findings in all and one wrong claim. Two sets are twice the reviewers, so their union is not proof of the value of mixing models. Not adopted in presets: results were not better. |
| pending | Run only when the user asks: rerun one finished debate's judge outside the presets at effort medium, with the same inputs; compare rulings, minutes and tokens | not yet run |
