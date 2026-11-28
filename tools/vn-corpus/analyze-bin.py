#!/usr/bin/env python3
"""Section-level size analysis for shipped VN executables.

Emits one CSV row per file: format, total bytes, code bytes (executable
sections), rodata/data/bss bytes, and which middleware/SDK banners were seen.

Usage: analyze-bin.py OUT.csv FILE [FILE...]
"""
import csv
import os
import re
import subprocess
import sys

SIGNALS = [
    # (bucket, label, needle)
    ("middleware", "CRI ADX", b"CRI ADX"),
    ("middleware", "CRI Sofdec", b"CRI SFD"),
    ("middleware", "CRI MPEG", b"CRI MPV"),
    ("middleware", "CRI M2V", b"CRI M2V"),
    ("middleware", "CRI MPS", b"CRI MPS"),
    ("middleware", "CRI CFG", b"CRI CFG"),
    ("middleware", "CRI CFT", b"CRI CFT"),
    ("middleware", "CRI SFH", b"CRI SFH"),
    ("middleware", "CRIWARE", b"CRIWARE"),
    ("middleware", "Sofdec2", b"Sofdec2"),
    ("middleware", "Bink", b"Bink Video"),
    ("middleware", "Bink2", b"BINK2"),
    ("middleware", "Scaleform", b"GFxMovieView"),
    ("middleware", "Scaleform2", b"Scaleform"),
    ("middleware", "FMOD", b"FMOD Sound System"),
    ("middleware", "Wwise", b"AK::SoundEngine"),
    ("third-party", "Squirrel", b"SquirrelError"),
    ("third-party", "Lua", b"$LuaVersion"),
    ("third-party", "zlib", b"inflate 1.2"),
    ("third-party", "libpng", b"libpng version"),
    ("third-party", "libjpeg", b"Independent JPEG Group"),
    ("third-party", "libvorbis", b"Xiph.Org libVorbis"),
    ("third-party", "libogg", b"libogg"),
    ("third-party", "FFmpeg", b"FFmpeg version"),
    ("third-party", "FreeType", b"The FreeType Project"),
    ("third-party", "SDL", b"Simple DirectMedia Layer"),
    ("third-party", "imgui", b"Dear ImGui"),
    ("sdk", "PS2 SDK", b"Sony Computer Entertainment"),
    ("sdk", "PS2 libpad", b"libpad: "),
    ("sdk", "PS2 libmc", b"libmc: "),
    ("sdk", "PS2 libdma", b"libdma: "),
    ("sdk", "PSP SDK", b"PSPSDK"),
    ("sdk", "PSP sceGu", b"sceGuInit"),
    ("crt", "MSVC CRT", b"Microsoft Visual C++ Runtime Library"),
    ("crt", "MinGW", b"__gxx_personality_v0"),
    ("crt", "Borland", b"Borland C++"),
]


SHT_PROGBITS, SHT_NOBITS = 1, 8
SHF_WRITE, SHF_ALLOC, SHF_EXEC = 0x1, 0x2, 0x4


def elf_sections(path):
    """Parse the ELF section header table directly: (name, type, size, flags).

    Done by hand because stripped PSP/PS2 PRX-style ELFs have empty section
    names, which makes column-based parsing of `readelf -S` ambiguous.
    """
    import struct
    with open(path, "rb") as f:
        data = f.read()
    if data[4] == 1:
        shoff, shentsize, shnum, shstrndx = (
            struct.unpack_from("<I", data, 0x20)[0],
            struct.unpack_from("<H", data, 0x2E)[0],
            struct.unpack_from("<H", data, 0x30)[0],
            struct.unpack_from("<H", data, 0x32)[0],
        )
        fmt = "<IIIIIIIIII"
    else:
        shoff, shentsize, shnum, shstrndx = (
            struct.unpack_from("<Q", data, 0x28)[0],
            struct.unpack_from("<H", data, 0x3A)[0],
            struct.unpack_from("<H", data, 0x3C)[0],
            struct.unpack_from("<H", data, 0x3E)[0],
        )
        fmt = "<IIQQQQIIQQ"
    if shnum == 0:  # extended numbering: real count lives in section 0
        shnum = struct.unpack_from(fmt, data, shoff)[5]
    stroff = 0
    if shstrndx < shnum:
        stroff = struct.unpack_from(fmt, data, shoff + shstrndx * shentsize)[4]
    secs = []
    for i in range(shnum):
        nameoff, stype, flags, addr, off, size = struct.unpack_from(
            fmt, data, shoff + i * shentsize)[:6]
        name = ""
        if stroff and nameoff:
            end = data.find(b"\0", stroff + nameoff)
            name = data[stroff + nameoff:end].decode("latin-1", "replace")
        secs.append((name, stype, size, flags))
    return secs


