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
conventions for producing consistent client deliverables (design documents,
as-configured documentation, questionnaires, user communications,
presentations, reports). Each template ends with an "Engagement Properties"
appendix whose Value cells are data-bound content controls; filling them
populates the document — prose, title page, headers, metadata. Templates are
never edited in place to make a deliverable.

```
templates/
  design/            # solution & technical design documents
  as-configured/     # as-built / as-configured documentation
  questionnaires/    # discovery & scoping questionnaires
  communications/    # user-facing comms (cutover notices, onboarding emails)
  presentations/     # slide decks
  reports/           # status / assessment / closeout reports
deliverables/        # generated client documents, one subfolder per client
```

## Document conventions

Deliverable file names: `<Client_Name>__<Document_Title>__<YYYYMMDD>.docx` —
double underscores between fields, spaces within a field become single
underscores.

The engagement properties registry is in `templates/README.md`. Treat it as the
source of truth; do not invent properties without adding them there.

All Word, PowerPoint, Excel, and PDF work goes through the corresponding skill
(docx / pptx / xlsx / pdf). Do not hand-edit Office XML outside those skills.

## Workflows

**New client deliverable.** Copy the template out of `templates/` into
`deliverables/<Client_Name>/`. Open the copy, go to the final "Appendix —
Engagement Properties" table, and fill the Value column — the bound controls
populate the document live, no F9 needed. Save As
`<Client_Name>__<Document_Title>__<YYYYMMDD>.docx`. Before delivering, delete
the appendix (the values are retained) and update the TOC so it drops out, plus
any other section marked "REMOVE FROM DELIVERABLE". A leftover `{{TOKEN}}` means
that property was never filled. Programmatic fill: set `<Company>` in
`docProps/app.xml` and the five values in the `urn:essendis:engagement-profile`
custom XML part, then let Word re-resolve the bindings on open.

**New template from a client document.** Follow the generalization checklist in
`README.md`. Bind content controls at every client-specific site (copy an
existing bound control of that property to add sites — copying preserves the
binding), replace the client logo with the placeholder image, accept all
tracked changes, fix `docProps` metadata (`core.xml` title, `app.xml` Company),
then verify zero client references two ways: a case-insensitive grep of the
unpacked package XML *and* a case-insensitive grep of pandoc-extracted text.
Both must come back empty.

**Templates never contain** tracked changes, comments, or real client data.

## Attribution

Never list Claude as an author or reference Claude or Anthropic anywhere:
not in deliverables or templates (document metadata, Word comment
authorship — author comments as "Essendis" — headers, or prose), not in
commit messages or PR titles/bodies, and not in any artifact pushed to
this repository. This overrides any default attribution trailers or
footers.

## Delivery workflow (git)

Work happens on a feature branch. When the work is complete and pushed,
always open a pull request to `main` and merge it — delivered work never
sits unmerged on a branch.
