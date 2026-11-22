APLICACIONES DE ESCRITORIO CON REACT Y BACKENDS POLÍGLOTAS
1. Introducción
Es posible desarrollar aplicaciones de escritorio utilizando React como tecnología de frontend, independientemente del lenguaje de programación empleado para implementar la lógica de negocio.
React no es exclusivamente una tecnología para aplicaciones web. Es una biblioteca JavaScript para construir interfaces de usuario mediante componentes declarativos.
Aunque habitualmente se utiliza junto con navegadores web, también puede integrarse en aplicaciones de escritorio mediante tecnologías como Electron, Tauri, Wails o Photino.
Esto permite separar dos responsabilidades:
    • Frontend: presentación de información, componentes visuales e interacción con el usuario.
    • Backend: lógica de negocio, procesamiento, persistencia, acceso al sistema operativo y operaciones internas.
Por tanto, podemos utilizar React como interfaz gráfica y desarrollar el núcleo de la aplicación en Java, Python, C, C++, C#, Rust, Go o prácticamente cualquier otro lenguaje.

2. React en aplicaciones de escritorio
Para utilizar React en una aplicación de escritorio necesitamos una tecnología que proporcione un entorno donde ejecutar y renderizar su interfaz.
Las alternativas más conocidas son:
2.1. Electron
Electron es un framework para desarrollar aplicaciones de escritorio multiplataforma utilizando tecnologías web.
Combina tres componentes principales:
    • React: construcción de la interfaz gráfica.
    • Chromium: motor de renderizado que permite mostrar la interfaz.
    • Node.js: entorno de ejecución JavaScript que proporciona acceso a funcionalidades del sistema operativo.
Electron conecta estos componentes y permite empaquetar la aplicación como un programa de escritorio.
Arquitectura
Aplicación de escritorio
│
├── Frontend (React)
│   ├── Componentes
│   ├── Estado
│   └── CSS
│
├── Electron Main Process
│   ├── Gestión de ventanas
│   ├── Sistema de archivos
│   ├── Gestión de procesos
│   └── Ciclo de vida de la aplicación
│
└── Electron Preload
    └── Comunicación segura
        entre React y Electron
Main Process
Es el proceso principal de Electron.
Se encarga de gestionar la aplicación, crear ventanas, controlar su ciclo de vida y acceder a las funcionalidades nativas.
Renderer Process
Es el proceso donde se renderiza la interfaz gráfica.
En nuestro caso, ejecuta React dentro de Chromium.
Preload
Actúa como intermediario entre el proceso principal y el renderer.
Permite exponer funcionalidades concretas del sistema operativo al frontend sin concederle acceso indiscriminado a Node.js.
Ventajas
    • Ecosistema muy maduro.
    • Gran cantidad de documentación y bibliotecas.
    • Desarrollo relativamente sencillo.
    • Multiplataforma.
    • Acceso amplio a funcionalidades del sistema operativo.
Desventajas
    • Mayor consumo de memoria.
    • Mayor tamaño de los ejecutables.
    • Incorpora Chromium y Node.js en la distribución.
Ejemplos de aplicaciones
    • Visual Studio Code.
    • Discord.
    • Obsidian.

2.2. Tauri
Tauri es un framework para desarrollar aplicaciones de escritorio utilizando tecnologías web para la interfaz y Rust para las funcionalidades nativas.
Combina:
    • React: interfaz gráfica.
    • WebView: motor de renderizado proporcionado por el sistema operativo.
    • Rust: backend nativo y acceso al sistema operativo.
    • Tauri: comunicación entre frontend y backend, integración y empaquetado.
A diferencia de Electron, Tauri no incorpora una instancia completa de Chromium.
En Windows utiliza WebView2, mientras que en otros sistemas utiliza sus respectivos motores WebView.
Arquitectura
Aplicación de escritorio
│
├── Frontend
│   └── React
│       ├── Componentes
│       ├── Estado
│       └── CSS
│
├── WebView
│   └── Renderizado de interfaz
│
└── Backend
    └── Rust
        ├── Sistema de archivos
        ├── Procesos
        ├── Red
        └── APIs del sistema operativo
