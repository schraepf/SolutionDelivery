# Templates

Client-neutral document templates. Every template is a normal Office file whose
client-specific text is carried by **data-bound content controls**, filled in
from an "Appendix — Engagement Properties (REMOVE FROM DELIVERABLE)" table at
the end of the document. Copy a template to instantiate one; never edit a
template in place to produce a deliverable.

## Engagement properties registry

| Property | Placeholder shown until filled | Meaning | Example |
|---|---|---|---|
| Client Name | {{CLIENT_NAME}} | Client's full display name (also fills the Company document property) | Contoso Concrete LLC |
| Client Abbreviation | {{CLIENT_ABBR}} | Short name/acronym (prose, policy names like "CC Teams Policy", admin usernames like CCADMIN) | CC |
| Client Primary Domain | {{CLIENT_DOMAIN}} | Primary SMTP/vanity domain | contoso.com |
| Client Tenant Subdomain | {{CLIENT_TENANT}} | The part before .onmicrosoft.us / .microsoftonline.us | contoso |
| Prepared By | {{AUTHOR_NAME}} | Essendis author on the title page | Jane Smith |
| Document Date | {{DOC_DATE}} | Date shown on the title page (M/D/YYYY) | 9/1/2026 |

The `{{TOKEN}}` strings are the *visible placeholder text* of the bound
controls, not find/replace targets. They are what an unfilled control displays,
which makes an unfilled document obvious at a glance; typing a value into the
appendix replaces them everywhere. Do not find/replace them, and do not invent
new properties without adding them to this registry first.

## Where the values live

A .docx is a zip of XML parts, and an engagement property is stored once per
document, then displayed in as many places as it is needed:

- **Client Name** — the built-in **Company** document property,
  `docProps/app.xml` `<Company>`. Binding it there means document metadata is
  filled in by the same keystroke that fills the title page.
- **The other five** — a small custom XML part inside the package, namespace
  `urn:essendis:engagement-profile`, with one element per property:
  `ClientAbbr`, `ClientDomain`, `ClientTenant`, `AuthorName`, `DocDate`.
- **One bound control per occurrence.** Every visible instance — body text in
  `word/document.xml`, running headers and footers in `word/header*.xml` and
  `word/footer*.xml` — is a separate content control bound to the same stored
  value. Nothing is duplicated; they all render the one value.
- **The appendix table is just another set of controls.** Its Value cells have
  no special status. Editing any bound instance of a property, in the appendix
  or in the body, edits the same stored value, and every other instance updates
  to match. That is also why deleting the appendix before delivery is safe: the
  store is untouched.

Spots that cannot host a content control — image alt-text (`descr` attributes)
and hyperlink or `mailto:` targets in `word/_rels/document.xml.rels` — carry no
tokens at all. They were neutralized when the templates were built, so there is
nothing there to fill or to leak.

## Catalog

| Template | Description |
|---|---|
| `design/Microsoft_Government_Cloud_Migration_Solution_Design.docx` | Full solution design for a Microsoft government cloud (GCC High / Azure Government) migration: governance, identity, networking, security, Teams/SharePoint/Exchange, migration approach, and Terms of Use / CUI warning appendices. |
| `design/Data_Migration_Design.docx` | Data migration design structured as an AvePoint Fly discovery questionnaire and build sheet: source/destination tenant profiles, workload inventory, waves, and cutover. Contains an internal-guidance section that is removed from the deliverable. |

Both documents also carry the Engagement Properties appendix, which is likewise
removed from the deliverable.

## Authoring rules for new templates

**Add new client-specific sites by copy-paste.** To make a new spot
client-specific, copy an existing bound content control for that property from
elsewhere in the document and paste it in — copying preserves the data binding,
so the pasted control is live immediately. Do not type a token by hand; a typed
`{{CLIENT_NAME}}` is inert text that will ship as-is. If you are unsure whether
a control came across bound, unzip the file and check that the site carries a
data binding rather than a literal `{{`, or type a test value in the appendix
and confirm the new spot follows. The underlying pattern, if you ever have to
build one by hand: a content control (`w:sdt`) whose `w:dataBinding` points at
the property's node in the `urn:essendis:engagement-profile` part — or, for
Client Name, at the Company document property — with the `{{TOKEN}}` string as
the control's displayed text until a value is stored.

**Keep Essendis branding.** The Essendis logo and tagline stay in the template.
Only *client* branding is genericized.

**Replace client logos with the placeholder.** Swap any client logo for the
neutral 225x225 "CLIENT LOGO" placeholder PNG, keeping the same anchor and
sizing so the layout holds.

**Mark internal-only sections.** Any section meant for the Essendis author
rather than the client gets `— REMOVE FROM DELIVERABLE` appended to its
heading, so it is obvious in the navigation pane and easy to find before
sending. The Engagement Properties appendix is marked this way.

**No tracked changes, no comments.** Accept or reject every revision and delete
all comments before committing a template. They travel inside the package and
will surface in the client's copy.

**Metadata hygiene.** Set `docProps/core.xml` title to the template's name,
leave `docProps/app.xml` `<Company>` as `{{CLIENT_NAME}}` — it is the Client
Name store's unfilled value, not a stray token — and set `DocSecurity` to `0`.

### Programmatic fill (automation)

A script or automated session can instantiate a copy without opening Word: set
`<Company>` in `docProps/app.xml`, set the five values in the
`urn:essendis:engagement-profile` custom XML part, and let Word or LibreOffice
re-resolve the bindings when the document is opened. The displayed text in
`document.xml` is regenerated from the bindings, so the stores are the only
thing that has to be written.

The retired CLI generator script can be recovered from git history if batch
generation is ever needed again.

Before committing a new template, verify it holds zero client references — see
the generalization checklist in the root [README](../README.md).
