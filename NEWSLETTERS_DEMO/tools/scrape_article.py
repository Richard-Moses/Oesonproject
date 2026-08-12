"""
Fetch a single URL and extract its readable text.

CLI usage:
    python tools/scrape_article.py <url>

Prints JSON with {url, title, text} to stdout. Used by the
curate_and_draft_newsletter workflow to pull source articles before
summarizing them.
"""
from __future__ import annotations

import json
import sys

import requests
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (compatible; NewslettersDemoBot/1.0)"

# Tags that are never part of the readable article body.
STRIP_TAGS = ["script", "style", "nav", "header", "footer", "form", "aside", "noscript"]


def scrape_article(url: str, timeout: int = 15) -> dict:
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(STRIP_TAGS):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    article = soup.find("article") or soup.find("main") or soup.body
    text = article.get_text(separator="\n", strip=True) if article else ""

    return {"url": url, "title": title, "text": text}


def main():
    if len(sys.argv) != 2:
        print("Usage: python tools/scrape_article.py <url>", file=sys.stderr)
        sys.exit(1)

    result = scrape_article(sys.argv[1])
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
