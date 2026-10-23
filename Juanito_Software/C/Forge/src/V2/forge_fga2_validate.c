
#include "forge_fga2_internal.h"

#include <limits.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

/* ---------- Lectura y decodificación ---------- */

static uint16_t read_u16_le(const unsigned char bytes[2])
{
    return (uint16_t)(
        (uint16_t)bytes[0] |
        ((uint16_t)bytes[1] << 8)
    );
}

static uint32_t read_u32_le(const unsigned char bytes[4])
{
    return (uint32_t)bytes[0]
        | ((uint32_t)bytes[1] << 8)
        | ((uint32_t)bytes[2] << 16)
        | ((uint32_t)bytes[3] << 24);
}

static uint64_t read_u64_le(const unsigned char bytes[8])
{
    uint64_t value = 0;

    for (unsigned int i = 0; i < 8; ++i) {
        value |= (uint64_t)bytes[i] << (i * 8u);
    }

    return value;
}

static ForgeStatus read_exact(FILE *file, void *buffer, size_t size)
{
    if (fread(buffer, 1, size, file) == size) {
        return FORGE_OK;
    }

    return ferror(file) ? FORGE_ERROR_IO : FORGE_ERROR_FORMAT;
}

/*
 * En Windows usamos las funciones de posicionamiento de 64 bits.
 * En otras plataformas utilizamos fseek/ftell.
 */
static bool seek_absolute(FILE *file, uint64_t offset)
{
#ifdef _WIN32
    if (offset > (uint64_t)LLONG_MAX) {
        return false;
    }

    return _fseeki64(file, (__int64)offset, SEEK_SET) == 0;
#else
    if (offset > (uint64_t)LONG_MAX) {
        return false;
    }

    return fseek(file, (long)offset, SEEK_SET) == 0;
#endif
}

static bool get_file_size(FILE *file, uint64_t *size)
{
#ifdef _WIN32
    if (_fseeki64(file, 0, SEEK_END) != 0) {
        return false;
    }

    __int64 position = _ftelli64(file);

    if (position < 0) {
        return false;
    }

    *size = (uint64_t)position;
#else
    if (fseek(file, 0, SEEK_END) != 0) {
        return false;
    }

    long position = ftell(file);

    if (position < 0) {
        return false;
    }

    *size = (uint64_t)position;
#endif

    return true;
}

/* ---------- Validación de UTF-8 ---------- */

/*
 * UTF-8 estricto:
 * - rechaza secuencias incompletas;
 * - rechaza codificaciones overlong;
 * - rechaza sustitutos UTF-16;
 * - rechaza puntos de código superiores a U+10FFFF.
 */
static bool is_valid_utf8(const unsigned char *text, size_t length)
{
    size_t i = 0;

    while (i < length) {
        unsigned char first = text[i];

        if (first <= 0x7Fu) {
            ++i;
            continue;
        }

        if (first >= 0xC2u && first <= 0xDFu) {
            if (length - i < 2 ||
                (text[i + 1] & 0xC0u) != 0x80u) {
                return false;
            }

            i += 2;
            continue;
        }

        if (first >= 0xE0u && first <= 0xEFu) {
            if (length - i < 3) {
                return false;
            }

            unsigned char second = text[i + 1];
            unsigned char third = text[i + 2];

            if ((second & 0xC0u) != 0x80u ||
                (third & 0xC0u) != 0x80u) {
                return false;
            }

            if (first == 0xE0u && second < 0xA0u) {
                return false;
            }

            if (first == 0xEDu && second >= 0xA0u) {
                return false;
            }

            i += 3;
            continue;
        }

        if (first >= 0xF0u && first <= 0xF4u) {
            if (length - i < 4) {
                return false;
            }

            unsigned char second = text[i + 1];
            unsigned char third = text[i + 2];
            unsigned char fourth = text[i + 3];

            if ((second & 0xC0u) != 0x80u ||
                (third & 0xC0u) != 0x80u ||
                (fourth & 0xC0u) != 0x80u) {
                return false;
            }

            if (first == 0xF0u && second < 0x90u) {
                return false;
            }

            if (first == 0xF4u && second > 0x8Fu) {
                return false;
            }

            i += 4;
            continue;
        }

        return false;
    }

    return true;
}

