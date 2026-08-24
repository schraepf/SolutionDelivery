# Essendis Solution Delivery

The documentation factory for Essendis client engagements. This repository
holds reusable, **client-neutral** document templates plus the conventions for
turning them into consistent client deliverables quickly: design documents,
as-configured documentation, questionnaires, user communications,
presentations, and reports.

The idea is simple. Every template ends with an **Engagement Properties**
appendix: a small table where you type the client name, domain, tenant, and the
rest. Those cells are bound content controls, so typing a value there fills it
in everywhere it belongs — body prose, title page, running headers, policy
names, email addresses — as you type. Nobody retypes a client name into a
60-page design document, and nobody ships a document with the previous client's
name still in its metadata.

## Repository structure

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

## Quick start: generating a client deliverable

1. **Copy the template out of `templates/`.** Never edit a template in place to
   produce a deliverable. Put the copy under
   `deliverables/<Client_Name>/`.

2. **Open the copy and go to the final appendix** — "Appendix — Engagement
   Properties (REMOVE FROM DELIVERABLE)". Fill in the Value column. Each Value
   cell shows its property token (`{{CLIENT_NAME}}`, `{{CLIENT_ABBR}}`, and so
   on) until you type over it, and the Example column shows the expected shape
   of the answer. The document populates as you go — no field refresh (F9)
   needed.

3. **Save As** using the naming convention:

   ```
   <Client_Name>__<Document_Title>__<YYYYMMDD>.docx
   ```

   For example
   `deliverables/Contoso_Concrete_LLC/Contoso_Concrete_LLC__Data_Migration_Design__20260901.docx`.

4. **Before delivering**, delete the Engagement Properties appendix — the values
   are retained after it is gone — then update the table of contents (F9, or
   right-click → Update Field) so the removed appendix drops out of it. Remove
   any other section whose heading is marked "REMOVE FROM DELIVERABLE" as well.

If a `{{TOKEN}}` is still visible anywhere in the document, that property was
never filled. That is the point of the placeholder text: an unfilled document is
unmistakable.

### How it works

The Value cells in the appendix are Word **data-bound content controls**. They
do not paste text around the document; they display a single stored value, and
every other place that property appears is another control bound to the same
store. Edit any one of them and the rest follow.

- **Live propagation.** Values appear throughout the document as you type them
  (in desktop Word, when you click out of the cell). There are no fields to
  refresh.
- **Works in the browser.** Bound controls resolve the same way in Word for the
  web as in desktop Word, so a deliverable can be filled in without installing
  anything.
- **Metadata fills itself.** Client Name is bound to the document's built-in
  **Company** property, so `docProps/app.xml` gets the client name at the same
  time the title page does.
- **Values survive the appendix.** The stored values live in the document
  properties and an embedded XML part, not in the table. Deleting the appendix
  before delivery does not blank the document.
- **Nothing hides in the plumbing.** Spots that cannot host a content control —
  image alt-text, hyperlink and `mailto:` targets — no longer carry tokens at
  all; they were neutralized when the templates were built.

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

The engagement properties registry lives in [templates/README.md](templates/README.md).

## Adding a new template

New templates usually start as a real client document. Generalizing it means
removing every trace of that client. Client-specific text is replaced by a
**bound content control** for the matching property — the practical way to add
one is to copy an existing instance of that property's control from elsewhere in
the document and paste it where you need it (pasting preserves the binding), or
to wrap the site per the pattern documented in
[templates/README.md](templates/README.md).

1. **Client names and abbreviations** → Client Name / Client Abbreviation
   controls, including policy names and admin usernames.
2. **Domains** → Client Primary Domain controls, in prose, examples, and email
   addresses.
3. **Tenant names** → Client Tenant Subdomain controls, including
   `*.onmicrosoft.us` and `*.microsoftonline.us` references.
4. **Staff names** → a Prepared By control, or a generic role if the name is not
   the document author.
5. **Client logos** → the neutral 225x225 "CLIENT LOGO" placeholder image.
   Essendis branding stays.
6. **Image alt-text** — check every image's `descr` attribute; logos are
   routinely described by client name. Alt-text cannot host a control, so write
   neutral text there.
7. **Document properties** — `docProps/app.xml` `<Company>` becomes
   `{{CLIENT_NAME}}` (it is the Client Name store's unfilled value);
   `docProps/core.xml` title becomes the template's name.
8. **Headers and footers** — running headers usually repeat the client name on
   every page.
9. **Hyperlink targets** — `mailto:` and URL targets in
   `word/_rels/document.xml.rels` hide client domains. These cannot be bound
   either; neutralize them.
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
by opening the finished template and confirming every property token still shows
as placeholder text, and that typing a test value into the appendix reaches
every site you expect.

Authoring rules — how to add bound sites so they survive Word, branding,
metadata hygiene — are in [templates/README.md](templates/README.md).

## A note on `deliverables/`

`deliverables/` is the working area for generated client documents, one
subfolder per client. Its contents may include client-confidential material.
Commit deliberately: generated documents do not belong in version control by
default, and anything that lands there should be there because someone decided
it should be.
