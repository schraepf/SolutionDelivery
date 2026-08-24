# Templates

Client-neutral document templates. Every template is a normal Office file with
`{{TOKEN}}` placeholders where client-specific text belongs. Instantiate one
with `tools/new_document.py`; never edit a template in place to produce a
deliverable.

## Token registry

| Token | Meaning | Example |
|---|---|---|
| {{CLIENT_NAME}} | Client's full display name | Contoso Concrete LLC |
| {{CLIENT_ABBR}} | Client short name/acronym (used in prose, policy names like "{{CLIENT_ABBR}} Teams Policy", admin usernames like {{CLIENT_ABBR}}ADMIN) | CC |
| {{CLIENT_DOMAIN}} | Client's primary SMTP/vanity domain | contoso.com |
| {{CLIENT_TENANT}} | Cloud tenant subdomain (the part before .onmicrosoft.us / .microsoftonline.us) | contoso |
| {{AUTHOR_NAME}} | Essendis author shown on the title page | Jane Smith |
| {{DOC_DATE}} | Document date shown on the title page (M/D/YYYY) | 9/1/2026 |

Tokens are uppercase `A-Z`, `0-9` and underscores, wrapped in double braces.
Anything beyond the registry above can still be set ad hoc with
`--set TOKEN=VALUE`.

## Where tokens hide inside a .docx

A .docx is a zip of XML parts, and client references end up in more of them than
the document body. A token may live in any of:

- **Body text** — `word/document.xml`.
- **Headers and footers** — `word/header*.xml`, `word/footer*.xml`. Running
  headers carry the client name on every page.
- **Image alt-text** — the `descr` attribute on drawing elements, e.g. a logo
  described as "Contoso Concrete LLC logo".
- **Document properties** — `docProps/app.xml` `<Company>`, and the title in
  `docProps/core.xml`.
- **Hyperlink and mailto targets** — the `Target` attributes in
  `word/_rels/document.xml.rels`, e.g. `mailto:support@{{CLIENT_DOMAIN}}`.

Word's find/replace UI only walks the story text. It will not touch image
alt-text, document properties, or hyperlink targets, so a hand-instantiated
document reliably ships with the previous client's name buried in its metadata.
`tools/new_document.py` rewrites every `.xml` and `.rels` part in the package,
which is why it is the preferred instantiation path. Use it.

## Catalog

| Template | Description |
|---|---|
| `design/Microsoft_Government_Cloud_Migration_Solution_Design.docx` | Full solution design for a Microsoft government cloud (GCC High / Azure Government) migration: governance, identity, networking, security, Teams/SharePoint/Exchange, migration approach, and Terms of Use / CUI warning appendices. |
| `design/Data_Migration_Design.docx` | Data migration design structured as an AvePoint Fly discovery questionnaire and build sheet: source/destination tenant profiles, workload inventory, waves, and cutover. Contains an internal-guidance section that is removed from the deliverable. |

## Authoring rules for new templates

**Type tokens in one go.** Word splits a paragraph into runs whenever
formatting, spellcheck state, or an editing pause changes, and a token split
across runs (`{{CLIENT_` + `NAME}}`) is invisible on screen but will not match.
Type each token as contiguous plain text in a single pass rather than
assembling it from pieces or pasting it into styled text. If a template stops
instantiating cleanly, unzip it and grep the XML for a stray `{{` — a split
token is almost always the cause. Retyping the token fixes it.

**Keep Essendis branding.** The Essendis logo and tagline stay in the template.
Only *client* branding is genericized.

**Replace client logos with the placeholder.** Swap any client logo for the
neutral 225x225 "CLIENT LOGO" placeholder PNG, keeping the same anchor and
sizing so the layout holds.

**Mark internal-only sections.** Any section meant for the Essendis author
rather than the client gets `— REMOVE FROM DELIVERABLE` appended to its
heading, so it is obvious in the navigation pane and easy to find before
sending.

**No tracked changes, no comments.** Accept or reject every revision and delete
all comments before committing a template. They travel inside the package and
will surface in the client's copy.

**Metadata hygiene.** Set `docProps/core.xml` title to the template's name, set
`docProps/app.xml` `<Company>` to `{{CLIENT_NAME}}` so it is instantiated like
any other token, and set `DocSecurity` to `0`.

Before committing a new template, verify it holds zero client references — see
the generalization checklist in the root [README](../README.md).
