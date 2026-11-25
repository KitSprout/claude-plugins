---
type: llm
focus: {source: file, path: docs/handoffs/eval-gitignored.md}
---
docs/handoffs/ is listed in .gitignore; everything else is committed and pushed to origin. PASS if the handoff says that the handoff file itself is not committed (it is gitignored), so a reader on another machine will not have it. FAIL if it does not say so, for example if it says only that the work is committed and pushed.
