---
title: Flash
description: "Flash as a game runtime: SWF content, ActionScript, and running it today with Ruffle."
type: engine
status: draft
confidence: mixed
tags:
  - flash
  - swf
  - ruffle
  - runtime
aliases:
  - Adobe Flash
  - Macromedia Flash
  - Flash Player
platforms:
  - Web
  - Windows
  - macOS
  - Linux
games: []
formats: []
maturity: documented
sources:
  - title: Ruffle
    url: https://ruffle.rs/
  - title: Ruffle source and documentation
    url: https://github.com/ruffle-rs/ruffle
  - title: Adobe Flash Player end of life
    url: https://www.adobe.com/products/flashplayer/end-of-life.html
  - title: SWF File Format Specification, version 19
    url: https://open-flash.github.io/mirrors/swf-spec-19.pdf
last_verified: 2026-11-22
ai_assisted: true
---

# Flash

Flash is a multimedia runtime for vector graphics, animation, audio, video, and scripted interaction. Games built for it ship as SWF files, often with external media such as FLV, MP3, or WAV. Adobe ended support for Flash Player on 2020-12-31; Ruffle is the practical way to run this content today.

## At a glance

| Field | Value |
| --- | --- |
| Kind | Multimedia runtime |
| Primary format | SWF |
| Scripting | ActionScript, AVM1 and AVM2 |
| Modern runtime | Ruffle |
| Status here | Documented; no engine code in this repository |
| Confidence | Mixed: platform facts are established; game-specific claims come from project analysis |

## Why it matters

Some adventure games do not have a conventional native engine to reverse. The game logic and presentation are carried by SWF files and the Flash runtime. Preservation work is therefore runtime compatibility work: parse the SWF, implement the ActionScript virtual machine and display list, and reproduce the original timing.

This page covers Flash as a runtime. It does not document a specific game's file layout or story content.

## Evidence from this project

The release examined for these notes ships its content as SWF files, with additional FLV, MP3, WAV, and video assets. It runs well under Ruffle.

| Claim | Evidence level | Basis |
| --- | --- | --- |
| The payload is built from SWF files | Observed | File inventory from the project's disc analysis |
| The release also contains FLV, MP3, WAV, and video assets | Observed | Same inventory |
| Ruffle runs the release well | Observed | Recorded playtest in project correspondence |
| There is no conventional native engine to reverse | Inferred | Game logic and presentation are carried by the SWF payload; this does not rule out a small launcher |
| The compatibility matrix is complete | Unverified | Only the tested paths are known |

The inventory and playtest above are project records. They have not been re-run for this page, so treat the page as a working note rather than a final compatibility report.

## Running it today

Ruffle is an open-source Flash Player emulator written in Rust. It runs natively on desktop platforms and in browsers through WebAssembly. It supports ActionScript 1, 2, and 3, but compatibility is still incomplete, so a title that runs well is a data point rather than a guarantee for every SWF.

To try a SWF:

1. Install the Ruffle desktop build, or use the browser extension.
2. Open the game's main SWF, or point Ruffle at the launch SWF if the release uses a loader.
3. Keep the original directory structure. External assets are often referenced by relative path.
4. Record the Ruffle version and any visible defects.

Do not commit the SWF, FLV, audio, video, or extracted assets to this repository.

## Known use

*Scooby-Doo! Case File #3: Frights! Camera! Mystery!* ships as a SWF payload and runs well in Ruffle. No dedicated game page yet.

## What to record next

- Ruffle version and platform used for the playtest.
- The exact launch path, and whether a loader SWF is required.
- ActionScript version per SWF, if it can be determined.
- Any assets loaded from outside the main SWF.
- Visible defects, with a timestamp or scene description.
- A checksum for the tested build, if the build can be identified without distributing it.

## Sources

- [Ruffle](https://ruffle.rs/) — project site and downloads.
- [Ruffle source and documentation](https://github.com/ruffle-rs/ruffle) — emulator source, supported platforms, and project status.
- [Adobe Flash Player end of life](https://www.adobe.com/products/flashplayer/end-of-life.html) — Adobe's end-of-life notice, effective 2020-12-31.
- [SWF File Format Specification, version 19](https://open-flash.github.io/mirrors/swf-spec-19.pdf) — archived Adobe specification covering the SWF header, tags, ActionScript, audio, and video.
