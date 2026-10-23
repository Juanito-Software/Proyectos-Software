
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "forge.h"
#include "forge_fga2_internal.h"

static uint64_t deserialize_u64_le(const unsigned char in[8])
{
    uint64_t value = 0;

    for (unsigned int i = 0; i < 8; ++i) {
        value |= (uint64_t)in[i] << (8u * i);
    }

    return value;
}

static ForgeStatus forge_info_fga1(
    FILE *file,
    uint64_t *original_size,
    uint64_t *data_size)
{
    unsigned char header[FORGE_HEADER_SIZE];

    if (fseek(file, 0, SEEK_SET) != 0) {
        return FORGE_ERROR_IO;
    }

    if (fread(header, 1, sizeof header, file) != sizeof header) {
        return ferror(file)
            ? FORGE_ERROR_IO
            : FORGE_ERROR_FORMAT;
    }

    const unsigned char expected_magic[4] = {
        0x46, 0x47, 0x41, 0x31
    };

    if (memcmp(header, expected_magic, sizeof expected_magic) != 0) {
        return FORGE_ERROR_FORMAT;
    }

    if (header[4] != FORGE_FORMAT_VERSION) {
        return FORGE_ERROR_VERSION;
    }

    if (header[5] != 0) {
        return FORGE_ERROR_UNSUPPORTED;
    }

    uint64_t parsed_original_size =
        deserialize_u64_le(header + 6);

    uint64_t parsed_data_size =
        deserialize_u64_le(header + 14);

    if (parsed_original_size != parsed_data_size) {
        return FORGE_ERROR_FORMAT;
    }

    if (parsed_data_size >
        UINT64_MAX - (uint64_t)FORGE_HEADER_SIZE) {
        return FORGE_ERROR_LIMIT;
    }

    if (fseek(file, 0, SEEK_END) != 0) {
        return FORGE_ERROR_IO;
    }

    long file_size = ftell(file);

    if (file_size < 0) {
        return FORGE_ERROR_IO;
    }

    if ((uint64_t)file_size < (uint64_t)FORGE_HEADER_SIZE ||
        (uint64_t)file_size - (uint64_t)FORGE_HEADER_SIZE
            != parsed_data_size) {
        return FORGE_ERROR_FORMAT;
    }

    *original_size = parsed_original_size;
    *data_size = parsed_data_size;

    return FORGE_OK;
}

ForgeStatus forge_info(
    const char *path,
    uint64_t *original_size,
    uint64_t *data_size)
{
    if (path == NULL || path[0] == '\0' ||
        original_size == NULL || data_size == NULL) {
        return FORGE_ERROR_ARGUMENT;
    }

    FILE *file = fopen(path, "rb");

    if (file == NULL) {
        return FORGE_ERROR_IO;
    }

    unsigned char magic[4];

    size_t bytes_read = fread(magic, 1, sizeof magic, file);

    if (bytes_read != sizeof magic) {
        ForgeStatus status = ferror(file)
            ? FORGE_ERROR_IO
            : FORGE_ERROR_FORMAT;

        if (fclose(file) == EOF && status == FORGE_OK) {
            status = FORGE_ERROR_IO;
        }

        return status;
    }

    const unsigned char fga1_magic[4] = {
        0x46, 0x47, 0x41, 0x31
    };

    const unsigned char fga2_magic[4] = {
        FORGE_FGA2_MAGIC_0,
        FORGE_FGA2_MAGIC_1,
        FORGE_FGA2_MAGIC_2,
        FORGE_FGA2_MAGIC_3
    };

    ForgeStatus status;

    if (memcmp(magic, fga1_magic, sizeof magic) == 0) {
        uint64_t parsed_original_size = 0;
        uint64_t parsed_data_size = 0;

        status = forge_info_fga1(
            file,
            &parsed_original_size,
            &parsed_data_size
        );

        if (fclose(file) == EOF && status == FORGE_OK) {
            status = FORGE_ERROR_IO;
        }

        if (status != FORGE_OK) {
            return status;
        }

        *original_size = parsed_original_size;
        *data_size = parsed_data_size;

        return FORGE_OK;
    }

    if (memcmp(magic, fga2_magic, sizeof magic) == 0) {
        if (fclose(file) == EOF) {
            return FORGE_ERROR_IO;
        }

        return forge_fga2_info(
            path,
            original_size,
            data_size,
            NULL
        );
    }

    if (fclose(file) == EOF) {
        return FORGE_ERROR_IO;
    }

    return FORGE_ERROR_FORMAT;
}
