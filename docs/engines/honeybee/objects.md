---
title: "HoneyBee — objects and textures"
description: "The #AM* block family used for models, textures, animation and menus in Sugar Sugar Rune, the .TWF draw descriptors that pair with each texture, and the six fixed-stride data tables."
type: engine
status: draft
confidence: mixed
tags:
  - playstation-2
  - textures
  - models
  - formats
sources:
  - title: NovelVM issue #60 — Support Sugar Sugar Rune engine
    url: https://github.com/monyarm/NovelVM/issues/60
platforms:
  - PlayStation 2
games: []
formats: []
maturity: partial
last_verified: 2026-11-25
ai_assisted: true
---

# HoneyBee — objects and textures

Content in `DATA_PS2.AFS` is a family of blocks with four-character magics that all share the `#AM` prefix. Six of them cover most of the archive; each was read only far enough to identify its role and its first table, so this page is a map, not a specification.

## At a glance

| Magic | Extension | Count | Role | Confidence |
| --- | --- | ---: | --- | --- |
| `#AMT` | `.amt` | 1,359 | Texture: header, offset table, 0x30-byte entries | observed |
| `#AMB` | `.amb` | 14 | Menu bundle wrapping several `#AMT` | observed |
| `#AMO` | `.amo` | 174 | Model; wraps a `#AMG` geometry block | observed |
| `#AMP` | `.amp` | 2,377 | Offset table, stride `0x14` | observed, role inferred |
| `#AMM` | `.amm` | 2,734 | Offset table, stride `0x2c` | observed, role inferred |
| `#AMG` | — | — | Geometry inside `#AMO` | observed as a magic only |
| `TWS\x06` | `.twf` | 323 | Per-texture draw descriptor | observed, fields partly read |

## `#AMT` — textures

An `#AMT` file is a header, an offset table, and one or more 0x30-byte texture entries. Verifying the arithmetic over all 1,359 files confirms the layout for 1,343 of them; the other 16 either have no entries or did not parse.

```text
0000  23 41 4d 54 | 20 00 00 00 | 00 00 00 00 | 02 00 00 00   #AMT, 0x20, 0, 2
0010  01 00 00 00 | 20 00 00 00 | 00 …                          count 1, table at 0x20
0020  30 00 00 00  00 …                                          entry offsets: one, 0x30
0030  00 00 00 00 | 61 00 00 00 | 13 00 00 00 | 0a 00 09 00     entry 0
0040  80 02 e0 01 | 60 00 00 00 | 00 b0 04 00 | 01 00 00 00
0050  00 00 00 00 | 80 b0 04 00 | 00 04 00 00 | b8 ff 00 00
```

| Offset | Type | Meaning |
| --- | --- | --- |
| `+0x00` | `char[4]` | `#AMT` |
| `+0x04` | `u32` | `0x20` — header size |
| `+0x08` | `u32` | `0` in every file read |
| `+0x0c` | `u32` | `2` in every file read |
| `+0x10` | `u32` | entry count |
| `+0x14` | `u32` | `0x20` — table offset |
| `+0x20` | `u32[count]` | entry offsets; entries are `0x30` bytes apart and the first is the table end rounded up to 16 bytes |

Entry record (0x30 bytes):

| Offset | Type | Meaning |
| --- | --- | --- |
| `+0x00` | `u32` | `0` in the files read |
| `+0x04` | `u32` | format code — `0x21` in 3,108 entries, `0x61` in 291 |
| `+0x08` | `u32` | `19` in every entry read |
| `+0x10` | `u16`, `u16` | width, height |
| `+0x18` | `u32` | exactly `width × height` in every entry checked |
| `+0x28` | `u32` | `0x300`, `0x400`, `0x1000`, `0x4000` or `0x10000` — size-like, not yet interpreted |

The verified invariant is `w × h == the u32 at +0x18` for every entry of every parseable file. `ADV_BGD_001.AMT` is one entry of 640 × 480 = 307,200, which is 0x4b000 — the number that first suggested the payload size.

Files may hold several entries: 837 hold one, 271 hold three, 97 hold two, 43 hold four, and the rest between five and sixteen. `FONT.AMT` is the largest at 79 entries and 2.6 MB, i.e. the font is a texture atlas in a single `.AMT`.

Two files are 32-byte stubs with count 0 — `BANNER_CATALOG_NAME_WINDOW.AMT` and `BANNER_CATALOG_TEXT_WINDOW.AMT` — so an empty `#AMT` is legal and a reader must tolerate it.

