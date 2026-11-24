---
title: "A98SYS payloads"
description: "What an A98SYS PAK holds once unpacked: the EDT, SAL and ED8 image headers, a palette block, the engine's own manifest, and the tools the developer shipped inside the archive."
type: engine
status: draft
confidence: mixed
tags:
  - windows
  - visual-novel
  - image-format
platforms:
  - Windows
games: []
formats: []
maturity: partial
sources:
  - title: VNDB — Bible Black -La Noche de Walpurgis-
    url: https://vndb.org/v9
last_verified: 2026-11-24
ai_assisted: true
---

# A98SYS payloads

This page is the census of what the archives carry, and what the bytes of each member look like. The image headers are measured; the image decompression is borrowed from the two public decoders named below.

## Census

`A98SYS.PAK` from the inspected English copy of *Bible Black -La noche de walpurgis-*, 1058 entries including the terminator:

| Extension | Count | What it is |
| --- | ---: | --- |
| `EDT` | 695 | Images, `.TRUE` magic |
| `SAL` | 264 | Small images, `.8Bit` magic |
| `ED8` | 33 | Images, `.8Bit` magic |
| `HGO` | 35 | Scene scripts, see [Scripts](scripts.md) |
| `WAV` | 20 | System sounds |
| `ENV` | 2 | Plain-text configuration |
| `TAG` | 1 | Plaintext manifest of the archive's own members |
| `ITW` | 1 | Offset table, unidentified |
| `IDE` | 1 | Shift-JIS text, engine configuration for the window |
| `BMP` | 1 | Uncompressed 480-pixel-wide bitmap |
| `EXE` | 1 | `FILEPACK.EXE`, the packer itself |
| `BAT` | 1 | `PK.BAT`, the packing script |
| `C  ` | 1 | `FILEPACK.C`, C source for the packer |
| — | 2 | `TAGHEAD` (5 bytes, `>..\r\n`) and the `..END` terminator |

`A98FAST.PAK` is smaller and holds the same families: 194 entries, 19 `HGO`, 135 `ED8`, 36 `EDT`, 1 `TAG`, 1 `BAT`.

## Images

All 695 `EDT` members begin with the same 34-byte header:

| Offset | Size | Field |
| --- | ---: | --- |
| `0x00` | 10 | Magic `.TRUE` followed by `8d 5d 8c cb 00` |
| `0x0a` | 4 | Constant `0x00000100` in every member inspected |
| `0x0e` | 2 | Width in pixels |
| `0x10` | 2 | Height in pixels |
| `0x12` | 4 | `0xffffffff` in every member inspected |
| `0x16` | 4 | Length of the diff block |
| `0x1a` | 4 | Length of the flag bitstream |
| `0x1e` | 4 | Length of the pixel data |
| `0x22` | — | Diff block, flag bitstream, pixel data |

The three lengths add up to the rest of the member exactly. `ACTIVE.EDT` (135,128 bytes) is 34 + 0 + 91,708 + 43,386; `ARF.EDT` is 3,829 = 34 + 0 + 1,476 + 2,319; `BLACK.EDT` is 56 = 34 + 0 + 16 + 6. The diff block is empty in these members — a non-zero length means the member is a patch over a base image named after an `.EDT_DIFF` marker.

Width is 640 and height 480 for nearly everything: `A136.EDT` (252,631 bytes) through `E151C.EDT` (8,094 bytes) share those two words. The exceptions are the opening and scrolling pictures, which are taller: `OP01.EDT` and `OP01A.EDT` are 960 rows, `OPSCROLL.EDT` 940 → 908 rows.

The pixel data is compressed, not a raw bitmap: a 640 × 480 image is 307,200 pixels and members run from under 800 to nearly 606,000 bytes. The published decoder is Crass's, which reads the flag stream as 32-bit little-endian words and emits BGR24, copying the first three bytes of each image raw and then either a raw triple, a predicted triple from one of a fixed set of neighbour offsets, or a run copied from an earlier offset.

`SAL` and `ED8` use the `.8Bit` magic in place of `.TRUE` and carry a 26-byte header:

