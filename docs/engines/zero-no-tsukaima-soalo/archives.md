---
title: "Soalo: archives"
description: "The .BIN/.HD pair used by the Zero no Tsukaima PS2 games, how the index works, and a quickbms script that splits a pair into numbered records."
type: engine
status: draft
confidence: observed
tags:
  - playstation-2
  - bin-hd
  - quickbms
  - zero-no-tsukaima
platforms:
  - PlayStation 2
games: []
formats: []
maturity: documented
sources:
  - title: QuickBMS
    url: https://aluigi.altervista.org/quickbms.htm
last_verified: 2026-11-24
ai_assisted: true
---

# Soalo: archives

Soalo does not have one archive format; it has one container mechanism, reused six times per game. Every data file is a `<NAME>.BIN` payload plus a `<NAME>.HD` index, and the index is nothing but a list of record sizes.

## At a glance

| | |
| --- | --- |
| Extension | `.BIN` payload, `.HD` index |
| Pairing | Same base name, `.HD` opened as `<NAME>.HD;1` on disc |
| Index type | Flat little-endian `u32` array of record sizes |
| Record order | File order, no offsets stored |
| Compression | None at the container level |
| Padding | Long `0xFF` runs inside records and after the last one |
| Pairs per game | Six (five in Concerto) |

## Layout

The index has no header, no magic, and no per-entry fields beyond the size:

| Field | Size | Notes |
| --- | ---: | --- |
| record size | 4 | little-endian `u32`; this is also the length of the record |

Record *n* starts at the sum of the previous records **rounded up to a 2048-byte boundary**, so the index doubles as an offset table. Reading it is a single pass: keep a running offset, read a size, copy that many bytes from the payload, then advance the offset by the size rounded up to 2048.

```text
offset(n) = sum over i < n of  ceil(size[i] / 2048) * 2048
```

That rounding is exact, not approximate: summing `ceil(size/2048) * 2048` over every index reproduces the payload size to the byte for all six containers in all three games. Symphony's `SYSTEM` index sums to 884,706 bytes of raw record data in a 927,744-byte file, and 927,744 is exactly what the padded sum gives.

| Container | Symphony | Fantasy | Concerto |
| --- | ---: | ---: | ---: |
| `SYSTEM` | 42 | 37 | — |
| `SCENE_ID` | 600 | 775 | 1921 |
| `SCENEDAT` | 2155 | 1598 | 1184 |
| `NORMAL` | 653 | 436 | 360 |
| `SOUND_ID` | 181 | 120 | 106 |
| `VOICE_ID` | 21152 | 28853 | 16192 |

Boundary checks: Symphony `SYSTEM` record 0 is a 4,894-byte script page, so record 1 starts at 6,144 with `0xFF` up to that point and its own content at 6,144; record 2 then starts at 12,288. Concerto and Fantasy behave the same way.

## Things that will trip up a naive reader

- **The sizes do not add up to the file size.** Symphony's `SYSTEM` records sum to 884,706 bytes of a 927,744-byte file; `SOUND_ID` sums to 380,907,904 of 381,030,400. The difference is the 2048-byte rounding of each record, not a hidden region — a reader that advances by the raw size drifts out of step from the first record on.
- **The fill after each record is `0xFF`, not zero.** Because a record starts on a boundary and the next one starts on the next boundary, the rounding slack trails each record. Measured over Symphony's `SCENE_ID`, every one of the 624,991 padding bytes is `0xFF`. That is why a naive text scan reports garbage at the end of a record, and why `SYSTEM`'s pages look `0xFF`-led: the slack of one page runs into the next.
- **Record boundaries are not block boundaries.** In `SCENEDAT` the image blocks are 2048-byte aligned like everything else, but they do not line up with the sizes in the index. Use the [texture carver](textures.md) for images instead of this splitter.
- **Zero-length records exist.** Symphony's `SYSTEM` index has one.

## Splitting a pair

```quickbms
# zero-no-tsukaima-bin-hd.bms
#
# Splits a Soalo .BIN/.HD pair into numbered records.
#
#   quickbms zero-no-tsukaima-bin-hd.bms SYSTEM.HD out/
#
# Input : the .HD index. The matching .BIN is opened from the same folder.
# Output: <NAME>_00000.bin, <NAME>_00001.bin, ... in the output folder.
#
# The .HD file is a flat array of little-endian uint32 record sizes.
# Records are stored back to back in the .BIN in the same order, but each
# one starts on a 2048-byte boundary, so the offset advances by the size
# rounded up to 2048.
#
# Caveats, by design:
#   - Records keep their 0xFF padding; nothing is trimmed.
#   - Sizes sum to less than the .BIN size; the difference is the rounding.
#   - SCENEDAT/NORMAL image blocks do not follow record boundaries. Use the
#     texture carver for those files.
#   - Zero-length records produce no file.

endian little

get HD_SIZE asize 0
math REC_COUNT = HD_SIZE
math REC_COUNT /= 4

# Build the payload name from the index name. Whether quickbms reports the
# basename with or without its extension, the result is the same.
get HD_NAME basename
string BASE_NAME = HD_NAME
string BASE_NAME -= ".HD"
string BIN_NAME = BASE_NAME
string BIN_NAME += ".BIN"

open FDSE BIN_NAME 1
get BIN_SIZE asize 1

set OFFSET long 0
set WRITTEN long 0

for i = 0 < REC_COUNT
    get REC_SIZE long 0

    if OFFSET < BIN_SIZE
        if REC_SIZE > 0
            string OUT_NAME p= "%s_%05d.bin" BASE_NAME i
            log OUT_NAME OFFSET REC_SIZE 1
            math WRITTEN += 1
        endif
    endif

    math STEP = REC_SIZE
    math STEP += 2047
    math STEP /= 2048
    math STEP *= 2048
    math OFFSET += STEP
next i

print "index: %HD_NAME% (%REC_COUNT% records)"
print "offset reached %OFFSET% of %BIN_SIZE% bytes"
```

Run it once per pair:

```sh
for hd in SYSTEM SCENE_ID SCENEDAT NORMAL SOUND_ID VOICE_ID; do
    quickbms zero-no-tsukaima-bin-hd.bms "$game/$hd.HD" "out/$hd"
done
```

The script runs clean under QuickBMS 0.12.0. On Symphony the printed offset reaches 927,744 bytes for `SYSTEM` and 7,804,928 for `SCENE_ID`, each exactly the payload size; on Fantasy `SYSTEM` gives 37 records and on Concerto `SCENE_ID` 1,921 records, again with the offset landing on the file size. That final offset is the quickest correctness check: if it is short, a record size was advanced without the 2048 rounding.

The `VOICE_ID` pair is the one case where splitting is not worth the disk: Fantasy's index alone describes 1.5 GB of records, and each record is a self-contained ADPCM clip that the executable addresses by index anyway.

## Verifying a split

- The printed `wrote` count should equal the index record count minus any zero-length entries.
- The printed byte coverage should be at or just under the payload size, never over.
- `SYSTEM_00000.bin` from Symphony should begin with a Shift-JIS comment and contain `SCWIDTH  <- 640;`.
- `SCENE_ID_00000.bin` from Concerto is a compressed block, not text: it opens with a little-endian size and the `01 00 00 00` word, then the codec stream. Decompress it to see the source.

## Unknowns

