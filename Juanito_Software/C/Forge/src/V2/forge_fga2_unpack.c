
#define WIN32_LEAN_AND_MEAN
#include <windows.h>

#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <io.h>

#include "forge_fga2_internal.h"

#define COPY_BUFFER_SIZE 65536u

typedef struct {
    char *path;
    uint16_t path_length;
    uint8_t type;
    uint64_t original_size;
    uint64_t stored_size;
    uint64_t data_offset;
} ForgeFga2UnpackEntry;

static ForgeStatus read_exact(FILE *file, void *buffer, size_t size)
{
    if (file == NULL || (buffer == NULL && size != 0)) {
        return FORGE_ERROR_ARGUMENT;
    }

    if (fread(buffer, 1, size, file) == size) {
        return FORGE_OK;
    }

    return ferror(file) ? FORGE_ERROR_IO : FORGE_ERROR_FORMAT;
}

static uint16_t read_u16_le(const unsigned char bytes[2])
{
    return (uint16_t)(
        (uint16_t)bytes[0] |
        ((uint16_t)bytes[1] << 8)
    );
}

static uint32_t read_u32_le(const unsigned char bytes[4])
{
    return (uint32_t)bytes[0]
        | ((uint32_t)bytes[1] << 8)
        | ((uint32_t)bytes[2] << 16)
        | ((uint32_t)bytes[3] << 24);
}

static uint64_t read_u64_le(const unsigned char bytes[8])
{
    uint64_t value = 0;

    for (unsigned int i = 0; i < 8; ++i) {
        value |= (uint64_t)bytes[i] << (i * 8u);
    }

    return value;
}

/*
 * Abre el archivo de entrada denegando la escritura a otros
 * procesos. Así el archivo no puede cambiar entre la validación
 * y la segunda pasada de extracción.
 */
static FILE *open_archive_read_only(const char *path)
{
    HANDLE handle = CreateFileA(
        path,
        GENERIC_READ,
        FILE_SHARE_READ,
        NULL,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );

    if (handle == INVALID_HANDLE_VALUE) {
        return NULL;
    }

    int fd = _open_osfhandle(
        (intptr_t)handle,
        _O_RDONLY | _O_BINARY
    );

    if (fd == -1) {
        CloseHandle(handle);
        return NULL;
    }

    FILE *file = _fdopen(fd, "rb");

    if (file == NULL) {
        _close(fd);
        return NULL;
    }

    return file;
}

static void free_entries(
    ForgeFga2UnpackEntry *entries,
    uint32_t entry_count)
{
    if (entries == NULL) {
        return;
    }

    for (uint32_t i = 0; i < entry_count; ++i) {
        free(entries[i].path);
    }

    free(entries);
}

static int path_is_safe(const char *path, uint16_t length)
{
    if (path == NULL || length == 0) {
        return 0;
    }

    /*
     * FGA2 paths are relative UTF-8 paths using '/'.
     * The shared validator also rejects Windows device names and
     * components whose trailing dots or spaces would be normalized
     * by the file system.
     */
    return forge_fga2_path_is_valid(
        (const unsigned char *)path,
        (size_t)length
    ) ? 1 : 0;
}

static ForgeStatus read_entries(
    FILE *source,
    uint32_t entry_count,
    ForgeFga2UnpackEntry **entries_out,
    uint64_t *index_size_out)
{
    *entries_out = NULL;
    *index_size_out = 0;

    if (entry_count > FORGE_FGA2_MAX_ENTRIES) {
        return FORGE_ERROR_LIMIT;
    }

    if (entry_count == 0) {
        return FORGE_OK;
    }

    ForgeFga2UnpackEntry *entries =
        calloc((size_t)entry_count, sizeof *entries);

    if (entries == NULL) {
        return FORGE_ERROR_MEMORY;
    }

    uint64_t index_size = 0;
    ForgeStatus status = FORGE_OK;

    for (uint32_t i = 0; i < entry_count; ++i) {
        unsigned char fixed[FORGE_FGA2_ENTRY_FIXED_SIZE];

        status = read_exact(source, fixed, sizeof fixed);
        if (status != FORGE_OK) {
            break;
        }

        uint16_t path_length = read_u16_le(fixed);
        uint8_t type = fixed[2];
        uint8_t flags = fixed[3];

        uint64_t original_size = read_u64_le(fixed + 4);
        uint64_t stored_size = read_u64_le(fixed + 12);
        uint64_t data_offset = read_u64_le(fixed + 20);

        if (path_length == 0 || flags != 0 || (type != FORGE_FGA2_ENTRY_FILE && type != FORGE_FGA2_ENTRY_DIRECTORY)) {
                status = FORGE_ERROR_FORMAT;
                break;
            }

        char *path = malloc((size_t)path_length + 1u);

        if (path == NULL) {
            status = FORGE_ERROR_MEMORY;
            break;
        }

        status = read_exact(source, path, path_length);

        if (status != FORGE_OK) {
            free(path);
            break;
        }

        path[path_length] = '\0';

        if (!path_is_safe(path, path_length)) {
            free(path);
            status = FORGE_ERROR_FORMAT;
            break;
        }

        if (type == FORGE_FGA2_ENTRY_DIRECTORY &&
            (original_size != 0 || stored_size != 0)) {
            free(path);
            status = FORGE_ERROR_FORMAT;
            break;
        }

        if (type == FORGE_FGA2_ENTRY_FILE &&
            original_size != stored_size) {
            free(path);
            status = FORGE_ERROR_FORMAT;
            break;
        }

        if (index_size >
            FORGE_FGA2_MAX_INDEX_SIZE -
                FORGE_FGA2_ENTRY_FIXED_SIZE -
                (uint64_t)path_length) {
            free(path);
            status = FORGE_ERROR_LIMIT;
            break;
        }

        index_size += FORGE_FGA2_ENTRY_FIXED_SIZE +
                      (uint64_t)path_length;

        entries[i].path = path;
        entries[i].path_length = path_length;
        entries[i].type = type;
        entries[i].original_size = original_size;
        entries[i].stored_size = stored_size;
        entries[i].data_offset = data_offset;
    }

    if (status != FORGE_OK) {
        free_entries(entries, entry_count);
        return status;
    }

    *entries_out = entries;
    *index_size_out = index_size;
    return FORGE_OK;
}