/* ---------- Validación de rutas ---------- */

static unsigned char ascii_lower(unsigned char c)
{
    if (c >= 'A' && c <= 'Z') {
        return (unsigned char)(c + ('a' - 'A'));
    }

    return c;
}

/*
 * Windows reserva una serie de nombres de dispositivo en todos los
 * directorios. CreateFileA("...\\CON") abre el dispositivo, no un
 * archivo dentro del destino de extracción.
 *
 * La comparación es insensible a mayúsculas y se aplica al nombre
 * base (antes del primer punto), de modo que "NUL.txt" también se
 * rechaza.
 */
static bool component_is_reserved_device(
    const unsigned char *component,
    size_t length
)
{
    static const char *const names[] = {
        "CON", "PRN", "AUX", "NUL",
        "CLOCK$", "CONIN$", "CONOUT$",
        "COM1", "COM2", "COM3", "COM4", "COM5",
        "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5",
        "LPT6", "LPT7", "LPT8", "LPT9",
        /* Windows también reconoce los dígitos superíndice. */
        "COM\xC2\xB9", "COM\xC2\xB2", "COM\xC2\xB3",
        "LPT\xC2\xB9", "LPT\xC2\xB2", "LPT\xC2\xB3"
    };

    size_t base_length = 0;

    while (base_length < length && component[base_length] != '.') {
        ++base_length;
    }

    /*
     * Windows ignora espacios y puntos finales al resolver el
     * nombre del dispositivo.
     */
    while (base_length > 0 &&
           (component[base_length - 1] == ' ' ||
            component[base_length - 1] == '.')) {
        --base_length;
    }

    for (size_t i = 0; i < sizeof names / sizeof names[0]; ++i) {
        const char *name = names[i];
        size_t name_length = strlen(name);

        if (name_length != base_length) {
            continue;
        }

        bool equal = true;

        for (size_t j = 0; j < name_length; ++j) {
            if (ascii_lower(component[j]) !=
                ascii_lower((unsigned char)name[j])) {
                equal = false;
                break;
            }
        }

        if (equal) {
            return true;
        }
    }

    return false;
}

static bool component_is_valid(
    const unsigned char *component,
    size_t length
)
{
    if (length == 0) {
        return false;
    }

    /*
     * Windows elimina los puntos y espacios finales de cada
     * componente. Aceptarlos permitiría que dos rutas distintas
     * del archivo acaben apuntando al mismo nombre en disco
     * ("evil." y "evil"), incluidas variantes de "..".
     */
    if (component[length - 1] == '.' ||
        component[length - 1] == ' ') {
        return false;
    }

    if ((length == 1 && component[0] == '.') ||
        (length == 2 &&
         component[0] == '.' &&
         component[1] == '.')) {
        return false;
    }

    if (component_is_reserved_device(component, length)) {
        return false;
    }

    return true;
}

bool forge_fga2_path_is_valid(
    const unsigned char *path,
    size_t length
)
{
    size_t component_start = 0;

    if (path == NULL || length == 0 || path[0] == '/') {
        return false;
    }

    if (!is_valid_utf8(path, length)) {
        return false;
    }

    for (size_t i = 0; i < length; ++i) {
        unsigned char c = path[i];

        /*
         * No admitimos controles ASCII, DEL, barra invertida
         * ni dos puntos en las rutas serializadas.
         */
        if (c < 0x20u || c == 0x7Fu ||
            c == '\\' || c == ':') {
            return false;
        }

        if (c == '/') {
            if (!component_is_valid(
                    path + component_start,
                    i - component_start)) {
                return false;
            }

            component_start = i + 1;
        }
    }

    return component_is_valid(
        path + component_start,
        length - component_start
    );
}

/*
 * Orden lexicográfico estricto por bytes.
 * No depende de la configuración regional.
 */
static bool path_is_less(
    const unsigned char *a,
    size_t a_length,
    const unsigned char *b,
    size_t b_length
)
{
    size_t common_length =
        a_length < b_length ? a_length : b_length;

    int comparison = memcmp(a, b, common_length);

    if (comparison != 0) {
        return comparison < 0;
    }

    return a_length < b_length;
}

/* ---------- Índice auxiliar de rutas ---------- */

