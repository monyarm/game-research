---
title: "TB_D3P: event scripts"
description: "The EVENT chapter files in Tiger & Bunny — Hero's Day: a fixed header, a u32 table, a Shift-JIS choice-label pool, and a bytecode whose instruction widths are decoded but whose operand meanings are not."
type: engine
status: draft
confidence: mixed
tags:
  - playstation-portable
  - script
  - bytecode
  - shift-jis
  - tiger-and-bunny
platforms:
  - PlayStation Portable
games:
  - tiger-and-bunny-heros-day
maturity: partial
sources: []
last_verified: 2026-11-24
ai_assisted: true
---

# TB_D3P: event scripts

The eleven `EVENT/CH00_00.EVT` … `CH10_00.EVT` files are the chapter-level scripts. They are not the dialogue — that lives in the [event data files](script.md) — and they are not a [section container](containers.md). They hold one thing that appears nowhere else on the disc: the text of the player's answers.

This page documents the string pool and the instruction widths, both observed and reproducible, and records what the operands mean as still open.

## Files

| File | Choice strings |
| --- | ---: |
| `CH00_00.EVT` | 1 (`ダミー` only) |
| `CH01_00.EVT` | 51 |
| `CH02_00.EVT` | 29 |
| `CH03_00.EVT` | 33 |
| `CH04_00.EVT` | 36 |
| `CH05_00.EVT` | 28 |
| `CH06_00.EVT` | 31 |
| `CH07_00.EVT` | 23 |
| `CH08_00.EVT` | 37 |
| `CH09_00.EVT` | 11 |
| `CH10_00.EVT` | 74 |

Sizes run from 955 bytes to 20,439 bytes. Every file's first string is `ダミー`, a placeholder, which suggests the label table is indexed from one and entry zero is unused.

## Layout

| Offset | Type | Meaning |
| --- | ---: | --- |
| `0x00` | `u32` | `0x80` — header size |
| `0x04`–`0x7f` | — | Zero |
| `0x80` | `u32[]` | Entry offsets into the bytecode; count differs per file |
| `0x90` | Shift-JIS | String pool, starting with `ダミー` |
| varies | — | Bytecode |

The `u32` table at `0x80` is a list of offsets into the file, not of counts or ids. `CH01_00.EVT` holds eight ascending values (`0x515`, `0x567`, `0x5f2`, `0x644`, `0x74b`, `0x79d`, `0x8a4`, `0x8f6`) whose deltas repeat as `0x52`, `0x107`, `0x52`, and `CH10_00.EVT` holds a long ascending run of them with the same repeated deltas, one entry per record: the records vary in length but are drawn from a small set of sizes. The first entry is where the bytecode starts, and in `CH00_00.EVT` it is `0x97`, which lands exactly on the first byte after the string pool: at `0x90` the bytes are `83 5f 83 7e 81 5b 00` — `ダミー` in Shift-JIS — and that string ends at `0x96`.

The entries also land on instruction boundaries, not on arbitrary bytes: `CH00_00.EVT`'s second entry, `0x171`, falls on a `0x00` byte that the walk below reaches as an opcode. The two other words in that file's table, `0x0` and `0x8c`, are not bytecode offsets — one is zero and the other points inside the table itself.

`CH10_00.EVT` shows single-byte records as well — `0x2160` and `0x2161` are consecutive table entries — so a record does not have a minimum length beyond one instruction.

## The strings are answers, not narration

Every string in every file is an option the player picks: `力を使う`, `力を使わない`, `耳をすます`, `バーナビーを追いかける`, `楓の様子を伺う`, `遺失物センターを探す`, `一緒にコウジロウ君を助けよう！`. There is no narration and no spoken line in any of the eleven files.

That division is worth stating plainly because it is the opposite of what the file names suggest. `EVENT/` is the branch structure; `PHASE/BIN/` is the prose.

## The bytecode

The body is a stream of variable-length instructions, and the records in the `0x80` table give the parse a hard anchor: a record starts at its table entry and must end exactly at the next one. A walk that keeps trying widths until every record in every file lands on its boundary finds a single consistent assignment, and it is the one below. It covers all eleven files — 584 records — with no unknown opcode anywhere.

| Opcode | Bytes | Notes |
| --- | ---: | --- |
| `0x00` | 1 | No operand |
| `0x01` | 5 | `u32` operand, always an in-file address |
| `0x09` | 6 | 7 for two rare second bytes |
| `0x0a` | 5 | `u32` operand, always an in-file address |
| `0x0c` | 7 | 11 when the second byte is `0x14` |
| `0x0d` | 6 | 7 for three rare second bytes |
| `0x0e` | 3 | — |
| `0x0f` | 3 | `0f <u16>`; `0f 36 00` opens a record, 577 sites against 584 records |
| `0x10` | 6 | `10 <tag> <u32>` |
| `0x11` | 1 | Opens a block |
| `0x12` | 1 | Closes a block |
| `0x13` | 6 or 10 | 10 when the trailing word is an in-file address |
| `0x14` | 10 | — |

