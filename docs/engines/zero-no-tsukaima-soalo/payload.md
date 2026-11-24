---
title: "Soalo: payload layout"
description: "Record maps for the six .BIN/.HD containers in all three Zero no Tsukaima PS2 games: SYSTEM, SCENE_ID, SCENEDAT, NORMAL, SOUND_ID, and VOICE_ID."
type: engine
status: draft
confidence: mixed
tags:
  - playstation-2
  - squirrel
  - bin-hd
  - zero-no-tsukaima
platforms:
  - PlayStation 2
games: []
formats: []
maturity: partial
sources: []
last_verified: 2026-11-24
ai_assisted: true
---

# Soalo: payload layout

Every data file in these games is a pair: a `.BIN` that holds the payload and a `.HD` that holds nothing but a list of record sizes. The pair mechanism itself is described on the [archives](archives.md) page. This page is about what is inside each container, and how the contents differ between the three builds.

The builds are named by their subtitles: **Concerto** (*Koakuma to Harukaze no Concerto*, 2007-02), **Fantasy** (*Muma ga Tsumugu Yokaze no Fantasy*, 2007-11), and **Symphony** (*Maigo no Period to Ikusen no Symphony*, 2008-11).

## At a glance

| Container | Purpose | Present in |
| --- | --- | --- |
| `SYSTEM` | Script library: `.nut` source pages, then the compiled closure units of the same modules | Fantasy and Symphony |
| `SCENEDAT` | Scene backgrounds | All three |
| `SCENE_ID` | Scene modules: compiled Squirrel closures on Fantasy and Symphony, source on Concerto | All three |
| `NORMAL` | UI and shared textures | All three |
| `SOUND_ID` | Audio banks | All three |
| `VOICE_ID` | One voice clip per record | All three |

Record count is always the `.HD` size divided by four, because the index is a flat array of little-endian `u32` sizes.

## Container sizes

| Container | Size (bytes) | Index (bytes) | Records |
| --- | ---: | ---: | ---: |
| **Symphony** | | | |
| `SYSTEM.BIN` | 927744 | 168 | 42 |
| `SCENE_ID.BIN` | 7804928 | 2400 | 600 |
| `SCENEDAT.BIN` | 179320832 | 8620 | 2155 |
| `NORMAL.BIN` | 11630592 | 2612 | 653 |
| `SOUND_ID.BIN` | 381030400 | 724 | 181 |
| `VOICE_ID.BIN` | 1252352000 | 84608 | 21152 |
| **Fantasy** | | | |
| `SYSTEM.BIN` | 655360 | 148 | 37 |
| `SCENE_ID.BIN` | 9320448 | 3100 | 775 |
| `SCENEDAT.BIN` | 129587200 | 6392 | 1598 |
| `NORMAL.BIN` | 6443008 | 1744 | 436 |
| `SOUND_ID.BIN` | 238710784 | 480 | 120 |
| `VOICE_ID.BIN` | 1556525056 | 115412 | 28853 |
| **Concerto** | | | |
| `SYSTEM.BIN` | absent | absent | — |
| `SCENE_ID.BIN` | 6492160 | 7684 | 1921 |
| `SCENEDAT.BIN` | 95215616 | 4736 | 1184 |
| `NORMAL.BIN` | 7194624 | 1440 | 360 |
| `SOUND_ID.BIN` | 150704128 | 424 | 106 |
| `VOICE_ID.BIN` | 981067776 | 64768 | 16192 |

The index sums never reach the `.BIN` size. Symphony `SYSTEM` sums to 884,706 of 927,744 bytes; `SOUND_ID` to 380,907,904 of 381,030,400. The difference is the 2048-byte rounding of each record: record *n* begins at the running sum of `align(size[i], 2048)` for `i < n`, and that sum reproduces the `.BIN` size exactly in all six containers on all three discs, so nothing is left over at the end. The fill itself is `0xFF` and nothing else — on Symphony's `SCENE_ID` the 624,991 padding bytes are all `0xFF`.

## `SYSTEM`: the script library

`SYSTEM` is the readable container, and it is the one container in the set with no compression and no 8-byte block header. On Symphony it is 42 records; records 0–31 are complete `.nut` source files stored verbatim in Shift-JIS, each beginning at a `//` or `/**` header or at a top-level assignment and ending on a closed statement. Record sizes are 732 to 54,064 bytes, and record 10 is zero-length. The `0xFF` that shows up at record starts is the inter-record fill, not page padding, and no record is split mid-token.

