---
title: "Decoding the scene containers"
description: "The OOCH scene container in Code Geass: Lost Colors: its header, the bit-flagged LZSS stream it carries, and a quickbms script that decodes every file on the disc."
type: note
status: reviewed
confidence: observed
tags:
  - playstation-portable
  - compression
sources:
  - title: VG Resource thread on OOCH files in Sonic Riders - Zero Gravity
    url: https://www.vg-resource.com/thread-36877.html
  - title: Fuwanovel thread on extracting Code Geass - Lost Colors data files
    url: https://forums.fuwanovel.moe/topic/11468-extracting-psp-game-data-files-code-geass-lost-colors/
  - title: GBAtemp thread on editing Code Geass - Lost Colors files
    url: https://gbatemp.net/threads/help-code-geass-lost-colors-translation.355017/
last_verified: 2026-11-24
ai_assisted: true
---

# Decoding the scene containers

`OOCH` is the compressed form of the plain [`pack`](archives.md) container. It carries a fixed `0x800`-byte header, and after it a bit stream that expands to a `pack` file of the size the header declares. The scheme is a byte-oriented LZSS with 8-bit distance and 8-bit length fields, and every one of the 1,454 `OOCH` files on the inspected disc decodes with it.

## At a glance

| | |
| --- | --- |
| Magic | `OOCH` at offset `0x00` |
| Header size | `0x800`, one sector |
| Payload | Starts at `0x800`, length is the file size minus `0x800` |
| Decoded size | `u32` at `0x0c` |
| Decoded form | A `pack` container, starting with the `pack` magic |
| Method | LZSS, 1 flag bit, 8-bit distance, 8-bit length, MSB-first |
| Sample | `USRDIR/root/000J.P`, 3,187 bytes to 25,872 |
| Extractor | [quickbms script](#extracting-it), below |

## Header

Offsets are file offsets. In the executable, this image maps virtual address `0xed7c0` to file offset `0xed814`, a `0x54`-byte gap, so a reference search has to pick one basis and stay on it.

| Offset | Type | Value | Meaning |
| --- | --- | --- | --- |
| `0x00` | `char[4]` | `OOCH` | Magic |
| `0x04` | `u32` | `0x08000001` | Type word; plain `pack` files carry `0x00020001` |
| `0x06` | `u16` | `0x0800` | Payload offset within the header sector |
| `0x08` | `u32` | file size − `0x800` | Packed payload size |
| `0x0c` | `u32` | varies | Decoded size |
| `0x10` | `u16` | `0x18` | Offset of the per-stream flag array |
| `0x12` | `u16` | `0x1c` | Offset of the per-stream width-pair offsets |
| `0x14` | `u8` | `1` | Number of codec streams |
| `0x18` | `u32` | `0` | Flags entry for the single stream |
| `0x1c` | `u32` | `32` | Offset of the first stream's width pair, i.e. `0x20` |
| `0x20` | `u32` | `8` | Distance field width in bits |
| `0x24` | `u32` | `8` | Length field width in bits |

Every field above except `0x08` and `0x0c` is identical in all 1,454 files, so the disc uses one compressor setting throughout. `u16` at `0x06` is where the payload begins; it reads `0x800` everywhere here, which is why the payload always starts on the sector boundary.

The initialiser does not read the widths from `0x1c`; it reads an **offset** from there and follows it. Its walk is `piVar6 = header + u16@0x12`, then per stream `uVar3 = *(u32 *)(header + *piVar6)`, `uVar5 = ((u32 *)(header + *piVar6))[1]`, with `piVar6` advancing one word per stream. With `0x1c` holding `0x20`, the two widths therefore come from `0x20` and `0x24`, both `8` — which is what the decoder needs. The same routine derives the masks (`0xff` for each), the input bytes per token (`(8 + 8 + 8) >> 3` = 3) and the longest token (17 bits), and only one codec class is reachable, the one at `0x127c7c`.

The loader picks the decoder by comparing the container's first word with the `OOCH` string, not by testing the type word: the routine at file offset `0x2d704` loads the word at file offset `0xed814` and compares it, with `0x2e480` doing the same for `pack` at `0xed81c`. Both loads are `$gp`-relative (`lui v0, 0xf; lw v0, -0x27ec(v0)`), which is why a search for absolute `lui` + `addiu` or `lui` + `ori` addressing finds no reference to either magic.

## The payload stream

The stream starts at `0x800` and is read **most significant bit first** within each byte. It is a flag bit followed by a token:

- flag `0` — literal: the next 8 bits are a byte, appended to the output.
- flag `1` — match: the next 8 bits are a distance, the next 8 bits after that a length, and `length` bytes are copied from `distance` bytes back in the output. **Neither field has a bias** — the distance is not `distance + 1` and the length is not `length + 3`.

Decoding stops when the output reaches the declared size at `0x0c`.

The first six tokens of `000J.P` show the grammar directly, because they spell the output's own magic:

| Bits consumed | Flag | Token | Output |
| --- | --- | --- | --- |
| `0` | `0` | literal `0111 0000` | `70` `p` |
| `0` | `0` | literal `0110 0001` | `61` `a` |
| `0` | `0` | literal `0110 0011` | `63` `c` |
| `0` | `0` | literal `0110 1011` | `6b` `k` |
| `0` | `0` | literal `0000 0001` | `01` |
| `0` | `0` | literal `0000 0000` | `00` |

The first four tokens consume `0x38 0x18 0x4c 0x66 0xb0 0x08` at one bit of flag per byte, which is why the payload prologue `38 18 4c 66` looks constant across every file in the container family: it is the first four literal bytes of `pack`, not a signature.

## Extracting it

```quickbms
# Code Geass: Lost Colors (PSP) - OOCH container decoder
#
# OOCH is the compressed form of the plain "pack" container. Structure:
#   0x00  char[4]  "OOCH"
#   0x04  u32      type word, 0x08000001
#   0x08  u32      packed payload size
#   0x0c  u32      decoded size
#   0x10  u16      offset of the per-stream flag array
#   0x12  u16      offset of the bit-width parameter pairs
#   0x14  u8       number of codec streams (1 on the inspected disc)
#   0x800          payload, an LZSS bit stream
#
# Bit stream, MSB first:
#   0 bit -> 8 raw bits, a literal byte
#   1 bit -> 8 bits distance, 8 bits length, copy that many bytes from
#            distance bytes back in the output (no bias on either field)
# Decoding stops at the decoded size declared at 0x0c.
#
# Usage: quickbms cls-ooch.bms 000J.P   -> writes 000J.P.pack
# Verified against all 1,454 OOCH files of the inspected disc: every
# output reaches the declared size and begins with the "pack" magic.

endian little

idstring "OOCH"

get TYPEWORD long      # 0x04
get PACKEDSIZE long    # 0x08
get DECODEDSIZE long   # 0x0c
get FLAGSOFF short     # 0x10
get PARAMOFF short     # 0x12
get NSTREAMS byte      # 0x14

goto 0x800
# getbits reads the bits MSB first only in big endian mode, and the header
# integers above are little endian, so switch after reading them.
endian big

log MEMORY_FILE 0 0    # empty output buffer

For POS = 0 < DECODEDSIZE
    getbits FLAG 1
    if FLAG == 0
        getbits VAL 8
        goto POS MEMORY_FILE
        put VAL byte MEMORY_FILE
        math POS += 1
    else
        getbits DIST 8
        getbits LEN 8
        math SRC = POS
        math SRC -= DIST
        For I = 0 < LEN
            math TMP = SRC
            math TMP += I
            goto TMP MEMORY_FILE
            get VAL byte MEMORY_FILE
            math TMP2 = POS
            math TMP2 += I
            goto TMP2 MEMORY_FILE
            put VAL byte MEMORY_FILE
        Next I
        math POS += LEN
    endif
Next

get SIZE asize MEMORY_FILE
print "decoded %SIZE% bytes (declared %DECODEDSIZE%)"

get NAME filename
string NAME += ".pack"
log NAME 0 DECODEDSIZE MEMORY_FILE
```

Run it as `quickbms -o cls-ooch.bms 000J.P`, keeping the input on standard input (`< /dev/null`) so an unrecognised command cannot wait for a reply.

## Evidence

The decode was checked by walking the whole disc tree, decoding every `OOCH` file and comparing the output length with the declared size and the first four output bytes with `pack`:

| Check | Result |
| --- | --- |
| `OOCH` files found | 1,454 of 2,816 files |
| Decoded to the declared size and starting with `pack` | 1,454 |
| Failures | 0 |
| Smallest, `K995J.P` | 2,272 bytes to 3,344 |
| `000J.P` | 3,187 bytes to 25,872 |
| Median, `BG_D01D.P` | 39,968 bytes to 65,520 |
| Largest, `OMKALLJ.P` | 1,949,930 bytes to 4,431,392 |

The quickbms script reproduces the byte-identical output of the reference decoder on `000J.P` and decodes `OMKALLJ.P` in eight seconds.

Two variants are close enough to be traps: adding one to the distance still reaches the declared size for `000J.P` but decodes to `01 00 01 00 …` instead of content, and any bias on the length desynchronises the literal stream within the first few tokens. A size match alone is not proof; the `pack` magic and the header's own fields are.

## The container is not unique to this game

`OOCH` is shared middleware rather than something written for *Lost Colors*. A public thread about *Sonic Riders: Zero Gravity* on PlayStation 2 and Wii describes the same magic and the same `38 18 4c 66` payload prologue, and that game ships an `OOCH` file beside a plain `.P` of the same kind. Nothing in this page's method depends on *Lost Colors* specifically, but the parameters above were measured on one disc and one compressor setting.

## What was tried before

The decode was found by static analysis, after a long series of guesses at the payload. The negative results are kept because they narrow what the format is not:

| Attempt | Result |
| --- | --- |
| zlib and raw deflate, window bits 15 / 31 / −15, payload offsets 0, 2, 4, 8, 16, 32 | No stream decoded |
| LZMA, alone and with the standard headers | No stream decoded |
| bzip2 | No stream decoded |
| LZSS, flag word 8/16/32 bits, MSB- and LSB-first, offset field 8/12/16 bits, length field 3/4/5/8 bits, length bias 1/2/3, window 2,048–32,768 | 96 combinations, none reached the declared size |
| Socio Art Logic method/length codec (from the *Zero no Tsukaima* games) | Decodes to 2,642 bytes at 54 % printable; wrong |

The LZSS sweep came within one parameter of the answer. It covered both field widths at 8 bits, but only in variants that bias the distance or the length, and this format biases neither; several sets decoded two or three plausible tokens and then hit a zero distance after 19–30 bytes, which is exactly how a one-byte skew behaves. The lesson is in the ordering rather than the search: the executable is plaintext, and reading the decoder took less time than the sweep did.

## What is still open

1. **Multiple streams.** The header allows one flag entry and a pair of parameters per stream, and the disc only ever uses one. Two or more streams are unexercised, so their order and interleaving are unknown.
2. **The DMA path.** The loader has a second decoder class selected by a mode field, used with a separate DMA buffer. Every file here takes the normal path, so the alternative is unread until a file selects it.

## Sources

- [VG Resource thread on OOCH files in Sonic Riders - Zero Gravity](https://www.vg-resource.com/thread-36877.html) — the shared container, the constant prologue, and the plain-versus-`OOCH` pairing.
- [Fuwanovel thread on extracting Code Geass - Lost Colors data files](https://forums.fuwanovel.moe/topic/11468-extracting-psp-game-data-files-code-geass-lost-colors/) — the in-memory plugin, the unpacker's limits, and the observation that no text encoding appears in RAM.
- [GBAtemp thread on editing Code Geass - Lost Colors files](https://gbatemp.net/threads/help-code-geass-lost-colors-translation.355017/) — independent confirmation that the `OOCH` payloads are not zlib.
