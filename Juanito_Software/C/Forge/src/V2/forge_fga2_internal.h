#ifndef FORGE_FGA2_INTERNAL_H
#define FORGE_FGA2_INTERNAL_H

#include "forge.h"
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

/*
 * Constantes internas de la implementación FGA2.
 * No forman parte de la API pública de libforge.
 */

/* Encabezado FGA2 */
#define FORGE_FGA2_FORMAT_VERSION 2u
#define FORGE_FGA2_HEADER_SIZE 26u

/* Identificación del contenedor: FGA2 */
#define FORGE_FGA2_MAGIC_0 0x46u
#define FORGE_FGA2_MAGIC_1 0x47u
#define FORGE_FGA2_MAGIC_2 0x41u
#define FORGE_FGA2_MAGIC_3 0x32u

/* Índice */
#define FORGE_FGA2_ENTRY_FIXED_SIZE 28u
#define FORGE_FGA2_MAX_PATH_SIZE UINT16_MAX

/* Límites de implementación */
#define FORGE_FGA2_MAX_ENTRIES 1000000u
#define FORGE_FGA2_MAX_INDEX_SIZE (256ULL * 1024ULL * 1024ULL)

/* Tipos de entrada */
#define FORGE_FGA2_ENTRY_FILE 0u
#define FORGE_FGA2_ENTRY_DIRECTORY 1u

/* FGA2 inicial no admite flags desconocidos */
#define FORGE_FGA2_SUPPORTED_FLAGS 0u

/*
 * Valida la estructura completa de un archivo FGA2.
 *
 * file debe estar abierto en modo binario.
 * La función comienza a leer desde el principio del archivo.
 * Los parámetros de salida pueden ser NULL.
 */

ForgeStatus forge_fga2_pack(
    const char *input_path,
    const char *output_path
);

ForgeStatus forge_fga2_unpack(
    const char *input_path,
    const char *output_path
);

ForgeStatus forge_fga2_validate(
    FILE *file,
    uint64_t *original_size,
    uint64_t *data_size,
    uint32_t *entry_count
);

/*
 * Valida una ruta serializada FGA2.
 *
 * Comprueba UTF-8 estricto, componentes, separadores y las
 * restricciones adicionales necesarias para extraer de forma
 * segura en Windows (nombres de dispositivo reservados,
 * puntos y espacios finales).
 */
bool forge_fga2_path_is_valid(
    const unsigned char *path,
    size_t length
);

ForgeStatus forge_fga2_info(
    const char *path,
    uint64_t *original_size,
    uint64_t *data_size,
    uint32_t *entry_count
);

ForgeStatus forge_fga2_write_u16_le(FILE *file, uint16_t value);
ForgeStatus forge_fga2_write_u32_le(FILE *file, uint32_t value);
ForgeStatus forge_fga2_write_u64_le(FILE *file, uint64_t value);
ForgeStatus forge_fga2_write_header(
    FILE *file,
    uint64_t original_size,
    uint64_t data_size,
    uint32_t entry_count
);
ForgeStatus forge_fga2_write_entry_header(
    FILE *file,
    uint16_t path_length,
    uint8_t entry_type,
    uint8_t entry_flags,
    uint64_t original_size,
    uint64_t stored_size,
    uint64_t data_offset
);

#endif