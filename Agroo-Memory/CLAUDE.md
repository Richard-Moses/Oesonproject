# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Agroo-Memory Card is a single-page, offline memory-matching (concentration) game — Black Star/Ghana-flag themed, produce-emoji cards on a red/gold/green board. It's built as one dependency-free HTML file and wrapped for Android via Capacitor for a Play Store release.

## Source of truth vs. packaged build

- **`index.html`** (repo root) is the real, editable source: all markup, CSS, and vanilla JS (no framework, no build step) live inline in this one file. Edit here.
- **`AgrooMemoryCard-android.zip`** is a *snapshot* of an already-generated Capacitor/Android Studio project (npm project, `android/` Gradle project, signing/store assets, `PLAY_STORE_GUIDE.md`). It embeds its own copies of `index.html` under `www/index.html` and `android/app/src/main/assets/public/index.html`.
- These copies drift from the root `index.html` the moment the root file is edited (as of the last zip refresh, both are in sync — but any future edit to `index.html` needs the same refresh). **Do not hand-edit the HTML inside the zip.** To refresh: unzip, copy the new `index.html` over `www/index.html`, then run `npm install && npx cap sync android` inside the unzipped project (this repopulates `android/app/src/main/assets/public/`). `capacitor.config.ts` requires `typescript` as a devDependency for `cap sync` to parse it — it's already in `package.json`; don't remove it. Actually compiling/signing the `.aab` requires Android Studio on a machine with the Android SDK, per `PLAY_STORE_GUIDE.md` inside the zip — there's no SDK/Gradle in this environment, so that step can't be done here.
- `play-store-assets/` holds the current Play Store listing images (icon, feature graphic, screenshots); these are duplicated inside the zip under `assets-src/` along with `generate_icons.py`, the script that produced the icon variants.

## Working with `index.html`

- Everything is one IIFE at the bottom of the file: game state (`state`), board construction (`buildBoard`), click/match logic (`onCardClick`, `checkMatch`), and a small on-the-fly Web Audio applause synth (`playApplause`/`playClap`) so no audio asset needs bundling.
- Board sizes are driven by the `SIZES` map (`3x4`/`4x4`/`4x5` → `{cols, pairs}`); the emoji deck comes from the `PRODUCE` array sliced to the pair count for the chosen size.
- Theming is CSS custom properties on `:root`, redefined for dark mode via both `prefers-color-scheme` and an explicit `[data-theme="dark"]` override — keep both in sync when changing colors.
- There's no test suite, linter, or build tool for this file. To check a change, open `index.html` directly in a browser (or serve the folder statically) and click through a game.

## Android/Play Store notes (from `PLAY_STORE_GUIDE.md` in the zip)

- Capacitor app id: `com.agroo.memorycard`; `webDir` is `www`.
- The Android build is intentionally offline-only (no `INTERNET` permission) and portrait-locked.
- Bump `versionCode`/`versionName` in `android/app/build.gradle` before any store update.

## Deployment

- **Web (live):** https://agroo-memory-card.netlify.app — a Netlify site deployed manually from this folder via `netlify deploy --dir=<folder with index.html> --prod --site-name agroo-memory-card`. It is **not** wired to auto-deploy from git; after editing `index.html`, redeploy manually or set up a Netlify build hook if that's wanted.
- **Repo:** this folder lives inside the `Oesonproject` monorepo (pushed to `origin` — see the repo's own notes on remotes before pushing; `main` has previously diverged from `origin/main` and needed a merge).