| Records | Content | Evidence |
| --- | --- | --- |
| 0–31 | `.nut` script source, Japanese comments, `class` / `function` / `dofile` | Printable ratio 0.64–0.99 |
| 32–41 | Ten compiled Squirrel closure units, each opening `FA FA 52 49 51 53 01` | Every record begins with the closure head and the `TRAP` slot label |

Fantasy has the same shape with one page fewer: records 0–30 are source (ratio 0.54–0.96) and 31–36 are six compiled closure units.

The compiled units are not a separate kind of record from the source — they are the same modules after the Squirrel compiler ran. Each one opens `FA FA`, Squirrel's closure-stream head, then the four characters `R I Q S` (Squirrel's `SQIR` tag written backwards), then a version byte `01`, the slot label `TRAP`, and a length-prefixed build path. Sizes on Symphony, records 32–41: 34,440 · 40,233 · 1,942 · 10,273 · 337,910 · 72,693 · 29,421 · 8,656 · 8,888 · 879 bytes. On Fantasy, records 31–36: 39,151 · 51,982 · 2,220 · 7,711 · 229,886 · 1,489 bytes.

Because the units are compiled, the module identity sits in the stream itself as a `TRAP` slot label and a build path rather than in a name table of its own.

Concatenating Symphony's text pages and dropping the `0xFF` runs gives 340,446 bytes of source with **65 `class` and 972 `function` declarations** across **36 `dofile` modules**:

```text
main.nut        game.nut        scenes.nut      variables.nut
player.nut      GamePlayer.nut  ScenePlayer.nut envinit.nut
Environment.nut EnvObject.nut   EnvBase.nut     EnvImage.nut
EnvLayer.nut    EnvBackLayer.nut EnvStageLayer.nut EnvLevelLayer.nut
EnvEventLayer.nut EnvSimpleLayer.nut EnvCharacter.nut
EnvBGM.nut      EnvSE.nut       action.nut      util.nut
Object.nut      BasicLayer.nut  GraphicLayer.nut translayer.nut
TEXTLAYER.NUT   msgwindow.nut   dialogwindow.nut selectwindow.nut
buttonlayer.nut voices.nut      sysvoices.nut   override.nut
multilayers.nut
```

The stream opens with the display constants and the global tables:

```text
// XXX 画面サイズ定義
SCWIDTH  <- 640;
SCHEIGHT <- 448;
EMPTY <- {};
savef <- null;  f <- {};  sf <- {};  tf <- {};
VAR_GAME / VAR_SYSTEM / VAR_TEMP / VAR_SYSTEMWORK
```

and closes in the data tables, which map a character to a costume name and a texture id:

| Character | Costume | Texture |
| --- | --- | --- |
| `ルイズ` | — | `TCG11_DRESSFACELEVEL` |
| `ギーシュ` | `タキシード` | `TCG04_DRESSFACELEVEL` |
| `シルフィード` | — | `TCG34_DRESSFACELEVEL` |

Record 38 is a length-prefixed string list beginning with `DataMake/SCENE/LESSON.NUT`. Records 34 and 35 reference scene scripts by name with the `.ks` extension (`BK3B_M01.ks`, `BK4B_M01.ks`, `ST09D_10.ks`). What that layer is, and why it exists next to `.nut`, is covered on the [scripts](scripts.md) page.

### String resources in compiled data

Compiled or packed regions delimit strings with a fixed tag:

| Field | Size | Value |
| --- | ---: | --- |
| tag | 4 | `0x08000010` (bytes `10 00 00 08`) |
| length | 4 | byte count of the payload |
| payload | length | Shift-JIS or ASCII, no terminator |

Tag counts locate text in `SYSTEM`, which is stored uncompressed:

| File | Symphony | Fantasy | Concerto |
| --- | ---: | ---: | ---: |
| `SYSTEM.BIN` | 10256 | 6306 | — |

`SCENE_ID`, `SCENEDAT`, and `NORMAL` are compressed block streams, so counting tags in their stored bytes measures the codec, not the content. Decoding a block exposes the surrounding data, literal runs included; that is where the `.ks` names below were read.

