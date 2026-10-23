
#include <inttypes.h>
#include <stdio.h>
#include <string.h>

#include "forge.h"

enum ForgeExitCode {
    FORGE_EXIT_SUCCESS = 0,
    FORGE_EXIT_ERROR = 1,
    FORGE_EXIT_USAGE = 2
};

static void print_usage(void)
{
    fprintf(stderr,
            "Uso:\n"
            "  forge pack <origen> <destino.fga>\n"
            "  forge unpack <origen.fga> <destino>\n"
            "  forge info <archivo.fga>\n"
            "  forge list <archivo.fga>\n"
            "  forge validate <archivo.fga>\n");
}

static int report_status(ForgeStatus status)
{
    if (status == FORGE_OK) {
        return FORGE_EXIT_SUCCESS;
    }

    fprintf(stderr, "Error: %s\n", forge_status_string(status));
    return FORGE_EXIT_ERROR;
}

static ForgeStatus print_entry(const ForgeEntryInfo *entry, void *user_data)
{
    (void)user_data;
    const char *type = entry->type == FORGE_ENTRY_DIRECTORY ? "DIR " : "FILE";
    printf("%-4s %12" PRIu64 " %s\n", type, entry->original_size, entry->path);
    return FORGE_OK;
}

static unsigned int read_format_version(const char *path)
{
    FILE *file = fopen(path, "rb");
    if (file == NULL) {
        return 0;
    }
    unsigned char header[5];
    size_t count = fread(header, 1, sizeof header, file);
    (void)fclose(file);
    if (count != sizeof header) {
        return 0;
    }
    if (memcmp(header, "FGA1", 4) == 0 || memcmp(header, "FGA2", 4) == 0) {
        return header[4];
    }
    return 0;
}

int main(int argc, char *argv[])
{
    ForgeStatus status;

    if (argc < 2) {
        print_usage();
        return FORGE_EXIT_USAGE;
    }

    if (strcmp(argv[1], "pack") == 0) {
        if (argc != 4) {
            print_usage();
            return FORGE_EXIT_USAGE;
        }

        status = forge_pack(argv[2], argv[3]);

        if (status != FORGE_OK) {
            return report_status(status);
        }

        printf("Archive FGA created successfully: %s\n", argv[3]);
        return FORGE_EXIT_SUCCESS;
    }

    if (strcmp(argv[1], "unpack") == 0) {
        if (argc != 4) {
            print_usage();
            return FORGE_EXIT_USAGE;
        }

        status = forge_unpack(argv[2], argv[3]);

        if (status != FORGE_OK) {
            return report_status(status);
        }

        printf("Archive extracted successfully: %s\n", argv[3]);
        return FORGE_EXIT_SUCCESS;
    }

    if (strcmp(argv[1], "info") == 0) {
        uint64_t original_size;
        uint64_t data_size;

        if (argc != 3) {
            print_usage();
            return FORGE_EXIT_USAGE;
        }

        status = forge_info(argv[2], &original_size, &data_size);

        if (status != FORGE_OK) {
            return report_status(status);
        }

        printf("Archive: %s\n", argv[2]);
        printf("Format version: %u\n", read_format_version(argv[2]));
        printf("original size: %" PRIu64 " bytes\n", original_size);
        printf("Data size: %" PRIu64 " bytes\n", data_size);

        return FORGE_EXIT_SUCCESS;
    }

    if (strcmp(argv[1], "list") == 0) {
        if (argc != 3) {
            print_usage();
            return FORGE_EXIT_USAGE;
        }
        status = forge_list(argv[2], print_entry, NULL);
        if (status != FORGE_OK) {
            return report_status(status);
        }
        return FORGE_EXIT_SUCCESS;
    }

    if (strcmp(argv[1], "validate") == 0) {
        if (argc != 3) {
            print_usage();
            return FORGE_EXIT_USAGE;
        }

        status = forge_validate(argv[2]);

        if (status != FORGE_OK) {
            return report_status(status);
        }

        printf("Valid Archive FGA: %s\n", argv[2]);
        return FORGE_EXIT_SUCCESS;
    }

    fprintf(stderr, "Error: Unknown command '%s'.\n", argv[1]);
    print_usage();

    return FORGE_EXIT_USAGE;
}
