# FGA2 Security Audit

Scope: FGA2 validation, packing, and extraction in Forge (`src/V2/`), with
focus on path traversal, Windows path semantics, filesystem collisions,
symlinks/junctions, time-of-check/time-of-use races, and resource limits.

Date: 2026-10-23

Result: three exploitable or format-breaking path issues were found and
fixed. Remaining limitations are documented below. The regression suite now
contains 75 passing tests, including the adversarial cases from this audit.

## Findings

### F1 — Reserved Windows device names were accepted (High, fixed)

An archive could contain entries named `NUL`, `CON`, `COM1`, `NUL.txt`,
etc. Validation accepted them, and extraction reported success while opening
a device handle instead of creating a file inside the destination. Depending
on the name, this can discard data, block on a device, or interact with
hardware such as a serial port.

Fix: the shared path validator now rejects Windows reserved base names in
any directory, case-insensitively, before the first dot. The list includes
`CON`, `PRN`, `AUX`, `NUL`, `CLOCK$`, `CONIN$`, `CONOUT$`, `COM1`-`COM9`,
`LPT1`-`LPT9`, plus the superscript variants `COM¹`-`COM³` and
`LPT¹`-`LPT³` that Windows also treats as devices. The same rule is applied
when packing, validating, and extracting.

### F2 — Trailing dots and spaces were accepted (Medium, fixed)

Components such as `evil.` and `evil ` passed validation. Windows removes
trailing dots and spaces, so `evil.` and `evil` resolve to the same name.
This breaks the format's uniqueness guarantees and creates aliasing between
index entries.

Attempts to turn this into an escape using `.. ` or `.. .` components did
not write outside the destination in testing: directory creation failed and
extraction aborted. That behavior depended on Win32 normalization and was
not a reliable security boundary.

Fix: components ending in `.` or ASCII space are rejected. This removes the
aliasing and the reliance on filesystem normalization.

### F3 — Case-insensitive path collisions were accepted (Medium, fixed)

Archives could contain both `A` and `a`, or directories `Dir` and `dir`.
Windows normally resolves these to the same path. Extraction did not escape
the destination and `CREATE_NEW` prevented file overwrite, but directories
could merge and the archive's logical tree no longer matched the filesystem.

Fix: validation now maintains an open-addressing hash table keyed by
FNV-1a over the ASCII-lowercased path. When two paths have the same length
and hash, the earlier path is re-read from the index and compared. Exact
case-insensitive duplicates are rejected as a format error. This covers
ASCII case folding only (see limitations).

### F4 — Large allocation from a tiny malformed archive (Low/Medium, fixed)

The header could declare up to 1,000,000 entries with an index far too small
to contain them. Validation allocated entry metadata based on the declared
count before proving the index could hold that many entries.

Fix: validation now rejects `entry_count * 28 > index_size` before allocating
metadata or the case-collision table.

### F5 — Source file replacement during packing (Medium, mitigated)

The inventory pass used `FindFirstFileA`, then `copy_file_data` reopened the
file with `fopen`, which follows reparse points. A file could be replaced by
a symlink or junction between the two passes, causing the packer to read a
different target than the one inventoried.

Fix: file data is opened with `CreateFileA` using
`FILE_FLAG_OPEN_REPARSE_POINT`, and the handle is rejected if it is a reparse
point or directory. The handle's size must equal the inventory size, and one
extra read verifies that the file did not grow.

Residual: an attacker with write access to the source tree can still modify
file contents in place without changing the size during the read. Packing
untrusted, concurrently modified trees is inherently racy.

### F6 — Archive mutation between validation and extraction (Medium, mitigated)

Extraction validated the archive from a `FILE *` opened with `fopen`, then
read it again to extract. Another process could modify the archive between
the two passes.

Fix: unpack now opens the archive with `CreateFileA(... GENERIC_READ,
FILE_SHARE_READ ...)`, denying concurrent writers for the lifetime of the
operation.

## Residual limitations

These are known and intentional for the frozen FGA2 implementation:

1. **Destination check-to-use race (TOCTOU).** `ensure_directory` checks
   reparse-point attributes and then creates or opens the path. An attacker
   who can modify the destination tree during extraction could replace a
   checked directory with a junction before a file is created. Win32 has no
   `openat`/`O_NOFOLLOW` equivalent that removes this race completely.
   Mitigation: extraction refuses existing reparse points and uses
   `CREATE_NEW`, so it does not overwrite existing files.
2. **Non-atomic extraction.** On failure, files and directories already
   created remain in the destination. There is no staging directory or
   rollback.
3. **ANSI APIs vs UTF-8 paths.** The format stores UTF-8 paths, but packing
   uses `FindFirstFileA`/`CreateFileA` and extraction uses ANSI Win32 APIs.
   Non-ASCII names are interpreted in the active ANSI code page and are not
   reliably preserved. Validating a non-ASCII archive succeeds; extracting
   it may produce different names. No separator injection was found because
   valid UTF-8 bytes cannot encode ASCII `/`, `\`, or `:` as path
   separators, but this is a correctness limitation, not a guarantee of
   round-trip fidelity.
4. **Case folding is ASCII-only.** Windows may treat some non-ASCII names as
   equal (for example, certain Unicode case pairs). Those collisions are not
   detected. `CREATE_NEW` still prevents file overwrite; directories could
   merge inside the destination.
5. **Short (8.3) name aliases.** A filesystem may alias a long name and a
   generated short name (for example, `PROGRA~1`). This can cause collisions
   inside the destination but does not provide a path escape.
6. **Validation reads.** `validate`, `info`, and `list` still open archives
   with ordinary read sharing. Concurrent modification can produce
   inconsistent output; no extraction occurs from those paths.
7. **FGA1 size limit.** FGA1 extraction uses 32-bit `long` file positioning
   and is limited to files below 2 GiB. This does not affect FGA2.
8. **No integrity/authentication.** FGA2 has no checksum or signature.
   Corruption that still satisfies the structural invariants is not
   detected. The format does not provide confidentiality or authenticity.

## Verification

Commands used:

```text
$env:PATH = 'C:\msys64\usr\bin;C:\msys64\ucrt64\bin;' + $env:PATH
make clean
make
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tests/test_forge.ps1
```

The build is clean under `-std=c17 -Wall -Wextra -Wpedantic -Werror`.
All 75 tests pass. The permanent suite covers:

- traversal and non-canonical paths;
- invalid UTF-8;
- reserved device names, including superscript variants;
- trailing dot/space components;
- case-insensitive file and directory collisions;
- missing/invalid parents, ordering, duplicates, and directory payloads;
- manipulated entry fields, oversized declared counts, extra data;
- packing and extracting through junctions;
- refusal to overwrite an existing destination file;
- acceptance of valid non-ASCII UTF-8 paths at format level.

See `FGA2_SPEC.md` for the frozen binary layout and validation invariants.
