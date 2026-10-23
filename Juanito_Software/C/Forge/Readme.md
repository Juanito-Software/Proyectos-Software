# Forge

**Forge General Archive** — a binary archive format and library written in C.

Forge is a systems programming project focused on binary file formats, serialization, archive management, validation, and safe file extraction.

The project is developed in C with an emphasis on explicit binary layouts, fixed-width integer types, little-endian serialization, input validation, and backward compatibility.

## Features

- Custom binary archive format.
- Explicit serialization and deserialization of integer fields.
- Little-endian binary encoding, independent of host byte order.
- Structural validation before archive data is processed.
- Single-file archives in FGA1.
- Multi-file archives with directory entries in FGA2.
- Windows-safe path validation, including reserved device names, trailing
  dots/spaces, and case-insensitive collisions.
- Command-line interface.
- Reusable C library: `libforge`.
- Separation of format-specific implementations.
- Strict compiler warnings during development.
- Planned compression, integrity verification, and further format extensions.

> **Development status:** Forge is under active development. Features and binary format details may evolve as the implementation progresses.

## Project structure

The project separates the public API, shared implementation, version-specific format implementations, and automated tests.

```text
Forge/
├── include/
│   └── forge.h              # Public API
├── src/
│   ├── common/              # Shared functionality
│   ├── v1/                  # FGA1 implementation
│   ├── v2/                  # FGA2 implementation
│   └── forge.c              # CLI entry point
├── tests/                   # Automated tests
├── docs/                    # Format specifications and security notes
├── Makefile
├── LICENSE
└── README.md
```

The directory layout represents the intended organization of the codebase. Individual files may be added or moved as development progresses.

- **`src/v1/`** contains implementation details specific to the original FGA1 format.
- **`src/v2/`** contains implementation details specific to the FGA2 multi-file format.
- **`src/common/`** contains functionality shared between format versions, such as status handling and other common operations.
- **`src/forge.c`** contains the command-line interface entry point.
- **`include/`** contains the public API exposed by `libforge`.
- **`tests/`** contains automated tests for validation, archive operations, and regression testing.

The CLI and public API should dispatch operations to the appropriate format implementation without unnecessarily exposing internal format-specific details.

The source directory version numbers refer to the archive format implementations, not to the version of the Forge library itself.

## Archive formats

Forge uses the `.fga` file extension.

| Format | Magic | Purpose |
|---|---|---|
| FGA1 | `FGA1` | Single-file archive |
| FGA2 | `FGA2` | Multi-file archive with an index |
| FGA3 | Planned | Compression and per-entry codec identification |

The first four bytes of an archive identify its format.

### FGA1 — Single-file archives

FGA1 is the original archive format. It stores a single file's data alongside the metadata required to validate and recover it.

Its header is 22 bytes long.

The FGA1 implementation is maintained separately from newer format implementations to preserve the original format's behavior and simplify backward-compatibility work.

### FGA2 — Multi-file archives

FGA2 extends Forge to support multiple files and directories in a single archive.

Its header is 26 bytes long and contains:

| Field | Size |
|---|---:|
| Magic | 4 bytes |
| Format version | 1 byte |
| Flags | 1 byte |
| Original size | 8 bytes |
| Stored data size | 8 bytes |
| Entry count | 4 bytes |

All multi-byte integer fields are serialized in little-endian order.

Each index entry contains:

- Path length.
- Entry type.
- Entry flags.
- Original size.
- Stored size.
- Data offset.
- UTF-8 path.

FGA2 stores its index immediately after the header, followed by the file data region. Directory entries are represented explicitly, and paths are relative paths using `/` as the separator.

The initial FGA2 format does not compress file data. For regular files, the original size and stored size must match. Directory entries contain no file data.

The validator checks the archive structure, entry metadata, offsets, sizes, path constraints, and directory hierarchy before accepting an archive.

The frozen FGA2 layout and its validation invariants are documented in
[docs/FGA2_SPEC.md](docs/FGA2_SPEC.md). The security review and its residual
limitations are documented in
[docs/FGA2_SECURITY_AUDIT.md](docs/FGA2_SECURITY_AUDIT.md).

### FGA3 — Planned

