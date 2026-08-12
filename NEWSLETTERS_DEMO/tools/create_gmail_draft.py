"""
Create a Gmail draft from a finished newsletter body.

CLI usage:
    python tools/create_gmail_draft.py "<subject>" <path-to-body-file> [name=path ...]

If the body file ends in .html, an HTML draft is created; any trailing
`name=path` arguments are embedded as inline images referenced in the HTML
as `<img src="cid:name">` (e.g. `logo=assets/logo.png
infographic=.tmp/infographic.png`). Otherwise a plain-text draft is
created and image arguments are ignored.

Creates a draft in the authenticated Gmail account (see tools/gmail_auth.py
for one-time setup). Never sends anything — the human reviews and sends the
draft manually from Gmail.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gmail_client import gmail_client  # noqa: E402


def parse_images(args: list[str]) -> dict[str, Path]:
    images = {}
    for arg in args:
        if "=" not in arg:
            print(f"Ignoring malformed image argument (expected name=path): {arg}", file=sys.stderr)
            continue
        name, path = arg.split("=", 1)
        images[name] = Path(path)
    return images


def main():
    if len(sys.argv) < 3:
        print(
            'Usage: python tools/create_gmail_draft.py "<subject>" <path-to-body-file> [name=path ...]',
            file=sys.stderr,
        )
        sys.exit(1)

    subject = sys.argv[1]
    body_path = Path(sys.argv[2])
    body_text = body_path.read_text(encoding="utf-8")

    if body_path.suffix.lower() == ".html":
        images = parse_images(sys.argv[3:])
        result = gmail_client.create_html_draft(subject=subject, html_body=body_text, images=images)
    else:
        result = gmail_client.create_draft(subject=subject, body_text=body_text)

    print(f"Draft created: id={result.draft_id} message_id={result.message_id}")
    print("Review and send it manually from Gmail.")


if __name__ == "__main__":
    main()
