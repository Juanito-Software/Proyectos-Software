#include <stdio.h>
#include "forge.h"

int main(int argc, char *argv[])
{
    if (argc != 2) {
        fprintf(stderr, "Uso: consumer <archivo.fga>\n");
        return 2;
    }

    ForgeStatus status = forge_validate(argv[1]);

    if (status != FORGE_OK) {
        fprintf(stderr, "Validación fallida: %s\n",
                forge_status_string(status));
        return 1;
    }

    printf("La biblioteca libforge ha validado correctamente: %s\n",
           argv[1]);

    return 0;
}