Compiled script units are stock Squirrel closure streams. The stream opens `FA FA 52 49 51 53 01`: `FA FA`, which is Squirrel's closure-stream head, then the four characters `R I Q S` — Squirrel's `SQIR` stream tag written backwards — then a version byte `01`. Symphony's `SYSTEM.BIN` holds ten of them, all on 2048-byte boundaries: 372,736 · 407,552 · 448,512 · 450,560 · 462,848 · 800,768 · 874,496 · 905,216 · 915,456 · 925,696. Each is followed by the slot label `TRAP` and a length-prefixed build path, one per module — `DataMake/SCENE/env…`, `sce…`, `voi…`, `var…`, `OVE…` (override), `LES…` three times (lesson), `sys…`, `mul…` (multilayers).

So the `.nut` text and the compiled units sit in the same `SYSTEM` pair, and the `0x08000010` tag above is the record type inside the closure stream rather than a container of its own.

## `SCENE_ID`: the scene modules

`SCENE_ID` is a block stream like `SCENEDAT` and `NORMAL`, built on 2048-byte boundaries. Each record starts with the same 8-byte header and is followed by `0xFF` fill up to the next boundary:

| Offset | Type | Meaning |
| --- | --- | --- |
| `0x00` | `u32` | Decoded size |
| `0x04` | `u32` | Interleave factor |
| `0x08` | — | Codec stream, described on the [textures](textures.md) page |

The second word is an interleave factor, not a content tag. After the codec returns the block is still interleaved: the decoded stream holds `factor` planes back to back, each of `size / factor` bytes, and the linear record is formed by taking one byte from each plane in turn before moving on. A factor of 1 therefore makes the pass a plain copy, and bytes past the last whole group are appended as they stand. In the inspected Symphony executable the transform is the routine at `0x116348`, called with the decoded buffer, the output, the decoded size and this word straight after the codec returns at `0x116048`. A record is only complete after both steps.

Factors, counted over every record in the container:

| Build | Records | Factor 1 | Factor 2 | Factor 8 | Factor 16 | Other |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Symphony | 600 | 11 | — | 525 | 64 | — |
| Fantasy | 775 | 2 | — | 631 | 142 | — |
| Concerto | 1920 | 377 | 1533 | — | — | 10 records at 3, 4, 6 or 12 |

With the transpose applied, every record in Symphony and Fantasy opens with the Squirrel closure head `FA FA 52 49 51 53 01 00 00 00`, then a `TRAP` slot label, then the `0x08000010` string tag and a build path:

```text
fa fa 52 49 51 53 01 00 00 00  TRAP  0x08000010  DataMake/SCENE/bk1a_00.nut  main …
```

All 600 Symphony records and all 775 Fantasy records carry exactly one `DataMake/SCENE/` path, and the names are unique per disc — `bk1a_00.nut` … `bk1a_m03.nut`, `bk1b_01.nut` … `bk4a_09.nut`. The record is a compiled scene module, the same shape as the compiled units in `SYSTEM`.

Concerto's records are the source of the same modules, and they stay readable:

```text
initVariable();
selectInit();
selectItem("共通部", (0x01000000 +1861), null, true);
select();            reset();
title("プロローグ");
set("event", {opacity = 100,y = 0,show = 1,level = 80,x = 0,image = (0x02000000 +1)});
```

Every Concerto record is fully printable once transposed, and its declared size is reproduced exactly. So Concerto keeps the scene scripts as source in this container while the later builds keep them compiled here and put their source library in `SYSTEM`.

The `0x01000000` and `0x02000000` constants in that source are container ids: the executable encodes a record as `(archive index << 24) | record index`, with archive 0 = `NORMAL`, 1 = `SCENE_ID` and 2 = `SCENEDAT`. The three archives are created and named at `0x1155e8` in the inspected executable, from the strings `NORMAL`, `SCENE_ID` and `SCENEDAT`.

### Extracting the scene modules

The script below walks the index, decodes each block, undoes the interleave and writes one file per record. It keeps Shift-JIS as it stands, so compiled records stay binary and Concerto's source stays readable text.

