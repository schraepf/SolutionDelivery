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

## Repository purpose & layout

Essendis's documentation factory: client-neutral document templates plus
tooling for generating consistent client deliverables (design documents,
as-configured documentation, questionnaires, user communications,
presentations, reports). Templates carry `{{TOKEN}}` placeholders;
`tools/new_document.py` fills them in to produce a deliverable. Templates are
never edited in place to make a deliverable.

```
templates/
  design/            # solution & technical design documents
  as-configured/     # as-built / as-configured documentation
  questionnaires/    # discovery & scoping questionnaires
  communications/    # user-facing comms (cutover notices, onboarding emails)
  presentations/     # slide decks
  reports/           # status / assessment / closeout reports
tools/               # generation scripts
deliverables/        # generated client documents, one subfolder per client
```

## Document conventions

Deliverable file names: `<Client_Name>__<Document_Title>__<YYYYMMDD>.docx` —
double underscores between fields, spaces within a field become single
underscores.

The placeholder token registry is in `templates/README.md`. Treat it as the
source of truth; do not invent tokens without adding them there.

All Word, PowerPoint, Excel, and PDF work goes through the corresponding skill
(docx / pptx / xlsx / pdf). Do not hand-edit Office XML outside those skills.

## Workflows

**New client deliverable.** Run the generator:

```
python tools/new_document.py templates/design/Data_Migration_Design.docx \
    --client-name "Contoso Concrete LLC" --client-abbr CC \
    --client-domain contoso.com --client-tenant contoso --author "Jane Smith"
```

Check the post-generation warning for unfilled tokens.

**New template from a client document.** Follow the generalization checklist in
`README.md`. Replace the client logo with the placeholder image, accept all
tracked changes, fix `docProps` metadata (`core.xml` title, `app.xml` Company),
then verify zero client references two ways: a case-insensitive grep of the
unpacked package XML *and* a case-insensitive grep of pandoc-extracted text.
Both must come back empty.

**Templates never contain** tracked changes, comments, or real client data.
