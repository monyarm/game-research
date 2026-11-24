---
title: Open questions
description: "What is still not established on each engine page, and what evidence would close it."
type: note
status: draft
confidence: mixed
tags:
  - methodology
sources: []
last_verified: 2026-11-24
ai_assisted: true
---

# Open questions

Each engine page ends with its own list of what is unread. This page collects the gaps that are still open, so a later session can start from the state of the evidence instead of re-deriving it. Every row names what is known, and what would settle it.

Nothing here is a plan. A row closes when a check produces evidence, and then the finding moves onto the engine page.

## CLS

*Code Geass: Lost Colors*, PSP. The executable, the `OOCH` codec, the `pack` layout and the scene text are documented.

| Open | What is known | What would close it |
| --- | --- | --- |
| The attribute word in front of every glyph | Each text cell is a `u16` attribute then a `u16` glyph index. The attribute is `0` on almost all of the 29,461 lines, `1` and `9` on a scattered minority. | The renderer that consumes the records, or a recorded playthrough aligned to the decoded lines. |
| The per-glyph metric fields | `FONTDATF` holds three `u32` per glyph outside the codepoint and index, all small integers. Their meaning is unread. | Drawing one glyph from the atlas with the fields applied and comparing against the shipped frame. |
| The constant `101` | Both font blocks carry `u16 101` at `0x0c` in all 646 files, while glyph counts vary from 107 to 297, so it is not the glyph count. | A file where the value differs, or the loader that reads the field. |
| Scene id to file name | `root/` and `ScStr/` hold the same families (`A###`, `F###`, `G###`, `J###`, `K###`, `BTL###`, `OP`, `OMKALL`) under different prefixes. | The join between a scene container and its `ScStr` file. |
| The records inside the scene containers | A `00 01 50 53 50` block of 16-byte records, 96 % zeros, with an ascending offset table. No text in them. | The loader that opens those blocks. |
| `OOCH` with more than one stream | The header carries a stream count and a flag array; every inspected file has one stream. | A file with a count above one. |
| The DMA decoder path | Reached when a field at offset `0xa4` of the streaming reader equals 3, backed by its own buffer. No inspected file takes the branch. | A file that reaches it, or the code path read statically. |

## TB_D3P

*Tiger & Bunny — Hero's Day*, PSP. Containers, textures, the dialogue in `PHASE/BIN` and the instruction widths of `EVENT/*.EVT` are documented.

| Open | What is known | What would close it |
| --- | --- | --- |
| What each event instruction does | All eleven chapter files walk to their last table boundary with no unknown opcode, 584 records, and the widths are recorded. The operands are not interpreted. | Correlating instructions with observable behaviour in a running game, or the interpreter's dispatch table. |
| Why `0x13` sometimes carries a second word | Ten bytes when the trailing word is an in-file address landing on an instruction start (725 of 726 sites), six otherwise (663 of 697 have no plausible second word). The rule that decides it is not established. | The interpreter, or a file whose instruction boundaries disagree with the rule. |
| Whether the parse is unique | The width table is consistent across all eleven files, but `0x00` absorbs any position, and a degenerate all-one-byte table also fits. | The interpreter. |
| What a `0x80` record is | The table at `0x80` lists entry offsets into the bytecode, one record per entry, and the first entry is the code start. Whether a record is a scene, a branch group or a label block is open. | Reading one record against the game's own progression. |
| The two non-offset words in `CH00_00.EVT` | After two real offsets the table holds `0x0` and `0x8c`; the other inspected chapter files do not have this shape. | Another file with the same shape, or `CH00_00.EVT`'s role (a template or a real chapter). |
| Whether `01 <u32>` operands are offsets or node ids | They always land inside the file and usually on an instruction start, which fits both readings. | The interpreter. |
| How the `EVENT` files are opened | `EVENT`, `.EVT` and `EVT` do not occur anywhere in the executable, so the files are not opened by a literal name built at runtime. | The directory walk or index that reaches them. |

## Soalo

*Zero no Tsukaima* on PS2, with *Kazeiro Surf* and *GA Geijutsuka* sharing the library. The packaging, the record pairs, the textures and the Squirrel binding are documented.

| Open | What is known | What would close it |
| --- | --- | --- |
| How `.ks` slot names relate to `SCENE_ID` record numbers | The two name sets coincide: 596 of the 600 Symphony records share a stem with a `.ks` name in `SYSTEM`, and the four that do not are staff or check scenes. But the names live in `SYSTEM` record 33 (`DataMake/SCENE/scenes.nut`) as 600 bare strings with no index beside them, in a different order from the container, and Concerto's source names no scene at all — only numbers. | The build toolchain, or a runtime trace of a scene load. |
| The `.ks` grammar | Only the name table is visible; the dialect is described nowhere in the data, and the scene modules that survive are Squirrel source or compiled Squirrel. | A script that survives round-tripping, or the Squirrel side that reads it. |
| What the compiled scene and library modules contain | Every `SCENE_ID` record and the `SYSTEM` closure units are stock Squirrel closure streams opening `FA FA 52 49 51 53 01`, each with a `TRAP` slot label and one length-prefixed build path. The bodies are compiled. | Walking the closure stream, or dumping a loaded module from a running copy. |
| The words in the constant `SOUND_ID` header record | Record 0 is empty and record 1 is the same 20 bytes on all three discs: `00000000 12ac0000 01000000 00100000 00000000`. | Reading them against the audio banks they precede. |
| Who wrote the script control layer | Socio Art Logic credits Concerto as "adventure library development excluding script control", and the Squirrel binding is the most distinctive part of the engine. | Credits research on the trilogy. |

## Flash runtime

*Scooby-Doo! Case File #3*, Windows. The SWF set and its Ruffle behaviour are documented; the gaps are playtest records rather than format questions.

| Open | What is known | What would close it |
| --- | --- | --- |
| A written playtest record | The set runs in Ruffle, and that is recorded as a result, not as a session log. | A dated run with the Ruffle version and platform. |
| The launch path | The projector's first SWF is not recorded. | Opening the disc's launcher once and noting the first file loaded. |
| Whether the 117 SWFs are the whole set | The inspected copy holds 117 v8/AVM1 SWFs; whether content loads from elsewhere is unchecked. | Watching for loads by relative path during a run. |
| Visible defects | None recorded. | A run with timestamps or scene descriptions. |
