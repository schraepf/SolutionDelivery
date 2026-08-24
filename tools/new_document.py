#!/usr/bin/env python3
"""Instantiate an Essendis document template into a client deliverable.

Replaces {{TOKEN}} placeholders throughout every XML part of a .docx package --
body text, headers/footers, image alt-text, document properties and hyperlink
targets -- which is why this is preferred over Word's find/replace.

Stdlib only. See templates/README.md for the token registry.
"""

import argparse
import datetime
import re
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Command-line flag -> placeholder token written inside the templates.
FLAG_TOKENS = [
    ("client_name", "CLIENT_NAME"),
    ("client_abbr", "CLIENT_ABBR"),
    ("client_domain", "CLIENT_DOMAIN"),
    ("client_tenant", "CLIENT_TENANT"),
    ("author", "AUTHOR_NAME"),
    ("date", "DOC_DATE"),
]

TOKEN_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")

# Parts of the package that hold text worth substituting. Everything else
# (images, fonts, the binary bits) is copied through untouched.
TEXT_SUFFIXES = (".xml", ".rels")


def is_text_part(name):
    return name.endswith(TEXT_SUFFIXES)


def xml_escape(value):
    """Escape a replacement value so it is safe to drop into XML."""
    value = value.replace("&", "&amp;")
    value = value.replace("<", "&lt;").replace(">", "&gt;")
    value = value.replace('"', "&quot;").replace("'", "&apos;")
    return value


def today_stamp():
    """Document date in M/D/YYYY with no zero padding."""
    now = datetime.date.today()
    return "%d/%d/%d" % (now.month, now.day, now.year)


def sanitize(name):
    """Client name -> filesystem-safe fragment.

    Whitespace runs become '_' and anything outside [A-Za-z0-9_-] is dropped.
    Dropping a character can strand its neighbouring underscores next to each
    other ("Smith & Sons" -> "Smith__Sons"), so runs are collapsed back to one:
    '__' is the field separator in the deliverable filename and must stay
    unambiguous.
    """
    collapsed = re.sub(r"\s+", "_", name.strip())
    kept = re.sub(r"[^A-Za-z0-9_-]", "", collapsed)
    return re.sub(r"_+", "_", kept).strip("_")


def scan_tokens(docx_path):
    """Map each {{TOKEN}} found in the package to (count, [part names])."""
    found = {}
    with zipfile.ZipFile(docx_path) as zf:
        for info in zf.infolist():
            if not is_text_part(info.filename):
                continue
            text = zf.read(info.filename).decode("utf-8", "replace")
            for token in TOKEN_RE.findall(text):
                entry = found.setdefault(token, [0, []])
                entry[0] += 1
                if info.filename not in entry[1]:
                    entry[1].append(info.filename)
    return found


def instantiate(template_path, out_path, values):
    """Copy the template to out_path, substituting {{TOKEN}} in text parts."""
    replacements = {"{{%s}}" % token: xml_escape(val) for token, val in values.items()}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(template_path) as src:
        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as dst:
            for info in src.infolist():  # preserve member order
                data = src.read(info.filename)
                if is_text_part(info.filename):
                    text = data.decode("utf-8")
                    for placeholder, value in replacements.items():
                        text = text.replace(placeholder, value)
                    data = text.encode("utf-8")
                dst.writestr(info, data)


def parse_set(pairs):
    """Turn --set TOKEN=VALUE strings into a dict, or fail loudly."""
    extra = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError("--set expects TOKEN=VALUE, got %r" % pair)
        token, value = pair.split("=", 1)
        token = token.strip()
        if not re.fullmatch(r"[A-Z0-9_]+", token):
            raise ValueError("--set token must be A-Z, 0-9 and underscores, got %r" % token)
        extra[token] = value
    return extra


def build_parser():
    parser = argparse.ArgumentParser(
        prog="new_document.py",
        description="Generate a client deliverable from an Essendis .docx template.",
        epilog=(
            "example:\n"
            "  python tools/new_document.py templates/design/Data_Migration_Design.docx \\\n"
            '      --client-name "Contoso Concrete LLC" --client-abbr CC \\\n'
            "      --client-domain contoso.com --client-tenant contoso \\\n"
            '      --author "Jane Smith"\n'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("template", type=Path, help="path to the .docx template")
    parser.add_argument("--client-name", help="client's full display name (fills {{CLIENT_NAME}})")
    parser.add_argument("--client-abbr", help="client short name or acronym (fills {{CLIENT_ABBR}})")
    parser.add_argument("--client-domain", help="client's primary SMTP/vanity domain (fills {{CLIENT_DOMAIN}})")
    parser.add_argument("--client-tenant", help="cloud tenant subdomain (fills {{CLIENT_TENANT}})")
    parser.add_argument("--author", help="Essendis author on the title page (fills {{AUTHOR_NAME}})")
    parser.add_argument("--date", help="title page date, M/D/YYYY (fills {{DOC_DATE}}; defaults to today)")
    parser.add_argument(
        "--set",
        action="append",
        default=[],
        metavar="TOKEN=VALUE",
        dest="extra",
        help="set any additional token; repeatable",
    )
    parser.add_argument("--out", type=Path, help="output path (overrides the default deliverables/ location)")
    parser.add_argument("--force", action="store_true", help="overwrite the output file if it already exists")
    parser.add_argument(
        "--list-tokens",
        action="store_true",
        help="list the tokens present in the template and exit without generating anything",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    template = args.template
    if not template.is_file():
        print("error: template not found: %s" % template, file=sys.stderr)
        return 1
    if not zipfile.is_zipfile(template):
        print("error: not a .docx package: %s" % template, file=sys.stderr)
        return 1

    if args.list_tokens:
        found = scan_tokens(template)
        if not found:
            print("No {{TOKEN}} placeholders found in %s" % template)
            return 0
        print("Tokens in %s:" % template)
        for token in sorted(found):
            count, parts = found[token]
            print("  %-20s %d occurrence(s)" % (token, count))
            for part in parts:
                print("      %s" % part)
        return 0

    values = {}
    for flag, token in FLAG_TOKENS:
        value = getattr(args, flag)
        if value is not None:
            values[token] = value
    values.setdefault("DOC_DATE", today_stamp())

    try:
        values.update(parse_set(args.extra))
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1

    if args.out:
        out_path = args.out
    else:
        if not args.client_name:
            print("error: --client-name is required to build the default output path "
                  "(or pass --out)", file=sys.stderr)
            return 1
        client = sanitize(args.client_name)
        if not client:
            print("error: --client-name has no usable characters for a folder name; "
                  "pass --out", file=sys.stderr)
            return 1
        stamp = datetime.date.today().strftime("%Y%m%d")
        filename = "%s__%s__%s.docx" % (client, template.stem, stamp)
        out_path = REPO_ROOT / "deliverables" / client / filename

    if out_path.exists() and not args.force:
        print("error: output already exists (use --force to overwrite): %s" % out_path, file=sys.stderr)
        return 1

    instantiate(template, out_path, values)
    print("Wrote %s" % out_path)

    leftover = scan_tokens(out_path)
    if leftover:
        print("\nwarning: unreplaced tokens remain in the output:")
        for token in sorted(leftover):
            count, parts = leftover[token]
            print("  %-20s %d occurrence(s) in %s" % (token, count, ", ".join(parts)))
        print("Provide the matching flag or --set TOKEN=VALUE, or edit the document by hand.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
