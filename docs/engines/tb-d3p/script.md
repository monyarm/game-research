---
title: "TB_D3P: script format"
description: "The four-section event data file in Tiger & Bunny — Hero's Day: record tables, the branch graph, outcome text, and the tagged bytecode that carries dialogue, speakers and voice ids."
type: engine
status: draft
confidence: observed
tags:
  - playstation-portable
  - script
  - shift-jis
  - tiger-and-bunny
platforms:
  - PlayStation Portable
games:
  - tiger-and-bunny-heros-day
maturity: partial
sources: []
last_verified: 2026-11-23
ai_assisted: true
---

# TB_D3P: script format

The dialogue of *Hero's Day* lives in eleven files, `PHASE/BIN/EV00DATA.BIN` through `EV10DATA.BIN`, one per chapter. Each is a [section container](containers.md) with exactly four sections, and each section has a different job.

The important property is that **nothing here is compressed or encrypted**. Chapter text is plaintext Shift-JIS, wrapped in a bytecode whose control bytes are all below `0x21`. Since Shift-JIS trail bytes are never below `0x40`, the two alphabets cannot be confused, which is what makes the format readable without a decoder.

## The four sections

| Index | Contents |
| ---: | --- |
| 0 | Offset table of per-scene records |
| 1 | Offset table of script records — the dialogue |
| 2 | Branch graph |
| 3 | Choice outcome text |

Section starts for every chapter:

| File | Size | Section starts |
| --- | ---: | --- |
| `EV00DATA.BIN` | 25040 | `0x20`, `0x4980`, `0x5e40`, `0x5e60`, `0x61d0` |
| `EV01DATA.BIN` | 566080 | `0x20`, `0x72780`, `0x89a80`, `0x89fd0`, `0x8a340` |
| `EV02DATA.BIN` | 342528 | `0x20`, `0x40720`, `0x53570`, `0x53920`, `0x53a00` |
| `EV03DATA.BIN` | 430592 | `0x20`, `0x56a40`, `0x68c20`, `0x69040`, `0x69200` |
| `EV04DATA.BIN` | 361936 | `0x20`, `0x45ad0`, `0x58140`, `0x584f0`, `0x585d0` |
| `EV05DATA.BIN` | 426816 | `0x20`, `0x57570`, `0x67d20`, `0x680b0`, `0x68340` |
| `EV06DATA.BIN` | 401952 | `0x20`, `0x4fb80`, `0x61b00`, `0x61eb0`, `0x62220` |
| `EV07DATA.BIN` | 335264 | `0x20`, `0x3e960`, `0x518c0`, `0x51be0`, `0x51da0` |
| `EV08DATA.BIN` | 444784 | `0x20`, `0x59e30`, `0x6c400`, `0x6c7b0`, `0x6c970` |
| `EV09DATA.BIN` | 90016 | `0x20`, `0xecf0`, `0x15d50`, `0x15ec0`, `0x15fa0` |
| `EV10DATA.BIN` | 960176 | `0x20`, `0xcc0e0`, `0xe9d20`, `0xea340`, `0xea6b0` |

## Sections 0 and 1: record tables

Both are an ascending `u32` offset list whose entries are **relative to the start of the section**, not to the file. The list's last entry is the section length, so the record count is the number of entries minus one.

| Section | `EV00DATA.BIN` table | Records |
| --- | --- | ---: |
| 0 | `0x10`, `0x4960` | 1 |
| 1 | `0x10`, `0x1150`, `0x14c0` | 2 |

Section 1 is where the dialogue sits. Its records are tagged bytecode; section 0's single record in chapter 0 is the exception described under [Unknowns](#unknowns).

## Section 2: branch graph

Fixed 16-byte header, then 12-byte entries.

| Offset | Type | Meaning |
| --- | ---: | --- |
| `0x00` | `u32` | Chapter number |
| `0x04` | `u32` | Entry count, including the sentinel |
| `0x08` | `u32` | Zero |
| `0x0c` | `u32` | Zero |

Each entry is three `u32` fields: a source node, a destination node, and the chapter number again. The chapter field is constant within a file and matches the file number — `EV05` carries 5, `EV10` carries 10. The last entry is `(999, 0, 0)`, a sentinel rather than a real node.

The declared count can exceed what the section holds by a few bytes — `EV05` announces 75 entries, which at 12 bytes plus the 16-byte header is 916 bytes against a 912-byte section — so a reader must tolerate a short final read rather than trust the count for bounds. Every section-2 length is a multiple of 16, which is why the shortfall only ever costs the last entry a few bytes.

Section-2 lengths, in bytes: EV00 32, EV01 1360, EV02 944, EV03 1056, EV04 944, EV05 912, EV06 944, EV07 800, EV08 944, EV09 368, EV10 1568.