| Offset | Size | Field |
| --- | ---: | --- |
| `0x00` | 10 | Magic `.8Bit` followed by the same `8d 5d 8c cb 00` |
| `0x0a` | 2 | Type; `256` is the only value seen, and the only one Crass handles |
| `0x0c` | 2 | Unknown, 0 in every member inspected |
| `0x0e` | 2 | Width in pixels |
| `0x10` | 2 | Height in pixels |
| `0x12` | 2 | Palette colour count, 256 in every member inspected |
| `0x14` | 2 | Unknown, 0 in every member inspected |
| `0x16` | 4 | Length of the compressed pixel data |
| `0x1a` | `colours × 3` | Palette, one byte per channel |
| — | — | Compressed pixel data |

`ARF_.ED8` (9,874 bytes, 186 × 71) is 26 + 768 + 9,080 exactly, and `AUTO_.ED8` (8,346), `CALBASE_.ED8` (1,710) and `CGM2B_.ED8` (2,862) reconcile the same way. `SAL` members are small (`A136.SAL` is 117 × 88, 8,102 bytes), `ED8` members are larger (`CG_BACK.ED8` covers 640 × 480 in 258,014 bytes). The names suggest sprites against backgrounds; that is a guess.

Both paths are decompressed by the A98SYS module in Crass and by `ArcADPACK.cs` in GARbro. Nothing here re-derives the predictor tables, so the field tables above are the part this project measured.

## The rest

- **`A98SYS.TAG`** (11,328 bytes) is a plaintext list of the archive's members, one per line, opening with `>..\r\n`. It duplicates the PAK index and is easier to read.
- **`A98SYS.ENV`** (3,015 bytes) and **`SETUP.ENV`** (1,953 bytes) are text configuration, comment lines starting `//`.
- **`HGSCWIN.IDE`** (669 bytes) is Shift-JIS text used to configure the game window.
- **`TS_BANK.ITW`** (2,576 bytes) begins with a run of increasing `u32` values (`0`, `0x98a`, `0x4d`, `0x77`, `0xd2`, …) which do not form a monotonic table. Unidentified.
- **`TSCR.BMP`** (135,174 bytes) is a plain `BM` file, 480 pixels wide, data at `0x306`. The engine's own screenshot-title graphic.
- **`FILEPACK.EXE`** (108,438 bytes, `MZ`), **`FILEPACK.C`** (5,297 bytes) and **`PK.BAT`** (241 bytes) are the developer's own packer, shipped inside the packed archive. The batch file sets `SET TARGET=A9…` before calling the executable.

Text in the C source and the batch file is not reproduced here; the point is that the engine's packaging tool is part of the game data.

## Voice

`VOICE.PAK` (168,099,000 bytes) and `VOICE2.PAK` (133,157,807 bytes) put the names in a second table after the offsets and mark the file with `u16` `0x4000` instead of a count; the layout and a tested extractor are on [Archives](archives.md#the-voice-archives). The members are `.WAV` files.

## Unknowns

- **What the predictor tables are.** Crass ships them, and this project has not re-derived them; the header fields above are measured, the decompression is borrowed.
- **Whether `.8Bit` type values other than 256 occur.** Crass refuses anything else, and no other value appears in this archive.
- **What `TS_BANK.ITW` is.** Its numbers are not offsets into itself.
- **What `EDT` stands for.** The extension does not appear in the executable's strings.
- **Whether the `.TRUE`/`.8Bit` magics are versioned.** Only one build has been inspected.

## Sources

- [VNDB — Bible Black -La Noche de Walpurgis-](https://vndb.org/v9) — the inspected release.
- [Crass 0.4.14.1 — `A98SYS ENGINE` module](https://github.com/shangjiaxuan/Crass-source/blob/master/crass-0.4.14.1/cui/A98SYS%20ENGINE/A98SYS%20ENGINE.cpp) — C++, module version 0.8.0 (2009-06-06), alpha; documents and decodes `.edt`, `.ed8` and `.sal`.
- [morkt/GARbro](https://github.com/morkt/GARbro) — `ArcFormats/ActiveSoft/ArcADPACK.cs`, MIT.
