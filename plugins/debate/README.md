# debate

One skill, `debate`, that runs a subagent debate or a multi-reviewer challenge and brings the result back to the user.

## Install

```
/plugin marketplace add KitSprout/claude-plugins
/plugin install debate@kitsprout
```

## Use

Ask in words in any language (「subagent 互相辯論」, "debate this plan"), or type the command:

```
/debate:debate [low|medium|high|max] [setting=value ...] <what to debate>
```

Examples: `/debate:debate the storage plan`, `/debate:debate high rounds=1 sides=2 the release checklist`, `/debate:debate low debaters=sonnet`. With no preset named, it runs `medium`, whose time and usage are close to those of debates run before this skill. With no subject, it takes the subject from the conversation and says how it read it. When only a rule or another skill calls for a debate, the session proposes it and waits.

## Presets

| Preset | Use when | sides | rounds | debaters | judge |
|---|---|---|---|---|---|
| `low` | a small or easily undone choice, a second opinion | 2 | 1 | `opus` | `opus`, effort high |
| `medium` | the default; most design decisions and plans | 3 | 2 | `opus` | `opus`, effort high |
| `high` | the last check before something costly to redo | 3 | 2 | `opus` | `fable`, effort high |
| `max` | only when asked; not measured | 4 | 2 | `opus` | `fable`, effort xhigh |

## Settings

| Setting | Choices |
|---|---|
| `sides` | 2, 3, 4 |
| `rounds` | 1, 2 |
| `debaters` | `opus`, `sonnet`, `fable`, `mixed` |
| `debater-effort` | unset (default), low, medium, high, xhigh |
| `judge` | `opus`, `fable` |
| `judge-effort` | high (default), xhigh, max |

Only the first word after the command can be a preset; effort values appear only after `=`. What each setting costs in time and usage, and what it buys, is in the skill.

## Files

- `skills/debate/SKILL.md`: the procedure.
- `skills/debate/references/brief-template.md`: the brief every agent reads, with the report form.
- `skills/debate/references/usage.md`: how to measure time and tokens, past runs, comparisons.
- `skills/debate/references/sources.md`: the research behind the rules, for maintaining the skill.
