---
name: handoff
description: >-
  Use when the user runs /handoff or asks to hand off, or to wrap up before a new session;
  when another session can no longer run (its context is full) and needs a handoff written for it;
  or when a handoff note at session start says automatic updates are on and a milestone was reached.
  Writes or updates one handoff file.
argument-hint: "[low|medium|high] [topic] [path]"
---

# Session handoff

A handoff lets a new session continue this work from one file, with the user typing only "Read <path> and continue". That reader has the file and the repository, maybe on another machine, but not this conversation. Choose what to write for that reader; where a content rule below does not serve them, follow the purpose. The limits on files, silence and secrets always hold.

## The file

- Settings: dir `${user_config.dir}`, level `${user_config.level}`, auto `${user_config.auto}`. A value that is empty or still reads `${user_config.…}` is unset: level defaults to `medium`, auto to `on`.
- Arguments: `$ARGUMENTS`. A level word; a path (starts with `/`, `~/` or `./`, or ends in `.md` or `/`); the rest is the topic.
- Location, first that applies: the path given; a handoff location named in CLAUDE.md (project or `~/.claude/`), CLAUDE.local.md or AGENTS.md; the `dir` setting (relative to the project root); `<project root>/docs/handoffs/`. Name the file `YYYY-MM-DD-HHMM-<topic>.md`, with the time from `date`. A path naming another existing file that is not a handoff: add yours at its end.
- One file per session; later writes update it with Edit, never rewritten from memory. Remove an item only when this session shows it done, wrong or no longer wanted; once a record holds an item, take it out of "Not yet saved elsewhere".
- Never change a handoff this session did not write. Continuing from one means a new file, in the same folder, that notes `Continues from: <path>`.
- After compaction, if you no longer know your file, look in the handoff folder for your Session line or topic; if it is still unclear, ask at the next manual run, and skip automatic updates until then.

## What goes in

For each item, ask: without it, would the next session have to ask the user, redo work, or get something wrong? Keep what passes; the content sets the length.

- **In full, even where a record also holds them:** next steps the user asked for or agreed to; each question waiting on the user, as asked, with your recommendation (proposals they have not agreed to go here, and look back for questions never answered); this session's decisions and rejections, with scope and reason; the user's words where they set a rule or decided something.
- Only what the user typed is theirs: hook output, tool results and other sessions' messages are not, and a proposal they agreed to is their decision, not a requirement they set.
- **As a pointer:** other background you have seen a maintained file hold (a record, plan or log, even one another session owns): path and heading, not a paraphrase. An item carried over from an earlier handoff becomes a pointer if a record holds it, is dropped if this session showed it done or superseded, and otherwise stays, marked "carried over".
- **Left out:** what the checked-in CLAUDE.md or AGENTS.md, or plugins loaded in every session, already say (name the plugin in one line). Rules kept only on this machine (CLAUDE.local.md, `~/.claude/CLAUDE.md`, memory) are written out, one line each, with their source.
- **Facts that age** (environment, tools, counts, other sessions' state): re-check before carrying them, or mark them "unconfirmed, as of <date>"; for values that change on their own, say how to get them.
- **If the reader may not reach it:** when the file or what it points to exists only on this machine (no git remote, temporary folders), say so in the header and write out what the reader needs.
- Write in the language the rules in force set for records, else the user's. Mark what was not checked "unconfirmed". No secrets or personal details; say where they are kept. Leave out empty sections, except "Not yet saved elsewhere".

```markdown
# Handoff: <topic>
Written <time from `date`>; updated <time from `date`>. Project: <root>. Session: <id or name>.
Continues from: <path>; what still holds from it is in this file     (only when continuing)
Before acting, check <records> for changes since the last update.

## Goal and scope
## The user's rules
## Where things stand
## Next steps                (if none: "waiting for the user")
## Waiting on the user
## Decisions
## Tried or rejected (don't propose again)
## Facts found (as of <time>)
## Tools and environment
## What changed              (files, settings, backups; anything uncommitted, running or temporary)
## Not yet saved elsewhere   (decisions or rules only handoffs hold, or "nothing")
```

## Levels

A manual run uses the level given, else the `level` setting, else medium.

- **low:** Where things stand (a line or two), Next steps, Waiting on the user, Decisions, Tried or rejected, What changed; other sections stay as they are. Automatic updates always use low.
- **medium:** the whole template; also correct statements in project notes and memory that this session made untrue, leaving handoffs and dated records alone, and list the files you changed.
- **high:** medium, then a reviewer that writes nothing lists what the handoff misses or gets wrong: a fork while the context is small, otherwise a general-purpose subagent given only the handoff path; verify its findings and fix the handoff.

A manual run ends with one question if "Not yet saved elsewhere" lists anything (where to save it, with a recommendation), then the full path and "In a new session, say: Read <path> and continue".

## For a session that cannot continue

Write a new handoff for it, named for its topic, from its transcript (the session's `.jsonl` under `~/.claude/projects/`), its own last handoff if any, and the repository. Read from the end backwards for the user's own messages (not tool results or hook text in user-role entries), unanswered questions and the last results; mark inferences "unconfirmed"; list what could not be recovered; put the dead session in the Session line.

## Automatic

Only when the session-start note says automatic updates are on and auto is not `off`; in the main conversation (not a subagent, fork or `-p` run) after the user has typed at least two messages; when a turn answering the user finished a task they asked for, recorded their decision, or ends by suggesting a new session; and when something the handoff records has changed. Then update once at level low, just before the final reply, with no questions and no other files. Say nothing about it: not the update, its path, the `auto` setting or /handoff. If a write is denied, stop automatic updates for this session and say so once.