```quickbms
# zero-no-tsukaima-scene-id.bms
#
# Recovers the scene modules from a Soalo SCENE_ID container.
#
#   quickbms zero-no-tsukaima-scene-id.bms SCENE_ID.HD out/
#
# Input : a .HD index; the matching .BIN is opened from the same folder.
# Output: one file per record, rec_NNNN.nut for Squirrel closures and source,
#         rec_NNNN.bin for anything else.
#
# A record is a block:
#   0x00  u32  decoded size
#   0x04  u32  interleave factor (1, or 8 and 16 on this disc)
#   0x08  command stream
# The stream decodes to "decoded size" bytes, then the block is de-interleaved
# by the factor before it is usable.
#
# The stream is a Socio Art Logic command loop. Six history slots hold earlier
# commands, seeded with six repeat commands:
#   0xDF 0x00, 0xDF 0x01, 0xDF 0xFF, 0xDF 0x80, 0xDF 0x7F, 0xDF 0xFE
# Command byte C, top three bits select the class:
#   C & 0xE0 == 0xC0  repeat: write the next stream byte (C & 0x1F) + 2 times
#   C & 0xE0 == 0xE0  literal: copy (C & 0x1F) + 1 bytes
#   otherwise         re-run entry (C >> 5), then move that entry to the front.
#                     Re-running a repeat writes its byte (C & 0x1F) + 2 times;
#                     re-running a literal copies (C & 0x1F & 3) + 1 bytes
#                     starting at 1 + ((C & 0x1F) >> 2) inside that literal.
# A literal or repeat is inserted at the front and the last slot is dropped.
# The last command may overshoot the declared size; the output is truncated.
#
# De-interleaving treats the decoded block as a matrix of "factor" columns and
# reads it column by column. Factor 1 is a straight copy.
#
# Measured with QuickBMS 0.12.0 on the three inspected discs:
#   Symphony (SLPS_258.98) SCENE_ID.HD   600 records written,   0 skipped, 55 s
#   Fantasy  (SLPS_258.30) SCENE_ID.HD   775 records written,   0 skipped, 69 s
#   Concerto (SLPS_257.08) SCENE_ID.HD  1920 records written,   1 skipped, 13 s
# Every decoded record matched its declared size. Compiled records begin with
# the Squirrel closure head FA FA 52 49 51 53; Concerto records are plain
# Shift-JIS Squirrel source.
#
# Shift-JIS text is kept as-is, so convert afterwards if needed:
#   iconv -f CP932 -t UTF-8 rec_0000.nut > rec_0000.utf8.nut

endian little

get HD_NAME basename
string BASE_NAME = HD_NAME
string BASE_NAME -= ".HD"
string BIN_NAME = BASE_NAME
string BIN_NAME += ".BIN"

open FDSE BIN_NAME 1

get HD_SIZE asize 0
math REC_COUNT = HD_SIZE
math REC_COUNT /= 4

set REC_START long 0
set MADE long 0
set SKIPPED long 0
set TRUNCATED long 0

For IDX = 0 < REC_COUNT
    math IOFF = IDX
    math IOFF *= 4
    goto IOFF 0
    get PACKED long 0

    math PAD = PACKED
    math PAD += 2047
    math PAD /= 2048
    math PAD *= 2048

    set DONE long 0

    if PACKED > 8
        goto REC_START 1
        get OUTLEN long 1
        get WORD long 1

        if OUTLEN > 0
            if OUTLEN <= 0x4000000
                if WORD < 1
                    math WORD = 1
                endif
                if WORD <= 64

                    math SEND = REC_START
                    math SEND += PAD

                    # --- command stream -------------------------------------
                    log MEMORY_FILE 0 0
                    math V0 = REC_START
                    math V0 += 8
                    set POS long 0

                    math H0 = 0x7FFFFF00
                    math H1 = 0x7FFFFF01
                    math H2 = 0x7FFFFFff
                    math H3 = 0x7FFFFF80
                    math H4 = 0x7FFFFF7f
                    math H5 = 0x7FFFFFfe

                    set KEEP long 1
                    For KEEP == 1
                        if POS >= OUTLEN
                            set KEEP long 0
                            break
                        endif
                        if V0 >= SEND
                            set KEEP long 0
                            break
                        endif

                        goto V0 1
                        get CMD byte 1
                        math BEF = V0
                        math LEN5 = CMD
                        math LEN5 &= 0x1F
                        math CLS = CMD
                        math CLS &= 0xE0

                        if CLS == 0xC0
                            math T = V0
                            math T += 1
                            goto T 1
                            get OPB byte 1
                            math N = LEN5
                            math N += 2
                            For R = 0 < N
                                put OPB byte MEMORY_FILE
                                math R += 1
                            Next
                            math POS += N
                            math V0 += 2
                            math H5 = H4
                            math H4 = H3
                            math H3 = H2
                            math H2 = H1
                            math H1 = H0
                            math H0 = BEF
                            set DONE long 1

                        elif CLS == 0xE0
                            math N = LEN5
                            math N += 1
                            math T = V0
                            math T += 1
                            goto T 1
                            For R = 0 < N
                                get OPB byte 1
                                put OPB byte MEMORY_FILE
                                math R += 1
                            Next
                            math POS += N
                            math V0 += 1
                            math V0 += N
                            math H5 = H4
                            math H4 = H3
                            math H3 = H2
                            math H2 = H1
                            math H1 = H0
                            math H0 = BEF
                            set DONE long 1

                        else
                            math M = CMD
                            math M >>= 5

                            math E = H0
                            if M == 1
                                math E = H1
                            elif M == 2
                                math E = H2
                            elif M == 3
                                math E = H3
                            elif M == 4
                                math E = H4
                            elif M == 5
                                math E = H5
                            endif

                            set SEED long 0
                            if E >= 0x70000000
                                set SEED long 1
                                math C2 = 0xDF
                                math OPB = E
                                math OPB &= 0xFF
                            else
                                goto E 1
                                get C2 byte 1
                            endif

                            math C2CLS = C2
                            math C2CLS &= 0xE0

                            if C2CLS == 0xC0
                                if SEED == 0
                                    math T = E
                                    math T += 1
                                    goto T 1
                                    get OPB byte 1
                                endif
                                math N = LEN5
                                math N += 2
                                For R = 0 < N
                                    put OPB byte MEMORY_FILE
                                    math R += 1
                                Next
                                math POS += N
                                set DONE long 1
                            elif C2CLS == 0xE0
                                math N = LEN5
                                math N &= 3
                                math N += 1
                                math T = LEN5
                                math T >>= 2
                                math T += 1
                                math T += E
                                goto T 1
                                For R = 0 < N
                                    get OPB byte 1
                                    put OPB byte MEMORY_FILE
                                    math R += 1
                                Next
                                math POS += N
                                set DONE long 1
                            endif

                            if M == 1
                                math H1 = H0
                                math H0 = E
                            elif M == 2
                                math H2 = H1
                                math H1 = H0
                                math H0 = E
                            elif M == 3
                                math H3 = H2
                                math H2 = H1
                                math H1 = H0
                                math H0 = E
                            elif M == 4
                                math H4 = H3
                                math H3 = H2
                                math H2 = H1
                                math H1 = H0
                                math H0 = E
                            elif M == 5
                                math H5 = H4
                                math H4 = H3
                                math H3 = H2
                                math H2 = H1
                                math H1 = H0
                                math H0 = E
                            endif

                            math V0 += 1
                        endif
                    Next

                    # --- de-interleave --------------------------------------
                    log MEMORY_FILE2 0 0
                    math ROW = OUTLEN
                    math ROW /= WORD
                    math BODY = ROW
                    math BODY *= WORD

                    For K = 0 < ROW
                        For M = 0 < WORD
                            math SRC = M
                            math SRC *= ROW
                            math SRC += K
                            goto SRC MEMORY_FILE
                            get OPB byte MEMORY_FILE
                            put OPB byte MEMORY_FILE2
                            math M += 1
                        Next
                        math K += 1
                    Next

                    if BODY < OUTLEN
                        math T = BODY
                        For I = T < OUTLEN
                            goto I MEMORY_FILE
                            get OPB byte MEMORY_FILE
                            put OPB byte MEMORY_FILE2
                            math I += 1
                        Next
                    endif

                    # --- output name ----------------------------------------
                    goto 0 MEMORY_FILE2
                    get FIRST byte MEMORY_FILE2
                    set IS_TEXT long 0
                    if FIRST == 0xFA
                        set IS_TEXT long 1
                    elif FIRST >= 0x20
                        if FIRST <= 0x7E
                            set IS_TEXT long 1
                        endif
                    endif

                    if IS_TEXT == 1
                        string OUT_NAME p= "rec_%04d.nut" IDX
                    else
                        string OUT_NAME p= "rec_%04d.bin" IDX
                    endif

                    if POS < OUTLEN
                        math TRUNCATED += 1
                    endif

                    log OUT_NAME 0 OUTLEN MEMORY_FILE2
                    math MADE += 1
                endif
            endif
        endif
    endif

    if DONE == 0
        math SKIPPED += 1
    endif

    math REC_START += PAD
Next IDX

string MSG p= "%d records written, %d skipped, %d short" MADE SKIPPED TRUNCATED
print "%MSG%"
```

