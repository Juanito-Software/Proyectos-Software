# springlessEasyBatch (Java Edition)

**Versión profesional de alto rendimiento para procesamiento batch en Java sin dependencias de Spring.**

## 🧠 ¿Qué es springlessEasyBatch?

`springlessEasyBatch` es una herramienta potente y minimalista para realizar procesamiento batch de datos en Java, diseñada como una alternativa ligera a los frameworks complejos basados en Spring. Esta versión está optimizada para entornos de producción exigentes, siendo ideal para empresas que buscan:

- Alto rendimiento
- Bajo consumo de recursos
- Sencillez de integración
- Licenciamiento comercial claro

---

## 🚀 Características destacadas

- ✅ Cero dependencias externas
- ⚙️ Configuración sencilla por archivo o código
- 🔄 Transformación y procesamiento de flujos en tiempo real
- 🧩 Compatible con múltiples fuentes (archivos, bases de datos, etc.)
- 🔐 Versión con licencia comercial para uso profesional

---

## 🏁 Requisitos

- Java 8 o superior
- Sistema operativo Windows, Linux o macOS
- Acceso a clave de licencia válida

---

## 📦 Instalación

1. Descarga el archivo `.jar` desde el portal de clientes o desde tu email de adquisición.
2. Ejecuta el jar desde la terminal o intégralo como dependencia en tu proyecto:

```java -jar springlessEasyBatch.jar```

Si se requiere activación, introduce tu clave cuando se solicite o configúrala como variable de entorno:

```export EASYPASS_KEY=tu_clave_de_licencia```


## 🛠️ Uso básico

Aquí tienes un ejemplo mínimo de uso programático:

```
EasyBatchProcessor processor = new EasyBatchProcessor();
processor.loadFromFile("data.csv");
processor.setMappingStrategy(MyCustomMapper::map);
processor.execute();
Para más ejemplos, consulta la carpeta examples/.
```

🔒 Licencia
Este software springlessEasyBatch está (Versión Java), está protegido por una Licencia de Uso Comercial Personalizada.

El uso sin autorización está estrictamente prohibido.

Su uso está limitado a los términos adquiridos (licencia individual, por equipo, etc.).

Está prohibida la copia, modificación, redistribución y análisis del código.

Requiere activación mediante clave de licencia proporcionada por Juanito Software.

Incluye soporte técnico, documentación oficial y actualizaciones según contrato.

Consulta el archivo LICENSE.txt para ver la licencia completa.



💬 Soporte
Los usuarios con licencia activa pueden contactar con el soporte técnico mediante:

📧 Email: benaldezperedaj@gmail.com

🌐 Web:

Tiempo de respuesta estimado: 24–48h en días laborables.

🧾 Facturación y actualizaciones
Tras adquirir una licencia válida, recibirás:

Una clave personal de activación

Acceso a actualizaciones menores durante 12 meses

Asistencia básica por email

Para soporte ampliado o desarrollo a medida, consulta nuestros planes empresariales.

📍 Estado del proyecto
🟢 Activo — Última versión: v1.0.0
📅 Fecha de lanzamiento: 24 de junio de 2025

© 2025 Juanito Software. Todos los derechos reservados.

