---
name: rescue
description: >-
  Writes a handoff for another session that can no longer run (its context is full),
  from its transcript and the repository.
argument-hint: "<session id or transcript path> [topic] [path]"
disable-model-invocation: true
---

# Rescue handoff

Write the handoff of another session that can no longer run, so a new session can take over its work.

- First read `${CLAUDE_PLUGIN_ROOT}/skills/handoff/SKILL.md` and follow its rules for the file, what goes in and the template: write the whole template and end as a manual run does. Read as a file, its placeholders are not filled in; the `dir` setting is `${user_config.dir}`. If you cannot read it or the transcript, stop and say so.
- Arguments: `$ARGUMENTS`. First the session's id or transcript path, then an optional topic and an optional output path (starts with `/`, `~/`, `./` or `../`, or ends in `.md` or `/`), which is the path given. With no id or path, or one that matches no transcript, list the few newest transcripts of this project other than this session's, with time and last user message, and ask; write nothing until the user picks.
- Sources: its transcript (its `.jsonl` under `~/.claude/projects/`; a session started from claude.ai has another id there: search the transcripts for its id or title), its own last handoff if any, and the repository. Its project is the transcript's `cwd`: use it for the location, the Project line and git. A transcript can be megabytes: filter it with a script.
- Read the transcript from the end backwards for the user's own messages, unanswered questions and the last results. Mark inferences "unconfirmed"; list what could not be recovered.
- Write a new file at the path given, else named for its topic. Put the dead session's id in the Session line, never `${CLAUDE_SESSION_ID}`: this file is not yours.
