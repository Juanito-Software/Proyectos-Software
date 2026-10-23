
#include "forge_fga2_internal.h"

#include <stddef.h>

/* ---------- Escritura de enteros little-endian ---------- */

static ForgeStatus write_exact(
    FILE *file,
    const unsigned char *buffer,
    size_t size
)
{
    if (file == NULL) {
        return FORGE_ERROR_ARGUMENT;
    }

    if (fwrite(buffer, 1, size, file) == size) {
        return FORGE_OK;
    }

    return FORGE_ERROR_IO;
}

ForgeStatus forge_fga2_write_u16_le(FILE *file, uint16_t value)
{
    unsigned char bytes[2] = {
        (unsigned char)(value & 0xFFu),
        (unsigned char)((value >> 8) & 0xFFu)
    };

    return write_exact(file, bytes, sizeof bytes);
}

ForgeStatus forge_fga2_write_u32_le(FILE *file, uint32_t value)
{
    unsigned char bytes[4] = {
        (unsigned char)(value & 0xFFu),
        (unsigned char)((value >> 8) & 0xFFu),
        (unsigned char)((value >> 16) & 0xFFu),
        (unsigned char)((value >> 24) & 0xFFu)
    };

    return write_exact(file, bytes, sizeof bytes);
}

ForgeStatus forge_fga2_write_u64_le(FILE *file, uint64_t value)
{
    unsigned char bytes[8];

    for (unsigned int i = 0; i < 8; ++i) {
        bytes[i] = (unsigned char)((value >> (i * 8u)) & 0xFFu);
    }

    return write_exact(file, bytes, sizeof bytes);
}

/* ---------- Encabezado FGA2 ---------- */

ForgeStatus forge_fga2_write_header(
    FILE *file,
    uint64_t original_size,
    uint64_t data_size,
    uint32_t entry_count
)
{
    if (file == NULL) {
        return FORGE_ERROR_ARGUMENT;
    }

    const unsigned char prefix[6] = {
        FORGE_FGA2_MAGIC_0,
        FORGE_FGA2_MAGIC_1,
        FORGE_FGA2_MAGIC_2,
        FORGE_FGA2_MAGIC_3,
        FORGE_FGA2_FORMAT_VERSION,
        FORGE_FGA2_SUPPORTED_FLAGS
    };

    ForgeStatus status = write_exact(file, prefix, sizeof prefix);

    if (status != FORGE_OK) {
        return status;
    }

    status = forge_fga2_write_u64_le(file, original_size);

    if (status != FORGE_OK) {
        return status;
    }

    status = forge_fga2_write_u64_le(file, data_size);

    if (status != FORGE_OK) {
        return status;
    }

    return forge_fga2_write_u32_le(file, entry_count);
}

/* ---------- Cabecera fija de una entrada ---------- */

ForgeStatus forge_fga2_write_entry_header(
    FILE *file,
    uint16_t path_length,
    uint8_t entry_type,
    uint8_t entry_flags,
    uint64_t original_size,
    uint64_t stored_size,
    uint64_t data_offset
)
{
    if (file == NULL) {
        return FORGE_ERROR_ARGUMENT;
    }

    ForgeStatus status = forge_fga2_write_u16_le(file, path_length);

    if (status != FORGE_OK) {
        return status;
    }

    const unsigned char type_and_flags[2] = {
        entry_type,
        entry_flags
    };

    status = write_exact(file, type_and_flags, sizeof type_and_flags);

    if (status != FORGE_OK) {
        return status;
    }

    status = forge_fga2_write_u64_le(file, original_size);

    if (status != FORGE_OK) {
        return status;
    }

    status = forge_fga2_write_u64_le(file, stored_size);

    if (status != FORGE_OK) {
        return status;
    }

    return forge_fga2_write_u64_le(file, data_offset);
}
