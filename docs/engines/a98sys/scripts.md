---
title: "A98SYS scripts"
description: "The HGO bytecode used by A98SYS games: its function table, where code starts, how text is stored, and why the published opcode table does not decode this build."
type: engine
status: draft
confidence: mixed
tags:
  - bytecode
  - visual-novel
  - windows
platforms:
  - Windows
games: []
formats: []
maturity: partial
sources:
  - title: jyxjyx1234/misc_game-chs — HGO disassembler
    url: https://github.com/jyxjyx1234/misc-game-chs
  - title: RikuKH3/bblack_transkit
    url: https://github.com/RikuKH3/bblack_transkit
last_verified: 2026-11-24
ai_assisted: true
---

# A98SYS scripts

Scene logic lives in `HGO` members. The container part is simple and measured; the instruction set is where the work stops.

## Function table

An HGO file opens with a `u32` function count, then one 36-byte record per function:

| Offset | Size | Field |
| --- | ---: | --- |
| `0x00` | 28 | Function name, NUL padded, ASCII, always starting with `$` |
| `0x1c` | 4 | Unidentified, `u32`; 2 for scene functions, 1 for `$dummy_func` and `$main` |
| `0x20` | 4 | Code offset, `u32`, relative to the end of the table |

`01.HGO` from the inspected `A98SYS.PAK` holds 16 functions and ends its table at 580 bytes. The first function's code begins exactly there, and every other entry lands on a plausible function start when its offset is added to 580, which is what identifies the base.

| Function | Field at `0x1c` | Code offset | Absolute |
| --- | ---: | ---: | ---: |
| `$sel_01` | 2 | 0 | 580 |
| `$sel_02` | 2 | 103 | 683 |
| `$sel_03` | 2 | 179 | 759 |
| `$sel_99` | 2 | 1351 | 1931 |
| `$dummy_func` | 1 | 1435 | 2015 |
| `$main` | 1 | 1755 | 2335 |

The names are scene selectors (`$sel_NN`) plus `$main` and `$dummy_func`; `$sel_99` skips from `$sel_14`, so the numbering is not dense.

## Code

Every function's code begins with the same four bytes, `04 80`, followed by four more that differ per function:

| Function | Bytes at entry |
| --- | --- |
| `$sel_01` | `04 80 0d 01 01 01 04 81` |
| `$sel_02` | `04 80 db 01 01 01 04 81` |
| `$sel_03` | `04 80 74 02 01 01 04 81` |
| `$main` | `01 01 01 40 64 61 74 65 00` |

Text is stored as zero-terminated Shift-JIS immediately after a two-byte opcode, so a dump of printable runs recovers the dialogue without understanding the instruction set. `01.HGO` shows this directly:

```text
04 81 "Play a trick on Imari" 00 01 01 01 10 03 01 01 01 01 02
```

`$main` in the same file opens with `01 01 01` and `@date`, an engine variable rather than dialogue.

## What the public opcode table says, and where it disagrees

`jyxjyx1234/misc_game-chs` publishes a disassembler for another A98SYS title (*Negapoji*) with roughly 150 two-byte opcodes and typed operands: `S` translatable Shift-JIS string, `s` ordinary string, `i`/`I` 32-bit values where `I` is a jump target, `b` byte, `w`/`W` word, `L` string list, `c` nested command. In that table `0481` takes `ScccI` and `0480` takes `I`.

The `0481` reading matches our copy: the bytes after it are a plain string. The `0480` reading does not. Every function in `01.HGO` begins `04 80` followed by values like `0d 01 01 01` and `74 02 01 01`, which are not offsets into a 136,892-byte file under any byte order.

So either `I` is not a plain 32-bit offset, or this build's table differs from the Negapoji one. Until that is settled, opcode semantics stay **unverified** and nothing on this page depends on them.

## Reading the text today

No extractor is published here, because a parser written against an unverified opcode table would produce confident nonsense. What works is a printable-run scan over the HGO member: Shift-JIS dialogue is contiguous, zero-terminated and not compressed, so every line can be listed and indexed by file and offset without decoding a single instruction.

That is enough to read a scene and to build a translation table, and it is not enough to rebuild the file.

## Unknowns

- **What the field at `0x1c` means.** It is 2 for scene functions and 1 for `$main`/`$dummy_func`; a parameter count and a flag are both plausible.
- **How `04 80` encodes its target.** Six bytes appear at every function entry, and the four after the opcode are unexplained.
- **Whether the opcode table is versioned.** `A98SYS Engine Ver.1.000701` is this build; Negapoji's build number is not known here.
- **Where the `A98` variable namespace lives.** `@date` in `$main` uses an `@` prefix that does not appear in the published operand classes.

## Sources

- [jyxjyx1234/misc_game-chs](https://github.com/jyxjyx1234/misc-game-chs) — `HGO_FILE.py` (container and dispatch), `opdict.py` (opcode table), `dump.py` (text extraction). No licence is stated in the repository.
- [RikuKH3/bblack_transkit](https://github.com/RikuKH3/bblack_transkit) — `bblack_hgotext.dpr`, a text injector for this engine driven by a `.tbl` of strings. No licence is stated in the repository.
