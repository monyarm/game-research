---
title: "A98SYS archives"
description: "The PAK container used by A98SYS games: a flat 16-byte-entry index, uncompressed members, and the voice archives that swap the index for numbered records."
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
  - title: morkt/GARbro — ArcADPACK.cs
    url: https://github.com/morkt/GARbro
last_verified: 2026-11-24
ai_assisted: true
---

# A98SYS archives

Every A98SYS archive inspected so far is flat: a count, a fixed-size index of names and absolute offsets, then the member data back to back with no compression. The terminator entry is included in the count, which makes the arithmetic easy to check. The two voice archives replace the name index with numbered records, and are covered further down.

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

`VOICE.PAK` and `VOICE2.PAK` ship alongside the three archives above and index their members differently. The first `u16` is the marker `0x4000`, not a count, and the real count follows it. Names live in a table after the offset table, not in the index itself.

| Offset | Size | Field |
| --- | ---: | --- |
| `0x00` | 2 | Marker, `u16` `0x4000` |
| `0x02` | 2 | Member count, `u16` |
| `0x04` | `8 × count` | Per member: `u32` key, `u32` absolute offset |
| `4 + 8 × count` | `16 × count` | Per member: 8-byte name, 4-byte extension, `u32` size, `u32` unused |
| `4 + 24 × count` | variable | Member data, concatenated |

Reading `0x4000` as a count gives 16,384, which is why the first look at these files suggested an obfuscated or keyed index. The arithmetic settles it: the first data offset is exactly `4 + 24 × count`, and the member sizes sum to the rest of the file.

| Archive | Size (bytes) | Count | Index ends | Member bytes |
| --- | ---: | ---: | ---: | ---: |
| `VOICE.PAK` | 168099000 | 4557 | 109372 | 167989628 |
| `VOICE2.PAK` | 133157807 | 3330 | 79924 | 133077883 |

Both sums land exactly: index end plus member bytes equals the file size. The members are `.WAV` files — `Y002005A.WAV` is 164,308 bytes — plus the same `TAG`, `TAGHEAD`, `PK.BAT` and `..END` entries the plain archives carry.

```text
# a98sys-voice.bms — extract an A98SYS voice archive (VOICE.PAK / VOICE2.PAK)
# layout: u16 0x4000 marker, u16 count, count x (u32 key, u32 offset),
#         count x 16-byte record (8-byte name, 4-byte extension, u32 size)
# usage: quickbms a98sys-voice.bms VOICE.PAK <out_folder>

endian little

get mark short
if mark != 0x4000
    print "not a voice archive: first u16 is %mark%"
    cleanexit
endif
get count short

# key/offset table: keep only the offset in array 10
math pos = 4
for i = 0 < count
    goto pos
    get key long
    get off long
    putarray 10 i off
    math pos + 8
next i

# name table follows immediately, 16 bytes per entry
set npos pos
for i = 0 < count
    goto npos
    getdstring raw 8
    getdstring ext 4
    get size long
    set nm string ""
    for j = 0 < 8
        getvarchr c raw j
        if c > 0x20
            strlen l nm
            putvarchr nm l c
        endif
    next j
    set nm2 string nm
    string nm2 + "."
    set ext2 string ext
    string nm2 + ext2
    getarray off 10 i
    log nm2 off size
    math npos + 16
next i
```

Verified on `VOICE2.PAK`: 3330 files, 133,077,883 bytes in total, matching the table above. The `u32` key in the offset record is presumably what the engine uses to find a line by number; nothing here shows how it is derived.

## Detection

| File | Size (bytes) | MD5 (first 5,000 bytes) | SHA-256 |
| --- | ---: | --- | --- |
| `A98SYS.PAK` | 106625509 | `c00a2c7376eeb66bb16b67cc75fcd169` | `c055bb87055c2b8adb9fdd0079ebcd6e1250171bd8e159570727662c5ff9faa9` |
| `A98FAST.PAK` | 5330183 | `2bd494dcf761cef0e8cf27e2e919db84` | `793093257aabeec7fc4ca4018f23ae1d6b702d588edb71f72ed1b6473ddb30c9` |
| `STREAM.PAK` | 38466393 | `03c75d91177aa52d4377893894c5f938` | `b9bda195a5e613f7406084886fca535a666abcfb6efb668027af0d99cc390206` |
| `VOICE.PAK` | 168099000 | `4cb308c0f363ae666acd5723a0f01519` | `38d5a132140a7699f7a1988ab8da9c370a64ef6d5ea9c695ea055b6a3692ecea` |
| `VOICE2.PAK` | 133157807 | `7073756e3b1997bdde58d492b2126dc4` | `e079261078879b6cac7bc583beeb78e4172ed0736284fc939fb7e46575badb8c` |

The rows come from `tools/sample-hashes.py` on the English release of *Bible Black -La noche de walpurgis-*. Sizes differ between releases: a Negaposi copy of `A98FAST.PAK` is 6,420,411 bytes where this `A98FAST.PAK` is 5,330,183, so these hashes identify a release, not the engine.

## Unknowns

- **Whether the terminator's offset is always the file size.** True in the three inspected archives; it is also the only way to size the last member, so a trim would break the container.
- **What the `>` header on the first member means.** It appears both at the start of the first member and inside `A98SYS.TAG`; the rest of `TAGHEAD` is `..\r\n`.
- **Whether any A98SYS title compresses its members.** Nothing in `.EDT`, `.SAL`, `.ED8`, `.HGO` or `.WAV` looks packed, and the archive stores no size or flag field that could mark one.
- **What the `u32` key in the voice index means.** Each voice record pairs a key with its offset; the engine must resolve a line to a key, but no mapping has been found.
- **Why the voice archives use a different index at all.** The offset table and the name table hold the same information; only the extra key field and the `0x4000` marker differ.

## Sources

- [RikuKH3/bblack_transkit](https://github.com/RikuKH3/bblack_transkit) — `src/bblack_paktool.dpr` reads and writes this layout. No licence is stated in the repository.
- [jyxjyx1234/misc_game-chs](https://github.com/jyxjyx1234/misc-game-chs) — `pack.py` reads the layout independently and repacks `A98SYS.pak` and `A98FAST.pak`. No licence is stated in the repository.
- [morkt/GARbro](https://github.com/morkt/GARbro) — `ArcFormats/ActiveSoft/ArcADPACK.cs`, MIT, handles both the plain `A98SYS` archive and the `0x4000` voice variant; the voice layout above follows its `TryOpenVoiceArchive`.
