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
last_verified: 2026-11-23
ai_assisted: true
---

# Soalo: payload layout

Every data file in these games is a pair: a `.BIN` that holds the payload and a `.HD` that holds nothing but a list of record sizes. The pair mechanism itself is described on the [archives](archives.md) page. This page is about what is inside each container, and how the contents differ between the three builds.

The builds are named by their subtitles: **Concerto** (*Koakuma to Harukaze no Concerto*, 2007-02), **Fantasy** (*Muma ga Tsumugu Yokaze no Fantasy*, 2007-11), and **Symphony** (*Maigo no Period to Ikusen no Symphony*, 2008-11).

## At a glance

| Container | Purpose | Present in |
| --- | --- | --- |
| `SYSTEM` | Script library: `.nut` source, compiled data, scene-script name tables, dialogue text | Fantasy and Symphony |
| `SCENEDAT` | Scene backgrounds | All three |
| `SCENE_ID` | Per-scene compressed blocks: compiled scene data on Fantasy and Symphony, script source on Concerto | All three |
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

The index sums never reach the `.BIN` size. Symphony `SYSTEM` sums to 884,706 of 927,744 bytes; `SOUND_ID` to 380,907,904 of 381,030,400. The remainder is padding inside and after the last record, not a separate region.

## `SYSTEM`: the script library

`SYSTEM` is the readable container. On Symphony it is 42 records; the first 33 are a **paged text stream** in Shift-JIS, cut mid-token at record boundaries, and each page begins with a run of `0xFF` padding. The record boundaries carry no structural meaning for the text; they exist because the container works in pages.

| Records | Content | Evidence |
| --- | --- | --- |
| 0–32 | `.nut` script source, Japanese comments, `class` / `function` / `dofile` | Printable ratio 0.64–0.99 |
| 33–39 | Binary tables: counts, string lists, scene-script names | Printable ratio 0.20–0.59 |
| 40–41 | Dialogue text: speaker, voice id, line, narrator gloss | 8,888 and 879 bytes, tagged strings |

Fantasy has the same shape with one page fewer: records 0–31 are text (ratio 0.54–0.96), then 32–36 are the binary tail (ratios 0.25, 0.04, 0.05, 0.23, 0.18).

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

## `SCENE_ID`: compressed blocks

`SCENE_ID` is a block stream like `SCENEDAT` and `NORMAL`, built on 2048-byte boundaries with the same 8-byte header and the same codec described on the [textures](textures.md) page. What changes between builds is the payload.

Counting block headers on 2048-byte boundaries finds 536 in Symphony, 633 in Fantasy, and 377 in Concerto. Decoding 120 of them per game and inspecting the first part of each block:

| Build | Blocks decoded | Payload | First bytes |
| --- | ---: | --- | --- |
| Symphony | 120 | Compiled scene data | `fa 00 00 74 43 61 10 6d ...` |
| Fantasy | 120 | Compiled scene data | `fa 00 00 74 43 64 00 61 ...` |
| Concerto | 120 | Squirrel source text | `/**\r\n * レイヤアクションモジュール関係ク ...` |

None of the 360 sampled blocks contained the word `function` in Symphony or Fantasy; the Concerto sample contained 233 occurrences. So Concerto keeps its script library as **plain source** in this container while the later builds keep **compiled units** here and put the source in `SYSTEM`.

Concerto's blocks open with the same documentation comment style as `SYSTEM`'s `main.nut`:

```text
/**
 * レイヤアクションモジュール関係
 */
```

The decoded sizes match the declared size exactly for these blocks: Symphony's first at offset 14336 declares 23,359 bytes and decodes to 23,359; Concerto's first at offset 2048 declares 34,593 and decodes to 34,593.

The blocks carry the second header word `8` in Symphony and Fantasy and `1` in Concerto. Whether that selects the decoder or records the content kind is not established.

## `SCENEDAT` and `NORMAL`: aligned image blocks

Both containers hold compressed TIM2 images in 2048-byte-aligned blocks, each introduced by the 8-byte header `u32` decoded size, `u32 1`. The decoded output is a complete TIM2 v4 file. Block framing, the codec, and the header inside the decoded image are covered on the [textures](textures.md) page.

`NORMAL` additionally holds `BITH` records (magic `0x42495448`) in four of Symphony's records, and both containers hold SFX and texture name strings such as `NORMAL\TL-GMODE_NEXT.TM2`.

## `SOUND_ID` and `VOICE_ID`

`SOUND_ID` carries a small header record. In Symphony, record 0 is 20 bytes and the index confirms it: `HD[1] = 20`. The header reads as counts and offsets:

```text
00000000 12ac0000 01000000 00100000 00000000
```

Later records are audio banks of several megabytes, with no `VAGp` or `VAGi` header anywhere in the file — one `VAG` string occurs once, far into the file, and is not a valid header. Music is sequenced rather than streamed as samples, so the banks hold instrument data, not finished tracks.

`VOICE_ID` is the simplest container in the set: one record per voice clip, no header at all, raw PS2 SPU ADPCM in 16-byte frames. A frame begins with a shift/filter byte and then compressed samples:

```text
09 00 2f e2 20 ff 2f f3 00 12 20 e2 10 01 4e 05
```

Record sizes are whole numbers of 16-byte frames. This is why voice ids from the script (`RUZ30001` and up) can be resolved by index without any further structure.

## Unknowns

- The `SCENE_ID` grammar: the block stream is understood, but what the compiled payload describes (scene, layer, or action) is not decoded.
- The second header word in `SCENE_ID` blocks: `8` on Fantasy and Symphony, `1` on Concerto.
- Whether `SCENE_ID` block boundaries line up with any per-scene numbering, and how the `.ks` scene names in `SYSTEM` map onto them.
- `SYSTEM`'s binary tail on Fantasy and Symphony: rec 36 on Symphony is a 337,910-byte count table, and the following records are unmapped.
- Whether `SOUND_ID` record 0's header is a bank table or a fixed 20-byte preamble; only one record has been examined.
