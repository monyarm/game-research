---
title: "Soalo: textures"
description: "How SCENEDAT and NORMAL pack TIM2 images into compressed, aligned blocks, and how to decode them."
type: engine
status: draft
confidence: mixed
tags:
  - playstation-2
  - tim2
  - textures
  - bin-hd
  - zero-no-tsukaima
platforms:
  - PlayStation 2
games: []
formats: []
maturity: partial
sources:
  - title: punk7890/PS2-Visual-Novel-Tool
    url: https://github.com/punk7890/PS2-Visual-Novel-Tool
  - title: "[PS2] Need help figuring out what to do next! (VG Resource forum)"
    url: https://vg-resource.com/threads/ps2-need-help-figuring-out-what-to-do-next.42169/
  - title: TM2/TIM2 Image (Reverse Engineering Wiki)
    url: https://rewiki.miraheze.org/wiki/TM2_TIM2_Image
last_verified: 2026-11-23
ai_assisted: true
---

# Soalo: textures

`SCENEDAT.BIN` (scene backgrounds) and `NORMAL.BIN` (UI) hold the game's images. Every image is stored as a compressed block on a 2048-byte boundary, and every block decodes to a complete TIM2 file.

## At a glance

| Property | `SCENEDAT.BIN` | `NORMAL.BIN` |
| --- | --- | --- |
| Block start | 2048-byte aligned | 2048-byte aligned |
| Block header | `u32` decoded size, `u32 1` | Same |
| First stream byte | `0xE6` | `0xE6` |
| First decoded bytes | `TIM2 04 00 01` | `TIM2 04 00 01` |
| Blocks (Symphony / Fantasy / Concerto) | 1955 / 1443 / 1100 | 435 / 292 / 320 |
| Blocks decoding to a TIM2 v4 header | 1950 / 1442 / 1093 | 434 / 291 / 319 |

The handful that do not decode are false matches for the marker inside other blocks' payloads, not a second format.

## Block framing

| Offset | Type | Value |
| --- | ---: | --- |
| +0 | `u32` | Decoded size in bytes |
| +4 | `u32` | `0x00000001` in every image block examined |
| +8 | — | Compressed stream, first byte `0xE6` |

The first block of `SCENEDAT.BIN` in Symphony, from offset 0:

```text
40 64 04 00 | 01 00 00 00 | e6 | 54 49 4d 32 | 04 00 01 | 27 e5 30 64 04 00 | 00 04 00 00 | 00 60 04 00 ...
```

`0xE6` splits as method 7, length 6: a literal run of seven bytes, which is exactly `TIM2 04 00 01`. The two bytes that follow are the beginning of the TIM2 header, still compressed.

## The codec

The stream is a byte-oriented command stream with a six-entry command history. Each command byte carries `method = byte >> 5` and `length = byte & 0x1f`.

| Method | Action |
| ---: | --- |
| 7 | Copy the next `length + 1` bytes literally |
| 6 | Repeat the next byte `length + 2` times |
| 0–5 | Re-run the command stored in history slot 0–5, with a new length |

Re-running works differently per kind. If the stored command was a repeat, the new length repeats the same byte `length + 2` times. If it was a literal, the command emits `(length & 3) + 1` bytes starting at `length >> 2` inside that literal — so one long literal serves as a dictionary for later short copies out of it.

The history starts pre-filled with repeats of `0x00`, `0x01`, `0xFF`, `0x80`, `0x7F`, and `0xFE`, so a stream can open with a run of any of those without having seen the byte first. This is what produces the long `0xFF` and `0x00` regions that made raw `SCENEDAT`/`NORMAL` look like padding.

One consequence for a decoder: the final command can overshoot the declared decoded size. Symphony's first `SCENEDAT` block declares 287,808 bytes and the command stream ends after emitting 287,809. Truncate to the declared size.

## Inside the decoded block

The first block of Symphony `SCENEDAT.BIN`, decoded:

```text
54 49 4d 32 | 04 | 00 | 01 00 | 00 00 00 00 00 00 00 00
30 64 04 00 | 00 04 00 00 | 00 60 04 00 | 30 00 00 01 | 00 01 03 05 ...
```

| Offset | Type | Value | Meaning |
| --- | ---: | ---: | --- |
| 0x00 | char[4] | `TIM2` | Magic |
| 0x04 | `u8` | 4 | Version |
| 0x05 | `u8` | 0 | Pixel format |
| 0x06 | `u16` | 1 | Image count |
| 0x08 | 8 bytes | zero | Reserved |
| 0x10 | `u32` | 287792 | Decoded size minus 16 |
| 0x14 | `u32` | 1024 | Palette size |
| 0x18 | `u32` | 286720 | Pixel data size, 640 × 448 |

That accounts for the block's decoded size exactly: 0x30 header + 1,024 palette + 16 + 286,720 pixels = 287,808. The same arithmetic holds for every `SCENEDAT` block in all three games that carries a palette; the 1,088-byte overhead the earlier version of this page measured is those three parts, not a fixed prefix.

`NORMAL` blocks mostly use a different size (Symphony's most common decoded sizes are 17,216, 14,144, 7,808, and 3,008 bytes, with a few full-screen 296,576-byte blocks). Blocks without a palette leave the `0x14` and `0x18` fields zero and carry their sizes further into the header, which is why a fixed field offset does not describe every block.

## Extracting

There is already a maintained tool for this format, so this repository links it instead of shipping a decoder:

- **[punk7890/PS2-Visual-Novel-Tool](https://github.com/punk7890/PS2-Visual-Novel-Tool)** — MIT licence, Copyright (c) 2024 punk7890. Godot 4 project; its Socio Art Logic handler reads `NORMAL.BIN`, `SCENEDAT.BIN`, and `SCENE_ID.BIN`, decompresses every block, and converts the TIM2 images to PNG. Its supported-games list names all three *Zero no Tsukaima* titles.

Split the `.BIN`/`.HD` pair first with the script on [Archives](archives.md) if you want the record boundaries; for images the alignment is enough, and the tool scans the file directly.

The `.HD` table for `SCENEDAT` is not a block index: blocks are separated by alignment padding that the table does not count, and a block can begin inside a record. Measured across Symphony `SCENEDAT`, the `0xFF` padding between blocks is 2,021,671 bytes against a `BIN`-minus-index difference of 2,035,653.

## Unknowns

- **The second header word.** It is `1` in image blocks; `SCENE_ID` carries `8` in Symphony and Fantasy and `1` in Concerto. Whether it selects a decoder, records a type, or is a version is not established.
- **Blocks without palette fields.** Their sizes sit at a different offset; the layout shift is not mapped.
- **What the records without any block header hold.** `SCENEDAT` has records with no `TIM2` block and no `0xE6` marker. Two different probes disagreed on their count, so this page states none.
- **Palette contents.** The palette is a full 1,024-byte 256-entry table in the blocks that have one; its entry format is untouched here.
