
#include "forge_fga2_internal.h"

#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <io.h>
#include <fcntl.h>

typedef struct {
    char *source_path;
    char *archive_path;
    uint64_t size;
    uint64_t data_offset;
    uint16_t path_length;
    uint8_t type;
} ForgeFga2PackEntry;

typedef struct {
    ForgeFga2PackEntry *entries;
    size_t count;
    size_t capacity;
    uint64_t original_size;
    uint64_t data_size;
    uint64_t index_size;
} ForgeFga2PackContext;

static void free_context(ForgeFga2PackContext *ctx)
{
    if (ctx == NULL) {
        return;
    }

    for (size_t i = 0; i < ctx->count; ++i) {
        free(ctx->entries[i].source_path);
        free(ctx->entries[i].archive_path);
    }

    free(ctx->entries);
    memset(ctx, 0, sizeof *ctx);
}

static char *duplicate_string(const char *value)
{
    if (value == NULL) {
        return NULL;
    }

    size_t length = strlen(value);

    if (length == SIZE_MAX) {
        return NULL;
    }

    char *copy = malloc(length + 1);

    if (copy == NULL) {
        return NULL;
    }

    memcpy(copy, value, length + 1);
    return copy;
}

static char *join_paths(const char *left, const char *right)
{
    if (left == NULL || right == NULL) {
        return NULL;
    }

    size_t left_length = strlen(left);
    size_t right_length = strlen(right);

    if (right_length > SIZE_MAX - 2 ||
        left_length > SIZE_MAX - right_length - 2) {
        return NULL;
    }

    char *result = malloc(left_length + right_length + 2);

    if (result == NULL) {
        return NULL;
    }

    memcpy(result, left, left_length);
    result[left_length] = '/';
    memcpy(result + left_length + 1, right, right_length + 1);

    return result;
}

static int compare_entries(const void *left, const void *right)
{
    const ForgeFga2PackEntry *a = left;
    const ForgeFga2PackEntry *b = right;

    return strcmp(a->archive_path, b->archive_path);
}

static ForgeStatus append_entry(
    ForgeFga2PackContext *ctx,
    const char *source_path,
    const char *archive_path,
    uint8_t type,
    uint64_t size
)
{
    if (ctx == NULL || source_path == NULL || archive_path == NULL) {
        return FORGE_ERROR_ARGUMENT;
    }

    size_t path_length = strlen(archive_path);

    if (path_length == 0 || path_length > FORGE_FGA2_MAX_PATH_SIZE) {
        return FORGE_ERROR_LIMIT;
    }

    if (!forge_fga2_path_is_valid(
            (const unsigned char *)archive_path,
            path_length)) {
        return FORGE_ERROR_FORMAT;
    }

    if (ctx->count >= FORGE_FGA2_MAX_ENTRIES) {
        return FORGE_ERROR_LIMIT;
    }

    if (type != FORGE_FGA2_ENTRY_FILE &&
        type != FORGE_FGA2_ENTRY_DIRECTORY) {
        return FORGE_ERROR_FORMAT;
    }

    if (type == FORGE_FGA2_ENTRY_DIRECTORY && size != 0) {
        return FORGE_ERROR_FORMAT;
    }

    if (ctx->count == ctx->capacity) {
        size_t new_capacity = ctx->capacity == 0
            ? 16
            : ctx->capacity * 2;

        if (new_capacity < ctx->capacity ||
            new_capacity > FORGE_FGA2_MAX_ENTRIES) {
            new_capacity = FORGE_FGA2_MAX_ENTRIES;
        }

        if (new_capacity <= ctx->capacity ||
            new_capacity > SIZE_MAX / sizeof *ctx->entries) {
            return FORGE_ERROR_LIMIT;
        }

        ForgeFga2PackEntry *new_entries = realloc(
            ctx->entries,
            new_capacity * sizeof *ctx->entries
        );

        if (new_entries == NULL) {
            return FORGE_ERROR_MEMORY;
        }

        ctx->entries = new_entries;
        ctx->capacity = new_capacity;
    }

    char *source_copy = duplicate_string(source_path);
    char *archive_copy = duplicate_string(archive_path);

    if (source_copy == NULL || archive_copy == NULL) {
        free(source_copy);
        free(archive_copy);
        return FORGE_ERROR_MEMORY;
    }

    ForgeFga2PackEntry entry = {
        .source_path = source_copy,
        .archive_path = archive_copy,
        .size = size,
        .data_offset = 0,
        .path_length = (uint16_t)path_length,
        .type = type
    };

    ctx->entries[ctx->count++] = entry;
    return FORGE_OK;
}

