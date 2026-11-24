---
name: re-disc-survey
description: Survey an unknown game disc or data format without repeating the traps already hit in this repository — false text runs, premature codec names, quickbms syntax, invented releases. Use when starting or continuing reverse-engineering work on a title, container or codec.
---

# Disc survey

Method and failure modes proven on this repository's titles. The method is cheap; the traps are what cost days.

## Order of operations

1. Inventory the tree: file counts, sizes, extensions, directory names.
2. Hash the samples you will cite with `tools/sample-hashes.py` — size plus MD5 of the first 5,000 bytes plus SHA-256, never hand-typed.
3. Read the executable. A plaintext ELF tells you more per hour than any data file.
4. Map the containers.
5. Look for text last, and only with a scanner you trust.

## Text scanning

A permissive Shift-JIS or UTF-8 regex over binary produces thousands of runs and all of them are noise — compressed pixels and 4-byte interleaves both pass a naive double-byte test. Two of this repository's files scored thousands of "runs" and contain no text at all.

Use a strict scanner: only runs of 3+ consecutive valid double-byte characters, no ASCII inside the run, and a filter requiring a minimum fraction of hiragana or katakana. Report the run count *and* the longest run; a real script lines up in short authored lines, which is itself a signal (this repository's dialogue caps at 20 full-width characters because it is pre-wrapped at 20).

Never cite a scan as evidence of text until you have read a decoded run and it makes sense.

## Format claims

A format claim needs a structural test, not a plausibility argument:

- arithmetic closes: `header + width * height == filesize`
- a declared size in the header is reproduced by the decoded output
- a magic string matches a sibling file the same engine left uncompressed

If none of those hold, the section is unknown, and the page says so.

## Codecs

Do not name a codec before a decoder reproduces the declared size on a real sample. "Probably LZSS" is a guess with a name attached, and it will be wrong.

Corollary: do not run a codec borrowed from a *different* engine over an unidentified payload. A failure says nothing and a success is uninterpretable. Establish who owns the format first — shared magic in another title, a middleware string in the binary, a documented library — and only then sweep parameters.

Cheap statistics separate compression from encryption before any decoder attempt: on a small payload, an encrypted stream shows roughly 250+ distinct byte values and near-zero zeros; a compressed stream shows noticeably fewer distinct values and a few percent zeros.

## Executable analysis lanes

Read the ELF header before choosing a lane (`readelf -h`). `e_type` decides most of it.

**PSP (Allegrex).** Decrypt first — a PPSSPP dump, not the shipped `EBOOT.BIN`; a file starting `~PSP` is still encrypted. REA can analyse it, but only as a static `ET_EXEC` with a parsed `.MIPS.abiflags` record: `pspfix.py in.bin out.bin` patches both. Then `open_binary` → `binary_overview`, and it runs Ghidra with `Allegrex:LE:32:default`, image base 0, so addresses equal file offsets. `search_strings` returns nothing on these targets — use `search_bytes` with a hex pattern.

**PS2 (Emotion Engine, r5900).** A retail executable is already `ET_EXEC` with `e_flags 0x20920001`, so no patching. REA refuses it — its provider allowlist admits the PSP variant only, and adding a Ghidra module does not change that. Use Ghidra headless directly from the tree that has the Emotion Engine module baked in:

```sh
EE=$PWD/.gc-roots/ghidra-ee/lib/ghidra
export JAVA_HOME=$PWD/.gc-roots/jdk
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
"$JAVA_HOME/bin/java" -Xmx2G -Djava.awt.headless=true \
  -Djava.system.class.loader=ghidra.GhidraClassLoader \
  -cp "$EE/Ghidra/Framework/Utility/lib/Utility.jar" ghidra.Ghidra \
  ghidra.app.util.headless.AnalyzeHeadless <proj> <name> \
  -import <elf> -processor r5900:LE:32:default [-noanalysis] [-postScript …]
```

`support/analyzeHeadless` from that tree is not usable: it resolves its install directory back to the plain Ghidra in the store, so the extension is never scanned ("Unsupported language"). The java command above is the only form that loads it. Two facts to record from the import log: `_mips_gp0_value` (the program's global pointer; gp-relative data refs resolve against it) and any section it skips without warning.

Extensions ship as a zip and may contain no compiled `.sla`; Ghidra needs one. Compile with `<install>/support/sleigh -a <module>/data/languages`, then rebuild the tree.

## Try the section container first

Many of these engines lay files out as: `u32 table size`, ascending `u32` absolute offsets, last entry equal to the file size as a sentinel, zero padding to the table size, then the sections back to back. If the first word is small and the last word of the run equals the file size, that is the container. Check for nesting — a section may itself be a container.

## quickbms

Installed at `/etc/profiles/per-user/monyarm/bin/quickbms`, version 0.12.0. Its manual is at `https://aluigi.altervista.org/papers/quickbms.txt`; read it instead of guessing. Traps that have already cost time:

- No `While … EndWhile`. Use `Do … While` or `For … Next`.
- `Next` alone never increments the loop variable — the increment must be spelled out. A bare `For` spins on one value forever.
- `set` does not assign numbers. Use `math`.
- `If` takes a single `VAR COND VAR`; there is no `&&`/`||`. Nest.
- `log MEMORY_FILE` overwrites instead of appending.
- An unknown command or a bad `print`/`string` format makes quickbms wait on stdin forever. Always run with `< /dev/null` and a timeout.
- `log` moves the file pointer, so re-`goto` at the top of every loop iteration.

## Scope discipline

- Describe the copy that was inspected. Do not mention another platform, port or edition unless a source shows it exists, and do not claim exclusivity either.
- One inspected disc is not evidence about the rest of a studio's catalogue.
- Report findings and wait for direction before writing pages, unless told otherwise.
