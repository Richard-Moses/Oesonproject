"""
Thin wrapper around the Gmail API — drafts only.

Deliberately has no send method. This module can create/update/list drafts
in Gmail so a human can review and send them manually. Nothing in this
project sends email; see CLAUDE.md's "never send without approval" rule.

Auth: installed-app OAuth flow via google-auth-oauthlib. Run
`python tools/gmail_auth.py` once to produce the cached token file; after
that, this module refreshes the token silently.
"""
from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv()

# gmail.compose is the narrowest Gmail scope that permits creating drafts.
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CREDENTIALS_PATH = Path(os.getenv("GMAIL_CREDENTIALS_FILE", PROJECT_ROOT / "credentials.json"))
TOKEN_PATH = Path(os.getenv("GMAIL_TOKEN_FILE", PROJECT_ROOT / "token.json"))


class GmailAuthError(RuntimeError):
    pass


@dataclass
class DraftResult:
    draft_id: str
    message_id: str


def load_credentials() -> Credentials:
    """Load cached credentials, refreshing if needed. Raises GmailAuthError
    with an actionable message if the one-time auth script hasn't been run.
    """
    if not TOKEN_PATH.exists():
        raise GmailAuthError(
            f"No Gmail token found at {TOKEN_PATH}. Run `python tools/gmail_auth.py` first."
        )
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), GMAIL_SCOPES)
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            TOKEN_PATH.write_text(creds.to_json())
        except RefreshError as exc:
            raise GmailAuthError(
                "Gmail token expired/revoked. Re-run `python tools/gmail_auth.py`."
            ) from exc
    return creds


def run_installed_app_flow() -> Credentials:
    """One-time interactive OAuth flow. Called by tools/gmail_auth.py."""
    if not CREDENTIALS_PATH.exists():
        raise GmailAuthError(
            f"No OAuth client file found at {CREDENTIALS_PATH}. Download it from Google "
            "Cloud Console (OAuth client, Desktop app type) and place it there."
        )
    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), GMAIL_SCOPES)
    creds = flow.run_local_server(port=0)
    TOKEN_PATH.write_text(creds.to_json())
    return creds


class GmailClient:
    def __init__(self) -> None:
        self._service = None

    @property
    def service(self):
        if self._service is None:
            creds = load_credentials()
            self._service = build("gmail", "v1", credentials=creds, cache_discovery=False)
        return self._service

    def create_draft(self, subject: str, body_text: str, to: Optional[str] = None) -> DraftResult:
        """Creates a plain-text Gmail draft in the authenticated account. Does not send it."""
        message = MIMEText(body_text)
        message["subject"] = subject
        if to:
            message["to"] = to
        return self._create_draft_from_message(message)

    def create_html_draft(
        self,
        subject: str,
        html_body: str,
        images: Optional[Dict[str, Path]] = None,
        to: Optional[str] = None,
    ) -> DraftResult:
        """Creates an HTML Gmail draft with inline images. Does not send it.

        `images` maps a cid name (referenced in `html_body` as
        `<img src="cid:NAME">`) to a local image file path.
        """
        message = MIMEMultipart("related")
        message["subject"] = subject
        if to:
            message["to"] = to
        message.attach(MIMEText(html_body, "html"))

        for cid_name, image_path in (images or {}).items():
            image_path = Path(image_path)
            image_part = MIMEImage(image_path.read_bytes())
            image_part.add_header("Content-ID", f"<{cid_name}>")
            image_part.add_header("Content-Disposition", "inline", filename=image_path.name)
            message.attach(image_part)

        return self._create_draft_from_message(message)

    def _create_draft_from_message(self, message) -> DraftResult:
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        draft = (
            self.service.users()
            .drafts()
            .create(userId="me", body={"message": {"raw": raw}})
            .execute()
        )
        return DraftResult(draft_id=draft["id"], message_id=draft["message"]["id"])


gmail_client = GmailClient()