## Section 3: choice outcome text

A `u32` record count, then fixed **216-byte records**, then zero padding to a 16-byte boundary.

Each record is five 40-byte slots — 20 full-width characters in Shift-JIS, NUL-padded — followed by a 16-byte tail.

| Slot | Contents |
| ---: | --- |
| 0–1 | What happened as a result of the choice |
| 2–3 | A hint towards the intended approach |
| 4 | The failure line |

The tail is twelve zero bytes and an increasing `u32`; its meaning is not established, but it behaves like an outcome index rather than data.

An example record from `EV02DATA.BIN`:

```text
ブラッドレッドを確保する為のアイデア
が浮かばなかった・・・
これまでに彼と遭遇した時の状況を振り返り、整理してみよう。
ヒントを見落として・・・
```

Record counts: EV00 4, EV01 4, EV02 1, EV03 2, EV04 1, EV05 3, EV06 4, EV07 2, EV08 2, EV09 1, EV10 4.

The 216-byte stride matters. Reading the section as `(length − 4) / count` bytes per record produces text that looks like Japanese but is shifted, which is the classic way to mistake a fixed-record table for a variable-length one.

## Section 1: the tag set

Text is stored as it is displayed, in Shift-JIS, with tag bytes interleaved. Every tag byte is below `0x21`; every text byte is `0x21` or above.

| Byte | Operand | Meaning |
| ---: | --- | --- |
| `0x12` | one byte | Opens a message record; the operand is `0x10` or `0x0e` |
| `0x1e` | six ASCII digits | Voice cue, forming a file name under `sound/Voice/` |
| `0x1c` | Shift-JIS string | Speaker name, NUL-terminated |
| `0x0e` | — | Closes the header group, before the text body |
| `0x11` | — | Ends the line |
| `0x08` | four ASCII digits | A second identifier, seen as `0112` |
| `0x00` | — | Terminates the record |

A decoded record from `EV01DATA.BIN` at `0x86042`, tags shown in angle brackets:

```text
まさか！　覚えてるよ <12> <10> [vo:029024] {楓} <0e> <11>
ホントに？ <12> <10> [vo:001365] {虎徹} <0e> <11>
あぁ、ちゃんと覚えてるさ <12> <0e> [vo:001366] {虎徹} <0e> <11>
（なにやってんだよ、俺・・・ <11> 正直に忘れたって言えばいいだろ！）
<12> <0e> [vo:029025] {楓} <0e> <11>
だよね！　忘れてたらサイアクだもん <12> <0e> [vo:001367] {虎徹} <0e> <11>
```

Two things are visible in that sample. Parenthesised lines are the protagonist's inner monologue, and `0x11` appears inside them as well, so the line break is a display control rather than a record boundary. And every line is at most 20 full-width characters because the script is authored pre-wrapped at that width — which is also why every automated text scan of this disc reports a maximum run of 20.

The voice cue maps onto the path format the executable builds: `sound/Voice/%03d/vo%03d%03d.at3`. The six-digit operand is split three and three, so `029024` is `sound/Voice/029/vo029024.at3`.

The counterpart file for these cues is in `SOUND/VOICE/`, which holds 7,732 files. That correspondence has not been checked file by file; it is inferred from the path format in the executable.

## Extraction

No script reader is needed, and none is shipped. The text is plaintext Shift-JIS inside an uncompressed section, so splitting the [container](containers.md) and decoding the result as Shift-JIS recovers every line.

What a plain string dump loses is the association between a line, its speaker and its voice cue, because those are separate tags rather than part of the text. Recovering them means walking the byte stream and treating anything below `0x21` as a tag, which is the table above and nothing more.

## Detection

| File | Size (bytes) | MD5 (first 5,000 bytes) | SHA-256 |
| --- | ---: | --- | --- |
| `EV01DATA.BIN` | 566080 | `eee04302aa6adde3e321dac53f781ab7` | `3e00fdd76f1a9c27b6b0901b31f3622614f29ddaf06a66c5c9e37e2430598e67` |

## Unknowns

- **`EV00DATA.BIN` section 0** is not text and is not the same bytecode the other chapters use. Its single record is 0x4950 bytes and contains repeating `ed f0` pairs with ascending small values, plus asset names such as `cha900101.tpl` split by single high bytes. Whether that is glyph data, a packed stream or a byte-plane layout is not established, and no codec is claimed for it.
- **Section 0 of the other chapters** holds one record per scene, but its contents have not been read beyond confirming the table shape.
- **The `0x08` operand** appears once in the sample and is documented only as a second identifier. It may be a flag or a text id.
- **The `0x12` operand** distinguishes two record shapes, `0x10` and `0x0e`, and the difference is not explained by the samples read.

## Sources

No public documentation of this format was found. The description above comes from the inspected copy.