Instruction counts across the eleven files:

| Opcode | Count | Opcode | Count |
| --- | ---: | --- | ---: |
| `0x00` | 1365 | `0x0d` | 126 |
| `0x01` | 6205 | `0x0e` | 140 |
| `0x09` | 636 | `0x0f` | 1223 |
| `0x0a` | 591 | `0x10` | 7939 |
| `0x0c` | 723 | `0x11` | 3314 |
| — | — | `0x12` | 3326 |
| — | — | `0x13` | 1423 |
| — | — | `0x14` | 58 |

The one width that is not decided by the opcode alone is `0x13`. The form `13 10 <word> <word>` is ten bytes when the second word is an address that falls inside the file and lands on an instruction start, and six bytes otherwise. Of the 726 ten-byte sites, 725 pass that test; of the 697 six-byte sites, 663 have no plausible second word at all. That is the rule used above, and it is the reason a table keyed on the opcode alone could not walk the stream.

Everything with an address operand — `0x01`, `0x0a`, and the second word of a ten-byte `0x13` — points at a byte that the parse reaches as an instruction start, which is the strongest evidence that the widths are right: the branch targets land.

`0x11` and `0x12` bracket blocks, with 3,314 opens against 3,326 closes, so a few closes do not follow an open directly. The repeated block of `<10 10 u32>` instructions followed by `<01 u32>` and a `12` is the most common shape, and the `<01 u32>` argument inside it is usually the same address across a run, which fits a shared target rather than a per-site value.

## What the widths do not settle

The parse is consistent, not proven unique. `0x00` is a one-byte instruction with no operand, so any byte the walk does not consume can be absorbed as one, and more than one width assignment can still reach a record boundary. The widths above are the assignment that also keeps every address operand landing on an instruction start; a reading without that constraint would fit the bytes as well, and a search that lets every opcode take any width does terminate with a degenerate assignment — most bytes one byte wide, hundreds of "instructions" — which fits the file without explaining it.

The second byte of most instructions is a descriptor, and its values cluster: `0x10`, `0x14` and `0x15` above `0x0f`, and `0x00`, `0x01`, `0x03`, `0x05`, `0x0a` below it. `0x0c` and `0x13` change operand count with it, so it is a type or a mode rather than padding, but what each value selects is not established.

The `EVENT` directory name and the `.EVT` extension are not present in the executable as bytes: a search of the whole loaded image for `EVENT`, `.EVT` and `EVT` finds nothing. The game therefore opens these files without a name string in the binary — a directory listing or an index — so there is no loader to find by name, and the opcode set has to come from the data or from a runtime trace.

## Extraction tooling

None is offered. The strings need no reader — they are plaintext Shift-JIS in an uncompressed file, so any string dumper recovers the labels. What is still missing is the mapping from answer to branch target, and that needs the operand meanings, not another extractor.

The [container](containers.md) splitter explicitly does not handle these files, and the quickbms detection test in that script rejects them, which is the intended behaviour.

## Detection

| File | Size (bytes) | MD5 (first 5,000 bytes) | SHA-256 |
| --- | ---: | --- | --- |
| `CH01_00.EVT` | 17181 | `7c7d0392c936814bd4dce84b415eb4b7` | `d61b6ee24aa45ef6530a7edc65e34f1fad22b284728fa032762e6e074642239b` |

## Unknowns

- What each instruction does, and what its operands mean. The widths say where instructions start and stop; they say nothing about what `0x10`, `0x13` or `0x0c` commands the game to do, or what the descriptor byte selects.
- Why `0x13` sometimes carries a second address word and sometimes does not. The rule above classifies the sites, but the two forms have not been matched to two behaviours.
- What the records in the `0x80` table are — one per offset, drawn from a small set of lengths — and whether they are scenes, branch groups or label blocks.
- Why `CH00_00.EVT` carries two words that are not offsets after its two real entries.
- Whether the `01 <u32>` operands are file offsets, record indices or node ids. They land on instruction starts, which fits a code address; `0x345` recurs many times in one file, which fits a node id. Both readings are open.
- Whether `CH00_00.EVT` is a real chapter or a template — it holds only the `ダミー` placeholder and is 955 bytes.

## Sources

No public documentation of this format was found. The description above comes from the inspected copy.