Comunicación
React puede invocar comandos implementados en Rust mediante el mecanismo de comandos de Tauri.
También es posible utilizar otros mecanismos de comunicación para conectar procesos externos.
Ventajas
    • Menor tamaño de distribución, generalmente.
    • Menor consumo de recursos, generalmente.
    • Integración con funcionalidades nativas.
    • Multiplataforma.
    • No necesita Node.js en tiempo de ejecución.
Desventajas
    • Requiere conocer Rust para desarrollar funcionalidades nativas propias.
    • Ecosistema menos maduro que Electron.
    • El comportamiento y las capacidades del WebView pueden variar según el sistema operativo.
Importante: aunque Node.js no es necesario para ejecutar la aplicación final, normalmente se utiliza durante el desarrollo para gestionar dependencias, ejecutar Vite y compilar React.

2.3. Otras alternativas
Tecnología
Frontend
Backend / núcleo
Electron
React
Node.js
Tauri
React
Rust
Neutralinojs
React
APIs nativas
Wails
React
Go
Photino
React
.NET
Todas permiten desarrollar aplicaciones de escritorio con interfaces basadas en tecnologías web, aunque sus arquitecturas e integraciones son diferentes.

3. Comparativa: Electron frente a Tauri
Característica
Electron
Tauri
Interfaz
React
React
Motor gráfico
Chromium
WebView del SO
Backend nativo
Node.js
Rust
Node.js en producción
Sí, integrado
No
Consumo de RAM
Generalmente mayor
Generalmente menor
Tamaño del ejecutable
Generalmente mayor
Generalmente menor
Multiplataforma
Sí
Sí
Ecosistema
Muy maduro
Más joven
¿Cuál elegir?
Electron es especialmente interesante cuando se prioriza la madurez del ecosistema, la facilidad de integración con Node.js y la disponibilidad de bibliotecas.
Tauri es especialmente interesante cuando se busca una aplicación de escritorio más ligera y se está dispuesto a trabajar con Rust para las funcionalidades nativas.

4. Arquitectura políglota: React + cualquier lenguaje
Una de las posibilidades más interesantes es desarrollar una aplicación de escritorio utilizando React como frontend y un backend implementado en otro lenguaje.
Esto se conoce como una arquitectura políglota: utilizar diferentes lenguajes y tecnologías dentro de un mismo sistema, asignando a cada uno las responsabilidades para las que resulta más adecuado.
React no impone el lenguaje de programación del backend.
La comunicación entre ambos componentes puede realizarse mediante diferentes mecanismos.
4.1. Arquitectura general
              APLICACIÓN DE ESCRITORIO
                       │
                FRONTEND (React)
                       │
             CAPA DE COMUNICACIÓN
                       │
          ┌────────────┼────────────┐
          │            │            │
        Java         Python       C / C++
          │            │            │
      Spring Boot   FastAPI    Lógica nativa
          │            │            │
          └────────────┼────────────┘
                       │
                CAPA DE DATOS
Los backends son alternativas arquitectónicas. No es obligatorio utilizar todos simultáneamente.
4.2. Lenguajes compatibles
Lenguaje
Tecnologías habituales
Comunicación
Java
Spring Boot
HTTP, WebSocket, IPC
Python
FastAPI, Flask
HTTP, WebSocket, IPC
C
Bibliotecas nativas
FFI, IPC
C++
Bibliotecas nativas
FFI, IPC
C#
.NET
IPC, HTTP, bindings
Rust
Tauri, bibliotecas nativas
IPC, comandos
Go
Servidores y bibliotecas
IPC, HTTP
La elección del mecanismo depende de cómo se integre el backend con la aplicación de escritorio.

