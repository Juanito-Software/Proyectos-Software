package com.example.ApiExtractData.service;

import com.example.ApiExtractData.assembler.*;
import com.example.ApiExtractData.dto.AttributeDTO;
import com.example.ApiExtractData.dto.AttributeTypeDTO;
import com.example.ApiExtractData.dto.AttributeTypeValueDTO;
import com.example.ApiExtractData.dto.ConfigDTO;
import com.example.ApiExtractData.model.Attribute;
import com.example.ApiExtractData.model.AttributeType;
import com.example.ApiExtractData.model.AttributeTypeValue;
import com.example.ApiExtractData.model.Config;
import com.example.ApiExtractData.repository.AttributeRepository;
import com.example.ApiExtractData.repository.AttributeTypeRepository;
import com.example.ApiExtractData.repository.AttributeTypeValueRepository;
import com.example.ApiExtractData.repository.ConfigRepository;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.databind.node.*;
import jakarta.persistence.EnumType;
import jakarta.transaction.Transactional;
import org.springframework.dao.DataAccessException;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.IOException;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Servicio que gestiona la serialización de configuraciones a formato JSON.
 * Este servicio se encarga de transformar las configuraciones almacenadas en la base de datos
 * en un archivo JSON estructurado, adaptado según el tipo de atributos definidos en las configuraciones.
 */

@Service
public class JsonManagerService {

    private final ConfigRepository configRepository;
    private final AttributeRepository attributeRepository;
    private final AttributeTypeRepository attributeTypeRepository;
    private final AttributeTypeValueRepository attributeTypeValueRepository;
    private final ConfigAssembler configAssembler;
    private final AttributeAssembler attributeAssembler;
    private final AttributeTypeAssembler attributeTypeAssembler;
    private final AttributeTypeValueAssembler attributeTypeValueAssembler;

    CustomObjectMapper mapper = new CustomObjectMapper(); // Creamos una instancia del Mapper que hemos modificado

    /**
     * Constructor de la clase JsonManagerService.
     *
     * @param configRepository Repositorio para gestionar las configuraciones.
     * @param attributeRepository Repositorio para gestionar los atributos.
     * @param attributeTypeRepository Repositorio para gestionar los tipos de atributos.
     * @param attributeTypeValueRepository Repositorio para gestionar los valores de tipos de atributos.
     * @param configAssembler Ensamblador para las configuraciones.
     * @param attributeAssembler Ensamblador para los atributos.
     * @param attributeTypeAssembler Ensamblador para los tipos de atributos.
     * @param attributeTypeValueAssembler Ensamblador para los valores de tipos de atributos.
     */
    public JsonManagerService(ConfigRepository configRepository, AttributeRepository attributeRepository, AttributeTypeRepository attributeTypeRepository, AttributeTypeValueRepository attributeTypeValueRepository, ConfigAssembler configAssembler, AttributeAssembler attributeAssembler, AttributeTypeAssembler attributeTypeAssembler, AttributeTypeValueAssembler attributeTypeValueAssembler) {
        this.configRepository = configRepository;
        this.attributeRepository = attributeRepository;
        this.attributeTypeRepository = attributeTypeRepository;
        this.attributeTypeValueRepository = attributeTypeValueRepository;
        this.configAssembler = configAssembler;
        this.attributeAssembler = attributeAssembler;
        this.attributeTypeAssembler = attributeTypeAssembler;
        this.attributeTypeValueAssembler = attributeTypeValueAssembler;
    }

    /**
     * Serializa las configuraciones obtenidas desde el repositorio a formato JSON.
     *
     * Este metodo obtiene las configuraciones principales (sin parentId) de la base de datos, las procesa recursivamente
     * y genera un archivo JSON en el que se almacenan los datos de las configuraciones
     * y sus hijos. La serialización se realiza mediante el uso de un CustomObjectMapper.
     *
     * @return La representación en cadena del JSON generado.
     * @throws IOException Si ocurre un error al intentar crear el archivo o escribir en él.
     * @throws JsonProcessingException Si ocurre un error durante la serialización del objeto a JSON.
     */
    public String serialize() throws IOException, JsonProcessingException {

        // Obtén las configuraciones principales (API_BASE_URI, ATTENDANCE, etc.)
        List<Config> configs = configRepository.findByParentIdIsNull();

        // Verifica si se encontraron configuraciones principales
        if (configs == null || configs.isEmpty()) {
            throw new IllegalStateException("No se encontraron configuraciones principales con parentId NULL");
        }

        // Crea el nodo raíz del JSON
        ObjectNode rootNode = mapper.createObjectNode();

        // Itera sobre las configuraciones principales
        for (Config config : configs) {
            processConfig(config, rootNode);
        }

        // Creamos un fichero donde se almacenaran los datos en formato JSON
        try {
            File fichero = new File("newConfig.json");
            fichero.createNewFile();
            mapper.writeValue(fichero, rootNode); // Escribir el JSON en el archivo
            // Devolvemos el json generado por consola y al swagger
            System.out.println(mapper.writeValueAsString(rootNode));
            return mapper.writeValueAsString(rootNode); // Convierte el objeto a una cadena JSON
        } catch (JsonProcessingException d) {
            System.err.println("Error serializing data: " + d.getMessage());
            d.printStackTrace();
            throw d;
        } catch (IOException e) {
            System.err.println("Error serializing data: " + e.getMessage());
            e.printStackTrace();
            throw e;
        }
    }

