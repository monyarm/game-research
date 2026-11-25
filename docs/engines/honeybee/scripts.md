---
title: "HoneyBee — scripts"
description: "The .PAC command stream in Sugar Sugar Rune: 0x25-tagged records with a command word and little-endian operands, the dialogue text command, and the point where a linear walk stops."
type: engine
status: draft
confidence: mixed
tags:
  - playstation-2
  - scripting
  - bytecode
  - shift-jis
sources:
  - title: NovelVM issue #60 — Support Sugar Sugar Rune engine
    url: https://github.com/monyarm/NovelVM/issues/60
platforms:
  - PlayStation 2
games: []
formats: []
maturity: partial
last_verified: 2026-11-25
ai_assisted: true
---

# HoneyBee — scripts

The 45 scene scripts in `DATA_PS2.AFS` are `.PAC` files with **no header**: byte 0 is the first command. Each command is a two-byte tag `0x25`, a two-byte command number, then little-endian operands. The dialogue text is stored inline as NUL-terminated Shift-JIS, which makes the text recoverable even without a full grammar.

The six other `.PAC` files are data tables, not scripts — see [objects and textures](objects.md).

## At a glance

| | |
| --- | --- |
| Container | None; the stream starts at offset 0 |
| Record tag | `25 00` (`u16 0x0025`) |
| Command | `u16`, little-endian, values `0x0000`–`0x0035` seen |
| Operands | little-endian, width per command |
| Text | command `0x0027`, NUL-terminated Shift-JIS |
| Scene scripts | 45 files, 50,168–187,256 bytes |
| Vantage point | `ADVENTURE_MAIN.PAC`, 50,168 bytes |

## Record shape

The first records of `ADVENTURE_MAIN.PAC`:

```text
0000  25 00 0f 00 02 01 00 00 00                       cmd 0x0f: u8 0x02, u32 1
0009  25 00 27 00 81 9f 83 41 83 68 … 00                cmd 0x27: 「オープニングメッセージ」
0027  25 00 02 00 2c 00 00 00                          cmd 0x02: u32 0x2c
002f  25 00 22 00 82 00 00 00 01 c8 00 00 00           cmd 0x22: u32, u8, u32
003d  25 00 20 00 ca 01 00 00 01 b1 04 00 00           cmd 0x20: u32, u8, u32
004b  25 00 20 00 22 01 00 00 01 b0 04 00 00
0059  25 00 20 00 32 01 00 00 01 7d 04 00 00
0077  25 00 02 00 ca 01 00 00
007f  25 00 03 00 7c 2d 00 00                          cmd 0x03: u32 0x2d7c
```

The `0x20` run is the clearest read: three assignments of consecutive destination slots (`0x1ca`, `0x122`, `0x132`) from consecutive source slots (`0x4b1`, `0x4b0`, `0x47d`), i.e. program initialisation. Command `0x03` takes a `u32` that is a plausible absolute offset into the same file, and `0x02` takes a `u32` that is used as an argument in both places it appears.

## Commands read so far

Widths below are the operand byte count after the four-byte header. Where a count is followed by two figures it is "measured with this width / total occurrences of that command", i.e. how consistent the width is.

| Command | Operands | Total len | Seen | Reading |
| --- | --- | ---: | ---: | --- |
| `0x0f` | `u8` type + `u32` | 9 | 417 | Typed constant or parameter |
| `0x27` | NUL-terminated Shift-JIS | variable | — | Dialogue line |
| `0x28` | NUL-terminated ASCII | variable | — | Debug string, e.g. `TIG_ADV_BGD       = `, `　PLACE = TRUE` |
| `0x02` | `u32` | 8 | — | Argument or id |
| `0x03` | `u32` | 8 | — | Offset / jump target |
| `0x20` | `u32`, `u8`, `u32` | 13 | 4,711 / 4,879 | Assign slot |
| `0x22` | `u32`, `u8`, `u32` | 13 | 3,098 / 3,144 | Assign slot, other form |
| `0x1d` | `u8`, `u32` | 9 | 3,546 | Push stack slot |
| `0x1e` | `u8`, `u32` | 9 | 2,026 | Pop stack slot |
| `0x15` | 10 bytes, contains floats | 14 | 18,310 / 18,790 | Vector or colour parameter |
| `0x2b` | 10 bytes | 14 | 72 / 72 | — |
| `0x2e` | 10 bytes | 14 | 43 / 43 | — |
| `0x32` | 1 byte | 5 | 90 / 90 | — |
| `0x11` | 6 bytes | 10 | 537 / 537 | — |
| `0x0b` | 6 bytes | 10 | 119 / 119 | — |
| `0x24` | none | 4 | 1,204 | — |
| `0x1f` | `u32` | 8 | 140 | — |
| `0x04` | 1 byte | 5 | 157 | — |