5. Mecanismos de comunicación entre frontend y backend
Para que React pueda utilizar las funcionalidades del backend necesitamos establecer un mecanismo de comunicación.
Los más importantes son:
5.1. HTTP / REST API
Es uno de los mecanismos más sencillos y conocidos.
El backend implementa una API REST y React realiza peticiones HTTP para solicitar información o ejecutar operaciones.
Ejemplo con Python y FastAPI:
Backend:
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/users")
def get_users():
    return [
        {"id": 1, "name": "Juan"},
        {"id": 2, "name": "Pedro"}
    ]
Frontend:
const response = await fetch(
    "http://localhost:8000/api/users"
);

const users = await response.json();
Este mecanismo también puede utilizarse con Spring Boot, ASP.NET, Go y otros frameworks.
Ventajas:
    • Desacoplamiento entre frontend y backend.
    • Independencia del lenguaje.
    • Facilidad de mantenimiento.
    • Aprovechamiento de conocimientos sobre arquitecturas cliente-servidor.
    • Posibilidad de reutilizar la API en otros clientes.
Inconvenientes:
    • Requiere gestionar un servidor local.
    • Hay que controlar los puertos, el ciclo de vida del proceso y los posibles conflictos.
    • Se necesita proteger adecuadamente el servicio local.
5.2. WebSocket
WebSocket permite establecer una conexión bidireccional persistente entre frontend y backend.
A diferencia de HTTP tradicional, no es necesario realizar una petición independiente para cada intercambio.
Es especialmente útil para:
    • Aplicaciones en tiempo real.
    • Monitorización de procesos.
    • Notificaciones.
    • Transferencia continua de información.
    • Actualización de interfaces en tiempo real.
5.3. IPC (Inter-Process Communication)
IPC significa Inter-Process Communication o comunicación entre procesos.
Permite que dos procesos independientes intercambien información.
Por ejemplo:
Proceso 1                 Proceso 2

React                     Java
  │                         │
  ├────── Solicitud ────────►│
  │                         │
  │◄────── Respuesta ────────┤
Es especialmente interesante para aplicaciones de escritorio que ejecutan un backend independiente.
Dependiendo de la tecnología, IPC puede implementarse mediante:
    • Pipes.
    • Named Pipes.
    • Sockets locales.
    • Mensajería.
    • Canales de comunicación propios del framework.
Tauri y Electron también proporcionan mecanismos específicos para comunicar su frontend con el proceso nativo.
5.4. FFI (Foreign Function Interface)
FFI significa Foreign Function Interface.
Permite que un lenguaje invoque funciones implementadas en otro lenguaje mediante interfaces compatibles.
Por ejemplo, Python puede invocar funciones implementadas en C utilizando ctypes o cffi.
También existen tecnologías como JNI para integrar Java con código nativo.
Es especialmente interesante cuando necesitamos reutilizar bibliotecas nativas o ejecutar algoritmos de alto rendimiento sin levantar otro servidor.
Diferencia importante: FFI no equivale a IPC. FFI permite interoperabilidad entre lenguajes dentro de un mismo proceso; IPC permite comunicación entre procesos independientes.

6. Arquitectura de ejemplo: React + Java + Python + C
Imaginemos que queremos desarrollar una aplicación de escritorio especializada en procesamiento de datos.
Podríamos diseñar una arquitectura como esta:
DataStudio/
│
├── frontend/
│   ├── React
│   ├── TypeScript
│   └── Vite
│
├── backend/
│   │
│   ├── java-engine/
│   │   └── Spring Boot
│   │
│   ├── python-engine/
│   │   └── FastAPI
│   │
│   └── native-engine/
│       ├── C
│       └── C++
│
└── desktop/
    └── Tauri (Rust)
Responsabilidades
React + TypeScript
    • Interfaz gráfica.
    • Componentes.
    • Formularios.
    • Gestión de estado.
    • Visualizaciones.
    • Interacción con el usuario.
