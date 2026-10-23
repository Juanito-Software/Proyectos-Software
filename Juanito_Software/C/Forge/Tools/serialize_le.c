
#include <stdint.h>
#include <stdio.h>

static void serialize_u16_le(uint16_t value, unsigned char out[2])
{
    for (unsigned int i = 0; i < 2; i++) {
        out[i] = (unsigned char)((value >> (8u * i)) & 0xFFu);
    }
}

static void serialize_u32_le(uint32_t value, unsigned char out[4])
{
    for (unsigned int i = 0; i < 4; i++) {
        out[i] = (unsigned char)((value >> (8u * i)) & 0xFFu);
    }
}

static void serialize_u64_le(uint64_t value, unsigned char out[8])
{
    for (unsigned int i = 0; i < 8; i++) {
        out[i] = (unsigned char)((value >> (8u * i)) & UINT64_C(0xFF));
    }
}

int main(void)
{
    unsigned char output[14];

    serialize_u16_le(UINT16_C(0x1234), output);
    serialize_u32_le(UINT32_C(0x12345678), output + 2);
    serialize_u64_le(UINT64_C(0x0123456789ABCDEF), output + 6);

    FILE *file = fopen("sample_le.bin", "wb");

    if (file == NULL) {
        perror("No se pudo abrir sample_le.bin");
        return 1;
    }

    size_t written = fwrite(output, 1, sizeof output, file);

    if (written != sizeof output) {
        perror("Error al escribir sample_le.bin");
        (void)fclose(file);
        return 1;
    }

    if (fclose(file) == EOF) {
        perror("Error al cerrar sample_le.bin");
        return 1;
    }

    printf("Se han serializado %zu bytes correctamente.\n", written);

    return 0;
}
