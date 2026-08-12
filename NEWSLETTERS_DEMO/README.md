# Newsletters Demo

A WAT-framework project (see [CLAUDE.md](CLAUDE.md)) that curates newsletter
content from source articles and lands a draft in Gmail for review.

## Overview

This project turns a topic into a finished newsletter issue, *The Roberts
Files*, and drops it into Gmail as a draft for a human to review and send —
it never sends anything automatically.

It runs on a "WAT" pattern (Workflows / Agents / Tools): a plain-language SOP
file (`workflows/curate_and_draft_newsletter.md`) defines what to do, an
agent makes the judgment calls (which sources are worth including, how to
word summaries), and Python scripts in `tools/` handle the deterministic
parts (scraping, image export, Gmail API calls).

End-to-end, one run does this:

1. Web-search for 4-6 credible news/analysis articles on the topic.
2. Scrape each one, skipping any that fail (paywalls, blocks).
3. Curate — drop anything off-topic or duplicate, pull out the real stats.
4. Generate a masthead logo (once, reused every issue) and a per-issue
   infographic — via Canva, with Gemini's image model (`generate_image.py`)
   as a fallback once its billing quota is available.
5. Write the HTML newsletter body.
6. Create the Gmail draft with both images embedded inline.
7. Hand it off for the human to review and send.

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