/*
 * Conservamos referencias a las rutas dentro del propio archivo,
 * no copias de todas ellas en memoria.
 */
typedef struct {
    uint64_t path_offset;
    uint64_t case_hash;
    uint16_t path_length;
    unsigned char entry_type;
} ForgeFga2PathRef;

/*
 * Hash FNV-1a sobre la ruta plegada a minúsculas ASCII.
 *
 * Windows compara nombres sin distinguir mayúsculas, por lo que
 * dos rutas que solo difieren en ASCII superior/inferior producen
 * el mismo nombre en disco. Se rechazan durante la validación.
 */
static uint64_t path_case_hash(
    const unsigned char *path,
    size_t length
)
{
    uint64_t hash = 1469598103934665603ULL;

    for (size_t i = 0; i < length; ++i) {
        hash ^= (uint64_t)ascii_lower(path[i]);
        hash *= 1099511628211ULL;
    }

    hash ^= (uint64_t)length;
    hash *= 1099511628211ULL;

    return hash;
}

static bool path_case_equal(
    const unsigned char *a,
    size_t a_length,
    const unsigned char *b,
    size_t b_length
)
{
    if (a_length != b_length) {
        return false;
    }

    for (size_t i = 0; i < a_length; ++i) {
        if (ascii_lower(a[i]) != ascii_lower(b[i])) {
            return false;
        }
    }

    return true;
}

/*
 * Busca una ruta exacta entre las entradas ya procesadas.
 *
 * Precondición: entries está ordenado lexicográficamente
 * y solo contiene entradas anteriores a la ruta actual.
 */
static ForgeStatus find_path(
    FILE *file,
    const ForgeFga2PathRef *entries,
    size_t count,
    const unsigned char *target,
    size_t target_length,
    bool *found,
    unsigned char *found_type
)
{
    size_t low = 0;
    size_t high = count;

    *found = false;

    while (low < high) {
        size_t mid = low + (high - low) / 2;
        const ForgeFga2PathRef *entry = &entries[mid];

        unsigned char *stored_path = malloc(entry->path_length);

        if (stored_path == NULL) {
            return FORGE_ERROR_MEMORY;
        }

        if (!seek_absolute(file, entry->path_offset)) {
            free(stored_path);
            return ferror(file) ? FORGE_ERROR_IO : FORGE_ERROR_LIMIT;
        }

        ForgeStatus status = read_exact(
            file,
            stored_path,
            entry->path_length
        );

        if (status != FORGE_OK) {
            free(stored_path);
            return status;
        }

        size_t common_length =
            entry->path_length < target_length
                ? entry->path_length
                : target_length;

        int comparison = memcmp(
            stored_path,
            target,
            common_length
        );

        if (comparison == 0) {
            if ((size_t)entry->path_length < target_length) {
                comparison = -1;
            } else if ((size_t)entry->path_length > target_length) {
                comparison = 1;
            }
        }

        free(stored_path);

        if (comparison == 0) {
            *found = true;
            *found_type = entry->entry_type;
            return FORGE_OK;
        }

        if (comparison < 0) {
            low = mid + 1;
        } else {
            high = mid;
        }
    }

    return FORGE_OK;
}

/*
 * Cada componente padre debe existir explícitamente como directorio.
 *
 * Ejemplo:
 *   assets/images/logo.png
 *
 * Requiere las entradas:
 *   assets          directorio
 *   assets/images   directorio
 *   assets/images/logo.png  fichero
 */
static ForgeStatus validate_path_parents(
    FILE *file,
    const ForgeFga2PathRef *entries,
    size_t count,
    const unsigned char *path,
    size_t path_length
)
{
    for (size_t i = 0; i < path_length; ++i) {
        if (path[i] != '/') {
            continue;
        }

        bool found;
        unsigned char parent_type = 0;

        ForgeStatus status = find_path(
            file,
            entries,
            count,
            path,
            i,
            &found,
            &parent_type
        );

        if (status != FORGE_OK) {
            return status;
        }

        if (!found || parent_type != FORGE_FGA2_ENTRY_DIRECTORY) {
            return FORGE_ERROR_FORMAT;
        }
    }

    return FORGE_OK;
}

/* ---------- Validador principal ---------- */

