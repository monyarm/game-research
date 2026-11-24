---
title: "A98SYS payloads"
description: "What an A98SYS PAK holds once unpacked: image headers for EDT, SAL and ED8, the engine's own manifest, and the tools the developer shipped inside the archive."
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

This page is the census of what the archives carry, and what the bytes of each member look like. Images are only partly decoded; everything else is identified.

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

All 695 `EDT` members begin with the same 18 bytes:

| Offset | Size | Field |
| --- | ---: | --- |
| `0x00` | 5 | Magic `.TRUE` |
| `0x05` | 4 | Constant `8d 5d 8c cb` in every member inspected |
| `0x09` | 2 | 0 |
| `0x0b` | 2 | 1 |
| `0x0d` | 1 | 0 |
| `0x0e` | 2 | Width in pixels |
| `0x10` | 2 | Height in pixels |
| `0x12` | — | Pixel data |

Width is 640 and height 480 for nearly everything: `A136.EDT` (252,631 bytes) through `E151C.EDT` (8,094 bytes) share those two words. The exceptions are the opening and scrolling pictures, which are taller: `OP01.EDT` and `OP01A.EDT` are 960 rows, `OPSCROLL.EDT` 940 → 908 rows.

The pixel data is not a raw bitmap. A 640 × 480 image is 307,200 pixels, and members range from under 8,000 to nearly 600,000 bytes, so the stream is compressed or run-length coded. No decoder is published here.

`SAL` and `ED8` use the `.8Bit` magic in place of `.TRUE` and the same header shape afterwards. `SAL` members are small (`A136.SAL` is 117 × 88, 8,102 bytes), `ED8` members are larger (`CG_BACK.ED8` covers 640 × 480 in 258,014 bytes). The names suggest sprites against backgrounds; that is a guess.

## The rest

- **`A98SYS.TAG`** (11,328 bytes) is a plaintext list of the archive's members, one per line, opening with `>..\r\n`. It duplicates the PAK index and is easier to read.
- **`A98SYS.ENV`** (3,015 bytes) and **`SETUP.ENV`** (1,953 bytes) are text configuration, comment lines starting `//`.
- **`HGSCWIN.IDE`** (669 bytes) is Shift-JIS text used to configure the game window.
- **`TS_BANK.ITW`** (2,576 bytes) begins with a run of increasing `u32` values (`0`, `0x98a`, `0x4d`, `0x77`, `0xd2`, …) which do not form a monotonic table. Unidentified.
- **`TSCR.BMP`** (135,174 bytes) is a plain `BM` file, 480 pixels wide, data at `0x306`. The engine's own screenshot-title graphic.
- **`FILEPACK.EXE`** (108,438 bytes, `MZ`), **`FILEPACK.C`** (5,297 bytes) and **`PK.BAT`** (241 bytes) are the developer's own packer, shipped inside the packed archive. The batch file sets `SET TARGET=A9…` before calling the executable.

Text in the C source and the batch file is not reproduced here; the point is that the engine's packaging tool is part of the game data.

## Voice

`VOICE.PAK` (168,099,000 bytes) and `VOICE2.PAK` (133,157,807 bytes) are not PAK archives in this layout. Both read `u16` 16384 where a count should be, and the following bytes are not names. See [Archives](archives.md#the-voice-archives).

## Unknowns

- **The compression used by `EDT`.** Every member is smaller than its pixel count, the header has no size field, and the same four constant bytes appear in every file.
- **Whether `.8Bit` carries a palette.** `SAL` and `ED8` are 8-bit by name, and no palette block has been located after the header.
- **What `TS_BANK.ITW` is.** Its numbers are not offsets into itself.
- **What `EDT` stands for.** The extension does not appear in the executable's strings.
- **Whether the `.TRUE`/`.8Bit` magics are versioned.** Only one build has been inspected.

## Sources

- [VNDB — Bible Black -La Noche de Walpurgis-](https://vndb.org/v9) — the inspected release.
