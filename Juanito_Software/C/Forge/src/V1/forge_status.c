
#include "forge.h"

const char *forge_status_string(ForgeStatus status)
{
    switch (status) {
        case FORGE_OK:
            return "Operación completada correctamente";

        case FORGE_ERROR_ARGUMENT:
            return "Argumento inválido";

        case FORGE_ERROR_IO:
            return "Error de entrada/salida";

        case FORGE_ERROR_FORMAT:
            return "Formato FGA inválido o archivo corrupto";

        case FORGE_ERROR_VERSION:
            return "Versión del formato no compatible";

        case FORGE_ERROR_UNSUPPORTED:
            return "Funcionalidad no soportada";

        case FORGE_ERROR_MEMORY:
            return "Error al reservar memoria";

        case FORGE_ERROR_LIMIT:
            return "Se ha superado un límite permitido";

        default:
            return "Estado de Forge desconocido";
    }
}