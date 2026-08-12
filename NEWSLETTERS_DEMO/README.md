# Newsletters Demo

A WAT-framework project (see [CLAUDE.md](CLAUDE.md)) that curates newsletter
content from source articles and lands a draft in Gmail for review.

## One-time setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Create a Google Cloud OAuth client (Desktop app type), download the JSON,
   and save it as `credentials.json` in the project root (gitignored).
3. Run the Gmail auth flow once:
   ```
   python tools/gmail_auth.py
   ```
   This opens a browser to sign in and caches `token.json`.

## Structure

- `workflows/` — SOPs describing what to do and how.
- `tools/` — Python scripts that do the actual work.
- `.tmp/` — disposable intermediate files (scraped articles, draft text).
- `.env` — API keys / config overrides (gitignored).

See `workflows/curate_and_draft_newsletter.md` for the current end-to-end
process.
