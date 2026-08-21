# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Agroo-Memory Card is a single-page, offline memory-matching (concentration) game — Black Star/Ghana-flag themed, produce-emoji cards on a red/gold/green board. It's built as one dependency-free HTML file and wrapped for Android via Capacitor for a Play Store release.

## Source of truth vs. packaged build

- **`index.html`** (repo root) is the real, editable source: all markup, CSS, and vanilla JS (no framework, no build step) live inline in this one file. Edit here.
- **`AgrooMemoryCard-android.zip`** is a *snapshot* of an already-generated Capacitor/Android Studio project (npm project, `android/` Gradle project, signing/store assets, `PLAY_STORE_GUIDE.md`). It embeds its own copies of `index.html` under `www/index.html` and `android/app/src/main/assets/public/index.html`.
- These copies drift from the root `index.html` as soon as the root file is edited (there is currently a known diff — the root file has a footer credit line the packaged copy lacks). **Do not hand-edit the HTML inside the zip.** To refresh the Android build after changing the root `index.html`: unzip, copy the new `index.html` over `www/index.html`, then run `npm install && npx cap sync android` inside the unzipped project (this repopulates `android/app/src/main/assets/public/`). Actually compiling/signing the `.aab` requires Android Studio, per `PLAY_STORE_GUIDE.md` inside the zip.
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
