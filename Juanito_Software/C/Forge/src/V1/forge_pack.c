
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define WIN32_LEAN_AND_MEAN
#include <windows.h>

#include "forge.h"
#include "forge_fga2_internal.h"

#define COPY_BUFFER_SIZE 4096u

static void serialize_u64_le(uint64_t value, unsigned char out[8])
{
    for (unsigned int i = 0; i < 8; i++) {
        out[i] = (unsigned char)(value >> (8u * i));
    }
}

static ForgeStatus copy_stream(
    FILE *source,
    FILE *destination,
    uint64_t *total_size)
{
    unsigned char buffer[COPY_BUFFER_SIZE];
    uint64_t total = 0;

    for (;;) {
        size_t n = fread(buffer, 1, sizeof buffer, source);

        if (n > 0) {
            if ((uint64_t)n > UINT64_MAX - total) {
                return FORGE_ERROR_LIMIT;
            }

            if (total + (uint64_t)n >
                UINT64_MAX - (uint64_t)FORGE_HEADER_SIZE) {
                return FORGE_ERROR_LIMIT;
            }

            if (fwrite(buffer, 1, n, destination) != n) {
                return FORGE_ERROR_IO;
            }

            total += (uint64_t)n;
        }

        if (n < sizeof buffer) {
            if (ferror(source)) {
                return FORGE_ERROR_IO;
            }

            break;
        }
    }

    *total_size = total;
    return FORGE_OK;
}

ForgeStatus forge_pack(
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

    DWORD source_attributes = GetFileAttributesA(source_path);
    if (source_attributes == INVALID_FILE_ATTRIBUTES) {
        return FORGE_ERROR_IO;
    }
    if ((source_attributes & FILE_ATTRIBUTE_DIRECTORY) != 0) {
        return forge_fga2_pack(source_path, destination_path);
    }
    if ((source_attributes & FILE_ATTRIBUTE_DEVICE) != 0) {
        return FORGE_ERROR_UNSUPPORTED;
    }

    FILE *source = fopen(source_path, "rb");

    if (source == NULL) {
        return FORGE_ERROR_IO;
    }

    FILE *temporary = tmpfile();

    if (temporary == NULL) {
        (void)fclose(source);
        return FORGE_ERROR_IO;
    }

    uint64_t data_size = 0;

    ForgeStatus status = copy_stream(source, temporary, &data_size);

    if (fclose(source) == EOF && status == FORGE_OK) {
        status = FORGE_ERROR_IO;
    }

    if (status == FORGE_OK && fflush(temporary) == EOF) {
        status = FORGE_ERROR_IO;
    }

    if (status == FORGE_OK && fseek(temporary, 0, SEEK_SET) != 0) {
        status = FORGE_ERROR_IO;
    }

    if (status != FORGE_OK) {
        (void)fclose(temporary);
        return status;
    }

    FILE *destination = fopen(destination_path, "wb");

    if (destination == NULL) {
        (void)fclose(temporary);
        return FORGE_ERROR_IO;
    }

    unsigned char header[FORGE_HEADER_SIZE] = {0};

    header[0] = 0x46;
    header[1] = 0x47;
    header[2] = 0x41;
    header[3] = 0x31;
    header[4] = FORGE_FORMAT_VERSION;
    header[5] = 0;

    serialize_u64_le(data_size, header + 6);
    serialize_u64_le(data_size, header + 14);

    if (fwrite(header, 1, sizeof header, destination) != sizeof header) {
        status = FORGE_ERROR_IO;
    }

    uint64_t copied_size = 0;

    if (status == FORGE_OK) {
        status = copy_stream(temporary, destination, &copied_size);
    }

    if (status == FORGE_OK && copied_size != data_size) {
        status = FORGE_ERROR_IO;
    }

    if (fclose(temporary) == EOF && status == FORGE_OK) {
        status = FORGE_ERROR_IO;
    }

    if (fclose(destination) == EOF && status == FORGE_OK) {
        status = FORGE_ERROR_IO;
    }

    return status;
}
