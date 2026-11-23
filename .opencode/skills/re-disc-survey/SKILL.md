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
