
#include <stdio.h>
#include <stdint.h>

#include "forge_fga2_internal.h"

ForgeStatus forge_fga2_info(
    const char *path,
    uint64_t *original_size,
    uint64_t *data_size,
    uint32_t *entry_count)
{
    if (path == NULL || path[0] == '\0') {
        return FORGE_ERROR_ARGUMENT;
    }

    FILE *file = fopen(path, "rb");

    if (file == NULL) {
        return FORGE_ERROR_IO;
    }

    uint64_t parsed_original_size = 0;
    uint64_t parsed_data_size = 0;
    uint32_t parsed_entry_count = 0;

    ForgeStatus status = forge_fga2_validate(
        file,
        &parsed_original_size,
        &parsed_data_size,
        &parsed_entry_count
    );

    if (fclose(file) == EOF && status == FORGE_OK) {
        status = FORGE_ERROR_IO;
    }

    if (status != FORGE_OK) {
        return status;
    }

    if (original_size != NULL) {
        *original_size = parsed_original_size;
    }

    if (data_size != NULL) {
        *data_size = parsed_data_size;
    }

    if (entry_count != NULL) {
        *entry_count = parsed_entry_count;
    }

    return FORGE_OK;
}
