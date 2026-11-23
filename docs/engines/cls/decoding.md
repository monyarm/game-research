---
title: "Decoding the scene containers"
description: "Why the OOCH payload stream in Code Geass: Lost Colors is still undecoded, what was tried, and where the answer has to come from."
type: note
status: draft
confidence: mixed
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
last_verified: 2026-11-23
ai_assisted: true
---

# Decoding the scene containers

This page records an unsolved problem rather than a format. The 1,454 `OOCH` files hold the game's scenes, their payloads are compressed, and nothing in the standard decoder set opens them.

No extractor is offered here on purpose. A quickbms script cannot be written against a compression scheme that is not known yet, and guessing one would only add a script that fails silently.

## The test case

`USRDIR/root/000J.P` is a small, representative sample:

| Field | Value |
| --- | ---: |
| File size | 3,187 bytes |
| Payload offset | `0x800` |
| Payload size | 1,139 bytes |
| Declared decoded size (`0x0c`) | 25,872 bytes |

The payload begins:

```text
38 18 4c 66 b0 08 00 04 00 00 80 20 20 8d 00 38 82 10 06
10 32 c3 41 60 a0 c0 12 81 4c a1 …
```

Two structural facts constrain the answer. First, the payload is compressed rather than encrypted: 204 distinct byte values in 1,139 bytes and 4 % zeros is far from the flat distribution a cipher produces, so a real entropy coder is at work. Second, it is not zlib or deflate at any of six plausible payload offsets, so the container carries its own scheme.

## What was tried

| Attempt | Result |
| --- | --- |
| zlib and raw deflate, window bits 15 / 31 / −15, payload offsets 0, 2, 4, 8, 16, 32 | No stream decoded |
| LZMA, alone and with the standard headers | No stream decoded |
| bzip2 | No stream decoded |
| LZSS, flag word 8/16/32 bits, MSB- and LSB-first, offset field 8/12/16 bits, length field 3/4/5/8 bits, length bias 1/2/3, window 2,048–32,768 | 96 combinations, none reached the declared size |
| 8-bit offset/length LZSS variant | No |
| Socio Art Logic method/length codec (from the *Zero no Tsukaima* games) | Decodes to 2,642 bytes at 54 % printable; wrong |

The LZSS sweep is the informative failure. Several parameter sets decode the first two or three tokens plausibly and then hit a zero offset, which stops the loop after 19–30 bytes. That pattern means the flag stream is being read with the wrong polarity or the wrong width — or that the stream is not flag-bit coded at all, and the first bytes are a parameter block rather than a token stream.

## The container is not unique to this game

`OOCH` is shared middleware rather than something written for *Lost Colors*. A public thread about *Sonic Riders: Zero Gravity* on PlayStation 2 and Wii describes the same four-byte container header, the same `OOCH` magic, and — the useful part — a payload prologue that "always starts with" `38 18 4c 66`. That is the same four bytes as the sample above, in a game from a different studio, running a different engine.

The same thread supplies the structural key: that game ships both an `OOCH` file and a plain file of the same extension, and the author expected a decoded `OOCH` to turn out to be "a standard pack file". *Lost Colors* has exactly the same split — 1,454 `OOCH` files and 520 plain `pack` files in the same folder — so `OOCH` is the compressed form of the `pack` container documented on the [archives](archives.md) page, not a separate archive family.

That gives the decode a structural test. A successful decode of an `OOCH` file should begin with the `pack` magic and a block table, whatever the payload bytes look like in the middle. No amount of text-printability scoring can substitute for that check, and it is the reason the failed attempts above can be judged wrong rather than merely unhelpful.

No decoder exists in public. Searching GitHub for the container name, for the game, and for the game-specific unpacker named in the 2015 thread returns nothing usable: the name appears only in that thread, and no repository implements the format.

## What the executable says

The executable is plaintext, so the decoder can be read rather than guessed. Three findings narrow the search.

**The string addresses were recorded wrongly at first.** The `OOCH` and `pack` strings sit in `.data` at virtual addresses `0xed7c0` and `0xed7c8` — eight bytes apart, in the same string pool. An earlier revision of this page gave `0xed814` and `0xed81c`, which is the file offset rather than the virtual address; `.data` has a `0x54`-byte gap between the two. This is corrected here, and it matters because every reference search was run against the wrong address first.

**Neither string is referenced.** Searching `.text` for the absolute form of either address (`lui` + `addiu`, `lui` + `ori`, and a `u32` compare against `'OOCH'` or `'pack'`) finds nothing. Resolving the global pointer does not help either: Metrowerks C for MIPS addresses small data through `$gp`, which in this binary is `0xf57fc`, and that resolves 2,351 data references across `.text` — but none of them lands on `0xed7c0` or `0xed7c8`. Nor does any word in `.data` point at either string. So the container is not dispatched by comparing its magic; it is dispatched on a header field, most likely the type word at `0x04` (`0x08000001` in the `OOCH` files, `0x00020001` in the plain packs). String-driven disassembly is a dead end.

**The header carries the parameters.** The fields at `0x14` through `0x24` (1, 0, 32, 8, 8) are identical in all 1,454 files while the payloads differ wildly. They are almost certainly the decoder's parameters, and the function that consumes them is the shortest path to the format.

## Where the answer has to come from

Two routes remain open, and both need more work than has been done here.

1. **Follow the header field, not the string.** Locate the code that reads the type word at `0x04` and walk forward to the routine that consumes the parameters at `0x14`–`0x24`. This is static work on a stripped binary with no symbol table, so it depends on tracing register flow from the file loader rather than on names.
2. **Observe it at runtime.** A 2015 fan-translation thread records that the previous project patched the text in memory through an emulator plugin rather than by decoding the files, which proves the plaintext exists in RAM at the right moment. A debugger breakpoint on the payload reader would show both the transform and the decoded buffer, and would settle the question faster than further static reading.

## What would count as done

The page becomes a format description once three things hold: a decoder reproduces the declared size at `0x0c` for a sample; the decoded output begins with the `pack` magic and a plausible block table; and the same decoder reproduces both for containers of very different sizes.

## Sources

- [VG Resource thread on OOCH files in Sonic Riders - Zero Gravity](https://www.vg-resource.com/thread-36877.html) — the shared container, the constant prologue, and the plain-versus-`OOCH` pairing.
- [Fuwanovel thread on extracting Code Geass - Lost Colors data files](https://forums.fuwanovel.moe/topic/11468-extracting-psp-game-data-files-code-geass-lost-colors/) — the in-memory plugin, the unpacker's limits, and the observation that no text encoding appears in RAM.
- [GBAtemp thread on editing Code Geass - Lost Colors files](https://gbatemp.net/threads/help-code-geass-lost-colors-translation.355017/) — independent confirmation that the `OOCH` payloads are not zlib.
