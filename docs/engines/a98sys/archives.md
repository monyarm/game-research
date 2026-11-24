---
title: "A98SYS archives"
description: "The PAK container used by A98SYS games: a flat 16-byte-entry index, uncompressed members, and the voice archives that do not follow it."
type: engine
status: draft
confidence: mixed
tags:
  - pak-archive
  - windows
  - visual-novel
platforms:
  - Windows
games: []
formats: []
maturity: partial
sources:
  - title: RikuKH3/bblack_transkit
    url: https://github.com/RikuKH3/bblack_transkit
  - title: jyxjyx1234/misc_game-chs
    url: https://github.com/jyxjyx1234/misc-game-chs
last_verified: 2026-11-24
ai_assisted: true
---

# A98SYS archives

Every A98SYS archive inspected so far is the same flat container: a count, a fixed-size index of names and absolute offsets, then the member data back to back with no compression. The terminator entry is included in the count, which makes the arithmetic easy to check.

## Layout

| Offset | Size | Field |
| --- | ---: | --- |
| `0x00` | 2 | Entry count, `u16` little-endian, terminator included |
| `0x02` | `16 × count` | Index entries |
| `2 + 16 × count` | variable | Member data, concatenated in offset order |

Each index entry is 16 bytes:

| Offset | Size | Field |
| --- | ---: | --- |
| `0x00` | 8 | Member name, space padded, Shift-JIS |
| `0x08` | 3 | Extension without the dot, NUL padded |
| `0x0b` | 1 | NUL |
| `0x0c` | 4 | Absolute offset of the member data, `u32` |

The last entry is a terminator. Its name is `..END`, its extension field is three spaces, and its offset equals the archive size, which is what gives the final member its length. A member called `TAGHEAD` holds five bytes, `>..\r\n` — the same marker that opens `A98SYS.TAG`.

Member size is not stored. It is the next entry's offset minus this entry's offset, so the table must be read in order.

## Worked example

`A98SYS.PAK` is 106,625,509 bytes with a count of 1058. The index therefore runs from `0x02` to `0x02 + 1058 × 16 = 16,930`, and the first member (`01.HGO`) indeed starts at 16,930.

| Archive | Size (bytes) | Count | Index end | First member offset |
| --- | ---: | ---: | ---: | ---: |
| `A98SYS.PAK` | 106625509 | 1058 | 16930 | 16930 |
| `A98FAST.PAK` | 5330183 | 194 | 3106 | 3106 |
| `STREAM.PAK` | 38466393 | 26 | 418 | 418 |

## Extraction

The script reads the index twice: once to collect offsets, once to emit files. It needs both passes because a member's size is only known from the entry that follows it.

```text
# a98sys-pak.bms — split an A98SYS PAK archive into its files
# usage: quickbms a98sys-pak.bms A98SYS.PAK <out_folder>
endian little
get count short
math last = count
math last - 1
# pass 1: read the offset table
for i = 0 < count
    math pos = i
    math pos * 16
    math pos + 2
    goto pos
    getdstring raw 8
    getdstring ext 3
    get zero byte
    get off long
    putarray 10 i off
next i
# pass 2: extract, size = next entry offset - this entry offset
for i = 0 < last
    math pos = i
    math pos * 16
    math pos + 2
    goto pos
    getdstring raw 8
    getdstring ext 3
    get zero byte
    get off long
    set nm string ""
    for j = 0 < 8
        getvarchr c raw j
        if c > 0x20
            strlen l nm
            putvarchr nm l c
        endif
    next j
    set out string nm
    string out + "."
    string out + ext
    math nxt = i
    math nxt + 1
    getarray endoff 10 nxt
    set size endoff
    math size - off
    log out off size
next i
```

Verified on `A98FAST.PAK`: 194 entries, 193 files written, 5,327,077 bytes in total. The archive is 5,330,183 bytes, and the difference, 3,106, is exactly `2 + 194 × 16`, so nothing is lost or duplicated.

The name loop drops every byte at or below `0x20` rather than only the trailing padding, so a member whose name contains an internal space would lose it. No such name appears in the three inspected archives.

## The voice archives

`VOICE.PAK` and `VOICE2.PAK` ship alongside the three archives above and do not follow the layout. Both read `u16` 16384 where a count would be, and the bytes that follow are not names:

| Archive | Size (bytes) | First bytes |
| --- | ---: | --- |
| `VOICE.PAK` | 168099000 | `cd 11 4b 43 2e 22 3c ab 01 00 59 39 72 26` |
| `VOICE2.PAK` | 133157807 | not yet read |

The executable contains the string `A98SYS_SEC`, which does not appear in any of the three plain archives. A keyed or obfuscated index is the likely explanation, and it is not established. Both files are commented out of the A98SYS skeleton in [the author's own NovelVM](https://github.com/monyarm/NovelVM) for the same reason.

## Detection

| File | Size (bytes) | MD5 (first 5,000 bytes) | SHA-256 |
| --- | ---: | --- | --- |
| `A98SYS.PAK` | 106625509 | `c00a2c7376eeb66bb16b67cc75fcd169` | `c055bb87055c2b8adb9fdd0079ebcd6e1250171bd8e159570727662c5ff9faa9` |
| `A98FAST.PAK` | 5330183 | `2bd494dcf761cef0e8cf27e2e919db84` | `793093257aabeec7fc4ca4018f23ae1d6b702d588edb71f72ed1b6473ddb30c9` |
| `STREAM.PAK` | 38466393 | `03c75d91177aa52d4377893894c5f938` | `b9bda195a5e613f7406084886fca535a666abcfb6efb668027af0d99cc390206` |

The rows come from `tools/sample-hashes.py` on the English release of *Bible Black -La noche de walpurgis-*. Sizes differ between releases: a Negaposi copy of `A98FAST.PAK` is 6,420,411 bytes where this `A98FAST.PAK` is 5,330,183, so these hashes identify a release, not the engine.

## Unknowns

- **Whether the terminator's offset is always the file size.** True in the three inspected archives; it is also the only way to size the last member, so a trim would break the container.
- **What the `>` header on the first member means.** It appears both at the start of the first member and inside `A98SYS.TAG`; the rest of `TAGHEAD` is `..\r\n`.
- **Whether any A98SYS title compresses its members.** Nothing in `.EDT`, `.SAL`, `.ED8`, `.HGO` or `.WAV` looks packed, and the archive stores no size or flag field that could mark one.
- **How the voice index is keyed.** No key has been found; see above.

## Sources

- [RikuKH3/bblack_transkit](https://github.com/RikuKH3/bblack_transkit) — `src/bblack_paktool.dpr` reads and writes this layout. No licence is stated in the repository.
- [jyxjyx1234/misc_game-chs](https://github.com/jyxjyx1234/misc-game-chs) — `pack.py` reads the layout independently and repacks `A98SYS.pak` and `A98FAST.pak`. No licence is stated in the repository.
