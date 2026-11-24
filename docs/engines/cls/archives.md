---
title: "CLS archives and containers"
description: "The container families in Code Geass: Lost Colors: OOCH scene files, pack image bundles, PPHD sound banks, and CRI audio and video files."
type: note
status: draft
confidence: observed
tags:
  - playstation-portable
  - container
sources: []
last_verified: 2026-11-23
ai_assisted: true
---

# CLS archives and containers

The extracted disc tree holds a little under 2 GB of content in five container families. Three are the engine's own, two are CRI's.

| Family | Files | Where | What it holds |
| --- | ---: | --- | --- |
| `OOCH` | 1,454 | `USRDIR/root/*.P` | Compressed scene payloads |
| `pack` | 520 root + 646 `ScStr` | `USRDIR/root/*.P`, `USRDIR/ScStr/*.P` | GIM images; font metrics and atlases |
| `PPHD`/`PBD` | 41 pairs | `USRDIR/SE/` | Sound-effect and scenario-voice banks |
| AFS | 1 | `USRDIR/Voice/VJ0.AFS` | 390,379,520 bytes of voice audio |
| ADX | 30 | `USRDIR/BGM/` | Music |

Video is 28 `PSMF` files in `USRDIR/Movie` (193 MB), and `USRDIR/Tex` holds 40 loose `.GIM` images.

## OOCH: the scene files

Every `OOCH` file carries a fixed `0x800`-byte header before its payload, and `payload size = file size − 0x800` holds for all 1,454 files with no mismatches. The fields that are constant across the set:

| Offset | Value | Meaning |
| --- | --- | --- |
| `0x00` | `OOCH` | magic |
| `0x04` | `0x08000001` | version |
| `0x08` | payload size | equals file size − `0x800` |
| `0x0c` | varies 3,344–4,431,392 | decoded size |
| `0x10` | `18 00 1c 00` | two `u16`, 24 and 28: offset of the per-stream flag array and of the codec parameters |
| `0x14` | 1 | number of codec streams |
| `0x18` | 0 | flags entry for the single stream |
| `0x1c` | 32 | codec parameter word |
| `0x20` | 8 | codec parameter word |
| `0x24` | 8 | codec parameter word |

The payload starts at `0x800` and is an LZSS bit stream that expands to a `pack` container; the grammar and a working extractor are on [Decoding the scene containers](decoding.md).

## pack: image and font bundles

Both the background packages and the per-scene font packages use one container.

| Offset | Field |
| --- | --- |
| `0x00` | `pack` |
| `0x04` | `0x00020001` |
| `0x08` | block count |
| `0x0c` | unknown, `0x07e40000` in one sample |
| `0x10` | block offsets, one `u32` per block |
| after offsets | total file size |
| at first offset | first block |

`USRDIR/root` holds 520 of these, all backgrounds: `BG_A00B.P` is 65,520 bytes with a single block at offset `0x20` that begins `MIG.00.1PSP`, a GIM image. A scan of all 650 sub-blocks across the folder found GIM headers in every one, so no `pack` in `root` carries anything else.

`USRDIR/ScStr` holds 646 of them, one per scene, and each has three blocks. `S000J.P` (76,096 bytes) is representative:

| Block | Offset | Magic | Contents |
| --- | ---: | --- | --- |
| 1 | `0x20` | `FONTDATF` | Glyph metrics: per-character widths, then counts |
| 2 | `0x12b0` | `MIG.00.1PSP` | GIM font atlas |
| 3 | `0x113e0` | `FONTSTLB` | Glyph offset and style table |

So `ScStr` is the per-scene font resource, not the script. A Shift-JIS scan of the file returns nothing but noise out of the atlas, which is what one would expect from an image block and not from text.

## PPHD: sound banks

`USRDIR/SE` holds 41 `.PHD` indexes with a matching `.PBD` payload each, including `B_SCENARIO` and `PLUS_SCENARIO` — the two scenario-voice banks that the executable names directly. A `.PHD` begins `PPHD`, then `0x38`, `0x00010000`, `0xFFFFFFFF`, `0x40`, and a pair of offsets; the rest is `0xFF` fill. The payloads are structured rather than high-entropy, so these banks are the one place where the audio side can be read without solving the scene compression.

## CRI files

`VJ0.AFS` is a CRI AFS archive, the standard container for voice banks, and the 30 music files are plain ADX — `B01.ADX` is 4,600,786 bytes and its header carries the `(c)CRI` mark. Both formats are documented elsewhere and are out of scope here; the point is that they account for 490 MB of the disc without involving the engine's own code.

## What is still open

All five families are decoded at the container level. What is left is inside them: the text and the state machine in each of the 1,454 decoded scene containers, and which of the `pack` sub-blocks belong to a scene rather than to a font or a background.

## Sources

None beyond the inspected copy; all figures above are measurements of the files in `USRDIR`.
