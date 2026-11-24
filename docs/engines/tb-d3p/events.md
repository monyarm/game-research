---
title: "TB_D3P: event scripts"
description: "The EVENT chapter files in Tiger & Bunny — Hero's Day: a fixed header, a u32 table, a Shift-JIS choice-label pool, and a bytecode whose opcode set is only partly decoded."
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

This page documents the string pool, which is observed and reliable, and records the bytecode as partially decoded. The opcode set is the one structure on this disc that has resisted reading.

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

## The bytecode: what is established

The body from `0x97` is variable-length instructions. Reading it byte by byte, these forms recur:

| Bytes | Length | Observation |
| --- | ---: | --- |
| `0f <u16>` + zero | 3 or 4 | Appears in long ascending runs — `0f 01`, `0f 02`, `0f 03`, `0f 05`, `0f 06`, `0f 0a`, `0f 0b`, `0f 0c`, `0f 0f`, `0f 10`, `0f 11`, `0f 37` — as if filling a table of slots. `0f 36 00 11` is followed by an `11` opcode, which reads as three bytes; the run `0f 01 00 00 0f 02 00 00` reads as four with the extra zero as a bare `0x00` instruction |
| `01 <u32>` | 5 | Arguments look like node ids: `0x19a`, `0x1b6`, `0x1de`, `0x20a`, `0x1ba`, `0x329`, `0x345`. `0x345` recurs many times, which argues for a shared target rather than a per-site address |
| `09 10 <u32>` | 6 | Seen as `09 10 00 00 00 00` |
| `13 10 <u32>` | 6 | Seen as `13 10 02 00 00 00` |
| `10 10 <u32>` | 6 | `10`, a `0x10` tag byte, then a `u32` operand |
| `11 <u8>` | 2 | Seen as `11 10` |
| `12` | 1 | Terminator; the following byte is an opcode, not an operand |
| `0d 00 10 00 00 00` | 6 or 7 | Trailing zero byte unsettled |
| `0e 01 00` | 3 | — |

A repeated block accounts for most of the stream: `<12 11>` then two `<10 10 u32>` then `<01 u32>`, with the middle arguments rising through `0x01`, `0x21`, `0x28`, `0x2a`, `0x2b`, `0x42` in one run while `01 <u32>` stays at `0x345`.

The file size is odd — 955 bytes — so the final instruction is three bytes long, which is consistent with the `0e 01 00` form.

## The bytecode: what is not established

A fixed opcode-to-width table cannot walk the file. With the widths that hold over the first hundred bytes — `0x00` 1, `0x01` 5, `0x10` 6, `0x11` 2, `0x12` 1, `0x0e` 3 — and any width for the rest, an exhaustive search over `CH00_00.EVT` from `0x97` to the end of the file finds no assignment that reaches the last byte exactly. The walk gets as far as `0x18f`, where the stream reads `13 10 01 00 00 00 | 99 01 00 00 | 0e 01 00`, and `0x99` is not a control byte: the `99 01 00 00` there looks like a `u32` operand, so the instruction before it must be seven bytes rather than six.

Two readings survive that failure, and neither has been proven:

- The widths are context-dependent — the same leading byte meaning different things depending on the previous instruction.
- One or more opcodes take a variable-length operand, most likely a length-prefixed list.

A search that lets every opcode take any width does terminate, but only with a degenerate assignment (most bytes one byte wide, hundreds of "instructions"), which fits the file without explaining it.

Regions the `01 <u32>` operands point at mostly land on `0f` or `09` instruction boundaries (`0x1a6`, `0x1ba`, `0x302`, `0x329`, `0x339`), but `0x345` does not. Under the context-dependent reading that inconsistency is expected; under the fixed-width reading it is a contradiction.

The `EVENT` directory name and the `.EVT` extension are not present in the executable as bytes: a search of the whole loaded image for `EVENT`, `.EVT` and `EVT` finds nothing. The game therefore opens these files without a name string in the binary — a directory listing or an index — so there is no loader to find by name, and the opcode set has to come from the data or from a runtime trace.

## Extraction tooling

None is offered. Nothing here needs a reader to get the strings out: they are plaintext Shift-JIS in an uncompressed file, so the label text is recoverable with any string dumper. What is missing is the mapping from answer to branch target, and that depends on the opcode set that is not yet decoded.

The [container](containers.md) splitter explicitly does not handle these files, and the quickbms detection test in that script rejects them, which is the intended behaviour.

## Detection

| File | Size (bytes) | MD5 (first 5,000 bytes) | SHA-256 |
| --- | ---: | --- | --- |
| `CH01_00.EVT` | 17181 | `7c7d0392c936814bd4dce84b415eb4b7` | `d61b6ee24aa45ef6530a7edc65e34f1fad22b284728fa032762e6e074642239b` |

## Unknowns

- The opcode set, as described above. `CH10_00.EVT` (20,439 bytes, 74 strings) is the best target for a second pass because it has the most branch instances.
- What the records in the `0x80` table are — one per offset, drawn from a small set of lengths — and whether they are scenes, branch groups or label blocks.
- Why `CH00_00.EVT` carries two words that are not offsets after its two real entries.
- Whether the `01 <u32>` operands are file offsets, record indices or node ids. `0x345` recurs, which fits a node id.
- Whether `CH00_00.EVT` is a real chapter or a template — it holds only the `ダミー` placeholder and is 955 bytes.

## Sources

No public documentation of this format was found. The description above comes from the inspected copy.
