
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "forge.h"
#include "forge_fga2_internal.h"

static uint64_t deserialize_u64_le(const unsigned char in[8])
{
    uint64_t value = 0;

    for (unsigned int i = 0; i < 8; i++) {
        value |= (uint64_t)in[i] << (8u * i);
    }

    return value;
}

static ForgeStatus forge_validate_fga1(const char *path)
{
    if (path == NULL || path[0] == '\0') {
        return FORGE_ERROR_ARGUMENT;
    }

    FILE *file = fopen(path, "rb");

    if (file == NULL) {
        return FORGE_ERROR_IO;
    }

    unsigned char header[FORGE_HEADER_SIZE];
    size_t count = fread(header, 1, sizeof header, file);

    if (count != sizeof header) {
        ForgeStatus status = ferror(file)
            ? FORGE_ERROR_IO
            : FORGE_ERROR_FORMAT;

        (void)fclose(file);
        return status;
    }

    const unsigned char expected_magic[4] = {
        0x46, 0x47, 0x41, 0x31
    };

    if (memcmp(header, expected_magic, sizeof expected_magic) != 0) {
        (void)fclose(file);
        return FORGE_ERROR_FORMAT;
    }

    if (header[4] != FORGE_FORMAT_VERSION) {
        (void)fclose(file);
        return FORGE_ERROR_VERSION;
    }

    if (header[5] != 0) {
        (void)fclose(file);
        return FORGE_ERROR_UNSUPPORTED;
    }

    uint64_t original_size = deserialize_u64_le(header + 6);
    uint64_t data_size = deserialize_u64_le(header + 14);

    if (original_size != data_size) {
        (void)fclose(file);
        return FORGE_ERROR_FORMAT;
    }

    if (data_size > UINT64_MAX - (uint64_t)FORGE_HEADER_SIZE) {
        (void)fclose(file);
        return FORGE_ERROR_LIMIT;
    }

    uint64_t payload_size = 0;
    unsigned char buffer[4096];

    for (;;) {
        size_t n = fread(buffer, 1, sizeof buffer, file);

        if (ferror(file)) {
            (void)fclose(file);
            return FORGE_ERROR_IO;
        }

        if ((uint64_t)n > UINT64_MAX - payload_size) {
            (void)fclose(file);
            return FORGE_ERROR_LIMIT;
        }

        payload_size += (uint64_t)n;

        if (payload_size > data_size) {
            (void)fclose(file);
            return FORGE_ERROR_FORMAT;
        }

        if (n < sizeof buffer) {
            break;
        }
    }

    if (payload_size != data_size) {
        (void)fclose(file);
        return FORGE_ERROR_FORMAT;
    }

    if (fclose(file) == EOF) {
        return FORGE_ERROR_IO;
    }

    return FORGE_OK;
}


ForgeStatus forge_validate(const char *path)
{
    if (path == NULL || path[0] == '\0') {
        return FORGE_ERROR_ARGUMENT;
    }

    FILE *file = fopen(path, "rb");
    if (file == NULL) {
        return FORGE_ERROR_IO;
    }

    unsigned char magic[4];
    size_t count = fread(magic, 1, sizeof magic, file);
    ForgeStatus status = FORGE_OK;

    if (count != sizeof magic) {
        status = ferror(file) ? FORGE_ERROR_IO : FORGE_ERROR_FORMAT;
    }

    if (fclose(file) == EOF && status == FORGE_OK) {
        status = FORGE_ERROR_IO;
    }
    if (status != FORGE_OK) {
        return status;
    }

    const unsigned char fga1_magic[4] = {0x46, 0x47, 0x41, 0x31};
    const unsigned char fga2_magic[4] = {
        FORGE_FGA2_MAGIC_0, FORGE_FGA2_MAGIC_1,
        FORGE_FGA2_MAGIC_2, FORGE_FGA2_MAGIC_3
    };

    if (memcmp(magic, fga1_magic, sizeof magic) == 0) {
        return forge_validate_fga1(path);
    }

    if (memcmp(magic, fga2_magic, sizeof magic) == 0) {
        file = fopen(path, "rb");
        if (file == NULL) {
            return FORGE_ERROR_IO;
        }
        status = forge_fga2_validate(file, NULL, NULL, NULL);
        if (fclose(file) == EOF && status == FORGE_OK) {
            status = FORGE_ERROR_IO;
        }
        return status;
    }

    return FORGE_ERROR_FORMAT;
}
