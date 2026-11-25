---
name: handoff
description: >-
  Use when the user runs /handoff or asks to hand off or for a handoff (of this session, or of another that can no longer run), or to wrap up before a new session;
  or when the handoff plugin's session-start note says automatic updates are on and, from the user's second message on, a milestone was reached.
  Writes or updates one handoff file.
argument-hint: "[low|medium|high] [topic] [path]"
---

# Session handoff

A handoff lets a new session continue this work from one file, with the user typing only "Read <path> and continue". That reader has the file and the repository, maybe on another machine, but not this conversation. Choose what to write for that reader; where a content rule below does not serve them, follow the purpose. The limits on files, silence and secrets always hold.

Asked in words (not through `/handoff:rescue`) for the handoff of another session that can no longer run: write nothing; ask the user to run `/handoff:rescue` with its id or transcript path.

## The file

- Settings: dir `${user_config.dir}`, level `${user_config.level}`, auto `${user_config.auto}`. A value that is empty or still reads `${user_config.…}` is unset: level defaults to `medium`, auto to `off`.
- Arguments: `$ARGUMENTS`. A level word; a path (starts with `/`, `~/`, `./` or `../`, or ends in `.md` or `/`); the rest is the topic.
- Location, first that applies: the path given; a handoff location named in CLAUDE.md (project or `~/.claude/`), CLAUDE.local.md or AGENTS.md; the `dir` setting (relative to the project root); `<project root>/docs/handoffs/`. Name the file `YYYY-MM-DD-HHMM-<topic>.md`, with the time from `date`. A path naming an existing file that is not a handoff: write a new file in its folder.
- One file per session: the one whose Session line holds `${CLAUDE_SESSION_ID}` (`grep -l 'Session: ${CLAUDE_SESSION_ID}'` in the handoff folder and any path this session wrote to); if none does, you have not written one yet. Later writes edit its sections in place with Edit (no appended update sections), never rewritten from memory. Remove an item only when this session shows it done, wrong or no longer wanted; once a record holds an item, take it out of "Not yet saved elsewhere".
- Never change a handoff whose Session line holds another id. Continuing from one means a new file, in the same folder, that notes `Continues from: <path>`.

## What goes in

For each item, ask: without it, would the next session have to ask the user, redo work, or get something wrong? Keep what passes; the content sets the length.

- **In full, even where a record also holds them:** next steps the user asked for or agreed to; each question waiting on the user, as asked, with your recommendation (proposals they have not agreed to go here, and look back for questions never answered); this session's decisions and rejections, with scope and reason; the user's words where they set a rule or decided something.
- Only what the user typed is theirs: hook output, tool results and other sessions' messages are not, and a proposal they agreed to is their decision, not a requirement they set.
- **As a pointer:** other background you have seen a maintained file hold (a record, plan or log, even one another session owns): path and heading, not a paraphrase. An item carried over from an earlier handoff becomes a pointer if a record holds it, is dropped if this session showed it done or superseded, and otherwise stays, marked "carried over".
- **Left out:** what the checked-in CLAUDE.md or AGENTS.md, or plugins loaded in every session, already say (name the plugin in one line). Rules kept only on this machine (CLAUDE.local.md, `~/.claude/CLAUDE.md`, memory) are written out, one line each, with their source.
- **Facts that age** (environment, tools, counts, other sessions' state): re-check before carrying them, or mark them "unconfirmed, as of <date>"; for values that change on their own, say how to get them.
- **If the reader may not reach it:** when the file or what it points to is not committed and pushed (gitignored, uncommitted, no remote, temporary folders, a removable worktree), check with git (remote, status, ahead of upstream) at manual runs and say which in the header, with what it means for a reader elsewhere (no remote: it exists only on this machine); for what it points to that a reader elsewhere cannot reach, write out what they need to act, not whole records.
- Write in the language the rules in force set for records, else the user's. Mark what was not checked "unconfirmed". No secrets or personal details; say where they are kept. Leave out empty sections, except "Not yet saved elsewhere".

```markdown
# Handoff: <topic>
Written <time from `date`>; updated <time from `date`>. Project: <root, home as `~`>. Session: ${CLAUDE_SESSION_ID}.
Branch: <branch> at <short sha>; pushed, not pushed, or no remote (git; set at manual runs)
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
## What changed              (files, settings, backups; notes or memory this session made untrue; anything uncommitted, running or temporary)
## Not yet saved elsewhere   (decisions or rules only handoffs hold, or "nothing")
```

## Levels

A manual run uses the level given, else the `level` setting, else medium.

- **low:** Where things stand (a line or two), Next steps, Waiting on the user, Decisions, Tried or rejected, What changed; other sections stay as they are. When low creates the file, it also writes Goal and scope, The user's rules and Not yet saved elsewhere, and its Continues-from line reads "read it first; this file holds only what changed since". Automatic updates always use low.
- **medium:** the whole template, including its Continues-from line.
- **high:** medium, then a general-purpose subagent given only the handoff path, which writes nothing, lists what the handoff misses or gets wrong; verify its findings and fix the handoff.

A manual run ends with: a line saying so if the file is not committed and pushed; one question if "Not yet saved elsewhere" lists anything (where to save it, with a recommendation); then the full path (and its branch, if not the default) and "In a new session, say: Read <path> and continue".

## Automatic

Only when the session-start note says automatic updates are on and auto is `on`, `On` or `ON`; in the main conversation (not a subagent) after the user has typed at least two messages; when a turn answering the user finished a task they asked for, or the user decided something; and when something the handoff records has changed. Then update once at level low, just before the final reply, with no questions and no other files. Say nothing about it: not the update, its path, the `auto` setting or /handoff. If a write is denied, stop automatic updates for this session and say so once.