static ForgeStatus collect_directory(
    ForgeFga2PackContext *ctx,
    const char *source_directory,
    const char *archive_directory
)
{
    char *search_pattern = join_paths(source_directory, "*");

    if (search_pattern == NULL) {
        return FORGE_ERROR_MEMORY;
    }

    WIN32_FIND_DATAA find_data;
    HANDLE find_handle = FindFirstFileA(search_pattern, &find_data);

    free(search_pattern);

    if (find_handle == INVALID_HANDLE_VALUE) {
        return FORGE_ERROR_IO;
    }

    ForgeStatus status = FORGE_OK;

    for (;;) {
        const char *name = find_data.cFileName;

        if (strcmp(name, ".") != 0 && strcmp(name, "..") != 0) {
            /*
             * Archive paths use '/' and cannot contain Windows
             * path separators or drive delimiters in a component.
             */
            if (strchr(name, '/') != NULL ||
                strchr(name, '\\') != NULL ||
                strchr(name, ':') != NULL) {
                status = FORGE_ERROR_FORMAT;
            } else {
                char *source_path = join_paths(source_directory, name);

                char *archive_path = archive_directory == NULL
                    ? duplicate_string(name)
                    : join_paths(archive_directory, name);

                if (source_path == NULL || archive_path == NULL) {
                    free(source_path);
                    free(archive_path);
                    status = FORGE_ERROR_MEMORY;
                } else {
                    DWORD attributes = find_data.dwFileAttributes;

                    /*
                     * Do not follow symbolic links, junctions,
                     * or other filesystem reparse points.
                     */
                    if ((attributes & FILE_ATTRIBUTE_REPARSE_POINT) != 0) {
                        status = FORGE_ERROR_UNSUPPORTED;
                    } else if ((attributes & FILE_ATTRIBUTE_DIRECTORY) != 0) {
                        status = append_entry(
                            ctx,
                            source_path,
                            archive_path,
                            FORGE_FGA2_ENTRY_DIRECTORY,
                            0
                        );

                        if (status == FORGE_OK) {
                            status = collect_directory(
                                ctx,
                                source_path,
                                archive_path
                            );
                        }
                    } else if ((attributes & FILE_ATTRIBUTE_DEVICE) == 0) {
                        uint64_t file_size =
                            ((uint64_t)find_data.nFileSizeHigh << 32) |
                            (uint64_t)find_data.nFileSizeLow;

                        status = append_entry(
                            ctx,
                            source_path,
                            archive_path,
                            FORGE_FGA2_ENTRY_FILE,
                            file_size
                        );
                    } else {
                        status = FORGE_ERROR_UNSUPPORTED;
                    }

                    free(source_path);
                    free(archive_path);
                }
            }
        }

        if (status != FORGE_OK) {
            break;
        }

        if (!FindNextFileA(find_handle, &find_data)) {
            DWORD error = GetLastError();

            if (error != ERROR_NO_MORE_FILES) {
                status = FORGE_ERROR_IO;
            }

            break;
        }
    }

    if (!FindClose(find_handle) && status == FORGE_OK) {
        status = FORGE_ERROR_IO;
    }

    return status;
}

