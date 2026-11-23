---
title: "TB_D3P: textures"
description: "The .TPL image format in Tiger & Bunny — Hero's Day: a 0x80-byte header, an inline 256-colour RGBA palette, and 8-bit index data, with a quickbms splitter."
type: engine
status: draft
confidence: observed
tags:
  - playstation-portable
  - texture
  - paletted
  - quickbms
  - tiger-and-bunny
platforms:
  - PlayStation Portable
games:
  - tiger-and-bunny-heros-day
maturity: documented
sources: []
last_verified: 2026-11-23
ai_assisted: true
---

# TB_D3P: textures

Every image on the disc is the same structure: a fixed `0x480`-byte preamble holding a header and a colour table, followed by one byte per pixel. There is no magic word and no colour-depth field — the pixel count is simply `width × height`, and the file ends exactly there.

881 files in `PHASE/TEXTURE` use this format, and so do the images embedded in the [section containers](containers.md) under `MENU/` and `GALLERY/`.

## Layout

| Offset | Type | Meaning |
| --- | ---: | --- |
| `0x00` | `u32` | Zero |
| `0x04` | `u32` | Width in pixels |
| `0x08` | `u32` | Zero |
| `0x0c` | `u32` | Zero |
| `0x10` | `u32` | Height in pixels |
| `0x14`–`0x18` | — | Zero |
| `0x1c` | `u32` | Palette offset, `0x80` |
| `0x20`–`0x24` | — | Zero |
| `0x28` | `u32` | Pixel offset, `0x480` |
| `0x2c`–`0x7c` | — | Zero in the samples checked |
| `0x80` | 1,024 bytes | 256 RGBA8 palette entries |
| `0x480` | `width × height` bytes | 8-bit palette indices, row-major |

Only four header fields carry data in the samples checked: width, height, the palette offset and the pixel offset. Everything else in the `0x80` bytes reads as zero, including the region from `0x2c` to `0x7c`.

The palette is ordinary RGBA8, four bytes per entry in red, green, blue, alpha order. A `BG` background begins `16 0a 05 ff`, `1d 0f 08 ff`, `23 12 0a ff` — a dark warm ramp, which is what a night scene's palette should look like.

## Verified sizes

The arithmetic closes exactly on every file checked, which is what establishes the format:

| File | Width | Height | Pixels | Pixels + 1,152 | File size |
| --- | ---: | ---: | ---: | ---: | ---: |
| `BG001A.TPL` | 480 | 272 | 130,560 | 131,712 | 131,712 |
| `BG003A.TPL` | 480 | 376 | 180,480 | 181,632 | 181,632 |
| `CHA010101.TPL` | 288 | 272 | 78,336 | 79,488 | 79,488 |

1,152 is `0x480`: `0x80` bytes of header plus 1,024 bytes of palette.

## What the images are

| Prefix | Count | Contents |
| --- | ---: | --- |
| `CHA` | 460 | Character sprites; names encode character, expression and variant |
| `FACE` | 215 | Face close-ups |
| `BG` | 101 | Full-screen backgrounds at 480 × 272 |
| `EG` | 97 | Unestablished; the prefix does not appear in any path string in the executable |
| `ED` | 8 | Unestablished |

Names are uppercase and follow patterns the executable builds (`cha%02d%02d%02d.tpl`, `face%02d%02d%02d.tpl`, `face%02d%02d%02dnext.tpl`), plus a `NEXT` variant seen as `CHA0101NEXT.TPL`. The numeric fields presumably mean character, pose and expression; the mapping was not checked against the game.

`BG` files are full-screen and character-free, which makes them the cleanest samples: 480 × 272 is exactly the PSP screen.

## Images inside containers

The same layout appears inside the [section container](containers.md). A section that holds an image starts with the header directly, so its palette sits at section offset `0x80` and its pixels at `0x480`, exactly as in a standalone file.

Examples, checked by arithmetic:

| File | Section | Size | Dimensions |
| --- | ---: | ---: | --- |
| `MENU/TITLE/EYECATCH001.BIN` | 2 | 263,296 | 512 × 512 |
| `MENU/TITLE/EYECATCH001.BIN` | 3 | 66,688 | 256 × 256 |
| `MENU/TITLE/EYECATCH001.BIN` | 4 | 132,224 | 256 × 512 |
| `GALLERY/GALLERYCHRDATABASETHUM.BIN` | 2–46 | 7,296 each | 96 × 64 |

So a thumbnail gallery is 45 sections of exactly one thumbnail each, and the eyecatch images are larger than the screen because they are shown scaled or cropped.

## Extraction tooling

The quickbms script below splits a `.TPL` into its palette and its index plane. It reads the two offsets from the header rather than assuming them, so it also works on a section that was carved out of a container.

```text
# tb-tpl.bms — split a TB_D3P .TPL image into palette and indices
# usage: quickbms tb-tpl.bms <file-or-folder> <output-folder>
# output: <name>.pal (1024 bytes, 256 x RGBA8) and <name>.idx (width*height bytes)

get FILE_SIZE asize
get BASE_NAME basename

goto 4
get WIDTH u32
goto 0x10
get HEIGHT u32
goto 0x1c
get PALETTE_OFFSET u32
goto 0x28
get PIXEL_OFFSET u32

string PALETTE_NAME p= "%s.pal" BASE_NAME
string INDEX_NAME p= "%s.idx" BASE_NAME

# 256 entries of four bytes each.
log PALETTE_NAME PALETTE_OFFSET 1024

# One byte per pixel, no padding, so the file ends here.
math PIXEL_COUNT = WIDTH
math PIXEL_COUNT *= HEIGHT
log INDEX_NAME PIXEL_OFFSET PIXEL_COUNT
```

The two output files are a straight split, not an image. Turning them back into a picture is a 256-entry table lookup over the index plane, which any paletted-image converter does without knowing anything about this engine.

## Detection

| File | Size (bytes) | MD5 (first 5,000 bytes) | SHA-256 |
| --- | ---: | --- | --- |
| `BG001A.TPL` | 131712 | `3ce5fba0ac4a9454e49f5c474b886c49` | `0eaa5742d6dbbb9bf26ea2e0d9d878d10372a2c9f65b77b88f56f0d8cc9911b7` |

## Unknowns

- The `0x2c`–`0x7c` region is zero in every sample checked but was not surveyed across all 881 files, so a field there cannot be ruled out.
- The `EG` and `ED` prefixes are unreferenced in the executable's path strings, so their role is unknown.
- No file on the disc uses anything other than 8-bit indices. Whether the header can express another depth was not established.
- Alpha is present in the palette but no transparency behaviour was observed.

## Sources

No public documentation of this format was found. The description above comes from the inspected copy.