def pe_sections(path):
    """Parse the PE section table directly: (name, raw_size, virt_size, is_code)."""
    import struct
    with open(path, "rb") as f:
        data = f.read(4096)
        f.seek(0)
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    with open(path, "rb") as f:
        f.seek(e_lfanew)
        hdr = f.read(24)
        nsec = struct.unpack_from("<H", hdr, 6)[0]
        opt_size = struct.unpack_from("<H", hdr, 20)[0]
        f.seek(e_lfanew + 24 + opt_size)
        table = f.read(40 * nsec)
    secs = []
    for i in range(nsec):
        raw = table[i * 40:(i + 1) * 40]
        name = raw[:8].rstrip(b"\0").decode("latin-1")
        vsize, vaddr, rsize, roff = struct.unpack_from("<IIII", raw, 8)
        chars = struct.unpack_from("<I", raw, 36)[0]
        secs.append((name, rsize, vsize, bool(chars & 0x20)))
    return secs


def pe_imports(path):
    out = subprocess.run(["objdump", "-p", path], capture_output=True, text=True).stdout
    dlls = re.findall(r"DLL Name:\s*(\S+)", out)
    return sorted(set(dlls))


def scan_signals(path):
    hits = []
    with open(path, "rb") as f:
        data = f.read()
    for bucket, label, needle in SIGNALS:
        if needle in data:
            hits.append(f"{bucket}:{label}")
    return hits


def analyze(path):
    with open(path, "rb") as f:
        magic = f.read(4)
    row = {"file": path, "format": "", "total": os.path.getsize(path),
           "code": "", "text": "", "rodata": "", "data": "", "bss": "",
           "imports": "", "signals": ""}
    if magic == b"\x7fELF":
        secs = elf_sections(path)
        row["format"] = "ELF"
        row["code"] = sum(s for _, t, s, fl in secs if t == SHT_PROGBITS and fl & SHF_EXEC)
        if not row["text"]:
            row["text"] = max([s for _, t, s, fl in secs
                               if t == SHT_PROGBITS and fl & SHF_EXEC] or [0])
        for n, t, s, fl in secs:
            if n == ".text":
                row["text"] = s
            elif n == ".rodata":
                row["rodata"] = s
            elif n == ".data":
                row["data"] = s
            elif n == ".bss":
                row["bss"] = s
        # unnamed sections: infer by flags
        if not row["rodata"]:
            row["rodata"] = sum(s for n, t, s, fl in secs
                                if not n and t == SHT_PROGBITS and fl & SHF_ALLOC
                                and not fl & SHF_WRITE and not fl & SHF_EXEC)
        if not row["data"]:
            row["data"] = sum(s for n, t, s, fl in secs
                              if not n and t == SHT_PROGBITS and fl & SHF_ALLOC and fl & SHF_WRITE
                              and not fl & SHF_EXEC)
        if not row["bss"]:
            row["bss"] = sum(s for n, t, s, fl in secs
                             if not n and t == SHT_NOBITS and fl & SHF_ALLOC)
    elif magic[:2] == b"MZ":
        secs = pe_sections(path)
        row["format"] = "PE"
        row["code"] = sum(r for _, r, v, c in secs if c)
        for n, r, v, c in secs:
            if n == ".text":
                row["text"] = r
            elif n == ".rdata":
                row["rodata"] = r
            elif n == ".data":
                row["data"] = r
            elif n == ".bss":
                row["bss"] = v
    elif magic == b"~PSP":
        row["format"] = "~PSP(encrypted)"
    else:
        row["format"] = "other:" + magic.hex()
    row["signals"] = ";".join(scan_signals(path))
    if row["format"] == "PE":
        row["imports"] = ";".join(pe_imports(path))
    return row


def main():
    out_path, files = sys.argv[1], sys.argv[2:]
    rows = [analyze(p) for p in files]
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(f"{r['total']:>10} {str(r['code']):>9} {r['format']:<16} {r['file']}")


if __name__ == "__main__":
    main()