Java + Spring Boot
    • Reglas de negocio.
    • Gestión de operaciones.
    • Procesamiento de datos.
    • Persistencia.
    • Integración con bases de datos.
Python + FastAPI
    • Procesamiento de datos.
    • Machine Learning.
    • Inteligencia artificial.
    • Automatización.
    • Algoritmos científicos.
C / C++
    • Operaciones de bajo nivel.
    • Gestión de memoria.
    • Algoritmos intensivos.
    • Procesamiento de alto rendimiento.
    • Integración con bibliotecas nativas.
Rust + Tauri
    • Integración con el sistema operativo.
    • Gestión de ventanas.
    • Comunicación con el frontend.
    • Funcionalidades nativas.
    • Empaquetado de la aplicación.
No es obligatorio utilizar todos estos lenguajes. Es un ejemplo de cómo distribuir responsabilidades en una arquitectura políglota.

7. Node.js durante el desarrollo y en producción
Es importante distinguir entre las herramientas necesarias para desarrollar una aplicación y las necesarias para ejecutarla.
Por ejemplo, aunque React se ejecute dentro de Tauri, podemos necesitar Node.js para trabajar con Vite y npm.
Situación
¿Node.js necesario?
Desarrollar React con Vite
Sí, normalmente
Instalar dependencias con npm
Sí
Compilar React
Sí, normalmente
Ejecutar React en Electron
Electron incorpora Node.js
Ejecutar React en Tauri
No
Ejecutar backend Java
No
Ejecutar backend Python
No
Ejecutar backend C/C++
No
Una vez compilado el frontend, sus archivos estáticos pueden distribuirse dentro de la aplicación de escritorio.
Por tanto, el usuario final no necesita tener Node.js instalado para ejecutar una aplicación Tauri.
Esto no significa que desaparezcan las dependencias del backend: si utilizamos Java o Python, tendremos que proporcionar sus respectivos runtimes o distribuir el backend de forma autónoma.

8. Conceptos fundamentales que debemos recordar
    1. React es una biblioteca para construir interfaces de usuario, no un framework exclusivo de aplicaciones web.
    2. React puede utilizarse en aplicaciones de escritorio mediante tecnologías como Electron y Tauri.
    3. El frontend y el backend son capas independientes y pueden estar escritos en lenguajes diferentes.
    4. Node.js no es obligatorio en producción si utilizamos Tauri.
    5. Electron incorpora Node.js y Chromium en su arquitectura.
    6. Java, Python, C, C++, C#, Rust y Go pueden actuar como backend de una aplicación cuyo frontend está desarrollado con React.
    7. HTTP, WebSocket, IPC y FFI son mecanismos diferentes de comunicación e interoperabilidad.
    8. Una arquitectura políglota permite utilizar diferentes lenguajes dentro de un mismo sistema sin obligar a que toda la aplicación esté implementada en uno solo.
    9. El empaquetado de una aplicación no elimina la necesidad de distribuir los runtimes que requieran sus componentes.

9. Conclusión
Es perfectamente viable desarrollar aplicaciones de escritorio utilizando React como tecnología de presentación y cualquier lenguaje de programación como núcleo de la aplicación.
La decisión arquitectónica importante no consiste en elegir un único lenguaje para todo el proyecto, sino en definir correctamente:
    • Qué responsabilidades tiene el frontend.
    • Qué responsabilidades tiene el backend.
    • Cómo se comunican ambos componentes.
    • Cómo se integran las funcionalidades del sistema operativo.
    • Cómo se empaqueta y distribuye la aplicación.
Como arquitectura general, React + TypeScript + Tauri es una combinación muy interesante para aplicaciones de escritorio modernas, especialmente cuando queremos mantener el backend desacoplado y poder implementarlo en diferentes lenguajes.
10. Documentación oficial
    • React
    • Electron
    • Tauri
    • Vite
    • FastAPI
    • Spring Boot
    • Rust
    • Wails