    /**
     * Procesa recursivamente una configuración y sus posibles configuraciones hijas,
     * y las agrega al nodo padre en formato JSON.
     *
     * Este metodo maneja diferentes tipos de atributos, tales como listas de nodos,
     * valores booleanos, numéricos, cadenas de texto, y enumeraciones.
     *
     * @param config La configuración a procesar.
     * @param parentNode El nodo padre al que se agregarán los datos procesados.
     */
    private void processConfig(Config config, ObjectNode parentNode) {

        // Verifica si la configuración tiene un atributo
        if (config.getAttribute() == null) {
            throw new IllegalStateException("La configuración con ID " + config.getId() + " no tiene un atributo asociado");
        }

        // Obtiene el nombre del atributo y el tipo de atributo
        String attributeName = config.getAttribute().getName();
        AttributeType attributeType = config.getAttribute().getAttributeType();
        String value = config.getDefaultValue();

        // Verifica que el atributo y el tipo de atributo estén correctamente configurados
        if (attributeType == null || attributeName == null) {
            throw new IllegalStateException("La configuración con ID " + config.getId() + " tiene atributos inválidos");
        }

        // Procesamiento de diferentes tipos de atributos
        switch (attributeType.getType()) {
            /**
             * Procesa la configuración de un nodo de tipo "NODE" en función de los atributos definidos.
             * Dependiendo del tipo de atributo y su valor, crea un nodo JSON con diferentes estructuras
             * y agrega los hijos correspondientes a dicho nodo.
             *
             * <p>Existen tres casos principales que se gestionan en este bloque:</p>
             * <ul>
             *     <li><strong>weighingScales</strong>: Crea un arrayNode con un conjunto de objetos que contienen un "id" y "name".</li>
             *     <li><strong>FILTER_ASSETS_TYPES</strong>: Crea un arrayNode con objetos que contienen "type" y "use", donde "use" es un valor booleano.</li>
             *     <li><strong>Otros casos</strong>: Si el atributo no corresponde a los anteriores, trata el valor como una lista de nodos y agrega los hijos del objeto.</li>
             * </ul>
             *
             * <p>En cada caso, los valores de los atributos como "id", "name", "type" y "use" son extraídos de los hijos de la configuración
             * y agregados al nodo principal de acuerdo con su tipo y formato.</p>
             *
             * @param config La configuración que se está procesando, que contiene los atributos a evaluar y los hijos a agregar.
             * @param attributeType El tipo de atributo de la configuración actual que determina cómo se debe procesar.
             * @param parentNode El nodo JSON padre donde se agregarán los datos procesados.
             * @param attributeName El nombre del atributo que se utilizará como clave en el nodo JSON.
             * @param value El valor asociado al atributo, utilizado para determinar si se trata de una lista o un solo valor.
             *
             * @throws NumberFormatException Si se produce un error al convertir un valor de tipo "id" a un entero.
             */
             case "NODE":
                if (attributeType.getList()) {
                    if(config.getAttribute().getName().equals("weighingScales")) {

                        // Crea un arrayNode para almacenar los resultados
                        ArrayNode arrayNode = mapper.createArrayNode();

                        // Obtiene los hijos del objeto (Config con el mismo parentId)
                        List<Config> children = configRepository.findByParentId(config.getId());

                        String[] ids = {};
                        String[] names = {};

                        ArrayList<Integer> idsFinal = new ArrayList<>();
                        ArrayList<String> namesFinal = new ArrayList<>();

                        // Itera sobre los hijos de la configuración
                        for (Config child : children) {
                            if (child.getAttribute().getName().equals("id")) {
                                // Usamos el ID del hijo directamente como único valor
                                String idValue = child.getDefaultValue();  // Usamos el ID del hijo
                                ids = idValue.split(";");
                            } else if (child.getAttribute().getName().equals("name")) {

                                // Suponemos que el valor "name" está separado por ";"
                                String nameValue = child.getDefaultValue();  // 'name' debería estar en el valor de 'defaultValue'
                                names = nameValue.split(";");
                            }


                            // Procesamos dependiendo de si el nombre del atributo es "id" o "name"
                            if (child.getAttribute().getName().equals("id")) {
                                // Si el atributo es "id", procesamos los valores de ids
                                for (int i = 0; i < ids.length; i++) {
                                    try {
                                        // Convertir a Integer y agregarlo a la lista
                                        idsFinal.add(Integer.parseInt(ids[i].trim()));
                                    } catch (NumberFormatException e) {
                                        // Manejar el caso en que no se pueda convertir el valor
                                        System.err.println("Error al convertir el id: " + ids[i]);
                                    }
                                }
                            } else if (child.getAttribute().getName().equals("name")) {
                                // Si el atributo es "name", procesamos los valores de names
                                for (int i = 0; i < names.length; i++) {

                                    namesFinal.add(names[i].trim());  // Asignamos el name directamente
                                }
                            }

                            // Agregar los objetos con "id" y "name" al arrayNode
                            for (int i = 0; i < names.length; i++) {
                                ObjectNode itemNodeName = mapper.createObjectNode();
                                itemNodeName.put("id", idsFinal.get(i));  // Asignamos el id directamente
                                itemNodeName.put("name", namesFinal.get(i));  // Asignamos el name directamente
                                arrayNode.add(itemNodeName);  // Agregamos el objeto al arrayNode
                            }
                        }

                        // Establece el arrayNode en el nodo padre
                        parentNode.set(attributeName, arrayNode);

                    }else if (config.getAttribute().getName().equals("FILTER_ASSETS_TYPES")){
                        // Crea un arrayNode para almacenar los resultados
                        ArrayNode arrayNode = mapper.createArrayNode();

                        // Obtiene los hijos del objeto (Config con el mismo parentId)
                        List<Config> children = configRepository.findByParentId(config.getId());

                        String[] types = {};
                        String[] uses = {};

                        ArrayList<String> typesFinal = new ArrayList<>();
                        ArrayList<Boolean> usesFinal = new ArrayList<>();

                        // Itera sobre los hijos de la configuración
                        for (Config child : children) {
                            if (child.getAttribute().getName().equals("type")) {
                                // Usamos el ID del hijo directamente como único valor
                                String typeValue = child.getDefaultValue();  // Usamos el ID del hijo
                                types = typeValue.split(";");
                            } else if (child.getAttribute().getName().equals("use")) {

                                // Suponemos que el valor "name" está separado por ";"
                                String useValue = child.getDefaultValue();  // 'name' debería estar en el valor de 'defaultValue'
                                uses = useValue.split(";");
                            }


                            // Procesamos dependiendo de si el nombre del atributo es "type" o "use"
                            if (child.getAttribute().getName().equals("type")) {
                                // Si el atributo es "type", procesamos los valores de types
                                for (int i = 0; i < types.length; i++) {
                                    typesFinal.add(types[i].trim());
                                }
                            } else if (child.getAttribute().getName().equals("use")) {
                                // Si el atributo es "use", procesamos los valores de uses
                                for (int i = 0; i < uses.length; i++) {
                                    // Convertir a booleano y agregarlo a la lista
                                    usesFinal.add(Boolean.parseBoolean(uses[i].trim()));
                                }
                            }

                            // Agregar los objetos con "type" y "use" al arrayNode
                            for (int i = 0; i < uses.length; i++) {
                                ObjectNode itemNodeName = mapper.createObjectNode();
                                itemNodeName.put("type", typesFinal.get(i));  // Asignamos el id directamente
                                itemNodeName.put("use", usesFinal.get(i));  // Asignamos el name directamente
                                arrayNode.add(itemNodeName);  // Agregamos el objeto al arrayNode
                            }
                        }

                        // Establece el arrayNode en el nodo padre
                        parentNode.set(attributeName, arrayNode);

                    }else{
                        // Si el tipo es una lista de nodos, tratamos como una lista de objetos
                        ArrayNode arrayNode = mapper.createArrayNode();

                        // Obtén los hijos del objeto (Config con el mismo parentId)
                        List<Config> children = configRepository.findByParentId(config.getId());
                        for (Config child : children) {
                            ObjectNode childNode = mapper.createObjectNode();
                            // Procesa cada hijo como un nodo
                            processConfig(child, childNode);
                            arrayNode.add(childNode);  // Agrega el nodo hijo al array
                        }
                        parentNode.set(attributeName, arrayNode);  // Establece el array de nodos en el JSON
                    }
                } else {
                        // Si no es una lista, se trata como un solo nodo
                        // Si hay un valor no nulo y no vacío, se procesa normalmente
                        ObjectNode childNode = mapper.createObjectNode();
                        parentNode.set(attributeName, childNode);  // Establece el nodo hijo

                        // Obtén los hijos del objeto (Config con el mismo parentId)
                        List<Config> children = configRepository.findByParentId(config.getId());
                        for (Config child : children) {
                            // Procesa recursivamente cada configuración hijo
                            processConfig(child, childNode);
                        }
                }
                break;

            /**
             * Procesa valores booleanos. Si el atributo es una lista, se parsean múltiples valores separados por ";".
             * Si no es una lista, se parsea un único valor booleano.
             *
             * @param config La configuración que se está procesando, que contiene los atributos a evaluar y los hijos a agregar.
             * @param attributeType El tipo de atributo de la configuración actual que determina cómo se debe procesar.
             * @param parentNode El nodo JSON padre donde se agregarán los datos procesados.
             * @param attributeName El nombre del atributo que se utilizará como clave en el nodo JSON.
             * @param value El valor asociado al atributo, utilizado para determinar si se trata de una lista o un solo valor.
             */
            case "BOOLEAN":
                if (attributeType.getIsList()) {
                        ArrayNode arrayNode = mapper.createArrayNode();
                        String[] items = value.split(";");
                        for (String item : items) {
                            arrayNode.add(Boolean.parseBoolean(item.trim()));
                        }
                        parentNode.set(attributeName, arrayNode);
                } else {
                    if (value != null && !value.isEmpty()) {
                        parentNode.put(attributeName, Boolean.parseBoolean(value));
                    }
                }
                break;

            /**
             * Procesa valores numéricos. Si el atributo es una lista, se parsean múltiples valores
             * separados por el delimitador ";" y se agregan al nodo como un array de números enteros.
             * Si no es una lista, se parsea un único valor numérico y se agrega directamente al nodo.
             *
             * @param value El valor del atributo que puede ser una lista de valores separados por ";" o un solo valor numérico.
             * @param attributeType El tipo de atributo que determina si se trata de una lista o un valor único.
             * @param parentNode El nodo JSON donde se almacenará el valor procesado.
             * @param attributeName El nombre del atributo que se utilizará como clave en el nodo JSON.
             *
             * @throws NumberFormatException Si un valor no puede ser convertido a un número entero, se captura y se agrega como String.
             */
            case "NUMERIC":
                if (value != null && !value.isEmpty()) {
                    if (attributeType.getIsList()) {
                        ArrayNode arrayNode = mapper.createArrayNode();
                        String[] items = value.split(";");
                        for (String item : items) {
                            try {
                                arrayNode.add(Integer.parseInt(item.trim()));
                            } catch (NumberFormatException e) {
                                arrayNode.add(item.trim());
                            }
                        }
                        parentNode.set(attributeName, arrayNode);
                    } else {
                        try {
                            parentNode.put(attributeName, Integer.parseInt(value));
                        } catch (NumberFormatException e) {
                            parentNode.put(attributeName, value);
                        }
                    }
                }
                break;

            /**
             * Procesa valores de tipo String. Si el atributo es una lista, se parsean múltiples valores
             * separados por el delimitador ";" y se agregan al nodo como un array de Strings. Si no es
             * una lista, se agrega un único valor de tipo String al nodo.
             *
             * @param value El valor del atributo, que puede ser una lista de valores separados por ";" o un único valor String.
             * @param attributeType El tipo de atributo que determina si el valor se trata como una lista o un valor único.
             * @param parentNode El nodo JSON donde se almacenará el valor procesado.
             * @param attributeName El nombre del atributo que se utilizará como clave en el nodo JSON.
             */
            case "STRING":

                if (value != null && !value.isEmpty()) {
                    if (attributeType.getIsList()) {

                        ArrayNode arrayNode = mapper.createArrayNode();
                        String[] items = value.split(";");

                        for (String item : items) {
                            arrayNode.add(item.trim());
                        }

                        parentNode.set(attributeName, arrayNode);
                    } else {
                        parentNode.put(attributeName, value);
                    }
                }else{
                    if (attributeType.getIsList()) {

                        ArrayNode arrayNode = mapper.createArrayNode();

                        parentNode.set(attributeName, arrayNode);
                    } else {
                        parentNode.put(attributeName, value);
                    }
                }
                break;

            /**
             * Procesa valores de tipo enum. Si el atributo corresponde a un enum válido, se procesan los valores
             * del enum especificados en la cadena de entrada. Si el valor proporcionado no corresponde a un enum válido,
             * se agrega el valor "INVALID" al nodo JSON.
             *
             * @param value El valor del atributo, que puede ser una lista de valores separados por ";" o un único valor que debe corresponder a un valor válido del enum.
             * @param attributeType El tipo de atributo que indica si el atributo corresponde a un enum y contiene la lógica para determinar si el valor es válido.
             * @param parentNode El nodo JSON donde se almacenará el valor procesado, que contendrá los valores válidos del enum o "INVALID" en caso de error.
             * @param attributeName El nombre del atributo que se utilizará como clave en el nodo JSON.
             *
             * @throws IllegalArgumentException Si el valor proporcionado no corresponde a un valor válido del enum.
             */
            case "ENUM":
                if (attributeType.getIsEnum()) {
                    // Si es un enum, procesamos el valor
                    if (value != null && !value.isEmpty()) {
                        // Dividir la cadena por ";" para obtener una lista de posibles valores
                        String[] enumValues = value.split(";");

                        // Crear un array para almacenar los valores válidos del enum
                        ArrayNode arrayNode = mapper.createArrayNode();

                        // Procesar cada valor
                        for (String enumValue : enumValues) {
                            try {
                                // Convertir el valor al enum correspondiente
                                EnumType enumConstant = EnumType.valueOf(enumValue.trim());  // Convertir el valor al enum
                                arrayNode.add(enumConstant.name());  // Agregar el nombre del enum al array
                            } catch (IllegalArgumentException e) {
                                // Si el valor no es válido, manejarlo (agregar "INVALID" o un valor por defecto)
                                System.out.println("Valor inválido para el enum: " + enumValue);
                                arrayNode.add("INVALID");  // Agregar "INVALID" si el valor no es válido
                            }
                        }
                    }
                }
                break;

            /**
             * Procesa valores que representan listas de valores de tipo enum. Si el atributo es una lista de enums,
             * se procesan sus valores para convertirlos en un formato adecuado.
             *
             * @param value El valor del atributo, que puede ser una lista de valores separados por ";" o un único valor correspondiente a un valor de tipo enum.
             * @param attributeType El tipo de atributo que indica si el atributo es una lista de enums, una lista simple o un enum único.
             * @param parentNode El nodo JSON donde se almacenarán los valores procesados, que puede contener una lista de valores de tipo enum o simples.
             * @param attributeName El nombre del atributo que se utilizará como clave en el nodo JSON.
             *
             * @throws IllegalArgumentException Si un valor no es un valor válido para el enum correspondiente.
             */
            case "LISTENUM":
                if (value != null && !value.isEmpty()) {
                    // Si es una lista de enums
                    if (attributeType.getIsList() && attributeType.getIsEnum()) {
                        // Si es una lista de enums, procesamos cada item como un enum
                        ArrayNode arrayNode = mapper.createArrayNode();
                        String[] items = value.split(";");
                        for (String item : items) {
                            try {
                                // Intentamos convertir cada item en un valor de enum correspondiente
                                EnumType enumValue = EnumType.valueOf(item.trim());  // Cambia EnumType por el tipo de enum que estés usando
                                arrayNode.add(enumValue.name());  // Agrega el nombre del enum al array
                            } catch (IllegalArgumentException e) {
                                // Si el valor no es un enum válido, puedes manejarlo de alguna manera
                                System.out.println("Valor inválido para el enum: " + item);
                                arrayNode.add("INVALID");  // O manejarlo como desees
                            }
                        }
                        parentNode.set(attributeName, arrayNode);  // Guardamos el array con los enum

                        // Si solo es una lista (no necesariamente de enums)
                    }
                }
                break;


            /**
             * Procesa atributos relacionados con el modo de máquina y rangos de datos.
             * Se manejan como listas o como enum según corresponda.
             *
             * @param value El valor del atributo a procesar, que puede ser una lista de valores o un valor individual.
             * @param parentNode El nodo JSON donde se almacenará el valor procesado.
             * @param attributeName El nombre del atributo que se utilizará como clave en el nodo JSON.
             */
            case "SPLIT_MACHINE_MODE":
            case "DEFAULT_DATA_RANGES":
            case "AUTO_MATERIAL_ON_FINISH":
            case "TYPE":
                if (attributeType.getIsList()) {
                    if (value != null && !value.isEmpty()) {
                        ArrayNode arrayNode = mapper.createArrayNode();
                        String[] items = value.split(",");
                        for (String item : items) {
                            arrayNode.add(item.trim());
                        }
                        parentNode.set(attributeName, arrayNode);
                    }
                } else if (attributeType.getIsEnum()) {
                    // Si es un enum, procesamos el valor
                    if (value != null && !value.isEmpty()) {
                        // Dividir la cadena por ";" para obtener una lista de posibles valores
                        String[] enumValues = value.split(";");

                        // Crear un array para almacenar los valores válidos del enum
                        ArrayNode arrayNode = mapper.createArrayNode();

                        // Procesar cada valor
                        for (String enumValue : enumValues) {
                            try {
                                // Convertir el valor al enum correspondiente
                                EnumType enumConstant = EnumType.valueOf(enumValue.trim());  // Convertir el valor al enum
                                arrayNode.add(enumConstant.name());  // Agregar el nombre del enum al array
                            } catch (IllegalArgumentException e) {
                                // Si el valor no es válido, manejarlo (agregar "INVALID" o un valor por defecto)
                                System.out.println("Valor inválido para el enum: " + enumValue);
                                arrayNode.add("INVALID");  // Agregar "INVALID" si el valor no es válido
                            }
                        }
                    }
                } else {
                    if (value != null && !value.isEmpty()) {
                        parentNode.put(attributeName, value);
                    }
                }
                break;

            /**
             * Procesa atributos que están relacionados con modos de máquina y rangos de datos,
             * y se manejan como listas de valores de tipo enum.
             *
             * @param value El valor del atributo, que puede ser una lista de enums separados por comas o un único valor enum.
             * @param attributeType El tipo de atributo que indica si el atributo es una lista de enums.
             * @param parentNode El nodo JSON donde se almacenarán los valores procesados, representados como una lista de enums.
             * @param attributeName El nombre del atributo que se utilizará como clave en el nodo JSON.
             */
            case "INDICATORS":
                if (attributeType.getIsList() && attributeType.getIsEnum()) {
                    // Si es una lista de enums
                    if (value != null && !value.isEmpty()) {
                        ArrayNode arrayNode = mapper.createArrayNode();
                        String[] items = value.split(";");

                        // Lista o conjunto de valores válidos de tu enum (ajusta esto con los valores reales)
                        Set<String> enumValues = Set.of("STEP", "SPLIT", "LAST_HOUR"); // Lista de valores de enum válidos en formato String

                        for (String item : items) {
                            // Verifica si el item es un valor válido en el enum
                            if (enumValues.contains(item.trim())) {
                                arrayNode.add(item.trim());  // Agrega el valor válido al ArrayNode
                            } else {
                                System.out.println("Valor inválido para el enum: " + item);
                            }
                        }

                        // Establece el arrayNode en el nodo, o un array vacío si no hay valores válidos
                        parentNode.set(attributeName, arrayNode);
                    }
                }
                break;

            /**
             * Procesa atributos cuyo tipo no coincide con ninguno de los casos anteriores.
             * Se maneja como un valor de tipo cadena de texto.
             *
             * @param value El valor del atributo, que se trata como una cadena de texto.
             * @param parentNode El nodo JSON donde se almacenará el valor procesado.
             * @param attributeName El nombre del atributo que se utilizará como clave en el nodo JSON.
             */
            default:
                // Si el tipo es "STRING" u otro, lo trata como cadena
                if (value != null && !value.isEmpty()) {
                    parentNode.put(attributeName, value);
                }
                break;
        }
    }


