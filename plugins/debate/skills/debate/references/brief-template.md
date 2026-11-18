# Debate brief: <question in a few words> (<date>)

Format: <review | option>. Preset: <low | medium | high | max> (<settings changed by the user, if any>). Reports go to `<folder>/`.

## Background
<What this is and where it stands, in a few lines. No recommendation of the author's.>

## The question
<One question. For an option debate: the options, one or two lines each, including doing less and doing nothing. If the user wants a plan as the outcome, say so and give the judge's length limit for it.>

## The user's aim and measures
<The user's own words, each with its source (message date, decision id). What counts as better here, and what is not a reason.>

## Decisions in force
<Quoted, each with its id and where to read it in full. Mark each "fixed" or "open to challenge".>

## Facts
<Each with its source. Numbers, limits and premises without a source are marked "no source".>

## Sources to read
<Paths or links, with the sections that matter. `subject.md` when the subject lived only in the conversation.>

## Scenarios every position must handle
<Three to six, taken from real use.>

## Rules for every agent
- Read-only everywhere except your own report file at the path your prompt gives. Change nothing else, push nothing, send no message to other sessions.
- In round one, do not read the other reports in the report folder; round two hands them to you.
- These commands would prompt the user and must never be run; if a step needs one, skip it and report it: <the commands that prompt on this machine, written out>.
- Tools that are missing or differ here: <for example no python3, `grep` is a wrapper>.
- Name the source of every claim (file and line, decision, command output) or mark it inferred. A failed command is missing evidence, not evidence against.
- Never read or print secrets. Write in <language>.

## What each report delivers
Start with a summary of at most 200 words; return only that summary to the caller.

Round one: numbered findings, most serious first. For each: what is wrong, its source, a concrete scenario, the change you propose, and how sure you are (high, medium, low). Then what you checked and found sound, and what you could not check.

Round two: each of the others' findings with agree, partly agree or disagree and the evidence; then your own findings as they now stand (kept, changed, withdrawn, and why).

| Output | Words, at most |
|---|---|
| Round one | <1,200> |
| Round two | <1,000> |
| Judge | <1,600> |
