
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "forge.h"
#include "forge_fga2_internal.h"

#define COPY_BUFFER_SIZE 4096u

static uint64_t deserialize_u64_le(const unsigned char in[8])
{
    uint64_t value = 0;

    for (unsigned int i = 0; i < 8; i++) {
        value |= (uint64_t)in[i] << (8u * i);
    }

    return value;
}

static ForgeStatus read_fga_header(
    FILE *source,
    uint64_t *original_size,
    uint64_t *data_size)
{
    unsigned char header[FORGE_HEADER_SIZE];

    size_t count = fread(header, 1, sizeof header, source);

    if (count != sizeof header) {
        return ferror(source)
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

    *original_size = deserialize_u64_le(header + 6);
    *data_size = deserialize_u64_le(header + 14);

    if (*original_size != *data_size) {
        return FORGE_ERROR_FORMAT;
    }

    if (*data_size > UINT64_MAX - (uint64_t)FORGE_HEADER_SIZE) {
        return FORGE_ERROR_LIMIT;
    }

    return FORGE_OK;
}

static ForgeStatus validate_payload(FILE *source, uint64_t data_size)
{
    unsigned char buffer[COPY_BUFFER_SIZE];
    uint64_t payload_size = 0;

    for (;;) {
        size_t n = fread(buffer, 1, sizeof buffer, source);

        if (ferror(source)) {
            return FORGE_ERROR_IO;
        }

        if ((uint64_t)n > UINT64_MAX - payload_size) {
            return FORGE_ERROR_LIMIT;
        }

        payload_size += (uint64_t)n;

        if (payload_size > data_size) {
            return FORGE_ERROR_FORMAT;
        }

        if (n < sizeof buffer) {
            break;
        }
    }

    return payload_size == data_size
        ? FORGE_OK
        : FORGE_ERROR_FORMAT;
}

static ForgeStatus forge_unpack_fga1(
    const char *source_path,
    const char *destination_path)
{
    if (source_path == NULL || source_path[0] == '\0' ||
        destination_path == NULL || destination_path[0] == '\0') {
        return FORGE_ERROR_ARGUMENT;
    }

    if (strcmp(source_path, destination_path) == 0) {
        return FORGE_ERROR_ARGUMENT;
    }

    FILE *source = fopen(source_path, "rb");

    if (source == NULL) {
        return FORGE_ERROR_IO;
    }

    uint64_t original_size = 0;
    uint64_t data_size = 0;

    ForgeStatus status = read_fga_header(
        source,
        &original_size,
        &data_size
    );

    if (status == FORGE_OK) {
        status = validate_payload(source, data_size);
    }

    if (status != FORGE_OK) {
        (void)fclose(source);
        return status;
    }

    /*
     * La validación ha llegado a EOF.
     * Volvemos al inicio del payload, tras la cabecera de 22 bytes.
     */
    if (fseek(source, (long)FORGE_HEADER_SIZE, SEEK_SET) != 0) {
        (void)fclose(source);
        return FORGE_ERROR_IO;
    }

    FILE *destination = fopen(destination_path, "wb");

    if (destination == NULL) {
        (void)fclose(source);
        return FORGE_ERROR_IO;
    }

    unsigned char buffer[COPY_BUFFER_SIZE];
    uint64_t remaining = data_size;

    while (remaining > 0) {
        size_t amount = sizeof buffer;

        if (remaining < (uint64_t)amount) {
            amount = (size_t)remaining;
        }

        size_t n = fread(buffer, 1, amount, source);

        if (n != amount) {
            status = ferror(source)
                ? FORGE_ERROR_IO
                : FORGE_ERROR_FORMAT;
            break;
        }

        if (fwrite(buffer, 1, n, destination) != n) {
            status = FORGE_ERROR_IO;
            break;
        }

        remaining -= (uint64_t)n;
    }

    if (fclose(source) == EOF && status == FORGE_OK) {
        status = FORGE_ERROR_IO;
    }

    if (fclose(destination) == EOF && status == FORGE_OK) {
        status = FORGE_ERROR_IO;
    }

    return status;
}


ForgeStatus forge_unpack(
    const char *source_path,
    const char *destination_path)
{
    if (source_path == NULL || source_path[0] == '\0' ||
        destination_path == NULL || destination_path[0] == '\0') {
        return FORGE_ERROR_ARGUMENT;
    }

    FILE *source = fopen(source_path, "rb");
    if (source == NULL) {
        return FORGE_ERROR_IO;
    }

    unsigned char magic[4];
    size_t count = fread(magic, 1, sizeof magic, source);
    ForgeStatus status = FORGE_OK;
    if (count != sizeof magic) {
        status = ferror(source) ? FORGE_ERROR_IO : FORGE_ERROR_FORMAT;
    }
    if (fclose(source) == EOF && status == FORGE_OK) {
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
        return forge_unpack_fga1(source_path, destination_path);
    }
    if (memcmp(magic, fga2_magic, sizeof magic) == 0) {
        return forge_fga2_unpack(source_path, destination_path);
    }
    return FORGE_ERROR_FORMAT;
}
