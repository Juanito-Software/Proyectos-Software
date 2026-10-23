
#ifndef FORGE_H
#define FORGE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define FORGE_VERSION_MAJOR 1
#define FORGE_VERSION_MINOR 0
#define FORGE_VERSION_PATCH 0

#define FORGE_FORMAT_VERSION 1
#define FORGE_HEADER_SIZE 22

typedef enum {
    FORGE_OK = 0,
    FORGE_ERROR_ARGUMENT,
    FORGE_ERROR_IO,
    FORGE_ERROR_FORMAT,
    FORGE_ERROR_VERSION,
    FORGE_ERROR_UNSUPPORTED,
    FORGE_ERROR_MEMORY,
    FORGE_ERROR_LIMIT
} ForgeStatus;

const char *forge_status_string(ForgeStatus status);

ForgeStatus forge_validate(const char *path);

ForgeStatus forge_info(
    const char *path,
    uint64_t *original_size,
    uint64_t *data_size
);

ForgeStatus forge_pack(
    const char *input_path,
    const char *output_path
);

ForgeStatus forge_unpack(
    const char *input_path,
    const char *output_path
);

typedef enum {
    FORGE_ENTRY_FILE = 0,
    FORGE_ENTRY_DIRECTORY = 1
} ForgeEntryType;

typedef struct {
    /* Valid only for the duration of the callback invocation. */
    const char *path;
    ForgeEntryType type;
    uint64_t original_size;
    uint64_t stored_size;
    uint64_t data_offset;
} ForgeEntryInfo;

typedef ForgeStatus (*ForgeEntryCallback)(
    const ForgeEntryInfo *entry,
    void *user_data
);

/* FGA2 only: FGA1 does not store entry paths. */
ForgeStatus forge_list(
    const char *path,
    ForgeEntryCallback callback,
    void *user_data
);

#ifdef __cplusplus
}
#endif

#endif
