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
last_verified: 2026-11-24
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
| `0x1c` | 32 | offset of the first stream's width pair, which is `0x20` |
| `0x20` | 8 | distance field width in bits |
| `0x24` | 8 | length field width in bits |

The payload starts at `0x800` and is an LZSS bit stream that expands to a `pack` container; the grammar and a working extractor are on [Decoding the scene containers](decoding.md).

## pack: image and font bundles

Every unpacked payload on the disc is a `pack`: the 1,166 files that are stored plain, and the 1,454 `OOCH` files once their payload is decoded. 2,620 of them were parsed.

| Offset | Field |
| --- | --- |
| `0x00` | `pack` |
| `0x04` | `u16` variant word: `1` on 2,512 containers, `2` on 23, and `3`, `4`, `5` or `7` on 85 more (below) |
| `0x06` | `u16`, always `2`, so the pair reads `0x00020001` as a `u32` |
| `0x08` | `u32` block count |
| `0x0c` | `u32` whose low half is always zero; the high half reads 100, 2,000, 2,020, 2,500, 8,000 or 8,100 depending on the container, and what it means is not established |
| `0x10` | `u32[count + 1]` ascending absolute block offsets; the last entry equals the file size |
| `align16(0x14 + 4 * (count + 1))` | first block |

The `u32` after the offsets is what makes the table unambiguous: `pack` at `0x20` with `count = 1` needs `0x10` to `0x17` for its two words, so the first block starts at the next 16-byte boundary. A block runs to the next offset.

What the first block of each container is:

| First block | Containers | What it is |
| --- | ---: | --- |
| `MIG.` | 1,208 | GIM image |
| `FONTDATF` | 646 | per-scene font metrics (`ScStr/`) |
| `00 01 50 53 50` | 646 | scene block, transparent header followed by `PSP` |
| `FGB` | 11 | two-block art and background packages |
| `PP` | 1 | sound bank |

Blocks nest: 646 containers also hold a `FONTSTLB` block, 247 hold an `FGB` chunk, and 2,061 of the 3,464 blocks overall are GIM images.

The 85 containers with a variant word of `3`, `4`, `5` or `7` are all `CH_FE_*` character art and use a different body: `0x08` is not a block count, a `u32 1` and a `u16` list sit between the header and the offsets, and the first block offset is `0x30`. That body is not mapped.

`USRDIR/ScStr` holds 646 of these, one per scene, and each has three blocks. `S000J.P` (76,096 bytes) is representative:

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

All five families are decoded at the container level. What is left is inside them.

The text layer has not been located. Decoding all 1,454 `OOCH` containers and scanning every result for Shift-JIS finds no plaintext dialogue: every run that survives a strict CP932 filter turns out to be GIM or `FGB` image payload, which decodes into long kanji and katakana sequences that read as noise. The scene files themselves (`A###J.P`, `F###J.P`, `J###J.P`, `K###J.P`, `BTL###J.P`, 2,272 to 33,563 bytes) are sparse tables headed `00 01 50 53 50`, 96 % zero bytes, built from 16-byte records with an offset table that ascends in steps of 16. `ScStr/<scene>.P` is the per-scene font subset described above, not script storage, and `FCL.DIR` is only the list of the seven `.cvm` archives.

None of `FONTSTLB`, `FONTDATF`, `FGB`, or `00 01 50 53 50` occurs as a byte sequence in the executable, so these blocks are not dispatched on their magic and a string hunt cannot find their loader. The same caveat applies to the working side of the format: `OOCH` and `pack` are both compared by routine at file offset `0x2d704` and `0x2e480`, and those two are the only magics in this engine that are.

That leaves the dialogue either in a container type not yet walked, or stored as indices into the font rather than as characters.

## Sources

None beyond the inspected copy; all figures above are measurements of the files in `USRDIR`.
