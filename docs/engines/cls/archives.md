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
| `pack` | 520 root + 646 `ScStr` | `USRDIR/root/*.P`, `USRDIR/ScStr/*.P` | GIM images; scene text and glyph tables |
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
| `FONTDATF` | 646 | per-scene glyph table (`ScStr/`) |
| `00 01 50 53 50` | 646 | scene block, transparent header followed by `PSP` |
| `FGB` | 11 | two-block art and background packages |
| `PP` | 1 | sound bank |

Blocks nest: 646 containers also hold a `FONTSTLB` block, 247 hold an `FGB` chunk, and 2,061 of the 3,464 blocks overall are GIM images.

The 85 containers with a variant word of `3`, `4`, `5` or `7` are all `CH_FE_*` character art and use a different body: `0x08` is not a block count, a `u32 1` and a `u16` list sit between the header and the offsets, and the first block offset is `0x30`. That body is not mapped.

## ScStr: the scene text

`USRDIR/ScStr` holds 646 of these, one per scene id, and each has three blocks. `S000J.P` (76,096 bytes) is representative:

| Block | Offset | Magic | Contents |
| --- | ---: | --- | --- |
| 1 | `0x20` | `FONTDATF` | 292 16-byte glyph records |
| 2 | `0x12b0` | `MIG.00.1PSP` | GIM atlas of the same glyphs |
| 3 | `0x113e0` | `FONTSTLB` | 42 text records |

This is where the dialogue is. The scenes store text as glyph indices, not as characters, and the two font blocks supply the mapping and the lines.

`FONTDATF` is a plain table of 16-byte records starting at `0x50`, one per glyph in that scene:

| Offset | Field |
| --- | --- |
| `+0x00` | `u32` metric, small integer |
| `+0x04` | `u16` Unicode codepoint, little endian |
| `+0x06` | `u16` glyph index, 1-based and ascending |
| `+0x08` | `u32` metric |
| `+0x0c` | `u32` metric |

The table is ordered by character, so record 1 is `U+3000`, 2 is `U+3001`, 3 is `U+3002`, 4 is `U+300C`, and the run continues through hiragana, katakana, kanji used in the scene, and fullwidth Latin. Glyph counts per file range from 107 to 297.

`FONTSTLB` header, at the start of block 3:

| Offset | Field |
| --- | --- |
| `0x0c` | `u16` `101`, the same value in every file |
| `0x0e` | `u16` `20`, the line width in characters |
| `0x10` | `u32` record count |
| `0x14` | `u32[count]` record offsets, relative to the block |

Each record is a run of 4-byte cells: `u16` attribute, then `u16` glyph index. A cell whose glyph index is `0` ends the record. So a record is one line of that scene's text, and the attribute word is the only part not yet read.

### Extracting the text

