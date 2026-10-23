
#include <stdint.h>
#include <stdio.h>

#define FGA_HEADER_SIZE 22u

static void serialize_u64_le(uint64_t value, unsigned char out[8])
{
    for (unsigned int i = 0; i < 8; i++) {
        out[i] = (unsigned char)((value >> (8u * i)) & UINT64_C(0xFF));
    }
}

int main(void)
{
    unsigned char header[FGA_HEADER_SIZE] = {0};

    const unsigned char magic[4] = {
        0x46, 0x47, 0x41, 0x31
    };

    const unsigned char version = 1;
    const unsigned char flags = 0;

    const uint64_t original_size = UINT64_C(1234);
    const uint64_t data_size = UINT64_C(1234);

    for (size_t i = 0; i < sizeof magic; i++) {
        header[i] = magic[i];
    }

    header[4] = version;
    header[5] = flags;

    serialize_u64_le(original_size, header + 6);
    serialize_u64_le(data_size, header + 14);

    FILE *file = fopen("header.fga", "wb");

    if (file == NULL) {
        perror("No se pudo abrir header.fga");
        return 1;
    }

    size_t written = fwrite(header, 1, sizeof header, file);

    if (written != sizeof header) {
        perror("Error al escribir la cabecera");
        (void)fclose(file);
        return 1;
    }

    if (fclose(file) == EOF) {
        perror("Error al cerrar header.fga");
        return 1;
    }

    printf("Cabecera FGA v1 escrita: %zu bytes.\n", written);

    return 0;
}
