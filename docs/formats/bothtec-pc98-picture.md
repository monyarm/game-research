---
title: "Bothtec PC-98 four-plane picture"
description: "The headerless .R1/.G1/.E1/.B1 bitplane set and .ALG analog palette used by Bothtec's PC-9801 games."
type: format
status: draft
confidence: observed
tags:
  - pc-98
  - graphics
  - bitplane
  - bothtec
engines: []
games:
  - ranma-half-hiryuu-densetsu
maturity: documented
samples:
  - name: RANMA1.R1
    size: 32000
    md5_first_5k: "b355078e1ccd025e226b1bdd0c7cfc99"
    sha256: "3920b77676030d399aecabb7fdc19ae0a13193c29a5590dcc4d96c8bc58a9769"
  - name: RANMA.ALG
    size: 96
    md5_first_5k: "291d1d66eb7e0edfc0ede57b8add9713"
    sha256: "e635828d72f2e4e721428740cf009afcf1af62aaae42469a51002c8ea8bc2244"
sources: []
last_verified: 2026-11-24
ai_assisted: true
---

# Bothtec PC-98 four-plane picture

A picture is four separate files with the same base name and a one-letter extension, one 1-bit plane each, plus one shared palette file. There is no header: every plane is exactly 32,000 bytes of raw PC-98 GDC video memory for a 640 × 400 screen, 80 bytes per row.

The developer README shipped on disk 8 of *Ranma ½: Hiryuu Densetsu* describes this set itself: `akane1.?1`, `ranma1.?1` and `tsubasa1.?1` are pictures that were not used in the game, `view.com` displays them, and `ranma.alg` is loaded as *analog palette data*.

## At a glance

| Field | Value |
| --- | --- |
| Extension | `.R1` with siblings `.G1`, `.E1`, `.B1`; palette `.ALG` |
| Used by | [*Ranma ½: Hiryuu Densetsu*](../games/ranma-half-hiryuu-densetsu.md) (PC-9801) |
| Sample | `RANMA1.R1` 32,000 bytes on disk 8 of the inspected copy |
| Dimensions | 640 × 400, fixed by the 80-byte row and the 32,000-byte plane length |
| Compression | none observed |
| Maturity | documented |
| Confidence | observed |

## Layout

Each of the four files is a full-screen monochrome plane in GDC order: rows top to bottom, 80 bytes per row, bit 7 of the first byte is the leftmost pixel. The four planes are combined per pixel into a 4-bit colour index.

| File | Plane | Bit in index |
| --- | --- | ---: |
| `NAME.B1` | blue | 0 |
| `NAME.R1` | red | 1 |
| `NAME.G1` | green | 2 |
| `NAME.E1` | intensity | 3 |

Bit order is the part that has to be got right: the common PC-98 convention is B/R/G/E from bit 0, and with that order the sample decodes to a recognisable picture. Any other assignment produces a wrong-coloured image rather than garbage, so it is worth checking against `VIEW.COM` output.

## Palette

`RANMA.ALG` is 96 bytes: 16 colours, three little-endian `u16` values each, in red, green, blue order. The channel value is the **low byte** of each word; the first entry is `00 00 00 00 d1 00`, i.e. red 0, green 209, blue 0. The high byte is not always zero — the red word of colour 9 at `0x36` is `4b 01`, giving 75 — so read the low byte only rather than shifting the word.

| Offset | Contents |
| --- | --- |
| `0x00` | colour 0, three `u16` (R, G, B) |
| … | one 6-byte entry per colour |
| `0x5a` | colour 15 |

One palette file is shared by every picture set on the disk: the README says `view.com` always loads `ranma.alg`, and the three sample sets contain no palette of their own. Colours can therefore look off for a picture the palette was not tuned for — `AKANE1` renders with green-tinted skin.

## Detection

| File | Size (bytes) | MD5 (first 5,000 bytes) | SHA-256 |
| --- | ---: | --- | --- |
| `RANMA1.R1` | 32000 | `b355078e1ccd025e226b1bdd0c7cfc99` | `3920b77676030d399aecabb7fdc19ae0a13193c29a5590dcc4d96c8bc58a9769` |
| `RANMA.ALG` | 96 | `291d1d66eb7e0edfc0ede57b8add9713` | `e635828d72f2e4e721428740cf009afcf1af62aaae42469a51002c8ea8bc2244` |

`RANMA1.G1`, `RANMA1.E1` and `RANMA1.B1` are 32,000 bytes each as well. Sizes and both hashes were produced with `tools/sample-hashes.py` from the extracted disk 8 tree.

## Extraction tooling

The converter reads one plane, finds its three siblings and `RANMA.ALG` by name in the same folder, and writes a 24-bit BMP. `RANMA.ALG` must be named exactly that; the three picture sets on disk 8 all use it.

