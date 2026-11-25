---
title: "HoneyBee — archives"
description: "The four CRI AFS archives Sugar Sugar Rune ships: standard AFS v1 tables with no stored filenames, plus the member inventory recovered by aligning the executable's manifest with each archive."
type: engine
status: draft
confidence: observed
tags:
  - playstation-2
  - cri
  - afs
  - archives
sources:
  - title: NovelVM issue #60 — Support Sugar Sugar Rune engine
    url: https://github.com/monyarm/NovelVM/issues/60
platforms:
  - PlayStation 2
games: []
formats: []
maturity: documented
last_verified: 2026-11-25
ai_assisted: true
---

# HoneyBee — archives

All game content lives in four **CRI AFS** archives under `BEE/`. The container is the standard AFS v1 table — magic, entry count, offset/size pairs, 0x800-aligned data — with no filenames stored, which is normal for the format. The names come from the executable instead (see [executable findings](executable.md)).

## At a glance

| Archive | Entries | Bytes | Contents |
| --- | ---: | ---: | --- |
| `BEE/DATA_PS2.AFS` | 7,077 | 440,100,864 | Models, textures, scripts, particle effects, video |
| `BEE/BGM_AFS.AFS` | 26 | 118,759,424 | ADX music |
| `BEE/VO_AFS.AFS` | 6,209 | 25,782,272 | ADX voice lines |
| `BEE/SE_AFS.AFS` | 124 | 17,041,408 | ADX sound effects |

`CACHE.LST` (71 bytes) lists all four paths, and `DUMMY.DAT` is an empty placeholder.

## Layout

AFS v1, little-endian:

| Offset | Type | Meaning |
| --- | --- | --- |
| `0x00` | `char[4]` | `AFS\0` |
| `0x04` | `u32` | entry count |
| `0x08` | `u32[count]` | absolute offset of each entry |
| `0x08 + 4 × count` | `u32[count]` | size of each entry, parallel to the offsets |
| aligned | bytes | entry data, each entry starting on a `0x800` boundary |

Observed table geometry:

| Archive | Table ends | First data offset | Entry size min / max / total |
| --- | --- | --- | --- |
| `DATA_PS2.AFS` | `0xdd30` | `0xe000` | 32 / 57,237,504 / 431,648,258 |
| `BGM_AFS.AFS` | `0xd8` | `0x800` | 927,744 / 8,638,464 / 118,754,126 |
| `SE_AFS.AFS` | `0x3e8` | `0x800` | 14,674 / 617,134 / 16,920,628 |
| `VO_AFS.AFS` | `0xc210` | `0xc800` | 3,438 / 3,438 / 21,346,542 |

The gap between the end of the table and the first offset is padded; in `DATA_PS2.AFS` the eight bytes at `0xdd28` look like one further offset/size pair (`0x28`, `0`-heavy) before the padding, which was not needed to read the archive and was not resolved.

The VO entries are all exactly 3,438 bytes and all begin `80 00 00 20`, i.e. an ADX stream with a 0x20-byte header.

## Detection

| File | Size (bytes) | MD5 (first 5,000 bytes) | SHA-256 |
| --- | ---: | --- | --- |
| `DATA_PS2.AFS` | 440100864 | `e682a16a5c2fea0f79a9f623fb7724d0` | `68d7ef0f1a0d6f1e4e7fdf9c1328fdc2ecd36c0a30b8421fb3f9cf7aa9060600` |
| `BGM_AFS.AFS` | 118759424 | `807654873d9efbd1eed3744ddc12d64f` | `12c30d669a965915224a50c3ffc100d57d537d777fb6e7552f26d3f10c447533` |
| `VO_AFS.AFS` | 25782272 | `22fdf7a993486f9ebd69bd7be249a885` | `2cf74874b79ef9c45d46813c857b2ef7511753584394ec8404606273fa42d609` |
| `SE_AFS.AFS` | 17041408 | `374e88b0d73b58373491012cc9335953` | `faceb8d454c0d3627b159035384bd1e6183e7b795151f729104b2fdfb572d1b1` |

## Tooling

No extractor is published here. AFS v1 is a documented CRI container with existing readers, and the user's runtime already implements it, so reimplementing it in this repository would duplicate working code. Anyone reading this page needs two steps:

1. Walk the offset/size table to get the entries.
2. Name them from the executable's manifest at index `36 + i` (see [executable findings](executable.md)).

Step 2 is what makes the archive readable: without it every entry is an anonymous number.

## Member inventory

Counts and extensions come from the manifest; the sizes and magics come from the archive entries themselves.