static ForgeStatus prepare_index(ForgeFga2PackContext *ctx)
{
    if (ctx == NULL) {
        return FORGE_ERROR_ARGUMENT;
    }

    if (ctx->count > 1) {
        qsort(
            ctx->entries,
            ctx->count,
            sizeof *ctx->entries,
            compare_entries
        );
    }

    uint64_t index_size = 0;
    uint64_t data_size = 0;

    for (size_t i = 0; i < ctx->count; ++i) {
        ForgeFga2PackEntry *entry = &ctx->entries[i];

        /*
         * Entries must have strictly increasing paths.
         * This rejects duplicate archive paths.
         */
        if (i > 0 &&
            strcmp(
                ctx->entries[i - 1].archive_path,
                entry->archive_path
            ) >= 0) {
            return FORGE_ERROR_FORMAT;
        }

        if (index_size >
            FORGE_FGA2_MAX_INDEX_SIZE - FORGE_FGA2_ENTRY_FIXED_SIZE) {
            return FORGE_ERROR_LIMIT;
        }

        index_size += FORGE_FGA2_ENTRY_FIXED_SIZE;

        if (entry->path_length > FORGE_FGA2_MAX_INDEX_SIZE - index_size) {
            return FORGE_ERROR_LIMIT;
        }

        index_size += entry->path_length;
        entry->data_offset = data_size;

        if (entry->type == FORGE_FGA2_ENTRY_FILE) {
            if (entry->size > UINT64_MAX - data_size) {
                return FORGE_ERROR_LIMIT;
            }

            data_size += entry->size;
        }
    }

    ctx->index_size = index_size;
    ctx->data_size = data_size;

    /*
     * FGA2 currently stores files without compression.
     * Therefore aggregate original size equals aggregate data size.
     */
    ctx->original_size = data_size;

    return FORGE_OK;
}

static ForgeStatus write_index(
    FILE *output,
    const ForgeFga2PackContext *ctx
)
{
    if (output == NULL || ctx == NULL) {
        return FORGE_ERROR_ARGUMENT;
    }

    for (size_t i = 0; i < ctx->count; ++i) {
        const ForgeFga2PackEntry *entry = &ctx->entries[i];

        uint64_t stored_size =
            entry->type == FORGE_FGA2_ENTRY_FILE ? entry->size : 0;

        ForgeStatus status = forge_fga2_write_entry_header(
            output,
            entry->path_length,
            entry->type,
            0,
            entry->size,
            stored_size,
            entry->data_offset
        );

        if (status != FORGE_OK) {
            return status;
        }

        if (fwrite(
                entry->archive_path,
                1,
                entry->path_length,
                output
            ) != entry->path_length) {
            return FORGE_ERROR_IO;
        }
    }

    return FORGE_OK;
}

static ForgeStatus copy_file_data(
    FILE *output,
    const ForgeFga2PackEntry *entry
)
{
    if (output == NULL || entry == NULL) {
        return FORGE_ERROR_ARGUMENT;
    }

    if (entry->type == FORGE_FGA2_ENTRY_DIRECTORY) {
        return FORGE_OK;
    }

    if (entry->type != FORGE_FGA2_ENTRY_FILE) {
        return FORGE_ERROR_FORMAT;
    }

    /*
     * Abrimos sin seguir enlaces simbólicos. Si el archivo cambió
     * entre el inventario y esta pasada (por ejemplo, fue sustituido
     * por un enlace), lo rechazamos en lugar de leer el destino.
     */
    HANDLE input = CreateFileA(
        entry->source_path,
        GENERIC_READ,
        FILE_SHARE_READ,
        NULL,
        OPEN_EXISTING,
        FILE_FLAG_OPEN_REPARSE_POINT |
            FILE_FLAG_SEQUENTIAL_SCAN,
        NULL
    );

    if (input == INVALID_HANDLE_VALUE) {
        return FORGE_ERROR_IO;
    }

    BY_HANDLE_FILE_INFORMATION information;

    if (!GetFileInformationByHandle(input, &information)) {
        (void)CloseHandle(input);
        return FORGE_ERROR_IO;
    }

    if ((information.dwFileAttributes &
         (FILE_ATTRIBUTE_REPARSE_POINT |
          FILE_ATTRIBUTE_DIRECTORY)) != 0) {
        (void)CloseHandle(input);
        return FORGE_ERROR_IO;
    }

    ULONGLONG actual_size =
        ((ULONGLONG)information.nFileSizeHigh << 32) |
        (ULONGLONG)information.nFileSizeLow;

    if ((uint64_t)actual_size != entry->size) {
        (void)CloseHandle(input);
        return FORGE_ERROR_IO;
    }

    unsigned char buffer[64 * 1024];
    uint64_t remaining = entry->size;
    ForgeStatus status = FORGE_OK;

    while (remaining > 0) {
        DWORD chunk = remaining < sizeof buffer
            ? (DWORD)remaining
            : (DWORD)sizeof buffer;

        DWORD bytes_read = 0;

        if (!ReadFile(
                input,
                buffer,
                chunk,
                &bytes_read,
                NULL
            ) || bytes_read != chunk) {
            status = FORGE_ERROR_IO;
            break;
        }

        if (fwrite(buffer, 1, bytes_read, output) != bytes_read) {
            status = FORGE_ERROR_IO;
            break;
        }

        remaining -= (uint64_t)bytes_read;
    }

    /*
     * Detect growth after the inventory pass.
     */
    if (status == FORGE_OK) {
        unsigned char extra_byte;
        DWORD extra_read = 0;

        if (!ReadFile(
                input,
                &extra_byte,
                1,
                &extra_read,
                NULL
            ) || extra_read != 0) {
            status = FORGE_ERROR_IO;
        }
    }

    if (!CloseHandle(input) && status == FORGE_OK) {
        status = FORGE_ERROR_IO;
    }

    return status;
}