```text
# bothtec-pc98-picture.bms — convert a Bothtec PC-98 four-plane picture to BMP
# input : any one of NAME.R1 / NAME.G1 / NAME.E1 / NAME.B1
#         (the other three planes and RANMA.ALG must sit in the same folder)
# output: NAME.bmp, 24-bit, 640 x (size / 80) pixels
# usage : quickbms bothtec-pc98-picture.bms "<...>/RANMA1.R1" <out_folder>

endian little
get fn fullname
get base basename
strlen flen base
math flen + 3
set root string fn
string root - flen          # folder that holds the input file, trailing separator included

# palette: 16 colours, three little-endian u16 each, channel value is the low byte
set p string root
string p + "RANMA.ALG"
open "" p 5
for i = 0 < 16
    get v short 5
    math v & 255
    putarray 0 i v
    get v short 5
    math v & 255
    putarray 1 i v
    get v short 5
    math v & 255
    putarray 2 i v
next i

# the four bitplanes: R = bit 1, G = bit 2, E = bit 3, B = bit 0
set p string root
string p + base
string p + ".R1"
open "" p 1
set p string root
string p + base
string p + ".G1"
open "" p 2
set p string root
string p + base
string p + ".E1"
open "" p 3
set p string root
string p + base
string p + ".B1"
open "" p 4

get psz asize 1
set rows psz
math rows / 80
set isz psz
math isz * 8
math isz * 3

log MEMORY_FILE 0 0
# BMP header, 24bpp, bottom-up rows
set fsz isz
math fsz + 54
put 0x42 byte MEMORY_FILE
put 0x4d byte MEMORY_FILE
put fsz long MEMORY_FILE
put 0 short MEMORY_FILE
put 0 short MEMORY_FILE
put 54 long MEMORY_FILE
put 40 long MEMORY_FILE
put 640 long MEMORY_FILE
put rows long MEMORY_FILE
put 1 short MEMORY_FILE
put 24 short MEMORY_FILE
put 0 long MEMORY_FILE
put isz long MEMORY_FILE
put 2835 long MEMORY_FILE
put 2835 long MEMORY_FILE
put 0 long MEMORY_FILE
put 0 long MEMORY_FILE

# BMP stores rows bottom-up, so walk the planes from the last row
for row = 0 < rows
    set srow rows
    math srow - 1
    math srow - row
    set line srow
    math line * 80
    for col = 0 < 80
        set off line
        math off + col
        goto off 1
        get vr byte 1
        goto off 2
        get vg byte 2
        goto off 3
        get ve byte 3
        goto off 4
        get vb byte 4
        for k = 0 < 8
            math m = 128
            math m >> k
            math idx = 0
            set t vr
            math t & m
            if t != 0
                math idx | 1
            endif
            set t vg
            math t & m
            if t != 0
                math idx | 2
            endif
            set t ve
            math t & m
            if t != 0
                math idx | 4
            endif
            set t vb
            math t & m
            if t != 0
                math idx | 8
            endif
            getarray c 2 idx
            put c byte MEMORY_FILE
            getarray c 1 idx
            put c byte MEMORY_FILE
            getarray c 0 idx
            put c byte MEMORY_FILE
        next k
    next col
next row

set onam string base
string onam + ".bmp"
log onam 0 fsz MEMORY_FILE
```

Run against the three disk 8 sets it wrote 640 × 400 BMPs of 768,054 bytes in about 1.6 seconds each, using 13 to 14 of the 16 palette entries. The `RANMA1` result shows a coloured seated Ranma among dark flowers in the left half of the canvas and a pale line-art duplicate in the right half.

Limits: the width is fixed at 640 in the header, the palette file name is fixed at `RANMA.ALG`, and the output is 24-bit BMP only. A picture of another width would need `640` replaced with `psz / rows`.

## Unknowns

- **The canvas holds two pictures.** Both halves of the rendered image look like separate 320 × 400 compositions. Whether the game displays one half at a time, and whether the plane origin differs from the headerless assumption, is not known.
- **Relation to `.A98` and `.ANI`.** The rest of the game's pictures use those extensions with a small header. Their payloads were not verified to be the same planes, so no converter is offered for them yet.
- **Palette scope.** Whether `.ALG` files other than `RANMA.ALG` exist in the game's own picture path, or the palette is fixed for the whole game, is not known.
- **No public documentation found.** Searches for Bothtec picture formats, `.A98`, `.ANI` and `.ALG` returned no format description. The `.A98` hits that exist describe AliceSoft's unrelated A98SYS archive.

## Sources

- No public source describes this format. The layout above was established from the inspected files and from `README.DOC` on disk 8 of the same copy, which documents the `.?1` naming, `view.com` and `ranma.alg` as analog palette data.
