
#include <stdint.h>
#include <stdio.h>

static uint16_t deserialize_u16_le(const unsigned char in[2])
{
    uint16_t value = 0;

    for (unsigned int i = 0; i < 2; i++) {
        value |= (uint16_t)((uint16_t)in[i] << (8u * i));
    }

    return value;
}

static uint32_t deserialize_u32_le(const unsigned char in[4])
{
    uint32_t value = 0;

    for (unsigned int i = 0; i < 4; i++) {
        value |= (uint32_t)in[i] << (8u * i);
    }

    return value;
}

static uint64_t deserialize_u64_le(const unsigned char in[8])
{
    uint64_t value = 0;

    for (unsigned int i = 0; i < 8; i++) {
        value |= (uint64_t)in[i] << (8u * i);
    }

    return value;
}

int main(void)
{
    unsigned char bytes[14];

    FILE *file = fopen("sample_le.bin", "rb");

    if (file == NULL) {
        perror("No se pudo abrir sample_le.bin");
        return 1;
    }

    size_t read_count = fread(bytes, 1, sizeof bytes, file);

    if (read_count != sizeof bytes) {
        if (ferror(file)) {
            perror("Error al leer sample_le.bin");
        } else {
            fprintf(stderr, "Error: el archivo tiene menos de 14 bytes.\n");
        }

        (void)fclose(file);
        return 1;
    }

    int extra = fgetc(file);

    if (extra != EOF) {
        fprintf(stderr, "Error: el archivo contiene bytes adicionales.\n");
        (void)fclose(file);
        return 1;
    }

    if (ferror(file)) {
        perror("Error al comprobar el final del archivo");
        (void)fclose(file);
        return 1;
    }

    if (fclose(file) == EOF) {
        perror("Error al cerrar sample_le.bin");
        return 1;
    }

    uint16_t a = deserialize_u16_le(bytes);
    uint32_t b = deserialize_u32_le(bytes + 2);
    uint64_t c = deserialize_u64_le(bytes + 6);

    printf("u16 = 0x%04X\n", (unsigned int)a);
    printf("u32 = 0x%08X\n", (unsigned int)b);
    printf("u64 = 0x%016llX\n", (unsigned long long)c);

    if (a != UINT16_C(0x1234)
        || b != UINT32_C(0x12345678)
        || c != UINT64_C(0x0123456789ABCDEF)) {
        fprintf(stderr, "Error: los valores reconstruidos no coinciden.\n");
        return 1;
    }

    printf("Verificacion correcta: los tres valores coinciden.\n");

    return 0;
}
