# CheReeSizer

Resize an image to an exact size without padding, then inspect the outermost pixels of all four edges at 8× to catch the white pad lines that online resizers leave behind (and that an upscale turns into visible stripes).

Everything runs locally. Nothing is uploaded.

## Download

Grab the latest build from the **Releases** page:

| System | File | Notes |
|---|---|---|
| Windows | `CheReeSizer_x.y.z_x64_en-US.msi` or `CheReeSizer_x.y.z_x64-setup.exe` | The installer isn't code-signed yet, so SmartScreen says "Windows protected your PC". Click **More info → Run anyway** once. |
| Linux (any distro) | `CheReeSizer_x.y.z_amd64.AppImage` | `chmod +x` it, then run it. |
| Ubuntu / Debian | `CheReeSizer_x.y.z_amd64.deb` | `sudo apt install ./CheReeSizer_x.y.z_amd64.deb` |
| Any browser, no install | `CheReeSizer.html` | Double-click to open. Saving uses the browser's normal download. |

## Using it

1. **Choose image**, drop a file on the preview, or paste with Ctrl+V.
2. Pick an output size (presets or exact pixels) and a fit mode:
   - **Exact** stretches to the target and never pads. This is the safe default.
   - **Contain** keeps the shape and pads the leftover. This is where pad lines come from.
   - **Cover** keeps the shape and crops the overflow.
3. Read the **Edge verdict** and the **Edge inspector**. A flat stripe hard against the amber rule is a defect; a varying bevel a few pixels in is real picture.
4. **Save image** as PNG, JPEG or WebP.

## Building

The desktop app is a [Tauri 2](https://tauri.app) wrapper around `src/index.html` (a single self-contained page). Pushing a tag `vX.Y.Z` runs `.github/workflows/release.yml`, which builds the Windows and Linux installers on GitHub's runners and publishes them on a Release, along with the standalone `CheReeSizer.html`.

Local build (needs Node and Rust): `npm ci`, then `npm run tauri build`.

`src/index.html` is the source of truth; edit it directly. `tools/port_artifact.py` is the one-time script that converted the original claude.ai artifact into it (embedded fonts, native Save As) and is kept for history only; re-running it would discard later changes such as the themes. Since v1.1.0 the icons in `src-tauri/icons/` are Cheree's artwork (the source PNGs live outside the repo); `tools/make_icons.py` only generated the original v1.0.0 placeholder icon.

## Versioning

Semantic versioning (`MAJOR.MINOR.PATCH`). The version lives in three places that must match: `package.json`, `src-tauri/Cargo.toml` and `src-tauri/tauri.conf.json`. Every commit adds an entry below, newest first.

## Changelog

### v1.1.0 (2026-10-01)
- **Themes:** the header's Theme button is now a picker with 7 themes: Auto (follows the system), Dark, Light, **Cheree** (pinks and magenta to match her icon), Ocean, Forest and High Contrast. Your choice is remembered between launches. The preview backdrops (Dark/Light/Checker/Magenta) are unchanged, since they're measurement tools.
- **New app icon:** Cheree with her milkshake and the CRS badge. The Windows .ico carries her own artwork at all five sizes (16, 32, 64, 128, 256), with no resampling.

### v1.0.0 (2026-10-01)
- First desktop release for Windows (.msi, .exe) and Linux (.AppImage, .deb), plus a standalone single-file HTML page.
- Ported from the claude.ai artifact: native Save As dialog in the app, a normal browser download in the HTML page.
- IBM Plex fonts embedded so it works fully offline.
- Build fix before the first release: the bundle category must be "Graphics and Design" (Tauri rejected "Graphics"); workflow actions updated to checkout@v5 / setup-node@v5.

## Licenses

IBM Plex is © IBM Corp., licensed under the SIL Open Font License 1.1 (see `OFL.txt`).
