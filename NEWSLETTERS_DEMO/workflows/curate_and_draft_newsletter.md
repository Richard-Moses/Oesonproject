# Workflow: Curate & Draft Newsletter — "The Roberts Files"

## Objective
Turn a topic into a single issue of **The Roberts Files**, complete with a
masthead logo and one data-driven infographic, and land it as an HTML Gmail
draft for human review. Never send it — the user sends manually from Gmail
after reviewing.

## Required inputs
- A topic for the issue (issue 1: agentic AI in 2026).
- Source article URLs — found via web search when none are supplied.
- `GEMINI_API_KEY` set in `.env` (free tier at https://aistudio.google.com/apikey)
  for logo/infographic generation.
- Gmail OAuth set up (`python tools/gmail_auth.py` run once — see README.md).

## Steps
1. **Find sources.** If no URLs are supplied, web-search for ~4-6 recent,
   credible articles (news/analysis, not ads/listicles) on the issue's
   topic. Confirm the shortlist looks reasonable before scraping.

2. **Scrape each source.** For every URL, run:
   `python tools/scrape_article.py <url>`
   This returns `{url, title, text}` as JSON. Save each result to `.tmp/`
   (e.g. `.tmp/article_1.json`) since it's disposable intermediate data.

3. **Curate.** Read the scraped text for each article and pick what's
   actually newsletter-worthy — this is a judgment step, not a script.
   Drop anything off-topic, paywalled to nothing, or duplicate. Also pull
   out 3-6 concrete stats or a trend series worth visualizing.

4. **Generate/reuse the logo.** If `assets/logo.png` doesn't exist yet,
   generate it once:
   `python tools/generate_image.py "<prompt for a clean masthead logo reading 'The Roberts Files'>" assets/logo.png`
   Reuse the cached file on every later issue — don't regenerate it.

5. **Generate the infographic.** Using the stats pulled in step 3, run:
   `python tools/generate_image.py "<prompt describing an infographic combining those stats/trend points with the issue's topic>" .tmp/infographic.png`
   This is a per-issue, disposable intermediate (regenerate each run).

6. **Draft the newsletter body.** Write a single HTML newsletter body
   combining: the logo (`<img src="cid:logo">`) at the top, a short intro,
   each curated item as headline + 2-3 sentence summary + source link, and
   the infographic (`<img src="cid:infographic">`) near the relevant
   section. Save it to `.tmp/newsletter_draft.html` while iterating.

7. **Create the Gmail draft.** Once the body is finalized:
   `python tools/create_gmail_draft.py "The Roberts Files — <issue topic>" .tmp/newsletter_draft.html logo=assets/logo.png infographic=.tmp/infographic.png`
   This creates an HTML draft in Gmail with both images embedded inline.
   It does not send anything.

8. **Hand off.** Tell the user the draft is ready in Gmail and let them
   review/edit/send it themselves.

## Edge cases
- **A source URL fails to scrape** (403, paywall, JS-rendered page with no
  server-side content): skip it, note it to the user, don't block the rest
  of the run on one bad source.
- **Gmail token expired/revoked:** `tools/gmail_client.py` raises
  `GmailAuthError` with instructions to re-run `tools/gmail_auth.py`.
- **No credentials.json yet:** same error path — user needs to place an
  OAuth client (Desktop app type) from Google Cloud Console at
  `credentials.json` first.
- **No `GEMINI_API_KEY`:** `tools/generate_image.py` should fail fast with
  a clear message pointing at https://aistudio.google.com/apikey rather
  than a raw API error.

## Open questions (update this workflow once decided)
- Fixed source list vs. ad-hoc URLs per run? (Currently: ad-hoc, via web
  search.)
- Newsletter cadence (weekly? on-demand?) — not yet decided.
- Any house style/tone for summaries beyond "headline + 2-3 sentences"?

## Learnings
- **2026-08-12:** `gemini-2.5-flash-image` ("Nano Banana") returned a hard
  free-tier quota of 0 requests, even with a valid `GEMINI_API_KEY`
  (Google shifted image generation behind billing in 2026). Until billing
  is enabled on the Google Cloud project, skip steps 4-5 (logo/infographic
  generation) and run step 6 without `<img>` tags. `create_gmail_draft.py`
  already treats the `logo=`/`infographic=` arguments as optional — just
  omit them in step 7.
- **2026-08-12 (follow-up):** After linking a real billing account to the
  project (confirmed via
  `console.cloud.google.com/billing/linkedaccount?project=<id>` showing a
  live cost dashboard), image generation *still* returned the same
  `FreeTier` / limit-0 error for a while. This is quota-tier propagation
  lag, not a billing problem — Google's account linkage is instant but the
  `generativelanguage.googleapis.com` quota bump to Tier 1 can take a few
  hours (occasionally up to 24h) to actually apply. Don't re-diagnose
  billing setup if the linkedaccount page already shows an active account;
  just wait and retry later.
- **2026-08-12 (current method):** Switched steps 4-5 to Canva instead of
  `tools/generate_image.py`, since the Gemini quota never cleared during
  issue 1's session. Process: call the Canva MCP `generate-design` tool
  (design_type `logo` for the masthead, `infographic` for the per-issue
  graphic), show the 4 candidate thumbnail links to the user for a pick,
  `create-design-from-candidate` on their choice, then `export-design`
  (png) and download the signed URL with `curl -sL ... -o <path>` into
  `assets/logo.png` / `.tmp/infographic.png`. No billing/quota issues hit.
  `create_gmail_draft.py` has no update method, only create — so adding
  images to an already-drafted issue means creating a new draft and
  deleting the old one (`gmail_client.service.users().drafts().delete()`,
  no wrapper method exists for this yet). Revisit `generate_image.py` once
  the Gemini quota is confirmed working, but Canva is the current default.