ForgeStatus forge_fga2_validate(
    FILE *file,
    uint64_t *original_size,
    uint64_t *data_size,
    uint32_t *entry_count
)
{
    unsigned char header[FORGE_FGA2_HEADER_SIZE];
    uint64_t actual_file_size;
    uint64_t declared_original_size;
    uint64_t declared_data_size;
    uint64_t index_end;
    uint64_t index_size = 0;
    uint64_t accumulated_original_size = 0;
    uint64_t accumulated_data_size = 0;
    uint32_t declared_entry_count;

    unsigned char *previous_path = NULL;
    size_t previous_path_length = 0;

    ForgeFga2PathRef *path_refs = NULL;
    uint32_t *case_table = NULL;
    size_t case_capacity = 0;
    ForgeStatus status;

    if (file == NULL) {
        return FORGE_ERROR_ARGUMENT;
    }

    if (!seek_absolute(file, 0)) {
        return ferror(file) ? FORGE_ERROR_IO : FORGE_ERROR_LIMIT;
    }

    status = read_exact(file, header, sizeof header);

    if (status != FORGE_OK) {
        return status;
    }

    /* Magic FGA2. */
    if (header[0] != FORGE_FGA2_MAGIC_0 ||
        header[1] != FORGE_FGA2_MAGIC_1 ||
        header[2] != FORGE_FGA2_MAGIC_2 ||
        header[3] != FORGE_FGA2_MAGIC_3) {
        return FORGE_ERROR_FORMAT;
    }

    if (header[4] != FORGE_FGA2_FORMAT_VERSION) {
        return FORGE_ERROR_VERSION;
    }

    if (header[5] != FORGE_FGA2_SUPPORTED_FLAGS) {
        return FORGE_ERROR_UNSUPPORTED;
    }

    declared_original_size = read_u64_le(&header[6]);
    declared_data_size = read_u64_le(&header[14]);
    declared_entry_count = read_u32_le(&header[22]);

    if (declared_entry_count > FORGE_FGA2_MAX_ENTRIES) {
        return FORGE_ERROR_LIMIT;
    }

    if (!get_file_size(file, &actual_file_size)) {
        return FORGE_ERROR_IO;
    }

    /*
     * Los datos ocupan los últimos DataSize bytes.
     * El índice debe caber entre el encabezado y los datos.
     */
    if (actual_file_size < FORGE_FGA2_HEADER_SIZE ||
        declared_data_size >
            actual_file_size - FORGE_FGA2_HEADER_SIZE) {
        return FORGE_ERROR_FORMAT;
    }

    index_end = actual_file_size - declared_data_size;

    if (index_end < FORGE_FGA2_HEADER_SIZE) {
        return FORGE_ERROR_FORMAT;
    }

    if (index_end - FORGE_FGA2_HEADER_SIZE >
        FORGE_FGA2_MAX_INDEX_SIZE) {
        return FORGE_ERROR_LIMIT;
    }

    /*
     * Cada entrada necesita al menos su cabecera fija. Comprobar
     * esto antes de reservar evita que una cabecera pequeña con
     * un contador enorme provoque una reserva de memoria grande.
     */
    if ((index_end - FORGE_FGA2_HEADER_SIZE) /
            FORGE_FGA2_ENTRY_FIXED_SIZE <
        (uint64_t)declared_entry_count) {
        return FORGE_ERROR_FORMAT;
    }

    if (!seek_absolute(file, FORGE_FGA2_HEADER_SIZE)) {
        return ferror(file) ? FORGE_ERROR_IO : FORGE_ERROR_LIMIT;
    }

    /*
     * Reservamos metadatos compactos, no las rutas completas.
     * El número de entradas ya está limitado por el formato,
     * por FORGE_FGA2_MAX_ENTRIES y por el tamaño del índice.
     */
    if (declared_entry_count > 0) {
        path_refs = calloc(
            (size_t)declared_entry_count,
            sizeof *path_refs
        );

        if (path_refs == NULL) {
            return FORGE_ERROR_MEMORY;
        }

        /*
         * Tabla de direcciones abierta para detectar rutas que
         * solo difieren en mayúsculas ASCII. Capacidad >= 2n
         * mantiene la ocupación por debajo del 50 %.
         */
        size_t required = (size_t)declared_entry_count * 2u;

        case_capacity = 1;

        while (case_capacity < required) {
            if (case_capacity > SIZE_MAX / 2u) {
                free(path_refs);
                return FORGE_ERROR_LIMIT;
            }

            case_capacity *= 2u;
        }

        case_table = calloc(case_capacity, sizeof *case_table);

        if (case_table == NULL) {
            free(path_refs);
            return FORGE_ERROR_MEMORY;
        }
    }

    for (uint32_t entry_index = 0;
         entry_index < declared_entry_count;
         ++entry_index) {

        unsigned char fixed[FORGE_FGA2_ENTRY_FIXED_SIZE];
        uint16_t path_length;
        unsigned char entry_type;
        unsigned char entry_flags;
        uint64_t entry_original_size;
        uint64_t entry_stored_size;
        uint64_t entry_data_offset;
        unsigned char *path = NULL;

        uint64_t remaining_index =
            index_end - FORGE_FGA2_HEADER_SIZE - index_size;

        if (remaining_index < FORGE_FGA2_ENTRY_FIXED_SIZE) {
            status = FORGE_ERROR_FORMAT;
            goto cleanup;
        }

        status = read_exact(file, fixed, sizeof fixed);

        if (status != FORGE_OK) {
            goto cleanup;
        }

        path_length = read_u16_le(&fixed[0]);
        entry_type = fixed[2];
        entry_flags = fixed[3];
        entry_original_size = read_u64_le(&fixed[4]);
        entry_stored_size = read_u64_le(&fixed[12]);
        entry_data_offset = read_u64_le(&fixed[20]);

        if (path_length == 0) {
            status = FORGE_ERROR_FORMAT;
            goto cleanup;
        }

        if (entry_type != FORGE_FGA2_ENTRY_FILE &&
            entry_type != FORGE_FGA2_ENTRY_DIRECTORY) {
            status = FORGE_ERROR_FORMAT;
            goto cleanup;
        }

        if (entry_flags != 0) {
            status = FORGE_ERROR_UNSUPPORTED;
            goto cleanup;
        }

        if ((uint64_t)path_length >
            remaining_index - FORGE_FGA2_ENTRY_FIXED_SIZE) {
            status = FORGE_ERROR_FORMAT;
            goto cleanup;
        }

        index_size +=
            FORGE_FGA2_ENTRY_FIXED_SIZE + (uint64_t)path_length;

        if (index_size > FORGE_FGA2_MAX_INDEX_SIZE) {
            status = FORGE_ERROR_LIMIT;
            goto cleanup;
        }

        path = malloc((size_t)path_length);

        if (path == NULL) {
            status = FORGE_ERROR_MEMORY;
            goto cleanup;
        }

        status = read_exact(file, path, path_length);

        if (status != FORGE_OK) {
            free(path);
            goto cleanup;
        }

        if (!forge_fga2_path_is_valid(path, path_length)) {
            free(path);
            status = FORGE_ERROR_FORMAT;
            goto cleanup;
        }

        /* Las rutas deben estar estrictamente ordenadas. */
        if (previous_path != NULL &&
            !path_is_less(
                previous_path,
                previous_path_length,
                path,
                path_length)) {
            free(path);
            status = FORGE_ERROR_FORMAT;
            goto cleanup;
        }

        /*
         * Validar cada componente padre antes de aceptar la entrada.
         * La búsqueda binaria reposiciona el archivo, por lo que
         * después regresamos al final de la ruta actual.
         */
        status = validate_path_parents(
            file,
            path_refs,
            (size_t)entry_index,
            path,
            path_length
        );

        if (status != FORGE_OK) {
            free(path);
            goto cleanup;
        }

        uint64_t current_index_position =
            FORGE_FGA2_HEADER_SIZE + index_size;

        if (!seek_absolute(file, current_index_position)) {
            free(path);
            status = ferror(file) ? FORGE_ERROR_IO : FORGE_ERROR_LIMIT;
            goto cleanup;
        }

        /*
         * Los datos de cada entrada empiezan exactamente donde
         * terminan los datos de los ficheros anteriores.
         */
        if (entry_data_offset != accumulated_data_size) {
            free(path);
            status = FORGE_ERROR_FORMAT;
            goto cleanup;
        }

        if (entry_type == FORGE_FGA2_ENTRY_DIRECTORY) {
            if (entry_original_size != 0 ||
                entry_stored_size != 0) {
                free(path);
                status = FORGE_ERROR_FORMAT;
                goto cleanup;
            }
        } else {
            /* FGA2 inicial no admite compresión. */
            if (entry_original_size != entry_stored_size) {
                free(path);
                status = FORGE_ERROR_FORMAT;
                goto cleanup;
            }

            if (entry_original_size >
                UINT64_MAX - accumulated_original_size) {
                free(path);
                status = FORGE_ERROR_FORMAT;
                goto cleanup;
            }

            if (accumulated_data_size > declared_data_size ||
                entry_stored_size >
                    declared_data_size - accumulated_data_size) {
                free(path);
                status = FORGE_ERROR_FORMAT;
                goto cleanup;
            }

            accumulated_original_size += entry_original_size;
            accumulated_data_size += entry_stored_size;
        }

        /*
         * Registrar la ubicación de la ruta para búsquedas
         * posteriores. index_size incluye el registro actual.
         */
        path_refs[entry_index].path_offset =
            current_index_position - path_length;

        path_refs[entry_index].path_length = path_length;
        path_refs[entry_index].entry_type = entry_type;

        /*
         * Windows no distingue mayúsculas en los nombres. Dos rutas
         * que solo difieren en ASCII superior/inferior colisionarían
         * durante la extracción, por lo que el archivo se rechaza.
         */
        uint64_t case_hash = path_case_hash(path, path_length);
        path_refs[entry_index].case_hash = case_hash;

        size_t slot = (size_t)(
            case_hash & (uint64_t)(case_capacity - 1u)
        );
        bool moved = false;

        for (;;) {
            uint32_t ref_plus_one = case_table[slot];

            if (ref_plus_one == 0) {
                case_table[slot] = entry_index + 1u;
                break;
            }

            const ForgeFga2PathRef *other =
                &path_refs[ref_plus_one - 1u];

            if (other->case_hash == case_hash &&
                other->path_length == path_length) {
                unsigned char *other_path =
                    malloc(other->path_length);

                if (other_path == NULL) {
                    free(path);
                    status = FORGE_ERROR_MEMORY;
                    goto cleanup;
                }

                if (!seek_absolute(file, other->path_offset)) {
                    free(other_path);
                    free(path);
                    status = ferror(file)
                        ? FORGE_ERROR_IO
                        : FORGE_ERROR_LIMIT;
                    goto cleanup;
                }

                status = read_exact(
                    file,
                    other_path,
                    other->path_length
                );

                if (status != FORGE_OK) {
                    free(other_path);
                    free(path);
                    goto cleanup;
                }

                bool same = path_case_equal(
                    other_path,
                    other->path_length,
                    path,
                    path_length
                );

                free(other_path);
                moved = true;

                if (same) {
                    free(path);
                    status = FORGE_ERROR_FORMAT;
                    goto cleanup;
                }
            }

            slot = (slot + 1u) & (case_capacity - 1u);
        }

        if (moved && !seek_absolute(file, current_index_position)) {
            free(path);
            status = ferror(file) ? FORGE_ERROR_IO : FORGE_ERROR_LIMIT;
            goto cleanup;
        }

        free(previous_path);
        previous_path = path;
        previous_path_length = path_length;
    }

    /*
     * El índice debe terminar exactamente donde comienzan
     * los datos; no se permiten bytes sobrantes entre ambos.
     */
    if (index_size != index_end - FORGE_FGA2_HEADER_SIZE) {
        status = FORGE_ERROR_FORMAT;
        goto cleanup;
    }

    if (accumulated_original_size != declared_original_size ||
        accumulated_data_size != declared_data_size) {
        status = FORGE_ERROR_FORMAT;
        goto cleanup;
    }

    if (original_size != NULL) {
        *original_size = declared_original_size;
    }

    if (data_size != NULL) {
        *data_size = declared_data_size;
    }

    if (entry_count != NULL) {
        *entry_count = declared_entry_count;
    }

    status = FORGE_OK;

cleanup:
    free(previous_path);
    free(case_table);
    free(path_refs);

    return status;
}
