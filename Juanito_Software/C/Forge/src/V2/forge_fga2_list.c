#include "forge_fga2_internal.h"

#include <stdlib.h>

static uint16_t read_u16_le(const unsigned char bytes[2])
{
    return (uint16_t)(
        (uint16_t)bytes[0] |
        ((uint16_t)bytes[1] << 8)
    );
}

static uint64_t read_u64_le(const unsigned char bytes[8])
{
    uint64_t value = 0;

    for (unsigned int i = 0; i < 8; ++i) {
        value |= (uint64_t)bytes[i] << (i * 8u);
    }

    return value;
}

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

ForgeStatus forge_list(
    const char *path,
    ForgeEntryCallback callback,
    void *user_data
)
{
    if (path == NULL || path[0] == '\0' || callback == NULL) {
        return FORGE_ERROR_ARGUMENT;
    }

    FILE *file = fopen(path, "rb");
    if (file == NULL) {
        return FORGE_ERROR_IO;
    }

    uint32_t entry_count = 0;
    ForgeStatus status = forge_fga2_validate(
        file,
        NULL,
        NULL,
        &entry_count
    );

    if (status != FORGE_OK) {
        (void)fclose(file);
        return status;
    }

    if (fseek(file, 0L, SEEK_SET) != 0) {
        (void)fclose(file);
        return FORGE_ERROR_IO;
    }

    unsigned char header[FORGE_FGA2_HEADER_SIZE];
    status = read_exact(file, header, sizeof header);
    if (status != FORGE_OK) {
        (void)fclose(file);
        return status;
    }

    for (uint32_t i = 0; i < entry_count; ++i) {
        unsigned char entry_header[FORGE_FGA2_ENTRY_FIXED_SIZE];
        status = read_exact(file, entry_header, sizeof entry_header);
        if (status != FORGE_OK) {
            break;
        }

        uint16_t path_length = read_u16_le(&entry_header[0]);
        unsigned char entry_type = entry_header[2];
        uint64_t original_size = read_u64_le(&entry_header[4]);
        uint64_t stored_size = read_u64_le(&entry_header[12]);
        uint64_t data_offset = read_u64_le(&entry_header[20]);

        if (path_length == 0) {
            status = FORGE_ERROR_FORMAT;
            break;
        }

        char *entry_path = malloc((size_t)path_length + 1u);
        if (entry_path == NULL) {
            status = FORGE_ERROR_MEMORY;
            break;
        }

        status = read_exact(file, entry_path, path_length);
        if (status != FORGE_OK) {
            free(entry_path);
            break;
        }
        entry_path[path_length] = '\0';

        ForgeEntryInfo entry = {
            .path = entry_path,
            .type = entry_type == FORGE_FGA2_ENTRY_DIRECTORY
                ? FORGE_ENTRY_DIRECTORY
                : FORGE_ENTRY_FILE,
            .original_size = original_size,
            .stored_size = stored_size,
            .data_offset = data_offset
        };

        status = callback(&entry, user_data);
        free(entry_path);

        if (status != FORGE_OK) {
            break;
        }
    }

    if (fclose(file) == EOF && status == FORGE_OK) {
        status = FORGE_ERROR_IO;
    }

    return status;
}