/*
 * Reject an output path located inside the input directory.
 * This prevents an existing output archive from being packed into itself.
 */
static ForgeStatus output_is_inside_input(
    const char *input_path,
    const char *output_path,
    int *result
)
{
    if (input_path == NULL || output_path == NULL || result == NULL) {
        return FORGE_ERROR_ARGUMENT;
    }

    *result = 0;

    DWORD input_length = GetFullPathNameA(input_path, 0, NULL, NULL);
    DWORD output_length = GetFullPathNameA(output_path, 0, NULL, NULL);

    if (input_length == 0 || output_length == 0) {
        return FORGE_ERROR_IO;
    }

    char *input_full = malloc((size_t)input_length + 1);
    char *output_full = malloc((size_t)output_length + 1);

    if (input_full == NULL || output_full == NULL) {
        free(input_full);
        free(output_full);
        return FORGE_ERROR_MEMORY;
    }

    DWORD input_result = GetFullPathNameA(
        input_path,
        input_length + 1,
        input_full,
        NULL
    );

    DWORD output_result = GetFullPathNameA(
        output_path,
        output_length + 1,
        output_full,
        NULL
    );

    ForgeStatus status = FORGE_OK;

    if (input_result == 0 || input_result > input_length ||
        output_result == 0 || output_result > output_length) {
        status = FORGE_ERROR_IO;
    } else {
        size_t root_length = strlen(input_full);

        while (root_length > 3 &&
               (input_full[root_length - 1] == '\\' ||
                input_full[root_length - 1] == '/')) {
            input_full[--root_length] = '\0';
        }

        if (_strnicmp(input_full, output_full, root_length) == 0) {
            char next = output_full[root_length];

            if (next == '\\' || next == '/') {
                *result = 1;
            }
        }
    }

    free(input_full);
    free(output_full);

    return status;
}

/*
 * Create a temporary file in the destination directory so the final
 * replacement can occur on the same volume.
 */