static ForgeStatus ensure_directory(const char *path)
{
    if (CreateDirectoryA(path, NULL)) {
        return FORGE_OK;
    }

    DWORD error = GetLastError();

    if (error != ERROR_ALREADY_EXISTS) {
        return FORGE_ERROR_IO;
    }

    DWORD attributes = GetFileAttributesA(path);

    if (attributes == INVALID_FILE_ATTRIBUTES) {
        return FORGE_ERROR_IO;
    }

    if ((attributes & FILE_ATTRIBUTE_DIRECTORY) == 0 ||
        (attributes & FILE_ATTRIBUTE_REPARSE_POINT) != 0) {
        return FORGE_ERROR_UNSUPPORTED;
    }

    return FORGE_OK;
}

static ForgeStatus ensure_directory_tree(const char *path)
{
    char *copy = _strdup(path);

    if (copy == NULL) {
        return FORGE_ERROR_MEMORY;
    }

    size_t length = strlen(copy);

    if (length == 0) {
        free(copy);
        return FORGE_ERROR_ARGUMENT;
    }

    /*
     * Create intermediate directories in the destination path.
     * Existing reparse-point directories are rejected.
     */
    for (size_t i = 0; i < length; ++i) {
        if (copy[i] != '\\' && copy[i] != '/') {
            continue;
        }

        /*
         * Do not attempt to create a drive root such as C:\.
         */
        if (i == 0 || (i == 2 && copy[1] == ':')) {
            continue;
        }

        char saved = copy[i];
        copy[i] = '\0';

        ForgeStatus status = ensure_directory(copy);

        copy[i] = saved;

        if (status != FORGE_OK) {
            free(copy);
            return status;
        }
    }

    ForgeStatus status = ensure_directory(copy);
    free(copy);
    return status;
}

static ForgeStatus build_entry_path(
    const char *root,
    const char *relative_path,
    char **result)
{
    *result = NULL;

    size_t root_length = strlen(root);
    size_t relative_length = strlen(relative_path);

    int needs_separator =
        root_length > 0 &&
        root[root_length - 1] != '\\' &&
        root[root_length - 1] != '/';

    if (root_length > SIZE_MAX - relative_length - 2u) {
        return FORGE_ERROR_LIMIT;
    }

    size_t total = root_length + relative_length +
                   (needs_separator ? 1u : 0u) + 1u;

    char *combined = malloc(total);

    if (combined == NULL) {
        return FORGE_ERROR_MEMORY;
    }

    memcpy(combined, root, root_length);

    size_t position = root_length;

    if (needs_separator) {
        combined[position++] = '\\';
    }

    memcpy(combined + position, relative_path, relative_length);
    combined[position + relative_length] = '\0';

    /*
     * Win32 accepts forward slashes, but use backslashes consistently
     * for the generated destination paths.
     */
    for (size_t i = root_length; i < position + relative_length; ++i) {
        if (combined[i] == '/') {
            combined[i] = '\\';
        }
    }

    *result = combined;
    return FORGE_OK;
}

static ForgeStatus create_entry_directories(
    const char *root,
    const char *relative_path)
{
    char *full_path = NULL;

    ForgeStatus status =
        build_entry_path(root, relative_path, &full_path);

    if (status != FORGE_OK) {
        return status;
    }

    status = ensure_directory_tree(full_path);
    free(full_path);

    return status;
}