Measured with QuickBMS 0.12.0 on the three inspected discs. Every record that was written reproduced its declared size exactly, and every one was checked byte for byte against a separate decoder written from the disassembly:

| Build | Index entries | Written | Skipped | Output |
| --- | ---: | ---: | ---: | --- |
| Symphony | 600 | 600 | 0 | about 17 MB, all 600 opening `FA FA 52 49 51 53` |
| Fantasy | 775 | 775 | 0 | about 21 MB, all 775 opening `FA FA 52 49 51 53` |
| Concerto | 1921 | 1920 | 1 | about 9 MB, all printable source |

The single skipped Concerto entry is the one zero-length index record. Nothing was under-filled on any disc: every block's command stream reached its declared size before the record's 2048-byte boundary.

Because the output is Shift-JIS where it is text at all, convert it before reading:

```sh
iconv -f CP932 -t UTF-8 rec_0000.nut > rec_0000.utf8.nut
```

## `SCENEDAT` and `NORMAL`: aligned image blocks

Both containers hold compressed TIM2 images in 2048-byte-aligned blocks, each introduced by the 8-byte header `u32` decoded size, `u32 1`. The decoded output is a complete TIM2 v4 file. Block framing, the codec, and the header inside the decoded image are covered on the [textures](textures.md) page.

