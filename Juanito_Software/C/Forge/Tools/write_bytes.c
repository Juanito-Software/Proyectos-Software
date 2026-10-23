
#include <stdio.h>

int main(void)
{
    const unsigned char bytes[] = {
        0x46, 0x47, 0x41, 0x31, 0x00
    };

    FILE *file = fopen("sample.bin", "wb");

    if (file == NULL) {
        perror("No se pudo abrir sample.bin");
        return 1;
    }

    size_t written = fwrite(bytes, 1, sizeof bytes, file);

    if (written != sizeof bytes) {
        perror("Error al escribir los bytes");
        fclose(file);
        return 1;
    }

    if (fclose(file) == EOF) {
        perror("Error al cerrar el archivo");
        return 1;
    }

    printf("Se han escrito %zu bytes en sample.bin\n", written);

    return 0;
}