```quickbms
# Code Geass: Lost Colors (PSP) - ScStr text extractor
#
# Every USRDIR/ScStr/<scene>.P file is a plain "pack" container with exactly
# three blocks:
#   0  "FONTDATF"  the scene's glyph table
#   1  "MIG.00.1"  the glyph atlas (PSP GIM image)
#   2  "FONTSTLB"  the scene's text, one record per line
#
# pack header (same layout as every other pack on this disc):
#   0x00 char[4] "pack"
#   0x04 u16     header variant
#   0x06 u16     always 2
#   0x08 u32     block count
#   0x0c u32     unknown
#   0x10 u32[n+1] ascending absolute block offsets, last == file size
#
# FONTDATF: 16-byte records from 0x50, one per glyph.
#   +4 u16  Unicode codepoint of the glyph
#   +6 u16  glyph index, 1-based and sequential
#   +0/+8/+12  per-glyph metrics
#
# FONTSTLB:
#   0x0c u16  101, constant
#   0x0e u16  20, the line width in characters
#   0x10 u32  record count
#   0x14 u32[count] record offsets, relative to the start of the block
#   each record is a run of 4-byte cells: u16 attribute, u16 glyph index.
#   A cell whose glyph index is 0 ends the record.
#
# Text is stored only as glyph indices, never as Shift-JIS, which is why no
# text scanner finds anything in this game's files.
#
# Usage: quickbms cls-scstr.bms S000J.P  -> writes S000J.P.txt
# Verified on the 646 files of the inspected disc: every file parses, 29,461
# records in total.

endian little

idstring "pack"

log MEMORY_FILE2 0 0   # block-offset array
log MEMORY_FILE3 0 0   # UTF-8 text output

goto 0x08
get BLOCKS long

# Block offsets go into MEMORY_FILE2, one u32 per block, plus the sentinel.
for i = 0 <= BLOCKS
    math POS = i
    math POS *= 4
    math POS += 0x10
    goto POS
    get VAL long
    math POS2 = i
    math POS2 *= 4
    goto POS2 MEMORY_FILE2
    put VAL long MEMORY_FILE2
next i

# FONTDATF base and FONTSTLB base
goto 0 MEMORY_FILE2
get DATBASE long MEMORY_FILE2
math POS = BLOCKS
math POS -= 1
math POS *= 4
goto POS MEMORY_FILE2
get STLBASE long MEMORY_FILE2

goto STLBASE
get UNK1 short       # 0x00 of FONTSTLB, part of the magic
goto STLBASE
math P = STLBASE
math P += 0x10
goto P
get RECS long
get STLEND long      # sentinel, the file size

math TBL = STLBASE
math TBL += 0x14

for R = 0 < RECS
    math P = R
    math P *= 4
    math P += TBL
    goto P
    get RSTART long
    math RSTART += STLBASE
    math P = R
    math P += 1
    math P *= 4
    math P += TBL
    goto P
    get REND long
    math REND += STLBASE

    math Q = RSTART
    for CELL = 0 < 4096
        if Q < REND
            goto Q
            get ATTR short
            get GIDX short
            if GIDX == 0
                break
            endif
            # look the glyph index up in FONTDATF
            math OFF = DATBASE
            math OFF += 0x50
            math TMP = GIDX
            math TMP -= 1
            math TMP *= 0x10
            math OFF += TMP
            math OFF += 4
            goto OFF
            get CP short
            # U+3000..U+FF5E: always three UTF-8 bytes
            math U1 = CP
            math U1 >>= 12
            math U1 |= 0xE0
            math U2 = CP
            math U2 >>= 6
            math U2 &= 0x3F
            math U2 |= 0x80
            math U3 = CP
            math U3 &= 0x3F
            math U3 |= 0x80
            get SIZE asize MEMORY_FILE3
            goto SIZE MEMORY_FILE3
            put U1 byte MEMORY_FILE3
            put U2 byte MEMORY_FILE3
            put U3 byte MEMORY_FILE3
            math Q += 4
        else
            break
        endif
    next CELL

    get SIZE asize MEMORY_FILE3
    goto SIZE MEMORY_FILE3
    put 0x0a byte MEMORY_FILE3
next R

get SIZE asize MEMORY_FILE3
get NAME filename
string NAME += ".txt"
log NAME 0 SIZE MEMORY_FILE3
print "wrote %NAME%: %RECS% records, %SIZE% bytes"
```

### Evidence

All 646 `ScStr` files parse with this layout and 0 failures, 29,461 records in total. `S000J.P` line 4 decodes to `Ｇ１ベースで保護されてる。一時的に、意識が混乱してたみたいだけど、どこにもケガはなかった。` and line 28 to `「わたくしユーフェミアが、ここに、行政特区日本の開設を、宣言します！」`. One record per file is a charset sample — `SK995J.P`'s second record is the whole glyph set in order, `アイウエオカキクケコ…` — and is not dialogue.

Because the text never exists as characters, no Shift-JIS scan can find it, which is why earlier scans of the whole tree came back empty.

## PPHD: sound banks

`USRDIR/SE` holds 41 `.PHD` indexes with a matching `.PBD` payload each, including `B_SCENARIO` and `PLUS_SCENARIO` — the two scenario-voice banks that the executable names directly. A `.PHD` begins `PPHD`, then `0x38`, `0x00010000`, `0xFFFFFFFF`, `0x40`, and a pair of offsets; the rest is `0xFF` fill. The payloads are structured rather than high-entropy, so these banks are the one place where the audio side can be read without solving the scene compression.

## CRI files

`VJ0.AFS` is a CRI AFS archive, the standard container for voice banks, and the 30 music files are plain ADX — `B01.ADX` is 4,600,786 bytes and its header carries the `(c)CRI` mark. Both formats are documented elsewhere and are out of scope here; the point is that they account for 490 MB of the disc without involving the engine's own code.

## What is still open

All five families are decoded at the container level. What is left is inside them.

The dialogue is found: it is in `ScStr`, as glyph indices, and the layout above reads it. What is left on the text side is the attribute word in each cell, the meaning of the per-glyph metric fields, why the `u16` at `FONTSTLB + 0x0c` is `101` in every file, and how a scene id in `root/` maps to a file name in `ScStr/`.

The scene containers themselves (`A###J.P`, `F###J.P`, `J###J.P`, `K###J.P`, `BTL###J.P`, 2,272 to 33,563 bytes) hold no text: they are sparse tables headed `00 01 50 53 50`, 96 % zero bytes, built from 16-byte records with an offset table that ascends in steps of 16. `FCL.DIR` is only the list of the seven `.cvm` archives.

None of `FONTSTLB`, `FONTDATF`, `FGB`, or `00 01 50 53 50` occurs as a byte sequence in the executable, so these blocks are not dispatched on their magic and a string hunt cannot find their loader; the blocks are identified by position inside a three-block `pack` instead. `OOCH` and `pack` are the only magics this engine compares, at file offsets `0x2d704` and `0x2e480`.

## Sources

None beyond the inspected copy; all figures above are measurements of the files in `USRDIR`.