static ForgeStatus extract_file(
    FILE *source,
    const char *root,
    const ForgeFga2UnpackEntry *entry,
    uint64_t data_start)
{
    if (entry->data_offset > UINT64_MAX - data_start) {
        return FORGE_ERROR_LIMIT;
    }

    uint64_t absolute_offset = data_start + entry->data_offset;

    if (absolute_offset > INT64_MAX) {
        return FORGE_ERROR_LIMIT;
    }

    if (_fseeki64(source, (__int64)absolute_offset, SEEK_SET) != 0) {
        return FORGE_ERROR_IO;
    }

    char *full_path = NULL;

    ForgeStatus status =
        build_entry_path(root, entry->path, &full_path);

    if (status != FORGE_OK) {
        return status;
    }

    /*
     * CREATE_NEW refuses to overwrite an existing file or follow an
     * existing file symlink. Parent directories must already exist.
     */
    HANDLE destination = CreateFileA(
        full_path,
        GENERIC_WRITE,
        0,
        NULL,
        CREATE_NEW,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );

    free(full_path);

    if (destination == INVALID_HANDLE_VALUE) {
        return GetLastError() == ERROR_FILE_EXISTS ||
               GetLastError() == ERROR_ALREADY_EXISTS
            ? FORGE_ERROR_ARGUMENT
            : FORGE_ERROR_IO;
    }

    unsigned char buffer[COPY_BUFFER_SIZE];
    uint64_t remaining = entry->stored_size;

    while (remaining > 0) {
        DWORD amount = sizeof buffer;

        if (remaining < (uint64_t)amount) {
            amount = (DWORD)remaining;
        }

        size_t read_count = fread(buffer, 1, amount, source);

        if (read_count != amount) {
            status = ferror(source)
                ? FORGE_ERROR_IO
                : FORGE_ERROR_FORMAT;
            break;
        }

        DWORD written = 0;

        if (!WriteFile(
                destination,
                buffer,
                amount,
                &written,
                NULL) ||
            written != amount) {
            status = FORGE_ERROR_IO;
            break;
        }

        remaining -= (uint64_t)amount;
    }

    if (!CloseHandle(destination) && status == FORGE_OK) {
        status = FORGE_ERROR_IO;
    }

    return status;
}

ForgeStatus forge_fga2_unpack(
    const char *input_path,
    const char *output_path)
{
    if (input_path == NULL || input_path[0] == '\0' ||
        output_path == NULL || output_path[0] == '\0') {
        return FORGE_ERROR_ARGUMENT;
    }

    if (strcmp(input_path, output_path) == 0) {
        return FORGE_ERROR_ARGUMENT;
    }

    FILE *source = open_archive_read_only(input_path);

    if (source == NULL) {
        return FORGE_ERROR_IO;
    }

    uint64_t original_size = 0;
    uint64_t data_size = 0;
    uint32_t entry_count = 0;

    ForgeStatus status = forge_fga2_validate(
        source,
        &original_size,
        &data_size,
        &entry_count
    );

    if (status != FORGE_OK) {
        (void)fclose(source);
        return status;
    }

    /*
     * Read the already-validated header and index again to retain
     * each path and its data offset for extraction.
     */
    if (_fseeki64(source, 0, SEEK_SET) != 0) {
        (void)fclose(source);
        return FORGE_ERROR_IO;
    }

    unsigned char header[FORGE_FGA2_HEADER_SIZE];

    status = read_exact(source, header, sizeof header);

    if (status != FORGE_OK) {
        (void)fclose(source);
        return status;
    }

    uint32_t header_entry_count = read_u32_le(header + 22);

    if (header_entry_count != entry_count) {
        (void)fclose(source);
        return FORGE_ERROR_FORMAT;
    }

    ForgeFga2UnpackEntry *entries = NULL;
    uint64_t index_size = 0;

    status = read_entries(
        source,
        entry_count,
        &entries,
        &index_size
    );

    if (status != FORGE_OK) {
        (void)fclose(source);
        return status;
    }

    if (index_size > UINT64_MAX - FORGE_FGA2_HEADER_SIZE) {
        free_entries(entries, entry_count);
        (void)fclose(source);
        return FORGE_ERROR_LIMIT;
    }

    uint64_t data_start =
        (uint64_t)FORGE_FGA2_HEADER_SIZE + index_size;

    /*
     * Reject a destination root that is itself a reparse point.
     * Existing output files are not overwritten.
     */
    status = ensure_directory_tree(output_path);

    if (status != FORGE_OK) {
        free_entries(entries, entry_count);
        (void)fclose(source);
        return status;
    }

    for (uint32_t i = 0; i < entry_count; ++i) {
        const ForgeFga2UnpackEntry *entry = &entries[i];

        if (entry->type == FORGE_FGA2_ENTRY_DIRECTORY) {
            status = create_entry_directories(
                output_path,
                entry->path
            );
        } else {
            status = extract_file(
                source,
                output_path,
                entry,
                data_start
            );
        }

        if (status != FORGE_OK) {
            break;
        }
    }

    free_entries(entries, entry_count);

    if (fclose(source) == EOF && status == FORGE_OK) {
        status = FORGE_ERROR_IO;
    }

    (void)original_size;
    (void)data_size;

    return status;
}