The last few are reliable because every occurrence of that command in the file has the same width. The high-frequency commands (`0x20`, `0x22`, `0x15`, `0x1d`, `0x1e`) are reliable for the opposite reason: their width is only very slightly less consistent, and the shortfall is explained by false matches inside text.

**Do not trust the naive tokeniser.** A scan that treats every `25 00` in the file as the start of a record reports `cmd 0x0007` 56,307 times and `cmd 0x0001` with three different widths — those are Shift-JIS and ASCII bytes from dialogue, not opcodes. Any opcode histogram from that scan is noise.

## Where a linear walk stops

Walking from byte 0, consuming records by the widths above and taking `0x27`/`0x28` as NUL-terminated strings, the parse reaches **0x457f of 50,168** and stops here:

```text
… 25 00 27 00 <SJIS text> 00
  25 06 1d 00 08 23 00 00 00 02 00 00 00 00 08 24 00 00 00
  25 00 28 00 "TIG_ADV_BGD       = " 00 08 23 00 00 00
  25 00 28 00 "TIG_ADV_MEET_…
```

Two things break the assumption. First, the byte after `0x25` is not always `0x00`: over the whole file it is `0x04` 143 times, `0x06` 98, `0x05` 92, `0x07` 57, `0x03` 57, `0x0b` 48, `0x0c` 36, `0x08` 20, `0x09` 19, `0x01` 4. So the four bytes are better read as a one-byte tag `0x25`, a **group byte**, and then the command word — with `0x04` and `0x06` groups carrying their own command sets. Second, five-byte items of the shape `08 23 00 00 00` appear between records, as if a second, shorter instruction form (one opcode byte plus a `u32`) shares the stream.

Which of those two readings is right is not settled. Neither breaks the text layer: dialogue is still `25 00 27 00` followed by a string, and that is what any extractor should key on first.

## FSM structure

The executable contains `EXECCMD`, `commandEndOperation`, `commandEndGuard`, `commandEnterFSM`, `commandChangeState` and `getGameStartState`, and two of the script names are `DOLL_FSM_01.PAC` … `DOLL_FSM_03.PAC`. So at least the doll scenes are explicit state machines, driven by commands that enter and leave states. The other scene scripts presumably follow the same model. This was read from strings only; no interpreter behaviour was checked.

## Text extraction

Dialogue is recoverable now, without the operand grammar: scan for `25 00 27 00`, read to the next NUL, decode as Shift-JIS. Two cautions, both observed in `ADVENTURE_MAIN.PAC`:

- Command `0x28` also carries NUL-terminated text, but it is ASCII debug output (`TIG_ADV_BGD       = `), not dialogue.
- Some dialogue strings are pure ASCII, and some embed colour and style markers of the form `&S0H24R90G60B60#` … `&/`, so the marker syntax has to be stripped before the text is usable.

No extractor script is published on this page yet. A quickbms extractor belongs here, but writing one before the operand widths are settled would only produce a script that the next grammar revision invalidates.

## Unknowns

- The operand layout of everything not in the table above, including the `0x04` and `0x06` groups.
- Whether `08 23 00 00 00` is a second instruction form or operand data.
- What `0x03` actually does — the value looks like an offset, but no jump was followed.
- The `&`-marker vocabulary (colour is clear from `H0`/`S0`/`R90`/`G60`/`B60`; the rest is not).
- How a scene script references textures, models and voice lines; the `.PAC` files contain no visible resource names.

## Sources

- [NovelVM issue #60](https://github.com/monyarm/NovelVM/issues/60) — tracking issue for a loader.
