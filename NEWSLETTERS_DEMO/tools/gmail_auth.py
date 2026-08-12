"""
One-time interactive Gmail OAuth setup.

Run from the project root:

    python tools/gmail_auth.py

This opens a browser window to sign in to the Gmail account that newsletter
drafts should land in, and caches a token to token.json (see .env for the
GMAIL_TOKEN_FILE / GMAIL_CREDENTIALS_FILE overrides). You only need to run
this once, and again if access is ever revoked.

Prerequisite: GMAIL_CREDENTIALS_FILE must point at an OAuth client JSON file
downloaded from Google Cloud Console (Desktop app type).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gmail_client import run_installed_app_flow  # noqa: E402


def main():
    print("Starting Gmail OAuth flow... a browser window should open.")
    run_installed_app_flow()
    print("Success. Token cached. You can now run tools that create drafts.")


if __name__ == "__main__":
    main()