FGA3 is planned to introduce compression while retaining support for existing archive versions.

The design is expected to identify the codec used by each entry, allowing different entries to use different storage methods.

Candidate algorithms include:

- Run-Length Encoding (RLE).
- Huffman coding.
- LZ-family compression.

The final binary layout, codec identifiers, and compatibility rules will be documented before implementation begins.

## Design principles

Forge follows these principles:

1. **Explicit binary layouts:** fields are serialized deliberately rather than by writing native C structures directly to disk.
2. **Portable integer encoding:** fixed-width integer types and little-endian serialization define the on-disk representation.
3. **Strict validation:** malformed sizes, invalid offsets, unsupported flags, and invalid paths must be rejected.
4. **Safe extraction:** archive paths must not be allowed to escape the destination directory.
5. **Backward compatibility:** introducing a new format version must not silently change the meaning of existing versions.
6. **Separation of concerns:** the public API, CLI, shared functionality, and format-specific implementations remain distinct.
7. **Resource limits:** validation must enforce documented limits before allocating memory or processing archive contents.
8. **Defensive file handling:** read, write, and extraction operations must handle I/O errors and unexpected end-of-file conditions.

## Building

Forge currently targets a Windows development environment using MSYS2 UCRT64 and GCC.

From the project root, build with:

```bash
make
```

The build uses strict C17 compiler options:

```text
-std=c17 -Wall -Wextra -Wpedantic -Werror
```

These options help detect language-standard violations, suspicious constructs, and compiler warnings during development.

The exact build targets and generated artifacts depend on the current `Makefile`.

When source files are moved between `src/v1/`, `src/v2/`, and `src/common/`, the corresponding source paths in the build configuration must be updated.

## Command-line interface

The command-line executable is named `forge`.

The intended interface covers operations such as:

- Packing files into an archive.
- Extracting archive contents.
- Validating archive structure.
- Displaying archive metadata.
- Listing archive entries.

Available commands depend on the current implementation. Run the executable's help command to inspect the commands currently supported.

The CLI should select the appropriate implementation based on the archive format or the requested operation.

## Public library

The reusable library is named `libforge`.

Its public API is declared in:

```text
include/forge.h
```

The API exposes archive operations and status codes without requiring callers to depend on internal implementation details.

Format-specific functions and structures should remain private unless there is a clear reason to expose them through the public API.

Shared functionality should be implemented once where practical, while format-specific validation and serialization remain isolated in their respective source directories.

## Development roadmap

- [x] Define the FGA1 binary format and initial archive operations.
- [x] Establish the initial library and CLI architecture.
- [x] Complete FGA2 integration across validation, packing, extraction, metadata, and entry listing.
- [x] Finalize the FGA2 implementation and perform a complete test pass.
- [x] Review FGA2 resource limits and extraction security.
- [ ] Define and document the FGA3 binary specification.
- [ ] Implement compression and decompression.
- [ ] Add archive integrity checks, including CRC32.
- [x] Expand corruption, boundary-condition, and regression testing.
- [ ] Document the final format specifications and stable public API.

The roadmap should be updated as features are implemented and verified.

## Security considerations

Archive parsers process potentially untrusted binary data. Validation must precede extraction, and size calculations must be checked for integer overflow.

Extraction must reject absolute paths, parent-directory traversal, invalid path components, and paths that could write outside the destination directory.

FGA2 additionally rejects Windows reserved device names (including `NUL`,
`CON`, `COM1`, and `NUL.txt` forms), components ending in a dot or space,
and paths that collide after ASCII case folding. Known residual risks,
including destination time-of-check/time-of-use races, non-atomic
extraction, and ANSI-versus-UTF-8 path handling, are listed in
[docs/FGA2_SECURITY_AUDIT.md](docs/FGA2_SECURITY_AUDIT.md).

Implementations should also account for symbolic links, filesystem collisions, platform-specific path behavior, and file modification during archive operations.

Compression support will require limits on decompressed output and other resource-consumption safeguards to mitigate decompression bombs and excessive memory or CPU usage.

Forge should not be considered suitable for protecting confidential data until its cryptographic design, key management, and authenticated-encryption implementation have been reviewed.

## License

See [LICENSE](LICENSE) for the applicable license terms.
