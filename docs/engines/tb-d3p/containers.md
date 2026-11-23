---
title: "TB_D3P: containers"
description: "The section container used by nearly every Tiger & Bunny — Hero's Day data file, and a quickbms script that splits it."
type: engine
status: draft
confidence: observed
tags:
  - playstation-portable
  - container
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

# TB_D3P: containers

Almost every data file in *Hero's Day* is the same structure: an offset table followed by a run of sections. There is no magic word and no version field. The only way to recognise the format is the shape of the table — ascending `u32` offsets whose last entry equals the file size.

## Layout

| Offset | Type | Meaning |
| --- | ---: | --- |
| `0x00` | `u32` | Table size in bytes, also the start of section 0 |
| `0x04` | `u32` | Start of section 1 |
| … | `u32` | Start of section *n* |
| `tableSize − 4` | `u32` | End of the last section — always equal to the file size |
| `tableSize` | — | Section 0 begins here |

The table is an ascending list of absolute file offsets. Section *i* runs from entry *i* to entry *i + 1*, so the number of sections is the number of entries minus one, and the final entry is a sentinel rather than a section start.

The first entry is `tableSize`, which closes the loop: the header says how large it is, and the table's first element confirms it. That property is what makes the format recognisable in files with no header fields at all.

## What the sections contain

The sections are not typed. What a section holds is decided by the file that contains it, and the same container carries images, offset tables, graphs and text in different files.

| File | Sections | Contents |
| --- | ---: | --- |
| `PHASE/BIN/EVnnDATA.BIN` | 4 | Two record tables, a branch graph, outcome text — see [Script](script.md) |
| `PHASE/TEXTURE/*.TPL` | — | Not a container; a single image |
| `MENU/TITLE/EYECATCH###.BIN` | 6 | An index in section 1, then 512×512 and 256×256 images |
| `MENU/TITLE/TITLEMENU_DATA.BIN` | 9 | An index of 8 entries, then images |
| `MENU/CUTIN.BIN` | 6 | Images |
| `MENU/HEROSELECTDATA.BIN` | 12 | Images and data |
| `GALLERY/GALLERYCHRDATABASETHUM.BIN` | 46 | 45 thumbnails of exactly 7,296 bytes each |
| `GALLERY/SCENE.BIN` | 3 | Three nested section containers |
| `TIMESHEET/SHEET.BIN` | 30 | Offset tables of records |
| `RESIDENT/RESIDENTDATA.BIN` | 10 | Mixed |
| `STAFFROLL/ROLLPACK.BIN` | 3 | Mixed |

Two things follow from that table. Images inside these files use the same `.TPL` layout as `PHASE/TEXTURE`, so the [texture](textures.md) description applies to them unchanged — the section simply starts with a `0x480`-byte image header instead of a file header. And sections can nest: the three sections of `SCENE.BIN` each begin with their own offset table, so a scene is a container of scene parts.

## Files that are not this container

| File | Shape |
| --- | --- |
| `EVENT/CHnn_00.EVT` | `0x80`-byte header, then a `u32` table, then bytecode — see [Event scripts](events.md) |
| `GALLERY/GALLERYCHRDATABASETEXT.BIN` | Starts `2d 00 00 00`, a count-based table of records |
| `GALLERY/GALLERYMUSICLIST.BIN` | Small count-based table |
| `MENU/KEEPOUT/KEEPOUT01–09.BIN` | 64-byte stubs, not containers |
| `PARAM.SFO`, `EBOOT.BIN`, `UMD_DATA.BIN` | Platform files |

`GALLERYCHRDATABASETEXT.BIN` and `GALLERYMUSICLIST.BIN` are the only two content files with a different table shape, which suggests they were written by a different code path — possibly the same one that reads the character database.

## Extraction tooling

All format readers in this repository are quickbms. The script below splits any section container into numbered parts. It detects the format by walking the table, so it exits cleanly on a file that is not a container instead of writing nonsense.

```text
# tb-container.bms — split a TB_D3P section container
# usage: quickbms tb-container.bms <file-or-folder> <output-folder>
# output: <basename>/<index>_<hex offset>.bin

get FILE_SIZE asize
get BASE_NAME basename

# The table is an ascending offset list whose last entry equals the file
# size, so counting entries until that sentinel gives the section count.
math ENTRIES = 0
do
    get ENTRY u32
    math ENTRIES += 1
while ENTRY < FILE_SIZE

if ENTRIES < 2
    print "not a TB_D3P section container"
    cleanexit
endif

# The last entry is the sentinel, not a section, so there is one fewer
# section than there are entries.
math SECTIONS = ENTRIES
math SECTIONS -= 1

goto 0
get START u32
math INDEX = 0
do
    math INDEX += 1
    math POSITION = INDEX
    math POSITION *= 4
    goto POSITION
    get NEXT u32
    math LENGTH = NEXT
    math LENGTH -= START
    string NAME p= "%s/%03d_%08x.bin" BASE_NAME INDEX START
    log NAME START LENGTH
    math START = NEXT
while INDEX < SECTIONS
```

Two notes on the script. The `while ENTRY < FILE_SIZE` test is what distinguishes a container from a random file: on anything else the first `u32` is unlikely to be an ascending offset, so it stops quickly and the section count comes out below two. And `SECTIONS` is decremented because the sentinel is an entry but not a section — a script that treats it as one writes a zero-byte part at the end.

## Detection

| File | Size (bytes) | MD5 (first 5,000 bytes) | SHA-256 |
| --- | ---: | --- | --- |
| `EV01DATA.BIN` | 566080 | `eee04302aa6adde3e321dac53f781ab7` | `3e00fdd76f1a9c27b6b0901b31f3622614f29ddaf06a66c5c9e37e2430598e67` |

`EV01DATA.BIN` is the sample the container description was checked against: four sections at `0x20`, `0x72780`, `0x89a80`, `0x89fd0`, ending at `0x8a340`, which is the file size.

## Unknowns

- The container has no type or version field, so a section's meaning cannot be derived from the container alone. Every file on the disc needs its own reading.
- `MENU/KEEPOUT/KEEPOUT01–09.BIN` are 64 bytes and hold one text run each. They were not tested against the splitter because a 64-byte file cannot contain a meaningful table.
- It is not known whether the sentinel is always the file size or merely the end of a region; every file checked so far ends with a value equal to the file size.

## Sources

No public documentation of this container was found. The description above comes from the inspected copy.
