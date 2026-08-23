# Church Security Album

A visual member-verification album for church security teams. Built for
~300 members: search or filter the photo grid, click any face for an
instant full-detail card (photo, ID, group, phone, verified status).

## Tech stack

- **Backend:** Python + Flask
- **Database:** SQLite via SQLAlchemy (`church.db`)
- **Frontend:** HTML5, CSS3, vanilla JavaScript (no frameworks)
- **PWA:** installable to a phone's home screen, works offline for the
  app shell (service worker caches CSS/JS/icons)

## Features

- Responsive photo grid with live search (by name or ID) and a group
  filter (Men / Women / Youth / Children) — both work together, no
  page reload
- Click any card to open a detail modal (140px circular photo, name,
  ID badge, group, phone, "Verified Member" status); on phones this
  becomes a bottom sheet instead of a centered popup
- Add Member form with photo upload, live photo preview, and
  duplicate-ID checking
- Single shared-password login gate — the whole app (including member
  photos) requires signing in first, since it holds real names, phone
  numbers, and photos
- Installable as a PWA with a generated app icon (see `make_icons.py`)

## Running it locally

```
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000`. The default login password is
`changeme123` — change it before using real data:

```
set CHURCH_APP_PASSWORD=your-new-password   # Windows
export CHURCH_APP_PASSWORD=your-new-password  # macOS/Linux
```

## Project structure

```
app.py                  Flask app, routes, DB model, auth
requirements.txt         Pinned dependencies
static/css/style.css     Shared styles (mobile-first, dark mode)
static/js/app.js         Search/filter, modal, photo preview, service worker registration
static/icons/            Generated PWA icons (see make_icons.py)
static/manifest.webmanifest
sw.js                    Service worker (app-shell caching)
templates/               base.html + index/add_member/login pages
uploads/photos/          Member photos (not tracked in git — created at runtime)
church.db                SQLite database (not tracked in git — created at runtime)
```

## Deployment notes

Member photos and the SQLite database live outside `static/` and are
only reachable through the login-gated `/photos/<filename>` route —
they are never served by Flask's default `/static/` handler.

Deployed on PythonAnywhere's free tier for persistent storage (unlike
most free hosts, its filesystem isn't wiped between restarts, so
uploaded photos and the database survive). The WSGI entry point is
`from app import app as application`.