static ForgeStatus create_temporary_output(
    const char *output_path,
    char temporary_path[MAX_PATH]
)
{
    DWORD full_length = GetFullPathNameA(output_path, 0, NULL, NULL);

    if (full_length == 0) {
        return FORGE_ERROR_IO;
    }

    if (full_length >= MAX_PATH) {
        return FORGE_ERROR_LIMIT;
    }

    char full_path[MAX_PATH];

    DWORD copied = GetFullPathNameA(
        output_path,
        MAX_PATH,
        full_path,
        NULL
    );

    if (copied == 0 || copied >= MAX_PATH) {
        return FORGE_ERROR_IO;
    }

    char *last_backslash = strrchr(full_path, '\\');
    char *last_slash = strrchr(full_path, '/');
    char *separator = last_backslash;

    if (separator == NULL ||
        (last_slash != NULL && last_slash > separator)) {
        separator = last_slash;
    }

    char directory[MAX_PATH];

    if (separator == NULL) {
        memcpy(directory, ".", 2);
    } else {
        size_t directory_length = (size_t)(separator - full_path);

        /*
         * Preserve a drive root such as C:\.
         */
        if (directory_length == 2 &&
            full_path[1] == ':') {
            directory_length = 3;
        }

        if (directory_length >= sizeof directory) {
            return FORGE_ERROR_LIMIT;
        }

        memcpy(directory, full_path, directory_length);
        directory[directory_length] = '\0';
    }

    if (GetTempFileNameA(directory, "fga", 0, temporary_path) == 0) {
        return FORGE_ERROR_IO;
    }

    return FORGE_OK;
}

ForgeStatus forge_fga2_pack(
    const char *input_path,
    const char *output_path
)
{
    if (input_path == NULL || output_path == NULL ||
        input_path[0] == '\0' || output_path[0] == '\0') {
        return FORGE_ERROR_ARGUMENT;
    }

    DWORD root_attributes = GetFileAttributesA(input_path);

    if (root_attributes == INVALID_FILE_ATTRIBUTES) {
        return FORGE_ERROR_IO;
    }

    if ((root_attributes & FILE_ATTRIBUTE_DIRECTORY) == 0) {
        return FORGE_ERROR_ARGUMENT;
    }

    if ((root_attributes & FILE_ATTRIBUTE_REPARSE_POINT) != 0) {
        return FORGE_ERROR_UNSUPPORTED;
    }

    int output_inside_input = 0;

    ForgeStatus status = output_is_inside_input(
        input_path,
        output_path,
        &output_inside_input
    );

    if (status != FORGE_OK) {
        return status;
    }

    if (output_inside_input) {
        return FORGE_ERROR_ARGUMENT;
    }

    ForgeFga2PackContext ctx = {0};

    status = collect_directory(&ctx, input_path, NULL);

    if (status == FORGE_OK) {
        status = prepare_index(&ctx);
    }

    if (status != FORGE_OK) {
        free_context(&ctx);
        return status;
    }

    char temporary_path[MAX_PATH];

    status = create_temporary_output(output_path, temporary_path);

    if (status != FORGE_OK) {
        free_context(&ctx);
        return status;
    }

    FILE *output = fopen(temporary_path, "wb");

    if (output == NULL) {
        DeleteFileA(temporary_path);
        free_context(&ctx);
        return FORGE_ERROR_IO;
    }

    status = forge_fga2_write_header(
        output,
        ctx.original_size,
        ctx.data_size,
        (uint32_t)ctx.count
    );

    if (status == FORGE_OK) {
        status = write_index(output, &ctx);
    }

    for (size_t i = 0; i < ctx.count && status == FORGE_OK; ++i) {
        status = copy_file_data(output, &ctx.entries[i]);
    }

    if (status == FORGE_OK && fflush(output) != 0) {
        status = FORGE_ERROR_IO;
    }

    if (status == FORGE_OK && _commit(_fileno(output)) != 0) {
        status = FORGE_ERROR_IO;
    }

    if (fclose(output) != 0 && status == FORGE_OK) {
        status = FORGE_ERROR_IO;
    }

    /* Validate the completed temporary archive before publishing it. */
    if (status == FORGE_OK) {
        FILE *verification_file = fopen(temporary_path, "rb");
        if (verification_file == NULL) {
            status = FORGE_ERROR_IO;
        } else {
            status = forge_fga2_validate(
                verification_file,
                NULL,
                NULL,
                NULL
            );
            if (fclose(verification_file) != 0 && status == FORGE_OK) {
                status = FORGE_ERROR_IO;
            }
        }
    }

    if (status == FORGE_OK) {
        if (!MoveFileExA(
                temporary_path,
                output_path,
                MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH
            )) {
            status = FORGE_ERROR_IO;
        }
    }

    if (status != FORGE_OK) {
        DeleteFileA(temporary_path);
    }

    free_context(&ctx);
    return status;
}
