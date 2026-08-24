## Maintaining this file
When you discover a project convention, correct a wrong assumption, or I give you an instruction that should apply permanently, propose an update to CLAUDE.md before finishing the task.

## How to work: plan, then orchestrate subagents

For all requests, Do the planning and design, then orchestrate the development
using subagents. When spawning subagents, select the model based on task
complexity:

- **claude-opus-5**: anything requiring judgment or generation — writing or
  modifying code, debugging, architectural analysis, security review,
  synthesizing findings across files.
- **sonnet**: moderate self-contained tasks — running test suites and
  summarizing failures, drafting docs, straightforward refactors with
  clear specs.
- **haiku**: purely mechanical retrieval — file discovery, grep-style
  searches, listing structure, fetching and extracting from logs.

When uncertain, escalate to the more capable model. Never route code
authorship or anything whose output you'll act on without verification
to haiku.