What is still **inferred**: that the payload after the entry table is raw indexed colour. The pixel bytes read as 8-bit indices, entry `+0x28` takes values `0x300` (768 = 256 × 3) and `0x400` (1024 = 256 × 4), which is where a palette would sit in either RGB555 or RGBA form, but no palette was located and no image was rendered. The binary links CRI **MPS** (1.924), a texture decoder, so the `0x21` and `0x61` format codes may mark compressed and uncompressed payloads rather than two uncompressed variants.

## `.TWF` — draw descriptors

Every `.AMT` in the manifest is followed by a `.TWF` named `<texture>_01`, and the files are small (the first is 452 bytes), so they are per-texture draw state rather than images:

```text
54 57 53 06 | 62 a8 00 00 | 00 32 00 00 | 80 25 00 00 | 0c 01 00 09
04 00 00 00 | ff ff ff ff | 02 00 00 00 | c0 00 00 00
```

`TWS` plus a version byte `0x06`, then a size-like word, a pair of small dimensions (`0x32`, `0x2580`), a tag `0x09 00 01 0c`, a sentinel `0xffffffff`, and floats that include `0x41a00000` (20.0f) pairs. The field roles are not established; the pairing and the size are.

## `#AMB` — menu bundles

14 files, all named after a menu screen. Each starts with its own header and then carries one or more embedded `#AMT` blocks — the first `#AMT` in `HEART`-class bundles sits at `+0x30`. So a menu's art is packed as textures inside one bundle rather than as separate `.AMT` entries.

## `#AMO` and `#AMG` — models

174 files. `#AMO` is a container: a header with a size word (e.g. `40 23 00 00`) and an embedded `#AMG` block at `+0x50`. `#AMG` is the geometry. Neither the vertex layout nor the palette or texture binding was read.

## `#AMP` and `#AMM` — offset tables

5,111 files between them, and both are tables of `u32` offsets that grow by a constant stride — `0x14` for `#AMP`, `0x2c` for `#AMM` — after the magic and a `0x20` word. The stride pattern means fixed-size records; what each record contains was not decoded. The counts suggest per-object and per-motion data: 2,377 `#AMP` and 2,734 `#AMM` against 174 models, i.e. roughly 14 parts and 16 motions per model if the blocks are grouped by model.

## `EFFE` particles and `Path` cameras

`EFFE` (31 `.BIN` files, 240–1,360 bytes) begins `EFFE` `CT2\0` then a size word and runs of floats (the first block is `-6.98f`), which is a particle or effect definition list. `Path` (8 `.ALP` files) holds NUL-padded records named `PATH001`, `PATH003`, `PATH004`, each with two integers and a float (e.g. `39.15f`) — camera or movement waypoints for a room.

## The six data tables

`ITEM_TABLE.PAC`, `ACTION_TABLE.PAC`, `CHARA_TABLE.PAC`, `FURNITURE_TABLE.PAC`, `TVPROG_TABLE.PAC` and `APPENDIX_BOOK_TABLE.PAC` are the only `.PAC` files that are not scripts. They have no magic: a zeroed header, then fixed-stride records. `ACTION_TABLE.PAC` opens with six `u32` fields (`0x10`, `1`, `1`, `3`, `0x1e`, `1`) and then runs of `25.0f` (`00 00 c8 41`) including negatives (`00 00 c8 c1`), which reads as a numeric parameter block per action. `CHARA_TABLE.PAC` uses `0x3f800000` (1.0f) in the same position of each record. `TVPROG_TABLE.PAC` mixes small counts with large integers (`0x14438`, `0x186a0`, `0x1d4c0`, `0x222e0`), i.e. schedule or timing values.

None of these tables was decoded; they are listed so that a later pass does not mistake them for scripts.

## Unknowns

- Where `#AMT` palettes live, and whether the `0x21`/`0x61` format codes mean CRI-MPS compressed versus raw.
- The meaning of entry `+0x28` (`0x300`–`0x10000`) and of the constant `19` at entry `+0x08`.
- What `#AMP` and `#AMM` records contain, and how a model references them.
- Whether `#AMG` stores vertices, display lists, or both.
- The `.TWF` field semantics, and why only 323 of 1,359 textures have one (probably because only full-screen backgrounds are drawn through it).
- The record layout of the six `*_TABLE.PAC` files.

## Sources

- [NovelVM issue #60](https://github.com/monyarm/NovelVM/issues/60) — tracking issue for a loader.