`NORMAL` additionally holds `BITH` records (magic `0x42495448`) in four of Symphony's records, and both containers hold SFX and texture name strings such as `NORMAL\TL-GMODE_NEXT.TM2`.

## `SOUND_ID` and `VOICE_ID`

`SOUND_ID` opens with an empty record and a constant. `HD[0]` is zero, so record 0 occupies no bytes, and record 1 is 20 bytes reading:

```text
00000000 12ac0000 01000000 00100000 00000000
```

That 20-byte record is byte-identical on all three discs. The other 20-byte entries in the same container are short audio clips with distinct payloads — 36 of them in Symphony, 6 in Fantasy — so the constant is a single header record, not a size class.

Later records are audio banks of several megabytes, with no `VAGp` or `VAGi` header anywhere in the file — one `VAG` string occurs once, far into the file, and is not a valid header. Music is sequenced rather than streamed as samples, so the banks hold instrument data, not finished tracks.

`VOICE_ID` is the simplest container in the set: one record per voice clip, no header at all, raw PS2 SPU ADPCM in 16-byte frames. A frame begins with a shift/filter byte and then compressed samples:

```text
09 00 2f e2 20 ff 2f f3 00 12 20 e2 10 01 4e 05
```

Record sizes are whole numbers of 16-byte frames. This is why voice ids from the script (`RUZ30001` and up) can be resolved by index without any further structure.

## Unknowns

- Whether a `SCENE_ID` build path (`DataMake/SCENE/bk1a_00.nut`) corresponds to a `.ks` name in `SYSTEM` (`BK3B_M01.ks`, `ST09D_10.ks`). The naming style matches and a build step plausibly renamed one to the other, but no record in either container names the other's extension.
- What the compiled scene modules do once loaded: the body after the build path is Squirrel bytecode and has not been walked.
- Whether `SCENE_ID` record order lines up with any per-scene numbering; the names are unique but not obviously ordered by chapter in the container itself.
- What the compiled closure units in `SYSTEM` contain: their slot labels (`TRAP`, one per module) and build paths are readable, but the module bodies are compiled Squirrel and have not been walked.
- What the constant `SOUND_ID` header record contains; one 20-byte record is all there is, and its five words are unread beyond being fixed.
