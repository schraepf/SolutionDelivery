# Essendis Solution Delivery

The documentation factory for Essendis client engagements. This repository
holds reusable, **client-neutral** document templates plus the tooling and
conventions for turning them into consistent client deliverables quickly:
design documents, as-configured documentation, questionnaires, user
communications, presentations, and reports.

The idea is simple. Templates carry `{{TOKEN}}` placeholders wherever
client-specific text belongs. A script fills them in. Nobody retypes a client
name into a 60-page design document, and nobody ships a document with the
previous client's name still in its metadata.

## Repository structure

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

## Quick start: generating a client deliverable

```
python tools/new_document.py templates/design/Data_Migration_Design.docx \
    --client-name "Contoso Concrete LLC" \
    --client-abbr CC \
    --client-domain contoso.com \
    --client-tenant contoso \
    --author "Jane Smith"
```

That writes:

```
deliverables/Contoso_Concrete_LLC/Contoso_Concrete_LLC__Data_Migration_Design__20260901.docx
```

Useful flags:

- `--list-tokens` — show which tokens a template uses and where they live,
  before you generate anything.
- `--set TOKEN=VALUE` — fill any token beyond the standard set; repeatable.
- `--date 9/1/2026` — override the title-page date (defaults to today).
- `--out PATH` — write somewhere other than the default `deliverables/` path.
- `--force` — overwrite an existing output file.

After generating, the script re-scans the output and warns about any `{{TOKEN}}`
still unfilled. That is expected when you skip an optional flag; it is a
reminder, not an error.

### The manual alternative, and why it is worse

You can copy a template and find/replace the `{{TOKENS}}` in Word. Be aware of
what that misses: Word's find/replace walks the document body only. It does
**not** reach image alt-text, document properties (`app.xml` `<Company>`), or
hyperlink and `mailto:` targets — all of which carry tokens in these templates.
A hand-instantiated document will look finished and still have placeholders, or
a prior client's name, buried in its metadata. The script rewrites every XML
part in the package, so it catches all of them. Prefer the script.

## Conventions

Deliverable file names follow:

```
<Client_Name>__<Document_Title>__<YYYYMMDD>.docx
```

Double underscores separate the three fields; spaces inside a field become
single underscores. For example:

```
Contoso_Concrete__Data_Migration_Design__20260901.docx
```

The placeholder token registry lives in [templates/README.md](templates/README.md).

## Adding a new template

New templates usually start as a real client document. Generalizing it means
removing every trace of that client:

1. **Client names and abbreviations** → `{{CLIENT_NAME}}` / `{{CLIENT_ABBR}}`,
   including policy names and admin usernames.
2. **Domains** → `{{CLIENT_DOMAIN}}`, in prose, examples, and email addresses.
3. **Tenant names** → `{{CLIENT_TENANT}}`, including `*.onmicrosoft.us` and
   `*.microsoftonline.us` references.
4. **Staff names** → `{{AUTHOR_NAME}}`, or a generic role if the name is not
   the document author.
5. **Client logos** → the neutral 225x225 "CLIENT LOGO" placeholder image.
   Essendis branding stays.
6. **Image alt-text** — check every image's `descr` attribute; logos are
   routinely described by client name.
7. **Document properties** — `docProps/app.xml` `<Company>` becomes
   `{{CLIENT_NAME}}`; `docProps/core.xml` title becomes the template's name.
8. **Headers and footers** — running headers usually repeat the client name on
   every page.
9. **Hyperlink targets** — `mailto:` and URL targets in
   `word/_rels/document.xml.rels` hide client domains.
10. **Accept all tracked changes** and delete all comments.

Then verify, rather than trusting the pass above. Unpack the document and sweep
the raw XML case-insensitively for the client's name, abbreviation, domain, and
tenant, then do the same against the extracted text:

```
mkdir -p /tmp/tmpl && unzip -o -q templates/design/New_Template.docx -d /tmp/tmpl
grep -ri -E 'contoso|concrete|\bcc\b' /tmp/tmpl && echo "FOUND -- not clean" || echo "clean"

pandoc -t plain templates/design/New_Template.docx | grep -i -E 'contoso|concrete'
```

Both sweeps must come back empty. The XML sweep catches metadata and alt-text;
the extracted-text sweep confirms the visible document reads correctly. Finish
by running `--list-tokens` on the finished template to confirm the placeholders
are intact and none got split across runs.

Authoring rules — how to insert tokens so they survive Word, branding, metadata
hygiene — are in [templates/README.md](templates/README.md).

## A note on `deliverables/`

`deliverables/` is the working area for generated client documents, one
subfolder per client. Its contents may include client-confidential material.
Commit deliberately: generated documents do not belong in version control by
default, and anything that lands there should be there because someone decided
it should be.
