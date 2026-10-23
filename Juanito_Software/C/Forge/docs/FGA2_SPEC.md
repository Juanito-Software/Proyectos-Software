# FGA2 Binary Format Specification

Status: frozen reference for the current FGA2 implementation.

All multi-byte integers are unsigned and stored in little-endian byte order.
All offsets are absolute file offsets measured from the start of the archive.

## Overview

An FGA2 archive is laid out as:

```text
+----------------------+  offset 0
| Header (26 bytes)    |
+----------------------+  offset 26
| Index (variable)     |
+----------------------+
| Data region          |
+----------------------+  end of file
```

The index is a sequence of entries. Each entry has a fixed 28-byte header
followed by a variable-length path. File data follows the index in the same
order as the file entries. Directory entries have no data.

There is no alignment or padding between fields, entries, index, or data.

## Header

Total size: 26 bytes.

| Offset | Size | Field | Value / meaning |
|---:|---:|---|---|
| 0 | 4 | Magic | ASCII `FGA2` (`46 47 41 32`) |
| 4 | 1 | Format version | `2` |
| 5 | 1 | Flags | Must be `0` in this version |
| 6 | 8 | Original size | Sum of the original sizes of all file entries |
| 14 | 8 | Data size | Total size of the data region |
| 22 | 4 | Entry count | Number of index entries |

Readers must reject an archive whose magic, version, or flags do not match
the values above.

## Index entry

Each entry occupies `28 + path_length` bytes.

| Offset (from entry start) | Size | Field |
|---:|---:|---|
| 0 | 2 | Path length (`path_length`) |
| 2 | 1 | Entry type |
| 3 | 1 | Entry flags |
| 4 | 8 | Original size |
| 12 | 8 | Stored size |
| 20 | 8 | Data offset |
| 28 | `path_length` | Path bytes (UTF-8, no terminator) |

Entry types:

| Value | Type |
|---:|---|
| 0 | Regular file |
| 1 | Directory |

Entry flags must be `0` in this version.

For a regular file:

- `original size == stored size` (FGA2 does not compress).
- `data offset` equals the sum of the stored sizes of all previous file
  entries.
- The stored bytes occupy exactly `stored size` bytes in the data region.

For a directory:

- `original size == 0`.
- `stored size == 0`.
- `data offset` equals the sum of the stored sizes of all previous file
  entries.

## Paths

Paths are serialized as UTF-8 without a trailing NUL.

- Paths are relative and use `/` as the separator.
- Paths must not start with `/`.
- Empty components, `.`, and `..` are forbidden.
- Backslash (`\`), colon (`:`), ASCII control characters, and DEL are
  forbidden.
- Each component must be non-empty and must not end in `.` or space.
  Windows removes those characters, which would alias distinct paths.
- Reserved Windows device names are forbidden as the base name (case
  insensitive, before the first dot): `CON`, `PRN`, `AUX`, `NUL`,
  `CLOCK$`, `CONIN$`, `CONOUT$`, `COM1`-`COM9`, and `LPT1`-`LPT9`.
  This also rejects forms such as `NUL.txt`.
- Paths must be unique byte-for-byte and strictly sorted in bytewise
  lexicographic order.
- Paths must also be unique under ASCII case folding, because Windows
  file systems are normally case-insensitive. Only ASCII `A`-`Z` /
  `a`-`z` folding is guaranteed by the format; full Unicode case folding
  is not implemented.
- Every parent component must have an explicit directory entry earlier
  in the index.
- The parent of an entry must be a directory, not a file.

Because entries are sorted, a parent always precedes its children.

## Limits

| Limit | Value |
|---|---:|
| Maximum entries | 1,000,000 |
| Maximum path length | 65,535 bytes (`UINT16_MAX`) |
| Maximum index size | 256 MiB (268,435,456 bytes) |
| Maximum data size | `UINT64_MAX`, subject to the actual file size |

The index must contain at least `entry_count * 28` bytes. A larger declared
entry count is rejected before allocating entry metadata.

## Validation invariants

A conforming validator checks, at minimum:

1. Header magic, version, and flags.
2. `entry_count <= 1,000,000`.
3. The declared data region fits inside the file.
4. The index region does not exceed 256 MiB.
5. The index can hold the declared number of fixed entry headers.
6. Each entry's fixed header and path fit inside the index region.
7. Entry type and flags are supported.
8. Path structure, UTF-8 validity, Windows-specific restrictions, order,
   uniqueness, case-insensitive uniqueness, and parent hierarchy.
9. Per-entry size rules and sequential data offsets.
10. `index_size` ends exactly where the data region begins, with no
    padding or gap.
11. The sum of file original sizes equals header `original size`.
12. The sum of file stored sizes equals header `data size`.
13. There are no extra bytes after the data region.

An archive is accepted only if all invariants hold.

## Versioning

FGA2 is frozen for the purposes of this milestone. New features that change
the on-disk layout or field semantics must use a new format version.
FGA2 readers must not silently reinterpret fields from other versions.