| Extension | Count | Magic / first bytes | What it is |
| --- | ---: | --- | --- |
| `.amm` | 2,734 | `#AMM` | Animation or motion blocks |
| `.amp` | 2,377 | `#AMP` | Object part or pose blocks |
| `.amt` | 1,359 | `#AMT` | Textures |
| `.twf` | 323 | `TWS\x06` | Per-texture draw descriptors |
| `.amo` | 174 | `#AMO` | Models; each wraps a `#AMG` |
| `.pac` | 51 | `0x25` opcode stream, or a plain record table | 45 scene scripts and 6 data tables |
| `.bin` | 31 | `EFFE` | Particle and effect definitions |
| `.amb` | 14 | `#AMB` | Bundles of `#AMT` textures (menus) |
| `.alp` | 8 | `Path` | Camera and movement paths |
| `.sfd` | 4 | `00 00 01 ba` | Sofdec video |
| `.irx`, `.ico`, `.sys`, `.afs` | 13 / 6 / 5 / 4 | — | IOP modules, save icon set, the archives themselves |
| `.fnb`, `.lst`, `.inl` | 1 each | — | `FONT.FNB` 131,070 bytes, `CACHE.LST`, `OrderingTable.inl` |

The 1,359 `.AMT` entries are not all standalone: the 14 `.AMB` bundles each wrap several `#AMT` blocks, so the texture count inside the archive is higher than the `.amt` count.

## Named members worth listing

**Scene scripts (45 `.PAC`).** `ADVENTURE_MAIN.PAC`, `DOLL_MAIN.PAC`, `DOLL_FSM_01..03.PAC`, `FLASH_VIEWER.PAC`; twelve battle scenes `SCE_BT_{AKAZAWA,AKIRA,AOTA,HIROSI,KUROBE,MIDORIKAWA,MIMURA,NISITANI,PIERRE,SIRATAKE,TAIZI}.PAC`; `SCE_CH_OP_MAIN_C/V.PAC` and `SCE_CH_END_MAIN_C/V.PAC`; `SCE_CM_HEARTGET.PAC`, `SCE_CM_MAGIC.PAC`; `SCE_DH_{JOE,KADAI,LIVING,MAMA,TERRACE,SEARCH,EXTRA}.PAC`; `SCE_GT_{MAYU,MEMBERS,NANAKO,NATUME}.PAC`; `SCE_MS_{AKIRA,HOUXSAULE,MIMURA,NISITANI,PIERRE}_{C,V}.PAC`; `SCE_MS_TEST_2.PAC`.

**Data tables (6 `.PAC`).** `ACTION_TABLE.PAC` 5,480 · `ITEM_TABLE.PAC` 23,248 · `CHARA_TABLE.PAC` 600 · `FURNITURE_TABLE.PAC` · `TVPROG_TABLE.PAC` 484 · `APPENDIX_BOOK_TABLE.PAC`. These are fixed-stride record tables, not scripts; see [objects and textures](objects.md).

**Video (4 `.SFD`).** `MV_OP.SFD` 56,035,328 · `MV_ED.SFD` 57,237,504 · `MV_HP_C.SFD` 5,574,656 · `MV_HP_V.SFD` 5,414,912. All are MPEG program streams, so the two large ones account for a quarter of `DATA_PS2.AFS`.

**Paths (8 `.ALP`).** `RMC_001/002/003`, `RML_001`, `RMT_001`, `RMV_001/002/003` — room camera and movement paths.

**Effects (31 `.BIN`).** `FX_001_01` … `FX_011_*`, 240–1,360 bytes each.

**Menus (14 `.AMB`).** `TITLE_MENU`, `SCOOL_MENU`, `DRESSUP_MENU`, `DRESSUP_TEXT`, `HEART`, `CATALOGSELLING_PAGE`, `LAYOUTSELECTION_MENU`, `INTERIORSELECT_MENU`, `ROOMCOORDINATE_MENU`, `DOLLHOUSE_MENU`, `STAGENAME_IMG`, `APPENDIX_MENU_ITEM_BOOK` and two more.

## Unknowns

- The 3,438-byte uniformity of the VO entries means the voice archive carries no per-line metadata; the line table lives elsewhere and was not found.
- Whether AFS entry order is meaningful to the engine, or every access is by manifest name. The `SCE_*` names suggest name-based lookup.
- The eight bytes between the `DATA_PS2.AFS` table end and its padding.

## Sources

- [NovelVM issue #60](https://github.com/monyarm/NovelVM/issues/60) — tracking issue for a loader.
