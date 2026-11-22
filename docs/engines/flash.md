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
| Scripting | ActionScript 1/2 (AVM1) in the inspected copy; Flash also supports AVM2/AS3 |
| Modern runtime | Ruffle |
| Status here | Documented; no engine code in this repository |
| Confidence | Mixed: platform facts are established; game-specific claims come from project analysis |

## Why it matters

Some adventure games do not have a conventional native engine to reverse. The game logic and presentation are carried by SWF files and the Flash runtime. Preservation work is therefore runtime compatibility work: parse the SWF, implement the ActionScript virtual machine and display list, and reproduce the original timing.

This page covers Flash as a runtime. It does not document a specific game's file layout or story content.

## Evidence from this project

A local 2007 Windows re-release was inspected with JPEXS Free Flash Decompiler 26.2.1 and ExifTool 13.59.

The directory is flat: 183 files, 144,858,832 bytes. The SWF set totals 125,045,416 bytes: 60 uncompressed `FWS`, 57 zlib `CWS`, none LZMA. The remaining files include 36 MP3, 3 WAV, 1 AIF, 2 FLV (On2 VP6 video with MP3 audio), and Windows installer/runtime files. The largest SWFs are `scooby_base.swf` (23,500,810 bytes), `CDC.swf` (10,239,921), `Title.swf` (6,666,801), and `StuntExtravaganza.swf` (6,556,643).

| Claim | Evidence level | Basis |
| --- | --- | --- |
| The installed copy contains 117 SWF files totaling 125,045,416 bytes | Observed | Recursive file inventory |
| Every SWF reports SWF version 8 | Observed | Header scan across all 117 files |
| The content is AVM1/AS2, not AVM2/AS3 | Observed | No `DoABC` tags in any SWF; 316 `DoAction`/`DoInitAction` tags total |
| The SWFs use standard tags and standard compression | Observed | Tag inventory: `PlaceObject2`, `DefineShape`, `DefineSprite`, `DefineSound`, `DefineFont3`, `ExportAssets`; `FWS` and `CWS` only |
| The launcher is a stock Macromedia Flash Player 8.0 r22 projector | Observed | PE version info: company `Macromedia, Inc.`, original name `SAFlashPlayer.exe`, file version `8.0.22.0` |
| `scooby_base.swf` is mainly an asset library | Observed | 23.5 MB of font and `DefineSound`/`ExportAssets` entries, with only six frame scripts |
| There is no custom container, encryption, or native engine layer | Observed | Normal SWF structure; no custom tags or encrypted SWFs found |
| Game logic is distributed across the SWF set | Inferred | `CDC.swf` and `Title.swf` contain game-facing scripts; the launcher itself is only a player |
| Ruffle runs the release well | Observed | Reported in the project's playtest notes; not re-run for this page |
| The compatibility matrix is complete | Unverified | Only the tested paths are known |

The inspected copy contains 117 SWFs. Do not generalize that count to other releases without checking them. The playtest result is a data point, not a guarantee for every scene or asset.

## Detection

These hashes identify the inspected files. They are recorded here; the files themselves are not distributed in this repository.

| File | Size (bytes) | MD5 (first 5,000 bytes) | SHA-256 |
| --- | ---: | --- | --- |
| `Scooby-Doo! Case File #3 - Frights! Camera! Mystery!.exe` | 1,622,602 | `3bfe46ec07db957d7ee208acb1cc49e7` | `d7f97359ad1d076bac5795c92ca7c992b9f13e240e1ebd7e21cdf5229624e991` |
| `scooby_base.swf` | 23,500,810 | `a433df7006d45ecf501b0d80581d70c4` | `b2fd40e0433629581137ea267b9c12b36f884a08bccb94cef3f52a9f77440b56` |
| `CDC.swf` | 10,239,921 | `39897c1da5290d86192f456c3d310b70` | `ac2527aef8fbacbc50d10f778ca8e1dab05b9a2ae9f4dec48c54ea94d44b663f` |
| `Title.swf` | 6,666,801 | `579a9cd759933925a527230325c4b7eb` | `2ed21fd5972b66ee6d2da15714c616bc67ca40ba98644e849945bb7a65b9667b` |
| `TLC.swf` | 34,390 | `460fa31e7252237a3fbb3e044f2ab439` | `926d225e8687774386386ff84a0d7c09a0b3c950ff22b0179e014be5ab63a261` |

The size/MD5 pair is the form ScummVM detection tables use. The SHA-256 is the whole-file identity used by this repository.

## Running it today

Ruffle is an open-source Flash Player emulator written in Rust. It runs natively on desktop platforms and in browsers through WebAssembly. The inspected copy is AVM1/AS2 content, which Ruffle supports well. Compatibility is still incomplete in general, so a title that runs well is a data point rather than a guarantee for every SWF.

To try a SWF:

1. Install the Ruffle desktop build, or use the browser extension.
2. Open the game's main SWF, or point Ruffle at the launch SWF if the release uses a loader.
3. Keep the original directory structure. External assets are often referenced by relative path.
4. Record the Ruffle version and any visible defects.

Do not commit the SWF, FLV, audio, video, or extracted assets to this repository.

## Known use

The inspected 2007 Windows re-release of *Scooby-Doo! Case File #3: Frights! Camera! Mystery!* ships as 117 SWF files plus MP3, WAV, AIF, and FLV media. The launcher is a stock Flash Player 8 projector. It runs well under Ruffle. No dedicated game page yet.

## What to record next

- Ruffle version and platform used for the playtest.
- The exact launch path, and which SWF the projector opens first.
- Whether the 117-file set is complete, or whether the release has optional content elsewhere.
- Any assets loaded from outside the main SWF, especially by relative path.
- Visible defects, with a timestamp or scene description.
- The MD5 of the first 5,000 bytes and SHA-256 for any additional tested build.

## Sources

- [Ruffle](https://ruffle.rs/) — project site and downloads.
- [Ruffle source and documentation](https://github.com/ruffle-rs/ruffle) — emulator source, supported platforms, and project status.
- [Adobe Flash Player end of life](https://www.adobe.com/products/flashplayer/end-of-life.html) — Adobe's end-of-life notice, effective 2020-12-31.
- [SWF File Format Specification, version 19](https://open-flash.github.io/mirrors/swf-spec-19.pdf) — archived Adobe specification covering the SWF header, tags, ActionScript, audio, and video.