    /*// metodo para serializar el objeto directamente desde la entidad
    public String serialize2() throws IOException, JsonProcessingException {

        // Crear un mapa para contener todos los datos
        ObjectNode rootNode = mapper.createObjectNode();


        // Antes cogiamos los objetos de sus respectivos repositorios ahora solo cogemos el objeto raiz, de esta manera si hemos deserializado usando dtos al serializar directamente desde la entidad se muestran los objetos anidados a config formando un tree, gracias a las anotaciones @jsonbackreference y @jsonmanagerreference

        // si deserializamos desde la entidad directamente a la hora de serializar desde la entidad solo nos mostraria config, tendriamos que descomentar las lineas
        // Recuperar los objetos Config directamente del repositorio
        List<Config> configs = configRepository.findAll();
        //List<Attribute> attributes = attributeRepository.findAll();
        //List<AttributeType> attributeTypes = attributeTypeRepository.findAll();
        //List<AttributeTypeValue> attributeTypeValues = attributeTypeValueRepository.findAll();


        // Agregar los objetos recuperados al nodo JSON raíz
        rootNode.putPOJO("configs", configs);
        //rootNode.putPOJO("attributes", attributes);
        //rootNode.putPOJO("attributeTypes", attributeTypes);
        //rootNode.putPOJO("attributeTypeValues", attributeTypeValues);

        // Creamos un fichero donde se almacenaran los datos en formato JSON
        try {
            File fichero = new File("config2.json");
            fichero.createNewFile();
            mapper.writeValue(fichero, rootNode); // Escribir el JSON en el archivo
            // Devolvemos el json generado por consola y al swagger
            System.out.println(mapper.writeValueAsString(rootNode));
            return mapper.writeValueAsString(rootNode); // Convierte el objeto a una cadena JSON
        } catch (JsonProcessingException d) {
            System.err.println("Error serializing data: " + d.getMessage());
            d.printStackTrace();
            throw d;
        } catch (IOException e) {
            System.err.println("Error serializing data: " + e.getMessage());
            e.printStackTrace();
            throw e;
        }
    }


    // metodo para serializar datos de los objetos en formato json pasandolos primero a dto, muestra los objetos separados pero incluyendo los ids de referencia
    public String serializeDTO() throws IOException, JsonProcessingException {
        ObjectNode rootNode = mapper.createObjectNode();

        try {
            // Recuperar todos los objetos Config del repositorio y los convierte a DTO
            List<ConfigDTO> configDTOs = configRepository.findAll().stream()// Obtiene los objetos config y los añade a una lista llamada config
                    .map(configAssembler::configToDTO)
                    .collect(Collectors.toList());

            List<AttributeDTO> attributeDTOs = attributeRepository.findAll().stream()
                    .map(attributeAssembler::attributeToDTO)
                    .collect(Collectors.toList());

            // Convertir todos los tipos de atributos a DTOs
            List<AttributeTypeDTO> attributeTypeDTOs = attributeTypeRepository.findAll().stream()
                    .map(attributeTypeAssembler::attributeTypeToDTO)
                    .collect(Collectors.toList());

            // Convertir todos los valores de tipos de atributos a DTOs
            List<AttributeTypeValueDTO> attributeTypeValueDTOs = attributeTypeValueRepository.findAll().stream()
                    .map(attributeTypeValueAssembler::attributeTypeValueToDTO)
                    .collect(Collectors.toList());

            // Añadir los DTOs al nodo JSON
            rootNode.putPOJO("attributes", attributeDTOs);
            rootNode.putPOJO("configs", configDTOs);
            rootNode.putPOJO("attributeTypes", attributeTypeDTOs);
            rootNode.putPOJO("attributeTypeValues", attributeTypeValueDTOs);

            // Creamos un fichero donde se almacenaran los datos en formato JSON
            File fichero = new File("configDTO.json");
            fichero.createNewFile();
            mapper.writeValue(fichero, rootNode); // Escribir en el archivo
            //devolvemos el json generado por consola y al swagger
            System.out.println(mapper.writeValueAsString(rootNode));
            return mapper.writeValueAsString(rootNode); // Convierte el objeto a una cadena JSON
        } catch (JsonProcessingException d) {
            System.err.println("Error serializing data: " + d.getMessage());
            d.printStackTrace();
            throw d;
        } catch (IOException e) {
            System.err.println("Error serializing data: " + e.getMessage());
            e.printStackTrace();
            throw e;
        }
    }




    // metodo deserializar datos del json en un objeto
    public void deserialize(String json) throws IOException {
        // This is the Jackson object that performs the deserialization
        try {
            // Read the JSON strings and convert it into JsonNode
            JsonNode rootNode = mapper.readTree(json);

            // Iterate over the fields of the root object
            rootNode.fields().forEachRemaining(field -> {
                String key = field.getKey();
                JsonNode value = field.getValue();

                // If the value is an object, process its content
                if (value.isObject()) {
                    processAndSaveEntity(key, value);
                } else if (value.isArray()) {

                    // If it's an array, iterate over the elements
                    value.forEach(arrayElement -> {
                        processAndSaveEntity(key, arrayElement);
                    });
                }
            });
        } catch (IOException e) {
            // Manejo de excepciones y log para verificar el error
            System.err.println("Error deserializing JSON: " + e.getMessage());
            e.printStackTrace();
            throw e; // Vuelve a lanzar la excepción para que el controlador pueda manejarla
        }
    }

    // Method to process and save entities based on the node type
    private void processAndSaveEntity(String key, JsonNode value) {
        JsonNodeType nodeType = value.getNodeType();
        switch (nodeType) {
            case OBJECT:
                // If the node is an object, map it to the appropriate entity class and save it.
                handleObjectNode(key, value, mapper);
                break;

            case ARRAY:
                // If the node is an array, iterate over the elements and process each one.
                value.forEach(arrayElement -> processAndSaveEntity(key, arrayElement));
                break;

            case STRING:
                System.out.println("Single String for key " + key + ": " + value);
                break;
            case NUMBER:
                System.out.println("Single number for key " + key + ": " + value);
                break;
            case BOOLEAN:
                // For single values, you might want to store or log them.
                System.out.println("Single value for key " + key + ": " + value.asText());
                break;

            default:
                System.out.println("Unknown or unhandled node type for key " + key + ": " + nodeType);
        }
    }

    // Helper method to handle OBJECT nodes and save them based on the key.
    private void handleObjectNode(String key, JsonNode value, ObjectMapper mapper) {
        switch (key) {
            case "config":
                Config config = mapper.convertValue(value, Config.class);
                try {
                    configRepository.save(config);
                } catch (DataAccessException e) {
                    System.err.println("Error saving Config: " + e.getMessage());
                }
                break;

            case "attribute":
                Attribute attribute = mapper.convertValue(value, Attribute.class);
                try {
                    attributeRepository.save(attribute);
                } catch (DataAccessException e) {
                    System.err.println("Error saving Attribute: " + e.getMessage());
                }
                break;

            case "attributeType":
                AttributeType attributeType = mapper.convertValue(value, AttributeType.class);
                try {
                    attributeTypeRepository.save(attributeType);
                } catch (DataAccessException e) {
                    System.err.println("Error saving attributeType: " + e.getMessage());
                }
                break;

            case "attributeTypeValue":
                AttributeTypeValue attributeTypeValue = mapper.convertValue(value, AttributeTypeValue.class);
                try {
                    attributeTypeValueRepository.save(attributeTypeValue);
                } catch (DataAccessException e) {
                    System.err.println("Error saving attributeTypeValue: " + e.getMessage());
                }
                break;

            default:
                // For other objects, if you just want to log or have custom logic for other entities:
                System.out.println("Unhandled object for key: " + key);
                break;
        }
    }


    // metodo deserializar json en objeto
    @Transactional
    public void deserializeDTO(String json) throws IOException{
        try {
            JsonNode rootNode = mapper.readTree(json);

            // iteramos por los valores de la coleccion
            rootNode.fields().forEachRemaining(field -> {
                String key = field.getKey();
                JsonNode value = field.getValue();

                //si es objeto
                if (value.isObject()) {
                    processAndSaveEntity2(key, value);
                } else if (value.isArray()) {//si es un array
                    value.forEach(arrayElement -> processAndSaveEntity2(key, arrayElement));// iteramos por el array y ejecutamos el metodo con el value del array
                }
            });
        } catch (IOException e) {
            System.err.println("Error deserializing JSON: " + e.getMessage());
            e.printStackTrace();
            throw e;
        }
    }

    //metodo para precesar y guardar la entidad
    private void processAndSaveEntity2(String key, JsonNode value) {

        JsonNodeType nodeType = value.getNodeType();
        switch (nodeType) {
            case OBJECT:
                handleObjectNode2(key, value);
                break;

            case ARRAY:
                value.forEach(arrayElement -> processAndSaveEntity2(key, arrayElement));
                break;

            case STRING:
                System.out.println("Single String for key " + key + ": " + value);
                break;

            case NUMBER:
                System.out.println("Single number for key " + key + ": " + value);
                break;

            case BOOLEAN:
                System.out.println("Single value for key " + key + ": " + value.asText());
                break;

            default:
                System.out.println("Unknown or unhandled node type for key " + key + ": " + nodeType);
        }
    }

    private void handleObjectNode2(String key, JsonNode value) {
        switch (key) {
            case "config":
                ConfigDTO configDTO = mapper.convertValue(value, ConfigDTO.class);
                ConfigAssembler configAssembler = new ConfigAssembler(attributeRepository, configRepository); // Crear instancia del ensamblador
                Config configEntity = configAssembler.configToEntity(configDTO);
                try {
                    configRepository.save(configEntity);
                } catch (DataAccessException e) {
                    System.err.println("Error saving Config: " + e.getMessage());
                }
                break;

            case "attribute":
                AttributeDTO attributeDTO = mapper.convertValue(value, AttributeDTO.class);
                AttributeAssembler attributeAssembler = new AttributeAssembler(configRepository, attributeTypeRepository, attributeRepository); // Crear instancia del ensamblador
                Attribute AttributeEntity = attributeAssembler.attributeToEntity(attributeDTO);
                try {
                    attributeRepository.save(AttributeEntity);
                } catch (DataAccessException e) {
                    System.err.println("Error saving Attribute: " + e.getMessage());
                }
                break;

            case "attributeType":
                AttributeTypeDTO attributeTypeDTO = mapper.convertValue(value, AttributeTypeDTO.class);
                AttributeTypeAssembler attributeTypeAssembler = new AttributeTypeAssembler(attributeRepository, attributeTypeRepository, attributeTypeValueRepository); // Crear instancia del ensamblador
                AttributeType AttributeTypeEntity = attributeTypeAssembler.attributeTypeToEntity(attributeTypeDTO);
                try {
                    attributeTypeRepository.save(AttributeTypeEntity);
                } catch (DataAccessException e) {
                    System.err.println("Error saving AttributeType: " + e.getMessage());
                }
                break;

            case "attributeTypeValue":
                AttributeTypeValueDTO attributeTypeValueDTO = mapper.convertValue(value, AttributeTypeValueDTO.class);
                AttributeTypeValueAssembler attributeTypeValueAssembler = new AttributeTypeValueAssembler(attributeTypeValueRepository, attributeTypeRepository); // Crear instancia del ensamblador
                AttributeTypeValue attributeTypeValueEntity = attributeTypeValueAssembler.attributeTypeValueToEntity(attributeTypeValueDTO);
                try {
                    attributeTypeValueRepository.save(attributeTypeValueEntity);
                } catch (DataAccessException e) {
                    System.err.println("Error saving AttributeTypeValue: " + e.getMessage());
                }
                break;

            default:
                System.out.println("Unhandled object for key: " + key);
                break;
        }
    }*/
}

