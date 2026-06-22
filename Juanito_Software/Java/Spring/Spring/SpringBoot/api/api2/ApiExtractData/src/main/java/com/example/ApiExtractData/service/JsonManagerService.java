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
import com.fasterxml.jackson.databind.node.JsonNodeType;
import com.fasterxml.jackson.databind.node.ObjectNode;
import jakarta.transaction.Transactional;
import org.springframework.dao.DataAccessException;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.IOException;
import java.util.*;
import java.util.stream.Collectors;

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

    ObjectMapper mapper = new CustomObjectMapper(); // Creamos una instancia del Mapper que hemos modificado

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

    // metodo para serializar el objeto directamente desde la entidad
    public String serialize() throws IOException, JsonProcessingException {

        // Crear un mapa para contener todos los datos
        ObjectNode rootNode = mapper.createObjectNode();

        // Antes cogiamos los objetos de sus respectivos repositorios ahora solo cogemos el objeto raiz, de esta manera si hemos deserializado usando dtos al serializar directamente desde la entidad se muestran los objetos anidados a config formando un tree, gracias a las anotaciones @jsonbackreference y @jsonmanagerreference

        // si deserializamos desde la entidad directamente a la hora de serializar desde la entidad solo nos mostraria config, tendriamos que descomentar las lineas
        List<Config> configs = configRepository.findAll();
        //List<Attribute> attributes = attributeRepository.findAll();
        //List<AttributeType> attributeTypes = attributeTypeRepository.findAll();
        //List<AttributeTypeValue> attributeTypeValues = attributeTypeValueRepository.findAll();


        // Añadir los datos al nodo raíz
        rootNode.putPOJO("configs", configs);
        //rootNode.putPOJO("attributes", attributes);
        //rootNode.putPOJO("attributeTypes", attributeTypes);
        //rootNode.putPOJO("attributeTypeValues", attributeTypeValues);

        // Creamos un fichero donde se almacenaran los datos
        try {
            File fichero = new File("config.json");
            fichero.createNewFile();
            mapper.writeValue(fichero, rootNode); // Escribir en el archivo un solo llamado
            // Devolvemos el json generado por consola y al swagger
            // System.out.println(mapper.writeValueAsString(rootNode));
            return mapper.writeValueAsString(rootNode); // Convierte el objeto a una cadena JSON
        } catch (JsonProcessingException d) {
            System.err.println("Error serializing data: " + d.getMessage());
            d.printStackTrace();
            throw d;
        }catch (IOException e) {
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

            //Escribir el fichero en un archivo
            File fichero = new File("configDTO.json");
            fichero.createNewFile();
            mapper.writeValue(fichero, rootNode); // Escribir en el archivo
            //devolvemos el json generado por consola y al swagger
            //System.out.println(mapper.writeValueAsString(rootNode));
            return mapper.writeValueAsString(rootNode); // Convierte el objeto a una cadena JSON
        } catch (JsonProcessingException d) {
            System.err.println("Error serializing data: " + d.getMessage());
            d.printStackTrace();
            throw d;
        }catch (IOException e) {
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
    }


    // metodo deserializar datos del json en un objeto
    /*public void deserialize(String json) throws IOException {
        // Crear instancia de ObjectMapper
        ObjectMapper mapper = new ObjectMapper();

        try {
            // Leer el JSON y convertirlo en un JsonNode
            JsonNode rootNode = mapper.readTree(json);

            // Iterar sobre el primer nivel (configuraciones principales)
            Iterator<Map.Entry<String, JsonNode>> rootFields = rootNode.fields();
            while (rootFields.hasNext()) {
                Map.Entry<String, JsonNode> field = rootFields.next();
                String configKey = field.getKey(); // Configuración del primer nivel
                JsonNode configNode = field.getValue(); // Nodo de configuración que contiene datos anidados
                JsonNodeType nodeType = configNode.getNodeType(); // Almacenamos el tipo de nodo

                // Crear y configurar el objeto Config
                Config config = new Config();
                config.setDescription("Example"); // Asignar configKey como descripción
                config.setIsCustom(true);  // Valor por defecto o ajustar según necesites
                config.setDefaultValue("default");
                config.setApplicationNode(configKey);  // añadimos el nombre de la configuracion
                config.setParent(null); // ponemos el parent principal a null
                Config savedConfig = configRepository.save(config); // guardamos la config y la almacenamos en una variable

                switch (nodeType) {
                    case STRING:
                        AttributeType attributeType = new AttributeType(); // creamos el objeto attributetypevalue
                        attributeType.setType(nodeType.name()); // establecemos el tipo de dato en funcion del tipo de nodo
                        attributeType.setEnumDescription("enumDesc");
                        attributeType.setIsEnum(false);
                        attributeType.setIsList(false);
                        AttributeType savedAttributeType = attributeTypeRepository.save(attributeType);


                        AttributeTypeValue attributeTypeValue = new AttributeTypeValue(); // creamos el objeto attributetypevalue
                        attributeTypeValue.setDescription("Example");
                        attributeTypeValue.setValue(configNode.textValue()); // Establecemos el valor del attributetypevalue en caso de que sea string
                        attributeTypeValue.setAttributeType(savedAttributeType);
                        attributeTypeValueRepository.save(attributeTypeValue);

                        break;
                    case OBJECT:
                        // Cuando el valor es un objeto, debemos recorrer sus campos
                        processObjectNode(configNode, savedConfig); // llamamos al metodo de forma recursiva
                        break;
                    default:
                        // Si el nodo no es un STRING ni un OBJECT, se podría manejar como un tipo desconocido
                        System.out.println("Nodo de tipo desconocido: " + nodeType);
                        break;
                }
            }
        } catch (IOException e) {
            System.err.println("Error deserializing JSON: " + e.getMessage());
            e.printStackTrace();
            throw e;
        }
    }

    // Metodo recursivo para manejar objetos anidados
    private void processObjectNode(JsonNode node, Config parentConfig) {
        Iterator<Map.Entry<String, JsonNode>> fields = node.fields();
        while (fields.hasNext()) {
            Map.Entry<String, JsonNode> entry = fields.next();
            String configOrAttributeKey = entry.getKey();
            JsonNode configOrAttributeValueNode = entry.getValue();
            JsonNodeType nodeType = configOrAttributeValueNode.getNodeType();

            Config childConfig = null; // Inicializar childConfig aquí, para usarlo en el bloque recursivo

            if (nodeType == JsonNodeType.OBJECT) {
                // Guardar config
                childConfig = new Config();
                childConfig.setDescription("Example"); // Asignar configKey como descripción
                childConfig.setIsCustom(true);  // Valor por defecto o ajustar según necesites
                childConfig.setDefaultValue("default");  // Ajustar según el JSON real
                childConfig.setApplicationNode(configOrAttributeKey);  // Ajustar según el JSON real
                childConfig.setParentId(parentConfig.getId());
                childConfig = configRepository.save(childConfig); // Guardamos el childConfig
            } else {
                // Guardar atributo
                Attribute attribute = new Attribute();
                attribute.setName(configOrAttributeKey);
                attribute.setConfig(parentConfig); // Asignamos parentConfig por defecto
                attributeRepository.save(attribute);
            }

            // Después de manejar el nodo actual, si es otro objeto, procesarlo recursivamente
            if (nodeType == JsonNodeType.OBJECT) {
                // Llamada recursiva: pasamos childConfig en lugar de parentConfig
                processObjectNode(configOrAttributeValueNode,childConfig);
            } else if (nodeType == JsonNodeType.STRING || nodeType == JsonNodeType.NUMBER || nodeType == JsonNodeType.BOOLEAN) {
                createAttributeTypeAndValue(configOrAttributeValueNode, nodeType.name(), "enumDesc");
            }
        }
    }

    private void createAttributeTypeAndValue(JsonNode valueNode, String type, String description) {
        AttributeType attributeType = new AttributeType();
        attributeType.setType(type);
        attributeType.setEnumDescription(description);
        attributeType.setIsEnum(false);
        attributeType.setIsList(false);
        AttributeType savedAttributeType = attributeTypeRepository.save(attributeType);

        AttributeTypeValue attributeTypeValue = new AttributeTypeValue();
        attributeTypeValue.setDescription("Example");
        attributeTypeValue.setValue(valueNode.asText());
        attributeTypeValue.setAttributeType(savedAttributeType);
        attributeTypeValueRepository.save(attributeTypeValue);
    }*/
}
