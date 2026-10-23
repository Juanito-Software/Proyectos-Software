Juan, vamos a convertir esto en un plan de formación serio. No quiero que te limites a memorizar respuestas para superar un test de React o Java: quiero que llegues al punto en el que puedas razonar las preguntas, detectar las respuestas incorrectas y resolver problemas aunque te cambien el enunciado.
Hay una distinción importante en tu caso: saber desarrollar aplicaciones y saber demostrar tus conocimientos en una prueba técnica son habilidades relacionadas, pero diferentes. Ya tienes proyectos con React, Angular, Java/Spring Boot, Python/FastAPI y Laravel, además de experiencia con pruebas automatizadas y CI/CD. Tu monorepo de GitHub, con TaskHub en React y sus 983 pruebas ejecutadas mediante CI/CD, constituye una base práctica real.
No necesitamos empezar de cero. Necesitamos consolidar los fundamentos, identificar lagunas concretas y practicar cómo se evalúan esos conocimientos en procesos de selección.
1. Nuestra estrategia de formación
Mi recomendación es construir un perfil de desarrollador Full Stack con fundamentos sólidos y especialización principal en backend, sin dejar de prepararte para ofertas centradas en frontend.
Los cuatro pilares de tu preparación
1. Fundamentos de programación
Tipos, memoria, referencias, funciones, asincronía, algoritmos, estructuras de datos, complejidad y programación orientada a objetos.
2. Tecnologías del puesto
React, Angular, Java/Spring Boot, Python/FastAPI y PHP/Laravel: sus mecanismos internos, APIs habituales y errores frecuentes.
3. Ingeniería de software
SQL, HTTP, REST, seguridad, testing, Git, CI/CD, Docker, arquitectura, rendimiento y depuración.
4. Preparación de entrevistas
Preguntas tipo test, fragmentos de código, detección de bugs, ejercicios prácticos, preguntas de diseño y explicación oral de decisiones técnicas.
La idea fundamental es que no estudiaremos cada tecnología como una isla. Aprenderemos primero los conceptos transferibles y después veremos cómo los implementa cada lenguaje o framework.
Por ejemplo, una vez entiendas las referencias, la mutabilidad y las actualizaciones de estado, será más sencillo comprender por qué React renderiza de nuevo un componente, por qué importa la inmutabilidad en Redux y cómo funcionan los objetos en Java o Python.
2. El itinerario completo
Este es el mapa de formación que propongo. El orden importa: si dominamos las bases, las particularidades de los frameworks dejan de parecer reglas arbitrarias.
Fase 1. Fundamentos que sirven para todos los puestos
Prioridad máxima
Duración orientativa: 2–3 semanas.
Tema
Qué debes llegar a dominar
Tipos y valores
Tipado estático y dinámico, coerción, igualdad y conversiones
Referencias y memoria
Valores frente a referencias, mutabilidad, identidad y aliasing
Funciones
Ámbito, closures, funciones de orden superior y recursividad
Programación orientada a objetos
Encapsulación, herencia, polimorfismo, interfaces y composición
Estructuras de datos
Arrays, listas enlazadas, pilas, colas, mapas, conjuntos y árboles
Algoritmos
Búsqueda, ordenación, recorridos y análisis de complejidad Big O
Concurrencia y asincronía
Hilos, tareas, promesas, async/await, bloqueos y condiciones de carrera
Gestión de errores
Excepciones, propagación, recuperación y diseño de errores
Aquí es donde trabajaremos preguntas como:
    • ¿Qué diferencia existe entre == y === en JavaScript?
    • ¿Por qué modificar un objeto no siempre provoca un renderizado en React?
    • ¿Qué significa que una operación no sea atómica?
    • ¿Por qué count++ no es necesariamente seguro entre varios hilos?
    • ¿Qué diferencia hay entre una excepción comprobada y una no comprobada en Java?
    • ¿Cuándo conviene utilizar una estructura Set en vez de una lista?
No bastará con que sepas elegir la respuesta correcta. Tendrás que explicar el motivo y reconocer cuándo cambia la respuesta según el lenguaje.
Fase 2. JavaScript moderno y TypeScript
Duración orientativa: 1–2 semanas.
Aunque tu objetivo no sea trabajar exclusivamente con JavaScript, es el puente fundamental entre React y buena parte del desarrollo frontend moderno.
Estudiaremos:
    • Tipos primitivos, objetos, igualdad y coerción.
    • let, const, ámbitos y hoisting.
    • Closures, contexto de this y funciones flecha.
    • Arrays, objetos, destructuring, spread y métodos funcionales.
    • Promesas, async/await, event loop, microtasks y macrotasks.
    • Módulos, errores, prototipos y clases.
    • TypeScript: type, interface, uniones, genéricos, narrowing, unknown y never.
    • Tipado estructural, inferencia y diferencias entre errores de compilación y ejecución.
Un punto importante será aprender a predecir qué imprime un fragmento de código. Muchas pruebas técnicas evalúan precisamente eso.
Fase 3. React en profundidad
Duración orientativa: 2–3 semanas.
Aquí abordaremos tanto las preguntas que te han planteado como los mecanismos que hay detrás de ellas.
Bloque
Contenido
Renderizado
Reconciliación, identidad de componentes, key, montaje y desmontaje
Estado
useState, actualizaciones funcionales, snapshots y batching
Hooks
useEffect, useRef, useMemo, useCallback y hooks personalizados
Rendimiento
React.memo, referencias estables, selectores y renders innecesarios
Composición
children, composición de componentes, Context y prop drilling
Estado global
Context + reducer, Redux Toolkit y Zustand
Datos asíncronos
Fetch, cancelación, errores, loading y caché
Formularios
Estado controlado, validación y manejo de errores
Testing
React Testing Library, Vitest/Jest y pruebas de comportamiento
Arquitectura
Separación por funcionalidades, componentes, hooks y servicios
Debes poder razonar, por ejemplo, qué sucede en este caso:
function Counter() {
  const [count, setCount] = useState(0);

  function increment() {
    setCount(c => c + 1);
    setCount(c => c + 1);
    setCount(c => c + 1);
  }

  return (
    <button onClick={increment}>
      {count}
    </button>
  );
}
Tendrás que explicar por qué el contador aumenta tres unidades, cómo interviene el batching, qué cambia si utilizamos setCount(count + 1) y cuándo React realiza el renderizado.
También distinguiremos los detalles específicos de React 18 de las diferencias que puedan existir en versiones posteriores.
Fase 4. Angular en profundidad
Duración orientativa: 1–2 semanas.
Como ya tienes experiencia práctica con Angular, aquí el objetivo será dominar sus conceptos evaluables y las decisiones arquitectónicas.
    • Componentes, plantillas y ciclo de vida.
    • Data binding, inputs, outputs y comunicación entre componentes.
    • Signals, computed y effect.
    • Servicios e inyección de dependencias.
    • RxJS: Observable, Subject, BehaviorSubject, map, switchMap, mergeMap y concatMap.
    • Formularios reactivos y validación.
    • Routing, guards y lazy loading.
    • Change detection y OnPush.
    • HTTP, interceptores y gestión de errores.
    • Testing, organización por funcionalidades y rendimiento.
Un ejemplo de pregunta que deberás saber resolver: ¿qué diferencia existe entre un Observable y una Promise, y por qué elegirías switchMap en una búsqueda donde el usuario escribe continuamente?
No quiero que memorices que un operador es «el mejor». Quiero que entiendas qué ocurre con las suscripciones, la concurrencia y los resultados anteriores.
Fase 5. Java y Spring Boot
Duración orientativa: 2–3 semanas.
Esta será una de nuestras áreas principales porque conecta directamente con tu experiencia de backend.
Java:
    • POO, interfaces, clases abstractas, records y enums.
    • Sobrecarga frente a sobrescritura.
    • Igualdad, equals() y hashCode().
    • Genéricos y colecciones.
    • Streams, lambdas y functional interfaces.
    • Checked y unchecked exceptions.
    • Optional, inmutabilidad y diseño de APIs.
    • JVM, heap, stack, garbage collector y gestión de memoria.
    • Hilos, volatile, synchronized, atomics y ejecutores.
    • JUnit, Mockito y pruebas unitarias.
Spring Boot:
    • Inyección de dependencias e inversión de control.
    • Beans y ciclo de vida.
    • Controllers, services y repositories.
    • Spring MVC y validación.
    • JPA/Hibernate, entidades y transacciones.
    • Seguridad, autenticación y autorización.
    • Configuración, perfiles y variables de entorno.
    • Manejo global de excepciones.
    • Testing de integración.
    • Spring Batch y procesamiento por lotes.
Aquí no nos limitaremos a saber escribir un @RestController. Tendrás que explicar por qué separamos controlador, servicio y repositorio, cómo funciona una transacción y qué problemas puede introducir una relación entre entidades mal diseñada.
Fase 6. Python y FastAPI
Duración orientativa: 1–2 semanas.
    • Tipado dinámico, mutabilidad e identidad de objetos.
    • Listas, tuplas, diccionarios, conjuntos y comprensiones.
    • Iteradores, generadores y decoradores.
    • Argumentos mutables por defecto y alcance de variables.
    • Excepciones, context managers y recursos.
    • Clases, herencia, MRO y métodos especiales.
    • Type hints, Protocol, genéricos y dataclasses.
    • Entornos virtuales, pyproject.toml, gestores de dependencias y packaging.
    • asyncio, corutinas, concurrencia y paralelismo.
    • FastAPI, Pydantic, dependencias y validación.
    • Pytest, fixtures, mocks y pruebas de APIs.
Dedicaremos especial atención a las diferencias entre concurrencia y paralelismo, y a por qué una función async no hace que automáticamente todas sus operaciones sean asíncronas.
Fase 7. PHP y Laravel
Duración orientativa: 1–2 semanas.
Como ya tienes un proyecto con Laravel, aprovecharemos esa base para repasar los detalles que suelen distinguir a alguien que sabe utilizar el framework de alguien que comprende su funcionamiento.
    • Tipos, comparación estricta y coerción.
    • Arrays, objetos, referencias y funciones.
    • Interfaces, traits, clases abstractas y namespaces.
    • Composer, autoloading y estándares PSR.
    • Inyección de dependencias y service container.
    • Ciclo de una petición HTTP en Laravel.
    • Routing, middleware, controllers y Form Requests.
    • Eloquent ORM, relaciones, scopes y carga anticipada.
    • Migraciones, transacciones y query builder.
    • Autenticación, autorización, policies y gates.
    • Validación, excepciones y respuestas HTTP.
    • Colas, jobs, eventos, listeners y caché.
    • PHPUnit/Pest, factories y tests de integración.
También practicaremos problemas típicos como el N+1 de Eloquent, asignación masiva insegura, validaciones duplicadas y lógica de negocio colocada incorrectamente en los controladores.
Fase 8. Conocimientos transversales de un Full Stack
Duración orientativa: 2 semanas, en paralelo con las anteriores.
Área
Competencias
HTTP y REST
Métodos, códigos de estado, idempotencia, headers, cookies y CORS
SQL
Joins, subconsultas, índices, transacciones, normalización y planes de ejecución
Bases de datos
Integridad, claves, aislamiento y concurrencia
Seguridad
XSS, CSRF, SQL injection, contraseñas, JWT, OAuth 2.0 y permisos
Git
Branches, merge, rebase, conflictos y pull requests
Testing
Unitarias, integración, contrato y extremo a extremo
CI/CD
Pipelines, quality gates, artefactos y despliegues
Docker
Imágenes, contenedores, redes, volúmenes y Docker Compose
Arquitectura
SOLID, Clean Architecture, monolitos modulares y patrones de diseño
Sistemas
Caché, colas, logging, observabilidad y rendimiento
Fase 9. Preparación de entrevistas y pruebas técnicas
Esta fase no es el examen final: empezará desde la primera semana y continuará durante todo el itinerario.
Practicaremos cinco formatos diferentes:
    1. Preguntas tipo test. Elegir una respuesta entre cuatro opciones, como las que me has ido pasando.
    2. Predicción de código. Indicar el resultado exacto, los renders o las excepciones.
    3. Corrección de errores. Encontrar bugs, condiciones de carrera, problemas de tipado y malas prácticas.
    4. Ejercicios de programación. Resolver problemas sin depender de la autocompletación de un IDE.
    5. Entrevistas orales. Explicar decisiones, comparar alternativas y defender una solución.
3. Cómo vamos a estudiar para que el conocimiento permanezca
No te recomendaría pasar semanas viendo vídeos o leyendo documentación de forma pasiva. La formación debe producir evidencia de que realmente has aprendido.
Rutina semanal propuesta
Estudiar el concepto
Entender la explicación, las reglas y los mecanismos internos.
25 %
Practicar con código
Escribir ejemplos pequeños, predecir resultados y experimentar.
35 %
Simular pruebas
Resolver preguntas sin apuntes y justificar cada respuesta.
25 %
Repasar los errores
Registrar las confusiones y volver a evaluarlas días después.
15 %
La rutina está pensada como una distribución inicial, no como una obligación matemática. Si fallas en un concepto, aumentaremos el tiempo dedicado a practicarlo.
Cada tema tendrá una ficha con:
    • Definición precisa.
    • Funcionamiento interno.
    • Ejemplos correctos e incorrectos.
    • Errores habituales en entrevistas.
    • Comparación con otros lenguajes o frameworks.
    • Preguntas de recuperación activa.
    • Un ejercicio práctico.
    • Criterios objetivos para considerar que lo dominas.
Además, mantendremos un registro de los fallos. No repetiremos todo el temario cada vez que te equivoques en una pregunta: identificaremos si el problema es conceptual, de sintaxis, de interpretación del enunciado o de falta de práctica.
4. Calendario de preparación: 16 semanas
Como punto de partida, propongo dedicar entre 8 y 10 horas semanales. Si dispones de menos tiempo, ajustaremos el ritmo sin sacrificar los fundamentos.
Semanas
Objetivo principal
1–2
Fundamentos, JavaScript/TypeScript y diagnóstico de lagunas
3–5
React, renderizado, hooks, estado global y testing
6–7
Angular, Signals, RxJS y arquitectura
8–10
Java, concurrencia, colecciones, excepciones y Spring Boot
11–12
Python, asincronía, FastAPI y testing
13–14
PHP, Laravel, Eloquent y seguridad
15
SQL, HTTP, Git, Docker, CI/CD y arquitectura
16
Simulacros completos y revisión de errores
Las áreas transversales se practicarán desde el principio. Al terminar estas 16 semanas, repetiremos el diagnóstico inicial para medir qué ha mejorado y qué necesita refuerzo. No consideraré que un tema está dominado simplemente porque hayas aprobado un test: también tendrás que explicar sus mecanismos y aplicarlos en código.
Este calendario es una primera vuelta intensiva, no una promesa de dominar cinco ecosistemas por completo en cuatro meses. La profundidad necesaria dependerá de las ofertas a las que quieras optar.
5. Empezamos con un diagnóstico real
Quiero que la primera sesión nos sirva para distinguir lo que ya dominas de lo que necesitas reforzar. No hace falta estudiar antes ni buscar las respuestas. Si no sabes alguna, es preferible reconocerlo: así podremos dirigir el esfuerzo donde más lo necesitas.
Prueba inicial
0 de 6
6 preguntas · Sin límite de tiempo · No resta puntos por fallar
1. En JavaScript, ¿qué ocurre con una variable declarada con const que contiene un objeto?
A. El objeto es completamente inmutable.
B. No se puede reasignar la variable, pero sus propiedades pueden modificarse.
C. El objeto se copia automáticamente en cada asignación.
D. El objeto no puede pasarse a otras funciones.
2. En React, ¿por qué puede volver a renderizarse un hijo envuelto en React.memo?
A. React.memo desactiva la comparación de props.
B. Porque el hijo siempre se renderiza cuando cambia cualquier estado de la aplicación.
C. Porque recibe una nueva referencia de función u otra prop que ha cambiado superficialmente.
D. Porque React.memo solo funciona con componentes de clase.
3. En Java, ¿qué afirmación sobre volatile es correcta?
A. Hace atómicas todas las operaciones sobre la variable.
B. Garantiza que solo un hilo acceda a la variable.
C. Proporciona garantías de visibilidad y orden de memoria, pero no hace atómico count++.
D. Solo sirve para variables primitivas.
4. En Angular, ¿qué operador RxJS resulta adecuado para una búsqueda HTTP donde una consulta nueva debe dejar de procesar la anterior?
A. switchMap
B. mergeMap
C. concatMap
D. tap
5. En SQL, ¿para qué sirve principalmente un índice?
A. Para garantizar que todas las consultas sean instantáneas.
B. Para acelerar determinadas búsquedas y operaciones, con costes de almacenamiento y escritura.
C. Para impedir que existan valores NULL.
D. Para sustituir las claves foráneas.
6. En Python, ¿qué devuelve normalmente una función declarada con async def cuando se llama sin await?
A. El resultado final de la función.
B. Un hilo nuevo ejecutando la función.
C. Un objeto coroutine.
D. Siempre una excepción SyntaxError.
Corregir respuestas
Mi objetivo es que podamos trabajar de manera continuada: una lección, ejercicios, corrección razonada, repaso espaciado y una pequeña prueba. Cuando aparezca un concepto que ya domines, avanzaremos más rápido; cuando encontremos una laguna, nos detendremos hasta resolverla.
Y una última consideración: no necesitas saberlo todo para optar a un empleo junior. Necesitas dominar los fundamentos, conocer con solvencia las tecnologías que aparecen en la oferta y ser capaz de razonar cuando te enfrentas a algo que no recuerdas. Esa es la capacidad que vamos a desarrollar.



Vamos a comenzar mi formación técnica para entrevistas. Mi resultado del diagnóstico inicial ha sido 2/6. Mis respuestas: 1: A; 2: D; 3: B; 4: A; 5: B; 6: D. Analiza mis errores y empieza por el primer tema que deba reforzar. Explícame los fundamentos, dame ejemplos de código, ejercicios y preguntas de entrevista. Avancemos tema a tema, sin saltar al siguiente hasta comprobar que entiendo el actual.
Juan, vamos a empezar en serio. Tu resultado ha sido de 2/6, pero lo importante no es la nota: es identificar qué conceptos necesitas reforzar y por qué.
No vamos a saltar de tecnología en tecnología intentando memorizar respuestas. Trabajaremos cada concepto hasta que puedas explicarlo, predecir qué sucede en el código y aplicarlo a un problema nuevo.
1. Análisis de tu diagnóstico
2/6
33,3 % de respuestas correctas
Diagnóstico inicial
Correctas: 4 y 5
Concurrencia de peticiones en Angular con switchMap e índices en SQL. Son dos conceptos importantes que ya has reconocido correctamente.
Incorrectas: 1, 2, 3 y 6
Mutabilidad en JavaScript, renderizado de React, visibilidad de memoria en Java y ejecución asíncrona en Python.
Estos cuatro errores no significan necesariamente que desconozcas las tecnologías. Nos indican que debemos reforzar los mecanismos internos que suelen evaluar los test técnicos.
Mi decisión es comenzar por JavaScript: variables, referencias y mutabilidad. Es un fundamento transversal para React y Angular, y nos permitirá abordar después cuestiones como las actualizaciones de estado, la comparación de objetos y los renders innecesarios.
Lección 1. const, referencias y mutabilidad en JavaScript
1.1. ¿Qué significa realmente const?
En JavaScript podemos declarar variables con const, let y, en código antiguo, var.
La diferencia fundamental entre const y let es si podemos reasignar el identificador.
let age = 25;

age = 26; // Correcto

const name = "Juan";

name = "Pedro"; // TypeError
Con let, podemos asignar otro valor a la variable.
Con const, no podemos reasignar el identificador después de su inicialización.
Pero aquí aparece una distinción fundamental: impedir la reasignación de una variable no es lo mismo que impedir que un objeto cambie.
1.2. Tu primer error: pensar que const hace inmutable un objeto
Esta era la primera pregunta del diagnóstico:
En JavaScript, ¿qué ocurre con una variable declarada con const que contiene un objeto?
La respuesta correcta era B: no puedes reasignar la variable, pero sí modificar las propiedades del objeto.
Veamos por qué.
const user = {
    name: "Juan",
    age: 30
};

user.age = 31;

console.log(user.age); // 31
Este código es válido. No hemos reasignado user; hemos modificado una propiedad del objeto al que hace referencia.
Sin embargo:
const user = {
    name: "Juan",
    age: 30
};

user = {
    name: "Pedro",
    age: 25
};
Este segundo código produce un TypeError, porque intenta asignar un objeto diferente al identificador user.
Visualiza la diferencia
Caso A: modificar una propiedad
user (const)
Objeto
name: "Juan"
age: 31
Permitido
El identificador sigue apuntando al mismo objeto.
Caso B: reasignar la variable
user (const)
Objeto original
name: "Juan"
age: 30
No permitido
Intentar que user apunte a otro objeto genera un error.
1.3. Valores primitivos frente a objetos
Para comprender las referencias, primero debemos distinguir dos categorías de valores.
Valores primitivos
Objetos
number
Objetos literales {}
string
Arrays []
boolean
Funciones
null
Instancias de clases
undefined
Otros objetos
Los primitivos incluyen también bigint y symbol.
Cuando copiamos un valor primitivo, obtenemos ese valor de forma independiente:
let a = 10;
let b = a;

b = 20;

console.log(a); // 10
console.log(b); // 20
Modificar b no cambia a.
Con los objetos ocurre algo diferente: cuando asignamos un objeto a otra variable, copiamos la referencia al objeto, no creamos automáticamente una copia independiente.
const a = { score: 10 };
const b = a;

b.score = 20;

console.log(a.score); // 20
console.log(b.score); // 20
¿Por qué?
Porque a y b hacen referencia al mismo objeto.
Variable a
Variable b
Un único objeto compartido
{ score: 20 }
Cambiar el objeto a través de cualquiera de las dos referencias afecta a lo que observan ambas variables.
Este fenómeno se conoce como aliasing: varias referencias permiten acceder al mismo objeto mutable.
Una precisión importante: JavaScript pasa los argumentos de función por valor. Cuando ese valor es una referencia a un objeto, la función recibe una copia de la referencia, que sigue apuntando al mismo objeto.
function updateUser(user) {
    user.age = 40;
}

const person = { age: 30 };

updateUser(person);

console.log(person.age); // 40
La función modifica el objeto compartido. Eso no significa que pueda reasignar la variable person del ámbito exterior.
1.4. ¿Cómo podemos crear un objeto nuevo?
Podemos utilizar el operador spread (...) para copiar superficialmente las propiedades de un objeto.
const original = {
    name: "Juan",
    age: 30
};

const copy = { ...original };

copy.age = 40;

console.log(original.age); // 30
console.log(copy.age);     // 40
Ahora los dos objetos son distintos.
Pero cuidado: el spread realiza una copia superficial, no una copia profunda.
const original = {
    name: "Juan",
    address: {
        city: "Santander"
    }
};

const copy = { ...original };

copy.address.city = "Madrid";

console.log(original.address.city); // Madrid
Aunque copy es un objeto diferente de original, ambos comparten la referencia al objeto anidado address.
Este detalle es muy importante en React, donde modificar accidentalmente objetos anidados puede causar errores difíciles de localizar.
2. Por qué esto importa en React
React utiliza la identidad de los valores y la comparación de referencias en distintas partes de su modelo de renderizado.
Observa este ejemplo:
const [user, setUser] = useState({
    name: "Juan",
    age: 30
});

function birthday() {
    user.age += 1;
    setUser(user);
}
¿Qué problema tiene?
Estás modificando el objeto existente y después pasas a setUser exactamente la misma referencia.
React puede considerar que el nuevo estado es idéntico al anterior mediante Object.is y omitir el renderizado. Además, has mutado un objeto que representa el estado anterior.
La forma adecuada es crear un objeto nuevo:
function birthday() {
    setUser(previousUser => ({
        ...previousUser,
        age: previousUser.age + 1
    }));
}
Ahora se cumplen dos condiciones:
    1. El estado anterior no se modifica.
    2. Se devuelve un objeto nuevo, con una referencia diferente.
Esto facilita que React detecte el cambio y mantiene un modelo de estado más predecible.
No significa que cualquier objeto nuevo garantice un único renderizado ni que React siempre tenga que renderizar inmediatamente. El comportamiento depende del contexto y del procesamiento de actualizaciones. Lo esencial es evitar mutaciones directas del estado.
3. Ejercicios de comprobación
Ahora quiero comprobar que has entendido el mecanismo y no solo memorizado las definiciones.
Responde sin ejecutar el código. Si dudas, explícame tu razonamiento: los errores nos servirán para detectar exactamente qué debemos reforzar.
Práctica 1
0/4 respondidas
1. ¿Qué imprime este código?
const user = { age: 20 }; const other = user; other.age = 25; console.log(user.age);
A. 20
B. 25
C. undefined
D. TypeError
2. ¿Qué sucede aquí?
const numbers = [1, 2, 3]; numbers.push(4); console.log(numbers.length);
A. Se produce un TypeError porque numbers es const.
B. Imprime 3 porque const impide modificar arrays.
C. Imprime 4 porque se modifica el array sin reasignar la variable.
D. Se crea automáticamente un array nuevo.
3. ¿Qué imprime este código?
const original = { score: 10 }; const copy = { ...original }; copy.score = 99; console.log(original.score);
A. 10
B. 99
C. undefined
D. TypeError
4. ¿Qué sucede al ejecutar este código?
const a = { value: 1 }; a = { value: 2 };
A. a.value pasa a valer 2.
B. El objeto se fusiona con el nuevo.
C. No sucede nada.
D. Se produce un TypeError por reasignar una variable const.
4. Pregunta oral de entrevista
Imagina que el entrevistador te pregunta:
«Si declaro un objeto con const, ¿por qué puedo modificar sus propiedades? ¿Qué diferencia hay entre reasignar una referencia y mutar el objeto al que apunta?»
Intenta responder con tus propias palabras, como si estuvieras en una entrevista real.
Primero completa los cuatro ejercicios y después dame tu explicación oral. Corregiremos ambas cosas y reforzaremos cualquier confusión que aparezca antes de pasar al siguiente concepto.



He completado la práctica 1 sobre const, referencias y mutabilidad. Mis respuestas: 1: B; 2: A; 3: B; 4: D. Analiza mis respuestas y mis razonamientos pendientes. Si no domino el tema, propón nuevos ejercicios equivalentes. No avances a otro tema hasta comprobar que entiendo las referencias y la mutabilidad.
---
«Si declaro un objeto con const, ¿por qué puedo modificar sus propiedades? ¿Qué diferencia hay entre reasignar una referencia y mutar el objeto al que apunta?» 
no se contestar esto
Juan, perfecto: precisamente para esto estamos haciendo la formación. Que me digas que no sabes contestar una pregunta es mucho más útil que memorizar una respuesta sin entenderla. Vamos a trabajar el concepto hasta que puedas explicarlo con seguridad en una entrevista.
Hay una buena noticia: el concepto se puede entender con un modelo mental bastante sencillo. Lo importante es distinguir tres cosas que JavaScript trata por separado: el identificador de una variable, la referencia que contiene y el objeto al que esa referencia permite acceder.
1. Corrección de tus cuatro ejercicios
Tus respuestas han sido:
Ejercicio
Tu respuesta
Correcta
Evaluación
1. Dos variables y un objeto compartido
B
B
Correcta
2. Modificar un array declarado con const
A
C
Incorrecta
3. Copia superficial con spread
B
A
Incorrecta
4. Reasignar una variable const
D
D
Correcta
Resultado: 2/4.
Los ejercicios 1 y 4 están bien. En cambio, los ejercicios 2 y 3 revelan una confusión concreta: estás mezclando la prohibición de reasignar una variable con la posibilidad de modificar el contenido de un objeto.
Eso es exactamente lo que vamos a corregir. No avanzaremos a otro tema todavía.
2. La explicación que necesitas entender
2.1. Una variable const es como una etiqueta que no puedes cambiar de sitio
Imagina este código:
const user = {
    name: "Juan",
    age: 30
};
Piensa en user como una etiqueta asociada a un objeto.
Identificador: user
Declarado con const
Objeto
name: "Juan"
age: 30
La regla de const es que no puedes hacer que el identificador user pase a contener una referencia diferente mediante una reasignación.
Sin embargo, sí puedes modificar las propiedades del objeto al que apunta.
user.age = 31;        // Permitido
user.name = "Pedro";  // Permitido
user.city = "Santander"; // Permitido

user = {}; // TypeError
Las tres primeras instrucciones modifican el objeto. La última intenta reasignar user.
Esta es la primera distinción que debes interiorizar:
    • Reasignar: intentar dar otro valor al identificador.
    • Mutar: modificar el contenido de un objeto que ya existe.
const impide la primera operación, pero no impide por sí mismo la segunda.
2.2. Por qué fallaste la pregunta del array
Tu respuesta al ejercicio 2 fue A:
const numbers = [1, 2, 3];

numbers.push(4);

console.log(numbers.length);
Pensaste que const impedía modificar el array.
Pero push() modifica el array existente. No reasigna la variable numbers.
El resultado es:
4
Puedes modificar sus elementos, añadir elementos, eliminarlos o utilizar otros métodos mutables, siempre que no intentes reasignar el identificador.
Por ejemplo:
const numbers = [1, 2, 3];

numbers[0] = 99;
numbers.push(4);
numbers.pop();

console.log(numbers); // [99, 2, 3]
Todas estas operaciones son válidas.
En cambio:
const numbers = [1, 2, 3];

numbers = [4, 5, 6]; // TypeError
Aquí sí intentas sustituir el valor asociado al identificador.
2.3. Por qué fallaste la pregunta del spread
Tu respuesta al ejercicio 3 fue B, pero el resultado correcto era A.
const original = { score: 10 };
const copy = { ...original };

copy.score = 99;

console.log(original.score);
El resultado es 10.
El operador spread crea un objeto nuevo y copia las propiedades propias enumerables del objeto original. Como score contiene un valor numérico, modificar esa propiedad en la copia no modifica la propiedad del original.
Visualmente:
Objeto original
{ score: 10 }
original
score: 10
copy
score: 99
Son dos objetos distintos. Cambiar una propiedad primitiva de la copia no modifica la misma propiedad del original.
Pero hay una trampa importante: el spread es una copia superficial.
const original = {
    score: 10,
    address: {
        city: "Santander"
    }
};

const copy = { ...original };

copy.address.city = "Madrid";

console.log(original.address.city); // "Madrid"
¿Por qué? Porque se ha creado un objeto exterior nuevo, pero las propiedades anidadas que contienen objetos siguen apuntando a los mismos objetos.
No hace falta que memorices todavía técnicas de copia profunda. Quiero que entiendas primero esta regla: dos objetos exteriores diferentes pueden compartir referencias a un mismo objeto interior.
3. Cómo contestar en una entrevista
Esta es una respuesta que podrías dar con un nivel adecuado para una entrevista junior:
Respuesta modelo
«En JavaScript, const impide reasignar el identificador después de inicializarlo, pero no hace que el objeto sea inmutable. Si declaro const user = { age: 30 }, puedo ejecutar user.age = 31 porque estoy modificando una propiedad del mismo objeto. En cambio, user = { age: 31 } intenta reasignar la variable y produce un error. Si quiero crear un objeto nuevo sin modificar el original, puedo utilizar el operador spread, aunque realiza una copia superficial».
No intentes repetirla palabra por palabra. Si comprendes el mecanismo, podrás explicarlo de distintas maneras y contestar preguntas de seguimiento.
4. Segunda ronda: ejercicios equivalentes
Vamos a comprobar si ya puedes aplicar el concepto en situaciones ligeramente diferentes. No consultes las explicaciones anteriores mientras respondes, si puedes evitarlo.
Práctica 2
0/5
1. ¿Qué ocurre?
const product = { price: 10 }; product.price = 15; console.log(product.price);
A. Se produce un TypeError.
B. Imprime 10.
C. Imprime 15.
D. Imprime undefined.
2. ¿Qué ocurre?
const items = ["A", "B"]; items.push("C"); console.log(items.join(","));
A. A,B
B. A,B,C
C. TypeError
D. undefined
3. ¿Qué imprime?
const a = { x: 1 }; const b = { ...a }; b.x = 2; console.log(a.x);
A. 1
B. 2
C. undefined
D. TypeError
4. ¿Qué imprime?
const a = { nested: { x: 1 } }; const b = { ...a }; b.nested.x = 2; console.log(a.nested.x);
A. 1
B. 2
C. undefined
D. TypeError
5. ¿Qué ocurre?
let a = { x: 1 }; const b = a; a = { x: 2 }; console.log(b.x);
A. 1
B. 2
C. TypeError
D. undefined
Tu siguiente tarea: completa los cinco ejercicios y después intenta explicar, sin copiar la respuesta modelo, por qué const permite modificar las propiedades de un objeto. Si todavía no te sale, lo trabajaremos con más ejemplos. No pasaremos al siguiente tema hasta que esta distinción esté clara.
Esto también podría interesarte.
Anuncio
Texto pegado(20261019-213326).txtDocumento
solo queria añadir que me deberias enseñar todo desde las bases
Sí, Juan. Y haces bien en insistir en ello: vamos a enseñar todo desde las bases, sin dar por supuesto que conoces un concepto porque ya hayas utilizado una tecnología en tus proyectos.
El plan que planteamos anteriormente sigue siendo válido, pero hay que aplicar un criterio importante: empezar por los fundamentos de programación y construir el conocimiento progresivamente. No quiero que memorices que const permite modificar las propiedades de un objeto; quiero que entiendas qué es una variable, qué contiene, cómo se representan los objetos y qué significa que dos variables hagan referencia al mismo objeto.
Seguiremos este orden:
    1. Fundamentos de programación: variables, tipos, valores, operadores, condiciones, bucles, funciones, memoria, referencias, mutabilidad y gestión de errores.
    2. Estructuras de datos y algoritmos: arrays, listas, mapas, conjuntos, búsqueda, ordenación y complejidad.
    3. JavaScript y TypeScript: sintaxis, funciones, ámbito, asincronía, promesas y los conceptos necesarios para entender React y Angular.
    4. React: componentes, props, estado, renderizado, hooks, rendimiento y pruebas.
    5. Angular: componentes, servicios, inyección de dependencias, Signals y RxJS.
    6. Java y Spring Boot: POO, colecciones, excepciones, memoria, concurrencia, APIs y Spring Batch.
    7. Python y FastAPI: tipos, objetos, funciones, asincronía, APIs y pruebas.
    8. PHP y Laravel: fundamentos del lenguaje, POO, peticiones HTTP, Eloquent, seguridad y pruebas.
    9. Ingeniería de software: SQL, HTTP, REST, seguridad, Git, testing, CI/CD, Docker y arquitectura.
    10. Simulacros de entrevistas: preguntas tipo test, análisis de código, ejercicios prácticos y explicaciones orales.
No obstante, no será una secuencia rígida: si un concepto de JavaScript requiere comprender primero las referencias, nos detendremos en las referencias. Si ya dominas algo, lo comprobaremos y avanzaremos más deprisa.
Cómo trabajaremos cada concepto
    • 1. Explicación desde cero: qué es, para qué sirve y por qué funciona así.
    • 2. Ejemplos sencillos: primero casos básicos y después casos más complejos.
    • 3. Comparaciones: cuando ayuden a entenderlo, incluyendo diferencias entre lenguajes.
    • 4. Práctica guiada: resolveremos ejemplos juntos antes de que tengas que hacerlo solo.
    • 5. Ejercicios de entrevista: preguntas tipo test, predicción de resultados y detección de errores.
    • 6. Comprobación real: tendrás que explicar el razonamiento con tus propias palabras, no solo acertar la respuesta.
Y una regla importante: si fallas, no significa que debamos pasar a otro ejercicio sin más. Revisaremos qué parte del concepto no está clara y la trabajaremos con ejemplos distintos hasta que puedas aplicarla.
¿Qué hacemos ahora?
Seguimos exactamente donde estamos: JavaScript, variables, referencias y mutabilidad. Es una buena base para entender posteriormente el estado de React, los objetos de Java y Python y muchos errores habituales en pruebas técnicas.
Ya tienes los cinco ejercicios pendientes. Puedes responderlos cuando quieras; los corregiremos uno por uno, explicando desde los fundamentos cualquier concepto que todavía no esté claro. No avanzaremos al siguiente tema hasta comprobar que lo entiendes.
No partiremos de la suposición de que ya lo sabes todo. Partiremos de lo que realmente comprendes y construiremos desde ahí.
Esto también podría interesarte.
Anuncio
Markdown pegado.mdDocumento
podemos ir en orden y usando java para empezar que es lo que he estudiado?
Sí, Juan. Vamos a seguir el orden del plan original, pero empezando por Java, que es el lenguaje que has estudiado en tu formación de DAM y con el que tienes experiencia profesional. Tiene sentido utilizarlo como punto de partida para construir unos fundamentos sólidos antes de pasar a JavaScript, React y Angular.
Hay un ajuste importante respecto al calendario anterior: en lugar de comenzar directamente con conceptos de varios lenguajes, estudiaremos primero los fundamentos utilizando Java. Después trasladaremos esos conocimientos a las demás tecnologías.
Nuestro itinerario de formación
1. Fundamentos de programación con Java
Empezamos aquí
Variables, tipos, operadores, condiciones, bucles, métodos, arrays, referencias, memoria, POO y excepciones. Todo explicado desde cero, sin dar conocimientos por supuestos.
2. Estructuras de datos y algoritmos
Listas, pilas, colas, mapas, conjuntos, búsquedas, ordenación y complejidad algorítmica.
3. Java avanzado y Spring Boot
Colecciones, genéricos, Streams, JVM, concurrencia, testing, inyección de dependencias, APIs REST, persistencia y Spring Batch.
4. JavaScript y TypeScript
Aprenderemos las diferencias respecto a Java: tipado, referencias, funciones, ámbito, asincronía y manejo de errores.
5. React y Angular
Componentes, estado, renderizado, hooks, Signals, RxJS, arquitectura y pruebas técnicas.
6. Python, FastAPI, PHP y Laravel
Desde las particularidades de cada lenguaje hasta el funcionamiento de sus frameworks.
7. Ingeniería de software y entrevistas
SQL, HTTP, seguridad, Git, testing, CI/CD, Docker, arquitectura y simulacros completos.
Cómo vamos a estudiar Java
No empezaremos directamente con volatile, Streams o patrones de diseño. Antes debemos comprobar que dominas los mecanismos básicos sobre los que se construyen.
Cada lección tendrá este orden:
    1. Explicación desde cero, con terminología técnica y ejemplos.
    2. Código Java comentado paso a paso.
    3. Ejemplos de qué ocurre en memoria cuando resulte relevante.
    4. Errores habituales y preguntas típicas de entrevistas.
    5. Ejercicios sencillos, seguidos de otros más difíciles.
    6. Una prueba final y una explicación con tus propias palabras.
Si algo no queda claro, nos detenemos. No pasaremos de tema solo por haber completado unos ejercicios.
Primera lección: ¿desde dónde empezamos?
Para ajustar el nivel correctamente, quiero comprobar primero tus conocimientos de Java. No es un examen para aprobar o suspender; es una forma de evitar tanto explicarte cosas que ya dominas como saltarnos fundamentos importantes.
1. ¿Qué nivel de Java sientes que tienes actualmente?
Necesito repasar desde qué es una variable y cómo funciona un programa.
Conozco la sintaxis y he programado, pero tengo lagunas en los fundamentos.
Programo con soltura, pero quiero profundizar en memoria, concurrencia y mecanismos internos.
2. ¿Qué temas crees que necesitas reforzar?
Puedes seleccionar varios. Si no lo tienes claro, déjalo como está.
Variables y tipos
Condiciones y bucles
Métodos y parámetros
Arrays y colecciones
Referencias y memoria
Programación orientada a objetos
Excepciones
Concurrencia e hilos
3. ¿Cuál es tu prioridad principal?
Superar pruebas técnicas y entrevistas de trabajo.
Comprender a fondo cómo funciona la programación.
Ambas cosas, con la misma importancia.
A partir de aquí construiremos una base que te sirva tanto para las entrevistas de Java como para comprender mejor el resto de tecnologías Full Stack.

Empezamos la formación desde las bases usando Java y siguiendo el itinerario acordado. Mi nivel actual: conozco sintaxis y he programado, pero tengo lagunas. Temas que quiero reforzar: Variables y tipos, Condiciones y bucles, Métodos y parámetros, Arrays y colecciones, Referencias y memoria, Programación orientada a objetos, Excepciones, Concurrencia e hilos. Prioridad: fundamentos y entrevistas por igual. Diseña la primera lección de Java acorde a esto y no avances sin comprobar mi comprensión.
Lección 1. Fundamentos de Java: variables, tipos y memoria
Juan, vamos a empezar por la base de todo el itinerario: entender cómo un programa representa los datos, los almacena y trabaja con ellos.
Como ya has programado en Java, no voy a tratarte como si nunca hubieras escrito código. Sin embargo, tampoco daré por entendido un concepto solo porque conozcas su sintaxis. Vamos a reconstruir los fundamentos, paso a paso, y relacionarlos con las preguntas que pueden aparecer en una entrevista técnica.
En esta primera lección nos centraremos en:
    • Variables, tipos de datos y asignaciones.
    • Tipos primitivos y tipos de referencia.
    • Diferencias entre valor, identidad y referencia.
    • Errores habituales en entrevistas técnicas.
Hoy no avanzaremos a condiciones, bucles ni métodos hasta comprobar que comprendes estos conceptos. Las referencias y la memoria las introduciremos de forma gradual; las estudiaremos más a fondo en su propio bloque.
1. ¿Qué es una variable?
Una variable es un elemento identificado por un nombre que permite almacenar un valor de un tipo determinado.
Por ejemplo:
int edad = 25;
Esta línea declara e inicializa una variable. Vamos a descomponerla:
int
Tipo
Indica qué clase de valor puede almacenar la variable.
edad
Nombre
Es el identificador que utilizamos para acceder a la variable.
= 25
Inicialización
Asigna el valor inicial 25 a la variable.
Podemos imaginarlo inicialmente como una casilla identificada con el nombre edad que contiene el número 25.
Representación conceptual
edad
25
Tipo: int
Esta representación es suficiente para empezar, aunque más adelante veremos por qué no todos los valores se comportan como números almacenados directamente.
Declarar no es lo mismo que inicializar
Observa la diferencia:
int edad;       // Declaración
edad = 25;      // Asignación
int puntos = 10; // Declaración e inicialización
    • Declarar: definir una variable, indicando su tipo y nombre.
    • Asignar: darle un valor.
    • Inicializar: darle su primer valor.
Hay una distinción importante en Java: una variable local debe recibir un valor antes de poder leerse.
public class Main {
    public static void main(String[] args) {
        int edad;
        System.out.println(edad); // Error de compilación
    }
}
El compilador rechaza el código porque edad no se ha inicializado. No debemos confundir esto con los campos de una clase, que reciben valores predeterminados si no los inicializamos explícitamente.
2. Tipos de datos: ¿qué puede contener una variable?
Java es un lenguaje de tipado estático. Esto significa que el tipo de una variable se determina al declararla y el compilador comprueba que los usos sean compatibles con ese tipo.
Por ejemplo:
int edad = 25;
edad = 26;       // Correcto
edad = "veinte"; // Error de compilación
La variable edad es de tipo int. Podemos cambiar su valor por otro entero, pero no asignarle directamente una cadena de texto.
Java organiza los tipos en dos grandes categorías.
2.1. Tipos primitivos
Java tiene ocho tipos primitivos:
Tipo
Qué representa
Ejemplo
byte
Enteros pequeños
byte nivel = 10;
short
Enteros de 16 bits
short año = 2026;
int
Enteros de 32 bits
int edad = 25;
long
Enteros de 64 bits
long poblacion = 8000000L;
float
Decimales de precisión simple
float precio = 9.5f;
double
Decimales de precisión doble
double pi = 3.14159;
char
Una unidad de código UTF-16
char letra = 'J';
boolean
Valor lógico verdadero o falso
boolean activo = true;
Algunos detalles que suelen aparecer en pruebas técnicas:
    • Un literal long suele llevar el sufijo L, como 100L.
    • Un literal float necesita normalmente el sufijo f, como 3.5f.
    • Los caracteres usan comillas simples: 'J'. Las cadenas usan comillas dobles: "Juan".
    • boolean solo admite true o false; no utiliza 0 y 1 como sustitutos directos.
Los tipos enteros tienen rangos diferentes. Por ejemplo, un byte admite valores entre −128 y 127, mientras que un int admite un rango mucho mayor.
byte numero = 127;
numero = 128; // Error de compilación: constante fuera del rango
Pregunta típica de entrevista: ¿por qué Java dispone de distintos tipos numéricos? Para representar diferentes rangos y necesidades de precisión, además de permitir expresar qué clase de dato esperamos manejar.
2.2. Tipos de referencia
Además de los primitivos, Java tiene tipos de referencia. Entre ellos están las clases, los arrays, las interfaces y los enumerados.
Por ejemplo:
String nombre = "Juan";
int[] numeros = {10, 20, 30};
String es una clase y int[] es un tipo array. Las variables nombre y numeros son variables de referencia.
Esta diferencia es fundamental:
    • Una variable primitiva almacena directamente un valor primitivo.
    • Una variable de referencia contiene una referencia a un objeto, o el valor especial null.
No todos los tipos de referencia tienen que ser objetos creados con new: las cadenas y algunos arrays, por ejemplo, pueden inicializarse de otras maneras.
3. Asignar una variable no siempre significa lo mismo
Aquí empieza una de las diferencias más importantes para comprender memoria y referencias.
Caso A: asignación de un primitivo
int a = 10;
int b = a;

b = 20;

System.out.println(a); // 10
System.out.println(b); // 20
¿Qué ha ocurrido?
    1. a contiene el valor 10.
    2. b = a copia ese valor a b.
    3. Cambiar b no modifica a.
a
10
b
20
Dos variables independientes: cada una tiene su propio valor.
Caso B: asignación de una referencia
Ahora vamos a trabajar con objetos.
class Persona {
    String nombre;
}
Y en el método main:
Persona a = new Persona();
a.nombre = "Ana";

Persona b = a;

b.nombre = "Luis";

System.out.println(a.nombre); // Luis
System.out.println(b.nombre); // Luis
¿Por qué imprime Luis en ambos casos?
Porque b = a no crea una nueva Persona. Copia la referencia que contiene a, por lo que ambas variables permiten acceder al mismo objeto.
a
Referencia
b
Referencia copiada

Un único objeto Persona
nombre = "Luis"
Las dos referencias apuntan al mismo objeto. Modificarlo a través de una de ellas se observa al acceder a través de la otra.
Este fenómeno se conoce como aliasing: varias variables hacen referencia al mismo objeto.
Hay dos operaciones distintas que conviene no confundir:
    • b.nombre = "Luis" modifica el objeto compartido.
    • b = new Persona() hace que b pase a referirse a otro objeto; no reasigna a.
Esta distinción será esencial cuando estudiemos arrays, colecciones, objetos mutables y paso de parámetros a métodos.
4. ¿Qué papel tiene null?
Una variable de referencia puede no apuntar a ningún objeto. Para expresar eso, Java dispone de null.
Persona persona = null;
System.out.println(persona.nombre); // NullPointerException
El código compila, pero al ejecutar la segunda línea se produce una NullPointerException: intentamos acceder a nombre a través de una referencia que no apunta a ningún objeto.
En cambio:
Persona persona = new Persona();
System.out.println(persona.nombre); // null
En este segundo caso, persona sí referencia un objeto. Lo que ocurre es que el campo nombre, al ser una referencia y no haberse inicializado explícitamente, tiene el valor predeterminado null.
La diferencia es importante:
    • La referencia persona puede ser null.
    • El objeto puede existir y contener un campo cuyo valor sea null.
    • Una variable primitiva como int no puede almacenar null.
5. Una excepción importante: String
Aunque String es un tipo de referencia, no se comporta como un objeto mutable normal. Las cadenas de Java son inmutables: una vez creada una cadena, su contenido no se modifica.
String texto = "Hola";
texto = texto + " Juan";

System.out.println(texto); // Hola Juan
No se ha modificado la cadena original. La expresión crea el resultado de concatenar las cadenas y la variable texto pasa a referirse al resultado.
Esto demuestra dos conceptos diferentes:
    • Mutabilidad del objeto: si se puede cambiar su contenido.
    • Reasignación de la variable: si se puede hacer que la variable se refiera a otro objeto.
No son lo mismo. Una referencia declarada con final tampoco hace automáticamente inmutable el objeto al que apunta.
final Persona persona = new Persona();

persona.nombre = "Ana";       // Correcto
persona = new Persona();      // Error de compilación
final impide reasignar esa variable después de inicializarla, pero no impide modificar los campos mutables del objeto.
6. Preguntas habituales de entrevista
Antes de hacer los ejercicios, quédate con estas distinciones:
Concepto
Qué significa
Tipo
Qué clase de dato puede manejar una variable
Valor primitivo
Se copia el valor al asignarlo a otra variable
Referencia
Permite acceder a un objeto
Mutabilidad
Posibilidad de modificar el estado de un objeto
null
Ausencia de una referencia a un objeto
final
Impide reasignar la variable una vez inicializada
Una pregunta frecuente es: «¿Java pasa los objetos por referencia?»
La respuesta precisa es que Java siempre pasa los argumentos por valor. Cuando el argumento es una referencia, se copia el valor de esa referencia. Así, un método puede modificar el objeto compartido, pero reasignar su parámetro no cambia la variable original del llamador.
Lo veremos con código cuando lleguemos a métodos y parámetros.
7. Tu primera prueba de comprensión
Ahora quiero comprobar si puedes aplicar lo explicado, no solo reconocer las definiciones. No necesitas ejecutar el código. Analiza cada fragmento y elige una respuesta.
Prueba 1 · Java básico
0 de 5
Responde las cinco preguntas. Después podrás corregirlas y leer la explicación de cada una.
1. ¿Qué sucede con este código?
int a = 5; int b = a; b = 8; System.out.println(a);
A. Imprime 5
B. Imprime 8
C. Produce un error de compilación
D. Imprime null
2. ¿Qué imprime el siguiente código?
Persona a = new Persona(); a.nombre = "Ana"; Persona b = a; b.nombre = "Luis"; System.out.println(a.nombre);
A. Ana
B. Luis
C. null
D. Error de compilación
3. ¿Cuál de estas afirmaciones sobre final es correcta?
A. Hace inmutable cualquier objeto
B. Impide modificar todos los campos del objeto
C. Impide reasignar la variable, pero no necesariamente modificar el objeto
D. Solo puede utilizarse con tipos primitivos
4. ¿Qué ocurre aquí?
int edad; System.out.println(edad);
A. Imprime 0
B. Imprime null
C. Produce un error de compilación
D. Produce siempre una NullPointerException
5. ¿Qué afirmación sobre String es correcta?
A. String es un tipo primitivo
B. Una cadena no puede reasignarse a otra variable
C. Las cadenas son inmutables, aunque una variable String puede reasignarse si no es final
D. String no puede ser null
Después de responder, explícame también con tus propias palabras la diferencia entre copiar el valor de un int y copiar la referencia de un objeto. Aunque la prueba salga bien, esa explicación me permitirá comprobar que comprendes el mecanismo.
Nos quedaremos en esta lección hasta que lo tengas claro.
Perfecto, Juan. Continuamos exactamente donde lo dejamos: Lección 1 de Java, variables, tipos y memoria. Todavía no pasaremos a condiciones, bucles ni métodos. Primero comprobaremos que comprendes cómo se comportan las variables y las referencias.
La prueba anterior incluía las soluciones, así que acertar las cinco preguntas no demuestra por sí solo que domines el tema. Vamos a hacer una comprobación nueva, con fragmentos de código que requieren razonar un poco más.
1. Repaso rápido: la idea fundamental
En Java hay dos comportamientos que debes distinguir:
    • Tipos primitivos: al asignar una variable a otra, se copia el valor.
    • Tipos de referencia: al asignar una variable a otra, se copia el valor de la referencia. Ambas pueden permitir el acceso al mismo objeto.
Por ejemplo, con un primitivo:
int a = 10;
int b = a;

b = 20;

System.out.println(a); // 10
System.out.println(b); // 20
Con un objeto:
class Persona {
    String nombre;
}

Persona a = new Persona();
a.nombre = "Ana";

Persona b = a;
b.nombre = "Luis";

System.out.println(a.nombre); // Luis
System.out.println(b.nombre); // Luis
En el segundo caso, b = a no crea una nueva persona. Copia la referencia y ambas variables permiten acceder al mismo objeto.
Una precisión importante: Java siempre pasa los argumentos por valor, incluso cuando el argumento es una referencia. Lo estudiaremos en profundidad cuando lleguemos a métodos.
2. Prueba de comprensión
Son cinco preguntas. No necesitas ejecutar el código ni consultar documentación. Para cada una, elige la respuesta y, si puedes, explica brevemente por qué.
Diagnóstico de la lección 1
0 de 5
1. ¿Qué imprime este código?
int x = 4; int y = x; x = 9; System.out.println(y);
A. 4
B. 9
C. null
D. Error de compilación
Tu razonamiento (opcional, pero recomendable)
2. ¿Qué imprime este código?
int[] a = {1, 2}; int[] b = a; b[0] = 7; System.out.println(a[0]);
A. 1
B. 7
C. 0
D. Error de compilación
Tu razonamiento (opcional, pero recomendable)
3. ¿Qué sucede aquí?
final int[] numeros = {1, 2}; numeros[0] = 8; numeros = new int[]{3, 4};
A. Las dos operaciones son válidas.
B. La primera falla porque el array es final.
C. La primera es válida, pero la reasignación produce un error de compilación.
D. El array se vuelve completamente inmutable.
Tu razonamiento (opcional, pero recomendable)
4. ¿Qué imprime este código?
Persona p = new Persona(); p.nombre = "Ana"; Persona q = new Persona(); q.nombre = "Luis"; q = p; System.out.println(q.nombre);
A. Luis
B. Ana
C. null
D. Error de compilación
Tu razonamiento (opcional, pero recomendable)
5. ¿Cuál es la afirmación correcta sobre null?
A. Una variable int puede almacenar null.
B. Toda variable local sin inicializar vale null.
C. Una referencia puede valer null; intentar acceder a un miembro mediante ella provoca una NullPointerException en ejecución.
D. Asignar null a una referencia produce siempre un error de compilación.
Tu razonamiento (opcional, pero recomendable)
Corregir respuestas
Puedes contestar las cinco preguntas antes de corregirlas. No hay penalización por fallar.
3. La explicación que quiero que me des
Además del test, contéstame con tus propias palabras a esta pregunta:
¿Cuál es la diferencia entre copiar el valor de un int y copiar la referencia de un objeto?
No busco una definición de memoria. Quiero que expliques qué sucede con las variables y por qué modificar una de ellas puede afectar —o no— a lo que observamos mediante la otra.
Con tus respuestas podré distinguir si el concepto está consolidado o si debemos practicar algún caso adicional. No avanzaremos hasta comprobar tu comprensión.
¿Cuál es la diferencia entre copiar el valor de un int y copiar la referencia de un objeto? 
copiar el valor de un int es simplemente oBTENER UN VALOR DE UNA VARIABLE Y ASIGNARSELO A OTRA, en cambio copiar una refrencia de un objeto hace que ambos objetos apunten a la misma direccion de memoria
Juan, tu explicación es correcta en lo esencial. Has identificado la diferencia fundamental: al copiar un int, se copia su valor; al copiar una referencia, ambas variables permiten acceder al mismo objeto.
Vamos a precisar un par de detalles para que puedas defender esta respuesta en una entrevista técnica.
1. Qué has entendido correctamente
Caso A. Copiar el valor de un int
int a = 10;
int b = a;

b = 20;

System.out.println(a); // 10
System.out.println(b); // 20
Cuando ejecutamos int b = a, el valor 10 se copia a b. A partir de ese momento, las variables son independientes.
Variable a
10
Variable b
20
Cada variable conserva su propio valor. Modificar b no modifica a.
Caso B. Copiar la referencia de un objeto
class Persona {
    String nombre;
}

Persona a = new Persona();
a.nombre = "Ana";

Persona b = a;
b.nombre = "Luis";

System.out.println(a.nombre); // Luis
Aquí también se copia un valor, pero ese valor es una referencia al objeto, no el objeto completo.
Tu expresión «ambos apuntan a la misma dirección de memoria» es una buena representación conceptual. Sin embargo, hay un matiz importante: Java no garantiza que puedas conocer o manipular directamente una dirección de memoria física. Lo preciso es decir que ambas variables contienen referencias al mismo objeto.
Variable a
Referencia
Variable b
Referencia copiada
Un único objeto Persona
nombre = "Luis"
Modificar el objeto mediante b también se observa al acceder a él mediante a.
2. El matiz que debes dominar
Hay una confusión frecuente: pensar que, porque a y b hacen referencia al mismo objeto, las dos variables son la misma variable.
No es así. Son dos variables distintas que contienen referencias al mismo objeto.
Observa este ejemplo:
Persona a = new Persona();
a.nombre = "Ana";

Persona b = a;

b = new Persona();
b.nombre = "Luis";

System.out.println(a.nombre); // Ana
System.out.println(b.nombre); // Luis
¿Qué ha cambiado?
    1. Inicialmente, a referencia una persona llamada Ana.
    2. b = a copia la referencia, por lo que ambas acceden a esa persona.
    3. b = new Persona() hace que b pase a referenciar un objeto nuevo.
    4. Cambiar el nombre de la nueva persona no afecta a la persona a la que sigue apuntando a.
La asignación de una referencia no crea un alias permanente: puedes reasignar cada variable de forma independiente.
3. Cómo respondería yo en una entrevista
Una respuesta técnicamente sólida sería:
Cuando asignamos una variable primitiva a otra, se copia su valor y ambas variables pasan a tener valores independientes. En cambio, cuando asignamos una variable de referencia a otra, se copia el valor de la referencia, por lo que ambas pueden acceder al mismo objeto. Si modificamos el estado de ese objeto a través de una referencia, el cambio será visible al acceder a él mediante la otra. Sin embargo, reasignar una de las variables no modifica la referencia almacenada en la otra.
Esta respuesta demuestra que entiendes el comportamiento, no solo la terminología.
4. Comprobación final
Antes de dar por consolidado el concepto, quiero comprobar que sabes aplicar esa distinción cuando cambian las operaciones.
¿Qué imprime este programa?
class Caja {
    int valor;
}

public class Main {
    public static void main(String[] args) {
        Caja a = new Caja();
        a.valor = 10;

        Caja b = a;
        b.valor = 20;

        b = new Caja();
        b.valor = 30;

        System.out.println(a.valor);
        System.out.println(b.valor);
    }
}
Selecciona la salida correcta:
A. Imprime 20 y 30.
B. Imprime 30 y 30.
C. Imprime 10 y 30.
D. Produce una excepción.
Explica qué ocurre con a y b en cada asignación.
Comprobar mi comprensión
No avanzaremos todavía a los siguientes temas. Si resuelves este caso y justificas correctamente el resultado, podremos considerar consolidada esta distinción y continuar con los siguientes aspectos de variables, tipos y memoria.
Juan, tu respuesta es correcta: opción C, imprime 10 y 30. Además, tu razonamiento demuestra que estás empezando a comprender cómo funcionan las referencias en Java. Hay un detalle en tu explicación que debemos corregir para que el concepto quede completamente asentado.
1. Corrección paso a paso
Vamos a seguir el estado de los objetos durante la ejecución.
Paso 1. Crear el primer objeto
Caja a = new Caja();
a.valor = 10;
Se crea un objeto Caja cuyo campo valor contiene 10. La variable a hace referencia a ese objeto.
a
Objeto Caja A
valor = 10
Paso 2. Copiar la referencia
Caja b = a;
b.valor = 20;
Aquí tu razonamiento es correcto: b recibe una copia de la referencia que contiene a. Las dos variables permiten acceder al mismo objeto.
Al ejecutar b.valor = 20, modificamos ese único objeto.
a
b
Objeto Caja A
valor = 20
Ambas referencias acceden al mismo objeto.
Paso 3. Reasignar b
b = new Caja();
b.valor = 30;
Este es el punto más importante de la pregunta.
La instrucción b = new Caja() crea un segundo objeto y hace que b lo referencie. No modifica el primer objeto ni cambia la referencia almacenada en a.
Por tanto, el estado final es el siguiente:
a
b
Objeto A
10
valor
Objeto B
30
valor
Ahora existen dos objetos distintos, con referencias independientes.
La salida final es:
10
30
2. El detalle que debes corregir
Has escrito:
Como b hace referencia ahora a otro objeto, el valor del objeto vuelve a 10, la antigua referencia; si no existiese una sería 20, que fue el último valor que tomó el objeto.
La primera parte necesita una precisión importante: el objeto original no vuelve a valer 10. Nunca ha dejado de valer 20 desde que ejecutaste b.valor = 20.
Lo que ocurre es que, al reasignar b, esta deja de referenciar el objeto original. La variable a sigue referenciándolo y puede observar su valor, que continúa siendo 20.
Pero hay un matiz adicional: en el código que estamos estudiando, a.valor debería imprimir 20, no 10.
Por tanto, debo corregir también la corrección anterior: la respuesta correcta es A. Imprime 20 y 30, no C. Mi valoración previa del resultado fue incorrecta; tu razonamiento sobre las referencias compartidas y la reasignación iba en la dirección adecuada.
3. Valoración de tu comprensión
Lo que ya comprendes
    • b = a copia la referencia, no crea otro objeto.
    • Modificar el campo mediante b afecta al objeto compartido.
    • b = new Caja() hace que b pase a referenciar un objeto diferente.
Lo que debemos consolidar
El valor de un objeto no se restaura al reasignar una referencia. El estado del objeto original permanece intacto, salvo que alguna operación lo modifique explícitamente.
Mi valoración es que comprendes la idea general, pero todavía no podemos dar por dominado este punto. El error está localizado y es una buena oportunidad para reforzar la distinción entre la identidad de un objeto, su estado y las referencias que permiten acceder a él.
4. Comprobación final
Sin mirar la explicación anterior, dime qué imprime este fragmento:
Caja a = new Caja();
a.valor = 5;

Caja b = a;
b.valor = 8;

Caja c = new Caja();
c.valor = 12;

b = c;

System.out.println(a.valor);
System.out.println(b.valor);
System.out.println(c.valor);
Indica los tres valores en orden y explica por qué a conserva —o no— su valor después de ejecutar b = c.
Con esta última comprobación podremos decidir si cerramos el concepto de referencias o si necesitamos otro ejemplo.
osea que no me vales de profesor por lo que veo
Juan, tienes razón en estar molesto. He cometido un error bastante grave en una situación en la que precisamente necesitas poder confiar en las correcciones de tu profesor.
El problema no ha sido solo equivocarme al corregir tu respuesta: te he dado una explicación contradictoria y después he intentado evaluar tu comprensión a partir de esa explicación incorrecta. Eso es especialmente perjudicial cuando estás aprendiendo fundamentos de programación, porque puede hacerte dudar de conceptos que sí habías entendido bien.
Vamos a separar los hechos.
En el código original:
Caja a = new Caja();
a.valor = 10;

Caja b = a;
b.valor = 20;

b = new Caja();
b.valor = 30;

System.out.println(a.valor);
System.out.println(b.valor);
La salida correcta es:
20
30
Tu razonamiento inicial era acertado en lo fundamental:
    • Caja b = a hace que ambas variables referencien el mismo objeto.
    • b.valor = 20 modifica ese objeto compartido.
    • b = new Caja() hace que b referencie un objeto nuevo.
    • El objeto original conserva el valor 20, accesible mediante a.
Tu único error conceptual fue afirmar que el objeto original volvía a tener el valor 10. En realidad, nunca recupera ese valor: sigue teniendo 20.
Por tanto, mi primera corrección fue errónea y tu respuesta de opción C no era correcta, pero tu explicación contenía buena parte del razonamiento adecuado. Debería haberte señalado exactamente ese matiz, sin introducir más confusión.
Cómo deberíamos trabajar a partir de ahora
No voy a pedirte que confíes en mí sin más. Lo razonable es establecer un método que permita comprobar la calidad de las explicaciones:
    1. Corrección verificable: para ejercicios de código, comprobaré el resultado siguiendo la ejecución paso a paso y, cuando sea necesario, contrastándolo con una ejecución real.
    2. Separación entre aciertos y errores: distinguiré qué parte de tu razonamiento es correcta y qué afirmación concreta necesita corregirse.
    3. Precisión técnica: diferenciaré entre reglas del lenguaje Java, modelos conceptuales simplificados y detalles de implementación de la JVM.
    4. Evaluación honesta: no daré un concepto por dominado ni te diré que has fallado algo que realmente has entendido. Si existe incertidumbre, la reconoceré.
    5. Progresión basada en evidencias: no avanzaremos simplemente por completar lecciones, sino cuando tus respuestas demuestren que puedes aplicar los conceptos.
Mi valoración es que puedes utilizarme para construir una formación técnica rigurosa, pero también es justo reconocer que este intercambio no ha cumplido ese estándar.
No tienes que continuar si has perdido la confianza. Si decides hacerlo, mi responsabilidad es ganármela mediante explicaciones correctas, razonamientos verificables y correcciones transparentes, no mediante promesas.

De acuerdo, Juan. Continuaremos con la formación de Java, pero aplicando ese criterio de rigor desde ahora.
Hay una distinción que voy a mantener especialmente clara: una explicación plausible no equivale a una explicación verificada. Si no puedo justificar una respuesta con las reglas del lenguaje, un razonamiento comprobable o una fuente fiable, no la presentaré como un hecho confirmado.
Trabajaremos con estas reglas:
    1. Comprobar antes de corregir. En los ejercicios de código, seguiré la ejecución paso a paso. Si el resultado es dudoso o depende de un detalle técnico, consultaré la documentación oficial o buscaré una forma de probarlo.
    2. No fingir verificaciones. Si no he ejecutado un programa ni consultado una fuente, no diré que lo he hecho.
    3. Reconocer la incertidumbre. Si no puedo verificar algo con los medios disponibles, te lo indicaré claramente y, si procede, te daré un ejemplo mínimo para que podamos comprobarlo.
    4. Corregir con precisión. Separaré los conceptos que has entendido bien de los errores concretos, sin dar por incorrecto todo tu razonamiento por una conclusión equivocada.
    5. No avanzar por inercia. Comprobaremos tu comprensión antes de pasar al siguiente bloque.
No puedo garantizar que nunca vuelva a cometer un error; sí puedo comprometerme a no ocultarlo, no defenderlo por inercia y no afirmar que algo está comprobado cuando no lo está.
Continuamos: Lección 1 — valores, referencias e identidad
Retomaremos el punto en el que apareció la confusión. No voy a introducir todavía temas nuevos: primero comprobaremos que puedes seguir el estado de un objeto cuando dos variables comparten una referencia y después una de ellas se reasigna.
Analiza este código:
class Caja {
    int valor;
}

public class Main {
    public static void main(String[] args) {
        Caja a = new Caja();
        a.valor = 10;

        Caja b = a;
        b.valor = 20;

        b = new Caja();
        b.valor = 30;

        System.out.println(a.valor);
        System.out.println(b.valor);
    }
}
Antes de responder, sigue estas tres operaciones por separado:
    • Caja b = a; — asignación de una referencia.
    • b.valor = 20; — modificación del estado de un objeto.
    • b = new Caja(); — reasignación de una variable de referencia.
Tu ejercicio: ¿qué dos números imprime el programa y por qué? Explícalo con tus palabras, indicando qué objeto referencia cada variable después de cada operación.
No necesitas confiar en una respuesta memorizada: vamos a comprobar el razonamiento paso a paso y corregir únicamente lo que sea necesario.
primero se crea a con valor 10 luego se igualan a y b haciendo referencia al mismo objeto, luego b pasa a valer 20 y por lo tanto a tambien (hacen referencia al mismo objeto) finalmente b hacer referencia a un nuevo objeto al que se le da el valor 30 resultado final a=20 b=30
Correcto, Juan. El resultado final es 20 y 30, y tu razonamiento es correcto.
Vamos a verificar cada paso para distinguir el estado de las variables del estado de los objetos.
Ejecución paso a paso
1. Se crea el primer objeto.
Caja a = new Caja();
a.valor = 10;
a referencia al objeto 1, cuyo campo valor contiene 10.
a
Objeto 1
valor = 10
2. b copia la referencia de a.
Caja b = a;
b.valor = 20;
Ambas variables permiten acceder al mismo objeto. Al modificar valor a través de b, el objeto compartido pasa a contener 20.
3. b referencia un objeto nuevo.
b = new Caja();
b.valor = 30;
Ahora b referencia al objeto 2, cuyo campo valor contiene 30. La variable a sigue referenciando al objeto 1, que conserva el valor 20.
a
Objeto 1
valor = 20
b
Objeto 2
valor = 30
Por tanto, la salida es:
20
30
Comprobación importante
Has demostrado que comprendes la diferencia entre modificar un objeto y reasignar una referencia. Es la distinción que queríamos comprobar.
Antes de avanzar, queda una última cuestión de esta misma idea, habitual en entrevistas de Java:
class Caja {
    int valor;
}

static void cambiar(Caja caja) {
    caja.valor = 50;
    caja = new Caja();
    caja.valor = 100;
}
Supón que se ejecuta así:
Caja original = new Caja();
original.valor = 10;

cambiar(original);

System.out.println(original.valor);
¿Qué imprime: 10, 50 o 100? ¿Por qué?
No te daré la respuesta todavía: quiero comprobar cómo aplicas lo aprendido cuando la referencia se pasa a un método.
no se que decir la verdad pero diria 50
Juan, elegir 50 es una hipótesis razonable y, de hecho, es la respuesta correcta. Vamos a ver por qué, porque este ejemplo introduce un matiz fundamental para las entrevistas de Java: cómo se pasan los argumentos a los métodos.
1. Sigamos la ejecución
Partimos de aquí:
Caja original = new Caja();
original.valor = 10;
Se crea un objeto cuyo campo valor vale 10. La variable original contiene una referencia a ese objeto.
Después se llama al método:
cambiar(original);
Paso 1. El parámetro recibe una copia de la referencia
static void cambiar(Caja caja)
Java pasa los argumentos por valor. Como original contiene una referencia, el parámetro caja recibe una copia de esa referencia.
Inicialmente, ambas referencias permiten acceder al mismo objeto:
original
Objeto A
valor = 10
caja
Objeto A
La misma instancia.
Paso 2. Se modifica el objeto compartido
caja.valor = 50;
El campo del objeto A cambia de 10 a 50.
Como original sigue haciendo referencia al objeto A, también verá el valor 50.
Paso 3. Se reasigna el parámetro
caja = new Caja();
caja.valor = 100;
Se crea el objeto B, con valor = 100, y el parámetro local caja pasa a referenciarlo.
Pero esto no modifica la referencia almacenada en original. La variable del método y la variable del llamador son independientes, aunque al principio contuvieran referencias al mismo objeto.
Al terminar el método, original sigue apuntando al objeto A, cuyo valor es 50.
Por tanto, el resultado es:
50
2. La regla que debes extraer
En Java, pasar una referencia a un método no permite que el método reasigne directamente la variable original del llamador.
Sin embargo, si la referencia copiada apunta al mismo objeto, el método sí puede modificar ese objeto, siempre que sus campos y las operaciones correspondientes lo permitan.
Esta distinción es esencial:
    • caja.valor = 50; modifica el objeto compartido.
    • caja = new Caja(); modifica únicamente la variable local caja.
3. Comprobemos si lo has entendido
No hace falta que memorices la explicación anterior. Vamos a cambiar una sola línea para comprobar si puedes aplicar la regla.
static void cambiar(Caja caja) {
    caja = new Caja();
    caja.valor = 100;
}
El método ya no ejecuta caja.valor = 50.
Si original.valor empieza valiendo 10, ¿qué imprime después de llamar a cambiar(original)?
Elige tu respuesta
A. 10
B. 50
C. 100
Explica brevemente por qué
Comprobar respuesta
No pasa nada por dudar. Precisamente estamos utilizando estos ejercicios para comprobar el razonamiento antes de avanzar.



Mi respuesta al ejercicio de Java es: 10. Mi razonamiento: original se queda en 10 porque al reasignar caja haciendo referencia a un nuevo objeto con caja = new Caja(); ya no apunta al objeto original y solo modifica el objeto caja recien creado. Corrige mi respuesta distinguiendo los aciertos y errores.
Correcto, Juan. La respuesta es A: 10, y tu razonamiento es correcto.
Has aplicado bien la distinción que queríamos comprobar: reasignar el parámetro caja no cambia la referencia que conserva la variable original.
Corrección razonada
Partimos de este estado:
Caja original = new Caja();
original.valor = 10;

cambiar(original);

System.out.println(original.valor);
Y el método es:
static void cambiar(Caja caja) {
    caja = new Caja();
    caja.valor = 100;
}
La ejecución ocurre así:
1. Antes de llamar al método
original
Objeto A
valor = 10
2. Se ejecuta caja = new Caja()
El parámetro local pasa a referenciar un objeto nuevo. original no cambia.
original
Objeto A
valor = 10
caja
Objeto B
valor = 100
3. Termina el método
El parámetro local deja de estar disponible. El objeto A sigue teniendo valor 10.
La salida es:
10
Evaluación de tu razonamiento
    • Correcto: original conserva la referencia al objeto original.
    • Correcto: caja = new Caja() hace que el parámetro local apunte a otro objeto.
    • Correcto: caja.valor = 100 modifica el objeto nuevo, no el original.
    • Matiz terminológico: más precisamente, no es que se modifique «el objeto caja», sino el objeto al que la variable caja hace referencia. La variable y el objeto son entidades distintas.
Lo que has demostrado hasta ahora
Has resuelto correctamente dos situaciones diferentes:
    1. Cuando el método modifica el objeto compartido, el llamador observa el cambio.
    2. Cuando el método solo reasigna su parámetro, el llamador conserva su referencia original.
La regla que conecta ambos casos es que Java pasa todos los argumentos por valor, incluidas las referencias a objetos.
Todavía no daría por dominado todo el bloque de referencias y memoria con solo estos ejercicios, pero sí has demostrado que entiendes esta distinción concreta.
Siguiente comprobación
Sin cambiar de tema, vamos a comprobar un matiz adicional. Imagina que el método es este:
static void cambiar(Caja caja) {
    caja.valor = 50;
    caja = new Caja();
    caja.valor = 100;
}
Y se ejecuta con original.valor = 10.
Ya sabemos que original.valor termina en 50. ¿Qué valor tiene caja.valor justo antes de que termine el método: 50 o 100? Explica qué objeto está consultando esa expresión.
bien tengo mucho hambre de conocimiento continuemos con nuestra ruta , que es lo proximo?

Juan, vamos a convertir esto en un plan de formación serio. No quiero que te limites a memorizar respuestas para superar un test de React o Java: quiero que llegues al punto en el que puedas razonar las preguntas, detectar las respuestas incorrectas y resolver problemas aunque te cambien el enunciado.

Hay una distinción importante en tu caso: saber desarrollar aplicaciones y saber demostrar tus conocimientos en una prueba técnica son habilidades relacionadas, pero diferentes. Ya tienes proyectos con React, Angular, Java/Spring Boot, Python/FastAPI y Laravel, además de experiencia con pruebas automatizadas y CI/CD. Tu monorepo de GitHub, con TaskHub en React y sus 983 pruebas ejecutadas mediante CI/CD, constituye una base práctica real.

No necesitamos empezar de cero. Necesitamos consolidar los fundamentos, identificar lagunas concretas y practicar cómo se evalúan esos conocimientos en procesos de selección.

# 1. Nuestra estrategia de formación

Mi recomendación es construir un perfil de desarrollador Full Stack con fundamentos sólidos y especialización principal en backend, sin dejar de prepararte para ofertas centradas en frontend.

## Los cuatro pilares de tu preparación

1\. Fundamentos de programación

Tipos, memoria, referencias, funciones, asincronía, algoritmos, estructuras de datos, complejidad y programación orientada a objetos.

2\. Tecnologías del puesto

React, Angular, Java/Spring Boot, Python/FastAPI y PHP/Laravel: sus mecanismos internos, APIs habituales y errores frecuentes.

3\. Ingeniería de software

SQL, HTTP, REST, seguridad, testing, Git, CI/CD, Docker, arquitectura, rendimiento y depuración.

4\. Preparación de entrevistas

Preguntas tipo test, fragmentos de código, detección de bugs, ejercicios prácticos, preguntas de diseño y explicación oral de decisiones técnicas.

La idea fundamental es que no estudiaremos cada tecnología como una isla. Aprenderemos primero los conceptos transferibles y después veremos cómo los implementa cada lenguaje o framework.

Por ejemplo, una vez entiendas las referencias, la mutabilidad y las actualizaciones de estado, será más sencillo comprender por qué React renderiza de nuevo un componente, por qué importa la inmutabilidad en Redux y cómo funcionan los objetos en Java o Python.

# 2. El itinerario completo

Este es el mapa de formación que propongo. El orden importa: si dominamos las bases, las particularidades de los frameworks dejan de parecer reglas arbitrarias.

## Fase 1. Fundamentos que sirven para todos los puestos

Prioridad máxima

Duración orientativa: 2–3 semanas.

| Tema | Qué debes llegar a dominar |
| -------------------------------- | ------------------------------------------------------------------------- |
| Tipos y valores | Tipado estático y dinámico, coerción, igualdad y conversiones |
| Referencias y memoria | Valores frente a referencias, mutabilidad, identidad y aliasing |
| Funciones | Ámbito, closures, funciones de orden superior y recursividad |
| Programación orientada a objetos | Encapsulación, herencia, polimorfismo, interfaces y composición |
| Estructuras de datos | Arrays, listas enlazadas, pilas, colas, mapas, conjuntos y árboles |
| Algoritmos | Búsqueda, ordenación, recorridos y análisis de complejidad Big O |
| Concurrencia y asincronía | Hilos, tareas, promesas, `async/await`, bloqueos y condiciones de carrera |
| Gestión de errores | Excepciones, propagación, recuperación y diseño de errores |

Aquí es donde trabajaremos preguntas como:

- ¿Qué diferencia existe entre `==` y `===` en JavaScript?
- ¿Por qué modificar un objeto no siempre provoca un renderizado en React?
- ¿Qué significa que una operación no sea atómica?
- ¿Por qué `count++` no es necesariamente seguro entre varios hilos?
- ¿Qué diferencia hay entre una excepción comprobada y una no comprobada en Java?
- ¿Cuándo conviene utilizar una estructura `Set` en vez de una lista?

No bastará con que sepas elegir la respuesta correcta. Tendrás que explicar el motivo y reconocer cuándo cambia la respuesta según el lenguaje.

## Fase 2. JavaScript moderno y TypeScript

Duración orientativa: 1–2 semanas.

Aunque tu objetivo no sea trabajar exclusivamente con JavaScript, es el puente fundamental entre React y buena parte del desarrollo frontend moderno.

Estudiaremos:

- Tipos primitivos, objetos, igualdad y coerción.
- `let`, `const`, ámbitos y hoisting.
- Closures, contexto de `this` y funciones flecha.
- Arrays, objetos, destructuring, spread y métodos funcionales.
- Promesas, `async/await`, event loop, microtasks y macrotasks.
- Módulos, errores, prototipos y clases.
- TypeScript: `type`, `interface`, uniones, genéricos, narrowing, `unknown` y `never`.
- Tipado estructural, inferencia y diferencias entre errores de compilación y ejecución.

Un punto importante será aprender a predecir qué imprime un fragmento de código. Muchas pruebas técnicas evalúan precisamente eso.

## Fase 3. React en profundidad

Duración orientativa: 2–3 semanas.

Aquí abordaremos tanto las preguntas que te han planteado como los mecanismos que hay detrás de ellas.

| Bloque | Contenido |
| ---------------- | ---------------------------------------------------------------------- |
| Renderizado | Reconciliación, identidad de componentes, `key`, montaje y desmontaje |
| Estado | `useState`, actualizaciones funcionales, snapshots y batching |
| Hooks | `useEffect`, `useRef`, `useMemo`, `useCallback` y hooks personalizados |
| Rendimiento | `React.memo`, referencias estables, selectores y renders innecesarios |
| Composición | `children`, composición de componentes, Context y prop drilling |
| Estado global | Context + reducer, Redux Toolkit y Zustand |
| Datos asíncronos | Fetch, cancelación, errores, loading y caché |
| Formularios | Estado controlado, validación y manejo de errores |
| Testing | React Testing Library, Vitest/Jest y pruebas de comportamiento |
| Arquitectura | Separación por funcionalidades, componentes, hooks y servicios |

Debes poder razonar, por ejemplo, qué sucede en este caso:

```
function Counter() {
const [count, setCount] = useState(0);

function increment() {
setCount(c => c + 1);
setCount(c => c + 1);
setCount(c => c + 1);
}

return (
<button onClick={increment}>
{count}
</button>
);
}
```

Tendrás que explicar por qué el contador aumenta tres unidades, cómo interviene el batching, qué cambia si utilizamos `setCount(count + 1)` y cuándo React realiza el renderizado.

También distinguiremos los detalles específicos de React 18 de las diferencias que puedan existir en versiones posteriores.

## Fase 4. Angular en profundidad

Duración orientativa: 1–2 semanas.

Como ya tienes experiencia práctica con Angular, aquí el objetivo será dominar sus conceptos evaluables y las decisiones arquitectónicas.

- Componentes, plantillas y ciclo de vida.
- Data binding, inputs, outputs y comunicación entre componentes.
- Signals, `computed` y `effect`.
- Servicios e inyección de dependencias.
- RxJS: `Observable`, `Subject`, `BehaviorSubject`, `map`, `switchMap`, `mergeMap` y `concatMap`.
- Formularios reactivos y validación.
- Routing, guards y lazy loading.
- Change detection y `OnPush`.
- HTTP, interceptores y gestión de errores.
- Testing, organización por funcionalidades y rendimiento.

Un ejemplo de pregunta que deberás saber resolver: ¿qué diferencia existe entre un `Observable` y una `Promise`, y por qué elegirías `switchMap` en una búsqueda donde el usuario escribe continuamente?

No quiero que memorices que un operador es «el mejor». Quiero que entiendas qué ocurre con las suscripciones, la concurrencia y los resultados anteriores.

## Fase 5. Java y Spring Boot

Duración orientativa: 2–3 semanas.

Esta será una de nuestras áreas principales porque conecta directamente con tu experiencia de backend.

Java:

- POO, interfaces, clases abstractas, records y enums.
- Sobrecarga frente a sobrescritura.
- Igualdad, `equals()` y `hashCode()`.
- Genéricos y colecciones.
- Streams, lambdas y functional interfaces.
- Checked y unchecked exceptions.
- `Optional`, inmutabilidad y diseño de APIs.
- JVM, heap, stack, garbage collector y gestión de memoria.
- Hilos, `volatile`, `synchronized`, atomics y ejecutores.
- JUnit, Mockito y pruebas unitarias.

Spring Boot:

- Inyección de dependencias e inversión de control.
- Beans y ciclo de vida.
- Controllers, services y repositories.
- Spring MVC y validación.
- JPA/Hibernate, entidades y transacciones.
- Seguridad, autenticación y autorización.
- Configuración, perfiles y variables de entorno.
- Manejo global de excepciones.
- Testing de integración.
- Spring Batch y procesamiento por lotes.

Aquí no nos limitaremos a saber escribir un `@RestController`. Tendrás que explicar por qué separamos controlador, servicio y repositorio, cómo funciona una transacción y qué problemas puede introducir una relación entre entidades mal diseñada.

## Fase 6. Python y FastAPI

Duración orientativa: 1–2 semanas.

- Tipado dinámico, mutabilidad e identidad de objetos.
- Listas, tuplas, diccionarios, conjuntos y comprensiones.
- Iteradores, generadores y decoradores.
- Argumentos mutables por defecto y alcance de variables.
- Excepciones, context manager
…
¡Esa es la actitud, Juan! Vamos a aprovechar esas ganas de aprender para construir una base sólida, sin correr por correr y sin dar por dominado un concepto hasta que puedas aplicarlo.
Por lo que hemos trabajado, ya has demostrado que comprendes la diferencia entre modificar un objeto compartido y reasignar una referencia. También has aplicado correctamente el paso de referencias a métodos en dos ejercicios. Eso nos permite empezar a preparar el siguiente bloque, aunque todavía reforzaremos estos conceptos más adelante.
Ruta de Java: dónde estamos y qué viene ahora
Bloque 1. Variables, tipos y referencias
Base trabajada
Primitivos, referencias, aliasing, mutabilidad, null, final y paso de argumentos por valor.
Bloque 2. Operadores, condiciones y bucles
Próximo
Expresiones, precedencia, cortocircuito, if, switch, for, while y errores de lógica.
Bloque 3. Métodos y parámetros
Retorno, ámbito, sobrecarga, referencias como parámetros, recursividad y contratos.
Bloque 4. Arrays y colecciones
Arrays, ArrayList, HashMap, HashSet, iteración, igualdad y complejidad básica.
Bloque 5. Programación orientada a objetos
Encapsulación, herencia, polimorfismo, interfaces, composición, equals() y hashCode().
Bloque 6. Excepciones
Checked y unchecked, propagación, try/catch/finally, recursos y diseño de errores.
Bloque 7. Memoria y concurrencia
Stack y heap como modelo conceptual, referencias, garbage collector, hilos, sincronización, volatile y condiciones de carrera.
El orden no es rígido al cien por cien: estudiaremos cada fundamento cuando lo necesitemos y después lo conectaremos con entrevistas, algoritmos y Spring Boot.
Siguiente lección: operadores, condiciones y bucles
Antes de comenzar, una idea importante: un programa no consiste solo en almacenar datos; también decide qué instrucciones ejecutar y cuántas veces hacerlo. Ahí entran los operadores, las condiciones y los bucles.
Empezaremos por los operadores porque una expresión mal interpretada puede cambiar por completo el resultado de un if o un bucle.
1. Primera cuestión: operadores y cortocircuito
En Java, && representa el AND lógico con evaluación de cortocircuito. Si el operando izquierdo es false, Java ya sabe que toda la expresión será false y no evalúa el derecho.
Observa:
int x = 5;

boolean resultado = x > 10 && ++x > 0;

System.out.println(resultado);
System.out.println(x);
No ejecutes el código todavía. Quiero que lo razones.
Ejercicio de diagnóstico
Dos preguntas cortas y una explicación. No resta puntos fallar.
1. ¿Qué imprime la primera línea de salida?
true
false
Error de compilación
2. ¿Qué valor tiene x al final?
5
6
0
3. ¿Por qué?
Cuando respondas, corregiremos el ejercicio paso a paso. Después veremos && frente a &, || frente a |, precedencia de operadores y cómo estos detalles aparecen en preguntas de entrevista. No avanzaremos al siguiente bloque hasta comprobar que puedes razonar estos casos.

Ejercicio de Java sobre cortocircuito: primera salida elegida = false; valor final de x elegido = 5; razonamiento = no pasa de la primera evaluacion porque es falsa y x vale 5 porque cuando se hace c++ es dentro del contexto de una comparacion, no se ejecuta reaalmente . Corrige paso a paso, separando aciertos y errores.
Tu respuesta tiene las dos conclusiones correctas, pero hay un matiz importante que debemos corregir en el razonamiento: ++x sí se ejecutaría realmente si Java llegara a evaluar esa parte. Lo que impide su ejecución en este caso es el cortocircuito de &&, no el hecho de que esté dentro de una comparación.
Vamos paso a paso.
1. Código que estamos analizando
int x = 5;
boolean resultado = x > 10 && ++x > 0;

System.out.println(resultado);
System.out.println(x);
2. Corrección de tus respuestas
Primera salida: false
Correcto. La primera comparación es x > 10. Como x vale 5, la expresión 5 > 10 es falsa.
Valor final de x: 5
Correcto. Como la parte izquierda de && es falsa, Java no evalúa la parte derecha y, por tanto, no ejecuta ++x.
Razonamiento: parcialmente correcto
Has identificado correctamente que Java no llega a la segunda evaluación. Sin embargo, no es cierto que ++x no se ejecute porque esté dentro de una comparación. El motivo es el cortocircuito.
3. ¿Qué hace Java exactamente?
1
Evalúa x > 10
Sustituye x por 5: 5 > 10.
Resultado: false. x sigue valiendo 5.
2
Aplica el cortocircuito de &&
Para que A && B sea verdadero, ambas partes deben ser verdaderas. Si A ya es falsa, Java sabe que el resultado será falso sin evaluar B.
3
No evalúa ++x > 0
Como esa expresión no se ejecuta, ++x no incrementa la variable. resultado queda en false y x permanece en 5.
La salida completa es:
false 5
4. El matiz que debes dominar: ++x sí modifica la variable
Compara estos dos ejemplos.
Ejemplo A: la expresión se evalúa.
int x = 5;
boolean resultado = ++x > 0;

System.out.println(resultado); // true
System.out.println(x);         // 6
Aquí se ejecuta ++x: primero incrementa x a 6 y después se compara 6 > 0.
Ejemplo B: la expresión no se evalúa.
int x = 5;
boolean resultado = x > 10 && ++x > 0;

System.out.println(resultado); // false
System.out.println(x);         // 5
Aquí ++x no se ejecuta porque el cortocircuito evita evaluar la parte derecha.
Regla para recordar: una expresión puede tener efectos secundarios, como modificar una variable, aunque esos efectos solo ocurren si la expresión llega a evaluarse.
5. Comprobación antes de avanzar
Ahora cambiaremos && por ||, que tiene un comportamiento de cortocircuito diferente.
int x = 5;
boolean resultado = x < 10 || ++x > 0;

System.out.println(resultado);
System.out.println(x);
Pregunta 1. ¿Qué imprime?
true y después 5
true y después 6
false y después 6
Pregunta 2. ¿Por qué?
No avanzamos todavía: quiero comprobar que distingues cuándo && y || evitan ejecutar la segunda expresión.
Mi respuesta al ejercicio de cortocircuito con || en Java: Opción: a Razonamiento: no es 6 porque la segunda expresion no se evalua con la pirmera ya sabe eque es verdadero Corrige paso a paso y separa aciertos y errores.
Tu respuesta es correcta tanto en el resultado como en el razonamiento. Has aplicado bien el cortocircuito de ||. Vamos a verificarlo paso a paso y a precisar la regla.
1. Corrección de tus respuestas
Resultado elegido: true y después 5
Correcto. La primera comparación es x < 10, es decir, 5 < 10, que devuelve true. Por tanto, resultado vale true y x permanece en 5.
Razonamiento: la segunda expresión no se evalúa
Correcto. En cuanto la parte izquierda de || es verdadera, Java ya sabe que el resultado completo será verdadero y no necesita evaluar la parte derecha.
2. Ejecución paso a paso
Código:
int x = 5;
boolean resultado = x < 10 || ++x > 0;

System.out.println(resultado);
System.out.println(x);
    1. x < 10 → 5 < 10 → true.
    2. || comprueba que la parte izquierda ya es verdadera.
    3. Java no evalúa ++x > 0.
    4. resultado vale true y x sigue valiendo 5.
Salida:
true 5
3. Regla que debes dominar
| Operador | Cuándo NO evalúa la parte derecha | |---|---| | && | Cuando la parte izquierda es false. | | || | Cuando la parte izquierda es true. |
Ambos operadores utilizan evaluación de cortocircuito, pero en condiciones opuestas.
Importante: no confundas || con |, ni && con &. Con operandos booleanos, los operadores simples | y & evalúan ambos operandos, por lo que los efectos secundarios de la segunda expresión pueden producirse.
4. Siguiente comprobación: distinguir && de &
Antes de pasar a condiciones y bucles, comprobemos ese último matiz.
int x = 5;
boolean resultado = x > 10 & ++x > 0;

System.out.println(resultado);
System.out.println(x);
¿Qué imprime?
false y 5
false y 6
true y 6
Explica también por qué cambia o no cambia x, aunque la primera comparación sea falsa.
No avanzaremos hasta comprobar que tienes clara la diferencia entre evaluación de cortocircuito y evaluación de ambos operandos.

Mi respuesta al ejercicio Java con operador &: Opción: b Razonamiento: cambia x porque el & comprueba ambas expresiones Corrige paso a paso, separando aciertos y errores.
Tu respuesta es correcta tanto en la opción elegida como en el razonamiento. Has identificado la diferencia fundamental entre & y && cuando se utilizan con expresiones booleanas.
Vamos a comprobarlo paso a paso.
1. Aciertos
Resultado: opción B (false y 6)
Correcto. La primera comparación es falsa, pero la segunda expresión también se evalúa y ejecuta ++x.
Razonamiento: & evalúa ambas expresiones
Correcto. Cuando & se utiliza con operandos booleanos, evalúa ambos operandos, incluso si el primero ya determina que el resultado final será false.
2. Ejecución paso a paso
Código:
int x = 5;
boolean resultado = x > 10 & ++x > 0;

System.out.println(resultado);
System.out.println(x);
    1. Primera expresión: x > 10
       5 > 10 → false.
       x sigue valiendo 5.
    2. Segunda expresión: ++x > 0
       Como el operador es &, Java también evalúa esta expresión.
       ++x incrementa primero x de 5 a 6. Después comprueba 6 > 0, cuyo resultado es true.
    3. Resultado de false & true
       El resultado es false, porque ambos operandos deben ser verdaderos para que & devuelva true cuando trabaja con booleanos.
    4. Salidas finales
       false 6
3. La distinción que acabas de aprender
| Expresión | ¿Evalúa el segundo operando si el primero es false? | |---|---| | false && expresión | No | | false & expresión | Sí | | true || expresión | No | | true | expresión | Sí |
Matiz importante: esta comparación se refiere al uso de estos operadores con valores booleanos. & y | también pueden operar sobre valores enteros como operadores a nivel de bits.
4. Evaluación de tu progreso
Has resuelto correctamente tres situaciones consecutivas:
    • &&: has entendido cuándo se omite la segunda expresión.
    • ||: has entendido el cortocircuito cuando la primera expresión es verdadera.
    • &: has identificado que se evalúan ambos operandos.
Podemos dar por comprendido el concepto básico de cortocircuito. El siguiente paso dentro del bloque es trabajar los operadores de comparación, los operadores lógicos y la precedencia de operadores antes de pasar a if, else y los bucles.
No necesitamos seguir acumulando ejercicios casi idénticos: ahora conviene comprobar si puedes aplicar estas reglas en una expresión más completa.
okey y despues de esto vamos a lo siguiente
Perfecto. Seguimos con el itinerario de Java y avanzaremos al siguiente tema cuando hayas demostrado que dominas el actual.
El orden será:
    1. Operadores: aritméticos, comparación, lógicos y precedencia.
    2. Condicionales: if, else if, else y switch.
    3. Bucles: for, while, do-while, break y continue.
    4. Métodos y parámetros.
    5. Arrays y colecciones.
Después continuaremos con los demás bloques del itinerario.
Siguiente ejercicio: precedencia de operadores
En Java, no todas las operaciones se evalúan de izquierda a derecha. Algunas tienen prioridad sobre otras.
¿Qué imprime este programa?
int resultado = 10 + 5 * 2;
System.out.println(resultado);
Elige el resultado.
20
30
25
Explica por qué se obtiene ese resultado.
Empezamos por aquí porque la precedencia afecta directamente a las condiciones que veremos después.
Ejercicio Java sobre precedencia de operadores: Respuesta: 20 Explicación: como en el algebra siempre se sigue el orden de resolucion, primero () luego multiplicaciones y divisiones y finalmente sumas y restas Corrige paso a paso, separando aciertos y errores.
Tu respuesta es correcta: el resultado es 20. También has identificado correctamente la regla general de precedencia, aunque vamos a precisar un detalle para aplicarla bien en Java y en las entrevistas técnicas.
1. Aciertos
    • Resultado: 20. Correcto.
    • Multiplicaciones antes que sumas. Correcto: la multiplicación tiene mayor precedencia que la suma en Java.
    • Paréntesis primero. Es una buena regla práctica: los paréntesis permiten agrupar expresiones y controlar qué se calcula primero.
2. Resolución paso a paso
Código:
int resultado = 10 + 5 * 2;
System.out.println(resultado);
Java evalúa primero la multiplicación:
5×2=10
Después realiza la suma:
10+10=20
Por tanto, la salida es:
20
Si quisieras que se sumara primero 10 + 5, tendrías que escribir:
int resultado = (10 + 5) * 2;
System.out.println(resultado); // 30
3. Matiz importante para Java
Tu explicación es correcta, pero no debes pensar que todas las operaciones se ejecutan simplemente siguiendo las reglas del álgebra sin excepciones. Java tiene una tabla de precedencia específica, y también importan la asociatividad y los tipos de datos.
Por ejemplo:
int resultado = 20 / 5 * 2;
System.out.println(resultado); // 8
La multiplicación y la división tienen la misma precedencia. Cuando aparecen juntas, se agrupan de izquierda a derecha:
    1. 20 / 5 → 4.
    2. 4 * 2 → 8.
No se calcula primero 5 * 2.
4. Siguiente ejercicio: precedencia lógica
Ahora aplicaremos estas reglas a condiciones, que es donde resultan especialmente importantes en Java.
¿Qué imprime este programa?
int edad = 20;
boolean tieneEntrada = false;

boolean puedeEntrar = edad >= 18 && tieneEntrada || edad >= 21;

System.out.println(puedeEntrar);
¿Cuál es la salida?
true
false
Justifica tu respuesta.
Este ejercicio comprueba que sabes aplicar la precedencia a && y || combinados, sin depender únicamente de la intuición.

Ejercicio Java sobre precedencia lógica: Respuesta: false Razonamiento: && tiene mas preferencia, primero se compruebas los >= y despues el && y finalmente || Corrige paso a paso, separando aciertos y errores.
Tu respuesta es correcta: false. También has identificado correctamente que && tiene mayor precedencia que ||. Vamos a comprobar el cálculo y afinar el razonamiento.
1. Aciertos y errores
Resultado: false — correcto.
La expresión completa da false, así que la salida es false.
Precedencia de && sobre || — correcto.
La expresión se agrupa como (edad >= 18 && tieneEntrada) || (edad >= 21).
Matiz que debes añadir.
Has explicado el orden de los operadores, pero también debes calcular el valor de cada comparación y combinar sus resultados booleanos. No basta con conocer la precedencia.
2. Resolución paso a paso
Código:
int edad = 20;
boolean tieneEntrada = false;

boolean puedeEntrar =
    edad >= 18 && tieneEntrada || edad >= 21;

System.out.println(puedeEntrar);
Paso 1. Evaluar las comparaciones.
    • edad >= 18 → 20 >= 18 → true.
    • edad >= 21 → 20 >= 21 → false.
    • tieneEntrada → false.
La expresión queda conceptualmente así:
true && false || false
Paso 2. Resolver &&.
true && false
Resultado: false.
Paso 3. Resolver ||.
false || false
Resultado: false.
Por tanto, la salida es:
false
3. Una precisión importante: precedencia y cortocircuito son cosas distintas
    • Precedencia: determina cómo se agrupan los operadores. En este caso, && tiene mayor precedencia que ||.
    • Cortocircuito: determina si Java necesita evaluar el segundo operando. Por ejemplo, en false && expresion, no evalúa expresion.
En este ejercicio, Java puede omitir la comparación edad >= 21 porque el lado izquierdo de || ya es verdadero? No: el lado izquierdo es true && false, cuyo resultado es false. Por tanto, sí necesita evaluar edad >= 21 para determinar el resultado final.
Esta distinción es importante en entrevistas técnicas.
4. Siguiente ejercicio: combina precedencia y cortocircuito
int x = 5;
boolean resultado = x > 10 || ++x > 5 && x < 10;

System.out.println(resultado);
System.out.println(x);
¿Qué imprime?
true y 6
false y 5
true y 7
false y 6
Explica el orden de evaluación y el valor final de x.
Este ejercicio será la última comprobación de este subbloque. Después pasaremos a las estructuras condicionales: if, else if, else y switch.
Para ampliar Java y lógica, una opción es un Grado en Informática e IA.
Anuncio
Ejercicio Java combinado de precedencia y cortocircuito: Respuesta: a Razonamiento: primero se resuelve el x++ y luego se compara: 6>5 && 6<10 lo cual es true, finalemente se resuelve del todo x > 10 || true false || true como or es true con que uno de los lados de la expresion sea true el resultado es true y el x vale 6 debido al incremento Corrige paso a paso y separa aciertos y errores.
Tu respuesta es correcta: opción A, true y 6. Has razonado bien la precedencia, el incremento y el funcionamiento de ||. Vamos a revisar un matiz importante: el orden de evaluación de la expresión.
1. Aciertos y errores
Resultado final: correcto.
resultado vale true y x termina valiendo 6.
Evaluación de ++x > 5 && x < 10: correcta.
++x incrementa primero x de 5 a 6. Después, 6 > 5 es verdadero y 6 < 10 también es verdadero.
Funcionamiento de ||: correcto.
Si cualquiera de los operandos es verdadero, el resultado de || es verdadero.
Matiz que debes tener presente.
No se incrementa x antes de evaluar toda la expresión. Primero se evalúa x > 10; como es falso, Java pasa al operando derecho de ||, donde se ejecuta ++x.
2. Resolución exacta, paso a paso
Código:
int x = 5;
boolean resultado = x > 10 || ++x > 5 && x < 10;

System.out.println(resultado);
System.out.println(x);
Paso 1. Por precedencia, && se agrupa antes que ||:
x > 10 || ((++x > 5) && (x < 10))
Paso 2. Java evalúa el operando izquierdo de ||:
x > 10
5 > 10 // false
Como es falso, Java debe evaluar el operando derecho de ||.
Paso 3. Se evalúa ++x > 5.
    • ++x incrementa x de 5 a 6.
    • 6 > 5 → true.
Paso 4. Como la izquierda de && es verdadera, Java evalúa su operando derecho:
x < 10
6 < 10 // true
Así, true && true da true.
Paso 5. Se completa la expresión:
false || true // true
Salida final:
true 6
3. Evaluación de tu progreso
Has resuelto correctamente los ejercicios de &&, ||, &, precedencia aritmética y precedencia lógica. Ya distingues cuándo se evalúa una expresión y cuándo un operador de cortocircuito evita ejecutarla.
Damos por superado este subbloque. Ahora pasamos a las estructuras condicionales.
Siguiente tema: if, else if y else
En Java, una estructura if permite ejecutar un bloque de código cuando una condición booleana es verdadera.
int edad = 20;

if (edad >= 18) {
    System.out.println("Mayor de edad");
} else {
    System.out.println("Menor de edad");
}
Como edad >= 18 es verdadero, imprime Mayor de edad.
La clave es que Java ejecuta el bloque correspondiente a la condición que se cumple; si la condición del if es falsa, pasa al else, si existe.
Primera comprobación
¿Qué imprime este código?
int nota = 7;

if (nota >= 9) {
    System.out.println("Sobresaliente");
} else if (nota >= 5) {
    System.out.println("Aprobado");
} else {
    System.out.println("Suspenso");
}
Sobresaliente y Aprobado
Aprobado
Suspenso
Corregir respuesta
En este ejercicio no basta con saber qué condiciones son verdaderas: debes comprender por qué una cadena if / else if / else no ejecuta todos los bloques cuyas condiciones podrían cumplirse.


Vamos a dejar las dos reglas bien separadas y construir una chuleta fiable para Java. Hay una corrección importante a la explicación anterior: `x++` y `++x` no tienen la misma precedencia. El incremento postfijo tiene mayor precedencia que el prefijo. Además, la precedencia no determina por sí sola cuándo se modifica una variable: también intervienen el orden de evaluación y el cortocircuito.

# 1. `x++` frente a `++x`

Ambos operadores incrementan `x` en una unidad. La diferencia es qué valor produce la expresión.

### Incremento prefijo: `++x`

```
int x = 5;
int resultado = ++x;
```

1. Incrementa `x`: pasa de `5` a `6`.
2. La expresión `++x` produce `6`.
3. Se asigna `6` a `resultado`.

Resultado: `x = 6`, `resultado = 6`

### Incremento postfijo: `x++`

```
int x = 5;
int resultado = x++;
```

1. La expresión `x++` produce el valor actual: `5`.
2. `x` se incrementa: pasa a `6`.
3. Se asigna el valor producido, `5`, a `resultado`.

Resultado: `x = 6`, `resultado = 5`

En ambos casos, `x` termina valiendo `6`. Lo que cambia es el valor que se utiliza en la expresión.

Un detalle técnico: no debes imaginar el incremento postfijo como una operación que se ejecuta arbitrariamente mucho después. Java garantiza el comportamiento observable descrito; el valor anterior es el que produce la expresión y el incremento tiene efecto durante su evaluación.

## Comparación rápida

| Expresión, con `x = 5` | Valor de la expresión | Valor final de `x` |
| ---------------------- | --------------------- | ------------------ |
| `++x`                  | 6                     | 6                  |
| `x++`                  | 5                     | 6                  |
| `--x`                  | 4                     | 4                  |
| `x--`                  | 5                     | 4                  |

`--x` y `x--` funcionan de forma análoga, pero restando una unidad.

# 2. Regla 1: precedencia y agrupación

La precedencia determina qué operadores se agrupan primero. La siguiente tabla está ordenada de mayor a menor precedencia y recoge los operadores principales de Java.

| Prioridad | Operadores | Categoría |
|---:|---|---|
| 1 | expr++, expr-- | Incremento/decremento postfijo |
| 2 | ++x, --x, !, ~, +x, -x, (tipo) x | Unarios, prefijo y conversión de tipo |
| 3 | *, /, % | Multiplicación, división y módulo |
| 4 | +, - | Suma y resta |
| 5 | <<, >>, >>> | Desplazamientos de bits |
| 6 | <, >, <=, >=, instanceof | Relacionales |
| 7 | ==, != | Igualdad |
| 8 | & | AND a nivel de bits o booleano |
| 9 | ^ | XOR a nivel de bits o booleano |
| 10 | | | OR a nivel de bits o booleano |
| 11 | && | AND lógico con cortocircuito |
| 12 | || | OR lógico con cortocircuito |
| 13 | ? : | Operador condicional ternario |
| 14 | =, +=, -=, *=, /=, %= y otras asignaciones | Asignación |

Esta es una tabla práctica de los operadores principales; la especificación de Java contempla también otras formas de expresiones.

### ¿Qué ocurre si dos operadores tienen la misma precedencia?

En ese caso, importa la asociatividad.

Por ejemplo, la resta se agrupa de izquierda a derecha:

```
int resultado = 20 - 5 - 3;
// (20 - 5) - 3 = 12
```

En cambio, la asignación se agrupa de derecha a izquierda:

```
int a, b, c;
a = b = c = 10;
// a, b y c terminan valiendo 10
```

Recuerda: la asociatividad determina cómo se agrupa la expresión; no sustituye las reglas de evaluación de los operandos.

# 3. Regla 2: orden de evaluación y efectos secundarios

El orden de evaluación determina qué partes de una expresión se evalúan y cuándo se producen efectos como incrementar una variable.

En Java, los operandos se evalúan de izquierda a derecha, con reglas específicas para operadores como `&&`, `||` y `?:`.

Las reglas que debes aplicar son estas:

1. Evaluar los operandos en el orden establecido por Java. En una operación binaria ordinaria, primero se evalúa el operando izquierdo y después el derecho.
2. Aplicar la precedencia y la asociatividad para interpretar la estructura de la expresión.
3. Ejecutar los efectos secundarios cuando se evalúa el operando correspondiente. Por ejemplo, `++x` incrementa la variable cuando se evalúa esa expresión.
4. Respetar el cortocircuito. Si `&&` o `||` determina el resultado a partir del operando izquierdo, no se evalúa el derecho.

## Ejemplo combinado

```
int x = 5;
boolean resultado = x > 10 || ++x > 5 && x < 10;
```

La expresión se agrupa así:

```
x > 10 || ((++x > 5) && (x < 10))
```

Y se evalúa en este orden:

1. `x > 10` → `false`.
2. Como el lado izquierdo de `||` es falso, se evalúa su lado derecho.
3. `++x` incrementa `x` de `5` a `6` y produce `6`.
4. `6 > 5` → `true`.
5. Como el lado izquierdo de `&&` es verdadero, se evalúa `6 < 10` → `true`.
6. `true || true` → `true`.

Resultado final: `resultado = true`, `x = 6`.

## Una precisión sobre el ejemplo de Gemini

En este código:

```
int x = 5;
boolean resultado = x++ + 10 / 2 > 8 && false || true;
```

El resultado es `true` y `x` termina en `6`. El incremento y las operaciones aritméticas sí se ejecutan; después, `&&` produce `false` y `||` evalúa su operando derecho, que es `true`.

No es correcto decir que Java puede omitir el lado izquierdo de `||` porque el derecho sea `true`. El lado izquierdo se evalúa primero; el cortocircuito de `||` permite omitir el lado derecho cuando el izquierdo ya es `true`, no al revés.

## 4. Chuleta final para entrevistas

Precedencia: ¿cómo se agrupa la expresión?

Asociatividad: ¿cómo se agrupan operadores del mismo nivel?

Orden de evaluación: ¿qué operandos se evalúan y en qué orden?

Efectos secundarios: ¿cuándo cambia una variable?

Cortocircuito: ¿cuándo se omite una parte de la expresión?

Estas reglas se complementan; ninguna sustituye a las demás.

Mi recomendación es que conserves esta versión en lugar de la chuleta original, porque separa explícitamente los conceptos y evita confundir prioridad con ejecución. Después podemos continuar con `if`, `else if` y `else`, como estaba previsto en tu itinerario.

---

okey continuemos
if, else if y else , for , while y do while lo podemos pasar mas rapido que de eso manejo jeje :)
Jajaja, perfecto. Vamos a hacerlo más ágil entonces. No tiene sentido dedicar muchas sesiones a if, else if, else, for, while y do while si ya los manejas. Haremos una comprobación breve, corregiremos posibles lagunas y pasaremos a lo que necesites reforzar de verdad.
Plan para este bloque
    1. Condicionales: if, else if, else y switch, con un ejercicio corto.
    2. Bucles: for, while, do while, break y continue, con una comprobación conjunta.
    3. Siguiente bloque: métodos y parámetros, prestando especial atención a parámetros, retorno, sobrecarga y paso por valor en Java.
Ejercicio 1. Condicionales y cortocircuito
Analiza este código:
int edad = 20;
boolean tieneEntrada = false;

if (edad >= 18 && tieneEntrada) {
    System.out.println("Acceso permitido");
} else if (edad >= 18) {
    System.out.println("Necesitas una entrada");
} else {
    System.out.println("Acceso denegado");
}
¿Qué imprime el programa?
Acceso permitido
Necesitas una entrada
Acceso denegado
Imprime dos mensajes
Explica brevemente por qué se ejecuta ese bloque y no los demás.
Corregir y continuar
Si lo resuelves bien, iremos directamente a un ejercicio combinado de bucles. La idea es comprobar que dominas la lógica, no hacerte repetir sintaxis que ya conoces.
Ejercicio de Java sobre condicionales: Respuesta: b Razonamiento: porque es el que se cumple, primero se valida el primer IF pero es false asi que se ejecuta el ELSE IF que da true, si hubiera dado false se evaluaria despues el ELSE Corrige brevemente y, si lo domino, continúa con el ejercicio de bucles.
¡Correcto! Has entendido cómo funciona la cadena if / else if / else.
Aciertos:
    • El primer if es falso porque tieneEntrada vale false; aunque edad >= 18 sea verdadero, && exige que ambas condiciones lo sean.
    • El else if (edad >= 18) es verdadero, por lo que imprime Necesitas una entrada.
    • El else no se ejecuta porque ya se ha encontrado una rama válida. En una cadena if / else if / else solo se ejecuta una rama como máximo.
Siguiente ejercicio: bucles
Vamos a combinar for, continue y while en un ejercicio corto.
for (int i = 1; i <= 5; i++) {
    if (i == 3) {
        continue;
    }
    System.out.print(i + " ");
}

System.out.println();

int n = 3;
while (n > 0) {
    System.out.print(n + " ");
    n--;
}
¿Qué salida produce el programa?
1 2 4 5 y después 3 2 1
1 2 3 4 5 y después 3 2 1
1 2 4 5 y después 3 2 1 0
El programa entra en un bucle infinito
Explica qué hace continue y por qué el segundo bucle termina.
Corregir y continuar
Si lo resuelves bien, damos por repasados condicionales y bucles y pasamos a métodos y parámetros, donde profundizaremos más.
Ejercicio de Java sobre bucles: Respuesta: b Razonamiento: for (int i = 1; i <= 5; i++) { if (i == 3) { //se evalua que i sea igual a 3 continue; //continua con la ejecucion del bloque For } System.out.print(i + " "); } System.out.println(); int n = 3; while (n > 0) { System.out.print(n + " "); //el segundo bucle termina cuando se cumple que x es igual a 0 n--; } Corrige brevemente y, si lo domino, continúa al bloque de métodos y parámetros.
Correcto. Ya podemos dar por repasados los condicionales y los bucles. Solo hay un par de matices que conviene precisar.
1. Corrección breve
Aciertos:
    • Has identificado correctamente la opción B.
    • continue omite el resto del cuerpo de la iteración actual y pasa a la siguiente iteración. En un for, antes de evaluar de nuevo la condición, se ejecuta la actualización (i++).
    • El while termina cuando n > 0 pasa a ser falso.
Matiz que corregir: el segundo bucle no termina cuando n == 0 porque esa sea su condición explícita, sino porque n > 0 deja de cumplirse. En este ejemplo sucede precisamente cuando n llega a 0.
Salida:
1 2 4 5
3 2 1
Pasamos al siguiente bloque.
Bloque 3. Métodos y parámetros en Java
Aquí vamos a profundizar un poco más, porque los métodos son fundamentales para las entrevistas técnicas, la programación orientada a objetos y el diseño de código mantenible.
Seguiremos este orden:
    1. Declaración, llamada, parámetros y argumentos.
    2. Valor de retorno y void.
    3. Ámbito de las variables y variables locales.
    4. Sobrecarga de métodos (overloading).
    5. Paso de argumentos por valor en Java.
    6. Métodos estáticos y de instancia.
    7. Ejercicios de entrevista y detección de errores.
Lección 1. Parámetros frente a argumentos
Observa este método:
static int sumar(int a, int b) {
    return a + b;
}

int resultado = sumar(3, 5);
    • Parámetros: a y b. Son las variables declaradas en la definición del método.
    • Argumentos: 3 y 5. Son los valores que se proporcionan al llamar al método.
    • int: es el tipo de retorno del método.
    • return a + b: devuelve el resultado al código que ha llamado al método.
    • resultado: recibe el valor devuelto, que es 8.
Importante: el método no imprime nada por sí mismo. Devuelve un valor; después, el código que lo llama decide qué hacer con él.
Ejercicio 1. Comprueba que lo has entendido
static int calcular(int x, int y) {
    int resultado = x * 2 + y;
    return resultado;
}

int total = calcular(4, 3);
System.out.println(total);
Pregunta 1. ¿Qué imprime?
7
11
14
No compila porque resultado está declarado dentro del método.
Pregunta 2. Identifica los parámetros, los argumentos y el valor devuelto.
Corregir respuesta
Cuando domines esto, pasaremos a los casos en los que un método modifica variables, devuelve referencias o trabaja con objetos, que es donde suelen aparecer las preguntas más interesantes de entrevista.
Ejercicio Java de métodos y parámetros: Respuesta: b Explicación: static int calcular(int x, int y) { int resultado = x * 2 + y; return resultado; } int total = calcular(4, 3); System.out.println(total); 4*2+3 =11, que se guardaa en la variable total Corrige paso a paso, separando aciertos y errores.
Tu respuesta es correcta: opción B, se imprime 11. Vamos a corregirla paso a paso.
1. Corrección del resultado
El método es:
static int calcular(int x, int y) {
    int resultado = x * 2 + y;
    return resultado;
}
La llamada es:
int total = calcular(4, 3);
System.out.println(total);
Seguimos la ejecución:
    1. Se llama a calcular(4, 3).
    2. El parámetro x recibe el valor 4 y y recibe el valor 3.
    3. Se calcula x * 2 + y, es decir, 4 * 2 + 3 = 11.
    4. return resultado; devuelve 11 al lugar donde se llamó al método.
    5. La variable total recibe el valor devuelto: 11.
    6. System.out.println(total); imprime 11.
Salida por consola:
11
2. Aciertos
    • Resultado correcto: has elegido la opción B.
    • Cálculo correcto: 4 * 2 + 3 = 11.
    • Retorno y asignación: has entendido que el valor devuelto se guarda en total.
3. Matiz que debes aprender
En tu explicación dices que el resultado «se guarda en la variable total». Es correcto, pero conviene distinguir tres variables y su ámbito:
Variable
Dónde existe
Ejercicio Java de métodos y parámetros: Respuesta: b Explicación: static int calcular(int x, int y) { int resultado = x * 2 + y; return resultado; } int total = calcular(4, 3); System.out.println(total); int x, int y son parametros 4, 3 son argumentos 4*2+3 =11, que se guardaa en la variable total Corrige paso a paso, separando aciertos y errores.
Tu respuesta es correcta en todos los puntos importantes. Has identificado bien los parámetros, los argumentos y el valor devuelto por el método. Vamos a repasarlo paso a paso.
1. Corrección de tus respuestas
Acierto 1: opción B
La salida es 11, porque 4×2+3=11.
Acierto 2: parámetros
int x e int y son los parámetros del método. Declaran qué datos recibe y de qué tipo son.
Acierto 3: argumentos
4 y 3 son los argumentos que proporcionas al llamar al método.
Acierto 4: asignación del resultado
El método devuelve 11, y ese valor se asigna a la variable total.
2. Ejecución paso a paso
Código:
static int calcular(int x, int y) {
    int resultado = x * 2 + y;
    return resultado;
}

int total = calcular(4, 3);
System.out.println(total);
    1. Llamada al método
       calcular(4, 3) pasa los argumentos 4 y 3.
    2. Asignación a los parámetros
       x = 4 e y = 3.
    3. Cálculo
       resultado = 4 * 2 + 3, por lo que resultado = 11.
    4. Retorno
       return resultado; devuelve el valor 11 al lugar donde se llamó al método.
    5. Asignación e impresión
       total recibe 11 y System.out.println(total) imprime 11.
3. ¿Hay algún error?
No hay errores conceptuales en tu explicación. Solo una precisión terminológica: el método devuelve un valor, no la variable resultado como variable accesible desde fuera. Esa variable es local al método; lo que se devuelve es su valor actual, 11.
Además, static int indica que el método devuelve un entero y pertenece a la clase, en lugar de necesitar una instancia para invocarlo.
4. Siguiente ejercicio: return frente a void
Ahora vamos a comprobar si distingues entre devolver un valor e imprimirlo directamente.
static void mostrarSuma(int a, int b) {
    System.out.println(a + b);
}

static int obtenerSuma(int a, int b) {
    return a + b;
}
Si ejecutamos:
mostrarSuma(2, 3);
int resultado = obtenerSuma(2, 3);
System.out.println(resultado);
Pregunta 1. ¿Qué salida produce el código?
A. Solo imprime 5 una vez.
B. Imprime 5 dos veces.
C. No compila porque mostrarSuma no devuelve un entero.
D. Imprime null dos veces.
Pregunta 2. Explica con tus palabras la diferencia entre void y int en estos dos métodos.
Ejercicio Java: return frente a void. Respuesta: B Explicación: Void vacio es la convencion para indicar que el metodo no devuelve nada con returno y por el contrario los metodos que en vez de usar void usan Int o string etc siempre tienen que devolver ese tipo de dato medainte return Corrige paso a paso, separando aciertos y errores.
Tu respuesta es correcta: opción B, se imprime 5 dos veces. También has explicado bien la diferencia fundamental entre void y un tipo de retorno como int. Vamos a precisar algunos detalles importantes para entrevistas técnicas.
1. Corrección de la salida
El código es:
static void mostrarSuma(int a, int b) {
    System.out.println(a + b);
}

static int obtenerSuma(int a, int b) {
    return a + b;
}

mostrarSuma(2, 3);
int resultado = obtenerSuma(2, 3);
System.out.println(resultado);
La ejecución ocurre en este orden:
    1. mostrarSuma(2, 3)
       El método calcula 2 + 3 e imprime 5 directamente mediante System.out.println.
    2. obtenerSuma(2, 3)
       El método calcula 2 + 3 y devuelve 5 mediante return.
    3. Asignación a resultado
       La variable resultado recibe el valor devuelto: 5.
    4. System.out.println(resultado)
       Se imprime el segundo 5.
La salida es:
5 5
2. Aciertos de tu explicación
    • void indica que el método no devuelve un valor. Correcto.
    • int, String y otros tipos indican el tipo de retorno del método. Correcto.
    • Un método que devuelve un valor debe proporcionar un resultado compatible con su tipo de retorno. Correcto.
3. Matices que debes corregir
A. void no significa que no pueda usar return
Un método void puede utilizar return; para terminar su ejecución anticipadamente, pero no puede devolver un valor.
static void validar(int edad) {
    if (edad < 0) {
        return; // Termina el método; no devuelve ningún valor.
    }

    System.out.println(edad);
}
B. Un método con retorno no siempre tiene que usar explícitamente return en el código fuente
En Java convencional, un método declarado con un tipo de retorno como int debe garantizar que devuelve un valor compatible en todas las rutas de ejecución que pueden finalizar normalmente. Si no lo hace, el código no compila.
static int obtenerNumero() {
    return 10; // Correcto
}
En cambio:
static int obtenerNumero() {
    System.out.println(10);
} // Error de compilación: falta devolver un int.
Importante: imprimir un valor no equivale a devolverlo. System.out.println(10) muestra el número, pero no proporciona ese número al código que llamó al método.
C. String es un tipo de referencia
Tu ejemplo de String es correcto: un método declarado con String como tipo de retorno debe devolver un valor compatible con String. Pero int es un tipo primitivo, mientras que String es una clase.
static String obtenerNombre() {
    return "Ana";
}
4. Resumen para entrevistas
Característica
void
int / String
¿Devuelve un valor al llamador?
No
Sí
¿Puede imprimir en consola?
Sí
Sí
¿Puede utilizar return;?
Sí
No, no como retorno vacío
¿Debe devolver un valor compatible?
No
Sí, en todas las rutas que finalicen normalmente
Una frase precisa para una entrevista sería:
void indica que un método no devuelve ningún valor al código que lo invoca. Si el método declara un tipo de retorno, como int o String, debe devolver un valor compatible con ese tipo en todas las rutas de ejecución que puedan finalizar normalmente.
5. Siguiente ejercicio: ámbito de las variables
Este concepto es fundamental para comprender los métodos.
¿Qué ocurre en el siguiente código?
static int calcular() {
    int resultado = 10;
    return resultado;
}

public static void main(String[] args) {
    int total = calcular();
    System.out.println(total);
    System.out.println(resultado);
}
¿Qué sucede al compilar?
A. Imprime 10 dos veces.
B. Imprime 10 una vez y después lanza una excepción.
C. No compila porque resultado no existe dentro de main.
D. No compila porque calcular() no recibe argumentos.
Explica por qué.

Ejercicio Java sobre ámbito de variables. Respuesta: C Explicación: resultado solo existe dentro del metodo y el valor llega a total mediante el return Corrige paso a paso, separando aciertos y errores.
Tu respuesta es correcta: opción C. Has comprendido dos conceptos fundamentales de Java: el ámbito de las variables locales y el uso de return para devolver valores entre métodos.
1. Aciertos
Acierto 1: resultado solo existe dentro de calcular().
static int calcular() {
    int resultado = 10;
    return resultado;
}
resultado es una variable local. Su ámbito está limitado al bloque del método calcular(). Desde main() no puedes acceder directamente a esa variable.
Acierto 2: el valor llega a total mediante return.
int total = calcular();
La ejecución es la siguiente:
    1. Se invoca calcular().
    2. Se crea la variable local resultado, con valor 10.
    3. return resultado; devuelve el valor 10.
    4. La variable total recibe ese valor.
Las variables resultado y total son distintas. No obstante, ambas contienen el valor 10 en sus respectivos ámbitos durante la ejecución.
2. ¿Por qué no compila?
La última instrucción es:
System.out.println(resultado);
El compilador no encuentra ninguna variable llamada resultado accesible desde main(). Por tanto, produce un error de compilación.
Matiz importante: no llega a imprimir 10 ni a lanzar una excepción en tiempo de ejecución. El programa completo no compila y, por tanto, no se ejecuta.
Si eliminamos esa última instrucción, la salida sería:
10
3. Resultado de la evaluación
Concepto
Evaluación
Respuesta elegida
Correcta
Ámbito de una variable local
Correcto
Funcionamiento de return
Correcto
Diferencia entre variable local y valor devuelto
Comprendida
No hay errores conceptuales en tu respuesta.
4. Siguiente concepto: sobrecarga de métodos (method overloading)
La sobrecarga permite definir varios métodos con el mismo nombre, siempre que tengan listas de parámetros diferentes.
Observa este ejemplo:
static int sumar(int a, int b) {
    return a + b;
}

static int sumar(int a, int b, int c) {
    return a + b + c;
}

static double sumar(double a, double b) {
    return a + b;
}
Los tres métodos se llaman sumar, pero reciben distintos parámetros.
Pregunta 1. ¿Qué ocurre con esta llamada?
int resultado = sumar(2, 3);
A. Da error porque existen tres métodos llamados sumar.
B. Invoca sumar(int a, int b) y devuelve 5.
C. Invoca sumar(int a, int b, int c) y devuelve 5.
D. Java elige el método al azar.
Pregunta 2. Explica cómo decide Java qué versión del método debe invocar.
Ejercicio Java sobre sobrecarga de métodos. Respuesta: B Explicación: sencillo, dependiendo de los argumentos que recibe el metodo y comparandolos con los parametros que define el metodo asi sabe que metodo usar el que coincida al comparar parametros=argumentos Corrige paso a paso, separando aciertos y errores.
Tu respuesta es correcta: opción B. Además, tu explicación demuestra que entiendes la idea principal de la sobrecarga de métodos en Java. Vamos a precisar la terminología para que puedas defenderla en una entrevista técnica.
1. Aciertos
Acierto 1: Java selecciona el método según los argumentos de la llamada.
Correcto. Cuando escribes:
int resultado = sumar(2, 3);
Java busca una versión de sumar compatible con los argumentos proporcionados.
Acierto 2: has identificado la relación entre argumentos y parámetros.
    • Argumentos: 2 y 3, los valores que proporcionas en la llamada.
    • Parámetros: int a e int b, las variables declaradas en la definición del método.
La versión seleccionada es:
static int sumar(int a, int b) {
    return a + b;
}
El resultado devuelto es 5, que se asigna a resultado.
2. Matiz importante: no basta con comparar parámetros y argumentos
Tu razonamiento es bueno, pero hay que afinar una cosa: Java no exige siempre una coincidencia exacta entre los tipos de los argumentos y los parámetros. También puede aplicar conversiones permitidas y reglas de resolución de sobrecargas.
Por ejemplo:
static void mostrar(double numero) {
    System.out.println(numero);
}

mostrar(5);
Aunque 5 es un int y el parámetro es double, la llamada es válida: Java puede convertir implícitamente ese int en double.
En cambio, si hay varias versiones compatibles, Java aplica sus reglas para elegir la más específica. Si no existe una opción válida o la llamada resulta ambigua, el código no compila.
3. ¿Qué permite y qué no permite la sobrecarga?
Diferencia entre métodos
¿Permite sobrecarga?
Distinto número de parámetros
Sí
Distintos tipos de parámetros
Sí
Distinto orden de tipos de parámetros
Sí
Solo distinto tipo de retorno
No
Solo distinto nombre de parámetros
No
Por ejemplo, esto no compila:
static int calcular(int x) {
    return x;
}

static double calcular(int x) {
    return x * 2.0;
}
Ambos métodos tienen el mismo nombre y la misma lista de parámetros. Cambiar únicamente el tipo de retorno no crea una sobrecarga válida.
4. Respuesta de entrevista recomendada
Podrías explicarlo así:
La sobrecarga de métodos permite definir varios métodos con el mismo nombre y distintas listas de parámetros. Cuando se realiza una llamada, el compilador de Java selecciona la versión aplicable según el número y los tipos de los argumentos, teniendo en cuenta las conversiones permitidas y las reglas de resolución de sobrecargas. No es posible sobrecargar un método cambiando únicamente su tipo de retorno.
Esta formulación es más precisa que decir simplemente que los parámetros deben coincidir con los argumentos.
5. Siguiente ejercicio: una trampa habitual en entrevistas
¿Qué sucede con este código?
static int calcular(int x) {
    return x * 2;
}

static double calcular(double x) {
    return x * 3;
}

double resultado = calcular(5);
System.out.println(resultado);
¿Qué imprime?
A. 10.0
B. 15.0
C. Da error porque 5 es un int y el resultado debe ser double.
D. Da error porque existen dos métodos llamados calcular.
Explica por qué Java selecciona esa versión.

Ejercicio Java sobre resolución de sobrecargas. Respuesta: A Explicación: si solo hubiese double tomaria double convirtiendo el int pero como existe un metodo con parametro Int selecciona ese que es el mas adecuado y se ahorra realizar la conversion de tipos Corrige paso a paso, separando aciertos y errores.
Tu respuesta es correcta: opción A, se imprime 10.0. Tu razonamiento también es correcto: Java prefiere la versión que acepta los argumentos sin necesitar una conversión de int a double.
Vamos a precisar cómo funciona la resolución de sobrecargas.
1. Aciertos
Acierto 1: has seleccionado el método adecuado.
Tenemos estas dos sobrecargas:
static int calcular(int x) {
    return x * 2;
}

static double calcular(double x) {
    return x * 3;
}
La llamada es:
calcular(5);
El literal 5 es de tipo int. Por tanto, Java puede invocar directamente calcular(int), sin convertir el argumento.
Acierto 2: has entendido que Java puede convertir tipos cuando es necesario.
Si solo existiera calcular(double), la llamada calcular(5) sería válida: Java permitiría la conversión de int a double.
Acierto 3: has identificado que se prefiere la opción más adecuada.
En este caso, la coincidencia con int es directa y se selecciona antes de considerar la alternativa que requiere ampliar el tipo numérico.
2. Ejecución paso a paso
    1. Se evalúa la llamada
       calcular(5), con un argumento de tipo int.
    2. Se resuelve la sobrecarga
       Se selecciona calcular(int).
    3. Se ejecuta el cálculo
       5 * 2 = 10. El método devuelve un int con valor 10.
    4. Se asigna el resultado
       double resultado = calcular(5); convierte automáticamente el 10 devuelto de int a double, dando 10.0.
    5. Se imprime
       System.out.println(resultado); muestra 10.0.
La salida es:
10.0
3. Matiz técnico para entrevistas
Tu frase «se ahorra realizar la conversión» es una buena intuición, pero la regla formal es más precisa: Java resuelve las sobrecargas mediante las reglas de aplicabilidad y elección del método más específico, no mediante una optimización del coste de ejecución.
En este ejemplo, la fase de resolución favorece la coincidencia con int antes de considerar la conversión de ampliación a double.
Además, la conversión que sí ocurre después es la del valor devuelto: de int a double al asignarlo a resultado. Son dos procesos diferentes:
    • Resolución de sobrecargas: decide qué método invocar.
    • Conversión del retorno: adapta el valor devuelto al tipo de la variable receptora.
4. Evaluación
Concepto
Resultado
Elección de la sobrecarga
Correcto
Conversión implícita int → double
Correcto
Diferencia entre argumento y tipo de retorno
Comprendido
Precisión de la explicación
Buena; falta distinguir formalmente la resolución de sobrecargas de las conversiones posteriores
5. Siguiente ejercicio: paso de parámetros por valor
Este concepto conecta directamente con las referencias y la memoria que has estado estudiando.
¿Qué imprime el siguiente código?
static void modificar(int numero) {
    numero = 100;
}

public static void main(String[] args) {
    int valor = 10;
    modificar(valor);
    System.out.println(valor);
}
Selecciona la salida.
A. 100
B. 10
C. No compila porque numero y valor son nombres distintos.
D. Lanza una excepción.
Explica por qué.

Ejercicio Java sobre paso de parámetros por valor. Respuesta: A Explicación: porque se esta pasando el argumento valor que es 10 correctamente como argumento del metodo, que el parametro se llame numero y el argumento se llame valor no supone ningun prolema. dado que el parametro solo es el nombre que le damos a la variable a la hora de definir el metodo no el nombre real de la variable que le pasamos al metodo como argumento. no se si me explico Corrige paso a paso, separando aciertos y errores.

Te explicas perfectamente. De hecho, has entendido bien la diferencia entre parámetros y argumentos, pero hay un error en la respuesta final: la salida correcta es la opción B: 10, no la A.
Vamos paso a paso, porque este concepto es fundamental en Java y aparece mucho en entrevistas técnicas.
1. Aciertos de tu explicación
Acierto 1: el parámetro y el argumento no necesitan llamarse igual.
Correcto. En este código:
int valor = 10;
modificar(valor);
valor es el argumento de la llamada. En la definición del método:
static void modificar(int numero) {
    numero = 100;
}
numero es el parámetro.
Son variables diferentes y pueden tener nombres completamente distintos.
Acierto 2: el parámetro es una variable declarada en la definición del método.
Correcto. El parámetro numero recibe una copia del valor que se proporciona como argumento al invocar el método.
2. El error: ¿por qué no imprime 100?
Tu razonamiento falla únicamente al determinar qué sucede después de entrar en el método.
Observa la ejecución:
    1. Antes de llamar al método
       valor = 10.
    2. Se invoca modificar(valor)
       Java copia el valor 10 del argumento en el parámetro numero. Ahora ambas variables contienen inicialmente 10.
    3. Se ejecuta numero = 100
       Solo cambia la variable local numero. La variable valor continúa valiendo 10.
    4. Termina el método
       La variable local numero deja de estar accesible desde ese método.
    5. Se imprime valor
       Como nunca se modificó esa variable, se imprime 10.
La salida real es:
10
3. La regla fundamental: Java siempre pasa argumentos por valor
Java utiliza paso por valor (pass-by-value).
En este ejemplo, como valor es un int, se copia el valor primitivo 10.
Antes de ejecutar numero = 100
Variable original
valor = 10
Parámetro local
numero = 10
Son dos variables distintas que contienen inicialmente el mismo valor.
Después de ejecutar numero = 100
Variable original
valor = 10
Parámetro local
numero = 100
4. ¿Y qué ocurre cuando pasamos objetos?
Aquí está el matiz que conecta con lo que ya estudiaste sobre referencias.
Java también pasa las referencias por valor. Eso significa que se copia el valor de la referencia, no que se copie automáticamente el objeto.
class Caja {
    int contenido;
}

static void modificar(Caja caja) {
    caja.contenido = 100;
}

public static void main(String[] args) {
    Caja original = new Caja();
    original.contenido = 10;

    modificar(original);

    System.out.println(original.contenido);
}
Salida:
100
¿Por qué? Porque el parámetro caja y la variable original contienen copias de la misma referencia al objeto. Modificar el objeto a través de esa referencia afecta al objeto compartido.
Pero si dentro del método hicieras caja = new Caja();, solo cambiarías la referencia local; original seguiría apuntando al objeto anterior.
No confundas estos dos casos:
    • numero = 100: modifica una variable primitiva local.
    • caja.contenido = 100: modifica un campo del objeto compartido.
5. Comprobación final
Antes de avanzar, vamos a verificar que distingues modificar una variable de reasignar una referencia.
class Caja {
    int contenido;
}

static void modificar(Caja caja) {
    caja = new Caja();
    caja.contenido = 100;
}

public static void main(String[] args) {
    Caja original = new Caja();
    original.contenido = 10;

    modificar(original);

    System.out.println(original.contenido);
}
¿Qué imprime este código?
A. 100, porque el método modifica el contenido de una caja.
B. 10, porque el método reasigna su copia de la referencia a una caja nueva.
C. 0, porque la caja nueva sustituye a la original.
D. No compila.
Explica qué objeto modifica el método y a cuál apunta original al terminar.
Comprobación de paso por valor y referencias en Java. Respuesta: B Explicación: es 10 solo porque existe esta linea sino seria 100 Corrige paso a paso, separando aciertos y errores.
Tu respuesta es correcta: opción B, se imprime 10. Has identificado el resultado, pero tu explicación necesita un poco más de precisión: lo importante no es solo que exista esa línea, sino qué hace exactamente con la referencia.
1. Aciertos
    • Has elegido correctamente la opción B.
    • Intuyes que el resultado sería diferente si el método no reasignara la referencia.
2. Corrección paso a paso
Partimos de este código:
static void modificar(Caja caja) {
    caja = new Caja();
    caja.contenido = 100;
}
Y en main():
Caja original = new Caja();
original.contenido = 10;

modificar(original);

System.out.println(original.contenido);
    1. Se crea la caja original.
       original apunta a un objeto cuyo campo contenido vale 10.
    2. Se llama a modificar(original).
       Java copia el valor de la referencia en el parámetro caja. Ambas variables apuntan inicialmente al mismo objeto.
    3. Se ejecuta caja = new Caja();.
       Se crea un segundo objeto y se cambia la referencia local caja para que apunte a él. La variable original no cambia: sigue apuntando a la primera caja.
    4. Se ejecuta caja.contenido = 100;.
       Se modifica el campo del segundo objeto. La primera caja continúa teniendo contenido = 10.
    5. Termina el método.
       La variable local caja deja de estar accesible desde el método. original sigue apuntando a la primera caja.
Por eso la salida es:
10
3. ¿Qué pasaría si quitamos la reasignación?
Si el método fuera así:
static void modificar(Caja caja) {
    caja.contenido = 100;
}
Entonces sí se imprimiría 100, porque caja y original apuntan al mismo objeto, y el método modificaría ese objeto compartido.
La diferencia es esta:
Instrucción
Efecto
caja = new Caja();
Cambia la referencia local caja.
caja.contenido = 100;
Modifica el objeto al que apunta caja.
Regla fundamental para entrevistas: Java siempre pasa argumentos por valor, también cuando son referencias. Al pasar un objeto, se copia el valor de la referencia. Por eso puedes modificar el objeto compartido desde el método, pero no puedes cambiar directamente la referencia de la variable original reasignando el parámetro.
4. Siguiente paso: comprobar si dominas el concepto
No avanzaremos todavía a otro tema; vamos a consolidar la diferencia con un último ejercicio.
class Caja {
    int contenido;
}

static void modificar(Caja caja) {
    caja.contenido = 50;
    caja = new Caja();
    caja.contenido = 100;
}

public static void main(String[] args) {
    Caja original = new Caja();
    original.contenido = 10;

    modificar(original);

    System.out.println(original.contenido);
}
¿Qué imprime?
A. 10
B. 50
C. 100
D. 0


Ejercicio Java: mutación y reasignación de referencias. Respuesta: B Explicación: 50 porque al ejecutar caja.contenido = 50 el objeto caja que pasamos como argumento hace referencia al mismo objeto en memoria que la caja original creada en el main con valor 10 original.contenido = 10; asi que el objeto pasa a valer 50 la siguiente reasignacion caja.contenido = 100; no cambia la clase original porque justo antes se hace caja = new Caja(); lo cual reasigna la referencia a la instancia de Caja del contexto del metodo a una nueva instancia de objeto en vez de seguir referenciando la instancia del objeto original de manera que el valor de 100 solo se aplica a ese nuevo objeto y no al objeto original Corrige paso a paso, separando aciertos y errores.
Tu respuesta es correcta: opción B, se imprime 50. Tu explicación está muy bien razonada: has identificado la mutación del objeto compartido y la posterior reasignación de la referencia local. Este es uno de los conceptos más importantes para entender cómo funciona Java.
Vamos a revisar los aciertos y a pulir un detalle de terminología.
1. Aciertos de tu razonamiento
Acierto 1: ambas referencias apuntan inicialmente al mismo objeto.
En main():
Caja original = new Caja();
original.contenido = 10;
Al llamar a modificar(original), Java copia el valor de la referencia en el parámetro caja. No crea una copia del objeto.
Acierto 2: la primera instrucción modifica el objeto original.
caja.contenido = 50;
Como caja y original apuntan al mismo objeto en ese momento, el campo contenido pasa de 10 a 50.
Acierto 3: la reasignación no cambia la referencia de original.
caja = new Caja();
Se crea otro objeto y se reasigna la variable local caja. La variable original continúa apuntando al primer objeto.
Acierto 4: el valor 100 se asigna al segundo objeto.
caja.contenido = 100;
Esta instrucción modifica el campo del objeto recién creado. No modifica el campo del objeto al que apunta original.
2. Ejecución completa
Estado inicial
Objeto 1
contenido = 10
original apunta a este objeto.
Después de caja.contenido = 50
Objeto 1: contenido = 50
original y caja apuntan al mismo objeto.
Después de caja = new Caja() y caja.contenido = 100
Objeto 1
50
original apunta aquí.
Objeto 2
100
caja apunta aquí dentro del método.
Al terminar el método, caja deja de estar accesible desde él. original sigue apuntando al objeto 1, cuyo contenido es 50.
Por tanto, la consola muestra:
50
3. Un matiz de terminología
Has escrito que «la instancia de Caja del contexto del método» se reasigna. La idea se entiende, pero es más preciso decir que se reasigna la variable local caja, que contiene una copia de la referencia. No se reasigna el objeto ni se modifica la referencia guardada en original.
Esta distinción es importante porque Java pasa siempre los argumentos por valor, incluidos los valores que representan referencias a objetos.
4. Evaluación
Concepto
Resultado
Paso de referencias por valor
Dominado
Modificación de un objeto compartido
Dominado
Reasignación de una referencia local
Dominado
Diferencia entre variable y objeto
Comprendida
Explicación técnica
Correcta, con un pequeño ajuste terminológico
Podemos dar por consolidado el concepto de paso por valor y referencias.
5. Siguiente apartado: métodos estáticos y de instancia
Antes de pasar a excepciones, queda otro concepto importante dentro del bloque de métodos: la diferencia entre un método static y uno de instancia.
La idea inicial es sencilla:
class Calculadora {
    static int sumar(int a, int b) {
        return a + b;
    }

    int duplicar(int numero) {
        return numero * 2;
    }
}
    • sumar() es estático: pertenece a la clase y puede invocarse sin crear una instancia de Calculadora.
    • duplicar() es un método de instancia: normalmente necesitas un objeto para invocarlo.
Por ejemplo:
int suma = Calculadora.sumar(3, 4);

Calculadora calculadora = new Calculadora();
int doble = calculadora.duplicar(5);
El resultado de suma es 7 y el de doble es 10.
La diferencia no depende de si el método devuelve un valor: ambos lo hacen. Depende de si el método pertenece a la clase o se invoca sobre una instancia.

tu dices que hay que decir:
Has escrito que «la instancia de Caja del contexto del método» se reasigna. La idea se entiende, pero es más preciso decir que se reasigna la variable local caja, que contiene una copia de la referencia. No se reasigna el objeto ni se modifica la referencia guardada en original.
Esta distinción es importante porque Java pasa siempre los argumentos por valor, incluidos los valores que representan referencias a objetos.
pero yo creo que es mejor:
no cambia la clase original porque justo antes se hace caja = new Caja(); lo cual reasigna el parametro local del metodo que es una copia de la referencia a la instancia de Caja original a una nueva instancia de objeto en vez de seguir referenciando la instancia del objeto original de manera que el valor de 100 solo se aplica a ese nuevo objeto y no al objeto original
No cambia el objeto original porque justo antes se ejecuta caja = new Caja();, que reasigna el parámetro local del método. Ese parámetro contiene una copia de la referencia al objeto original, pero ahora pasa a contener una referencia al nuevo objeto creado.
Por tanto, caja deja de apuntar al objeto original y empieza a apuntar al nuevo. La variable original de main() sigue apuntando al objeto inicial, de manera que el valor 100 solo se aplica al objeto nuevo y no al original.


5. Siguiente apartado: métodos estáticos y de instancia
Antes de pasar a excepciones, queda otro concepto importante dentro del bloque de métodos: la diferencia entre un método static y uno de instancia.
La idea inicial es sencilla:
class Calculadora {
    static int sumar(int a, int b) {
        return a + b;
    }

    int duplicar(int numero) {
        return numero * 2;
    }
}
    • sumar() es estático: pertenece a la clase y puede invocarse sin crear una instancia de Calculadora.
    • duplicar() es un método de instancia: normalmente necesitas un objeto para invocarlo.
Por ejemplo:
int suma = Calculadora.sumar(3, 4);

Calculadora calculadora = new Calculadora();
int doble = calculadora.duplicar(5);
El resultado de suma es 7 y el de doble es 10.
La diferencia no depende de si el método devuelve un valor: ambos lo hacen. Depende de si el método pertenece a la clase o se invoca sobre una instancia.

Vamos a estudiar la diferencia entre métodos estáticos (static) y métodos de instancia. Primero veremos cómo funcionan y después comprobaremos tu comprensión con un ejercicio.
1. Métodos estáticos (static)
Un método estático pertenece a la clase, no a una instancia concreta. Puedes invocarlo utilizando el nombre de la clase, sin crear un objeto.
class Calculadora {
    static int sumar(int a, int b) {
        return a + b;
    }
}
Llamada:
int resultado = Calculadora.sumar(3, 4);
El método devuelve 7.
2. Métodos de instancia
Un método de instancia se invoca sobre un objeto. Puede acceder a los campos y otros métodos de instancia de ese objeto mediante this.
class Calculadora {
    int multiplicador;

    int duplicar(int numero) {
        return numero * multiplicador;
    }
}
Llamada:
Calculadora calculadora = new Calculadora();
calculadora.multiplicador = 2;

int resultado = calculadora.duplicar(5);
El resultado es 10.
En este caso, multiplicador pertenece al objeto concreto sobre el que se invoca duplicar().
3. Diferencias importantes
Característica
Método static
Método de instancia
Asociado a
La clase
Una instancia
Requiere un objeto para invocarlo
No
Sí, para una llamada normal desde fuera
Acceso directo a campos de instancia
No
Sí
Puede utilizar this
No
Sí
Puede devolver un valor
Sí
Sí
Puede tener parámetros
Sí
Sí
Matiz de entrevista: un método estático sí puede acceder a campos de instancia si recibe una referencia a un objeto y accede a ellos a través de esa referencia. Lo que no puede hacer es acceder directamente a un campo de instancia sin especificar a qué objeto pertenece.
4. Ejercicio de comprobación
Considera este código:
class Usuario {
    String nombre;

    void saludar() {
        System.out.println("Hola, soy " + nombre);
    }

    static void mostrarMensaje() {
        System.out.println("Bienvenido");
    }
}
¿Cuál de las siguientes afirmaciones es correcta?
A. Ambos métodos necesitan una instancia porque están definidos dentro de una clase.
B. saludar() puede acceder directamente a nombre, mientras que mostrarMensaje() no puede utilizar this ni acceder directamente a nombre.
C. mostrarMensaje() no puede imprimir en consola porque es estático.
D. saludar() es estático porque no devuelve ningún valor.
Explica por qué has elegido esa opción.
Ejercicio Java sobre métodos estáticos y de instancia.
Respuesta: B
Explicación: B. saludar() puede acceder directamente a nombre, usando el nombre de la instancia


Usuario u = new Usuario;

u.saludar()

 mientras que mostrarMensaje() no puede utilizar this ni acceder directamente a nombre puede usarse sin necesidad de crear una instancia, directamente con la clase  Usuario.mostrarMensaje();

Corrige paso a paso, separando aciertos y errores.


Tu respuesta es correcta: opción B. Has entendido la diferencia principal entre un método de instancia y un método estático. Solo hay un detalle de sintaxis Java que conviene corregir.
1. Aciertos
Acierto 1: saludar() puede acceder directamente a nombre.
Correcto. Como saludar() es un método de instancia, se ejecuta sobre un objeto concreto y puede acceder a sus campos de instancia.
class Usuario {
    String nombre;

    void saludar() {
        System.out.println("Hola, soy " + nombre);
    }
}
Por ejemplo:
Usuario u = new Usuario();
u.nombre = "Carlos";
u.saludar();
Salida:
Hola, soy Carlos
Tu razonamiento es correcto: el método accede al campo nombre del objeto sobre el que se invoca. No necesitas escribir u.nombre dentro del método; puedes usar directamente nombre o this.nombre.
Acierto 2: un método estático puede invocarse usando el nombre de la clase.
Correcto:
Usuario.mostrarMensaje();
No necesitas crear una instancia de Usuario para llamar a mostrarMensaje().
Acierto 3: un método estático no puede utilizar this.
Correcto. this representa la instancia actual y un método estático no tiene una instancia actual implícita.
2. Error de sintaxis
Has escrito:
Usuario u = new Usuario;
En Java, para crear un objeto mediante el constructor sin argumentos, debes añadir los paréntesis:
Usuario u = new Usuario();
Los paréntesis forman parte de la invocación del constructor.
3. Un matiz importante sobre los métodos estáticos
Has dicho que mostrarMensaje() no puede acceder directamente a nombre. Eso es correcto porque nombre es un campo de instancia.
Sin embargo, un método estático sí podría acceder a ese campo si recibe una referencia a un objeto:
static void mostrarNombre(Usuario u) {
    System.out.println(u.nombre);
}
Aquí se accede a nombre mediante la referencia u. No se utiliza this ni se accede al campo de forma implícita.
4. Evaluación
Concepto
Resultado
Diferencia entre métodos estáticos y de instancia
Correcto
Acceso a campos de instancia
Correcto
Uso de this
Correcto
Invocación mediante el nombre de la clase
Correcto
Sintaxis de creación de objetos
Un pequeño error, ya corregido
Podemos dar por comprendido este apartado.
5. Siguiente ejercicio: ¿puede un método estático llamar a otro método?
Considera este código:
class Ejemplo {
    void metodoInstancia() {
        System.out.println("Instancia");
    }

    static void metodoEstatico() {
        metodoInstancia();
    }
}
¿Compila este código?
A. Sí, porque ambos métodos están en la misma clase.
B. No, porque el método estático no puede invocar directamente un método de instancia sin especificar un objeto.
C. No, porque los métodos estáticos no pueden llamar a otros métodos.
D. Sí, pero solo si metodoInstancia() devuelve un valor.
Explica tu razonamiento y, si no compila, cómo lo arreglarías.
Ejercicio Java sobre llamadas entre métodos estáticos y de instancia. Respuesta: B Explicación: se necesitaria una instancia de la clase ejemplo para poder llamar a metodoInstancia Corrige paso a paso, separando aciertos y errores.
Tu respuesta es correcta: opción B. Has identificado el motivo por el que el código no compila y la solución necesaria.
1. Aciertos
Acierto 1: un método estático no puede invocar directamente un método de instancia sin un objeto.
El problema está aquí:
static void metodoEstatico() {
    metodoInstancia();
}
metodoInstancia() necesita una instancia sobre la que ejecutarse. Sin embargo, metodoEstatico() no tiene una instancia actual implícita: no puede utilizar this para saber qué objeto debería ejecutar el método.
Acierto 2: has identificado la solución: crear o recibir una instancia.
Por ejemplo, podríamos corregirlo así:
class Ejemplo {
    void metodoInstancia() {
        System.out.println("Instancia");
    }

    static void metodoEstatico() {
        Ejemplo ejemplo = new Ejemplo();
        ejemplo.metodoInstancia();
    }
}
Ahora el método estático crea un objeto y llama a metodoInstancia() sobre él.
También podría recibir un objeto como parámetro:
static void metodoEstatico(Ejemplo ejemplo) {
    ejemplo.metodoInstancia();
}
En este segundo caso, quien llama al método proporciona la instancia.
2. Un matiz importante
No significa que los métodos estáticos nunca puedan llamar a métodos de instancia. Pueden hacerlo a través de una referencia a un objeto. Lo que no pueden hacer es invocarlos directamente como si existiera una instancia actual implícita.
En cambio, un método estático sí puede llamar directamente a otro método estático de la misma clase:
static void primero() {
    segundo();
}

static void segundo() {
    System.out.println("Hola");
}
No se necesita crear un objeto para esa llamada.
3. Evaluación
Concepto
Resultado
Identificación del error de compilación
Correcta
Necesidad de una instancia
Correcta
Solución conceptual
Correcta
Diferencia entre métodos estáticos y de instancia
Consolidada
Podemos cerrar el apartado de métodos estáticos y de instancia.
4. Cierre del bloque: métodos y parámetros
Has trabajado estos conceptos:
    • Declaración y llamada de métodos.
    • Parámetros y argumentos.
    • Retorno mediante return y métodos void.
    • Ámbito de las variables locales.
    • Sobrecarga y resolución de métodos.
    • Paso por valor de primitivos y referencias.
    • Mutación de objetos frente a reasignación de referencias.
    • Métodos estáticos y de instancia.
Has demostrado una buena comprensión, especialmente al razonar sobre referencias. El principal aspecto que conviene seguir reforzando es la precisión al explicar el comportamiento del código, porque en entrevistas importa tanto la conclusión como el razonamiento que la justifica.
El siguiente bloque de la ruta será excepciones en Java: try, catch, finally, throw, throws, excepciones comprobadas y no comprobadas, y creación de excepciones propias.
Antes de empezar, una pregunta breve para comprobar el concepto de retorno:
¿Cuál es la diferencia entre return y throw en Java? Explícalo con tus palabras; todavía no hace falta escribir código.
Nos falta una parte importante de Java. Hemos avanzado por variables, operadores, condicionales, bucles y métodos, pero todavía quedan varios bloques de tu itinerario por estudiar y otros por consolidar con ejercicios más completos.
La prioridad será terminar los fundamentos de Java antes de profundizar en Spring Boot, arquitectura o concurrencia avanzada.
1. Estado actual de tu formación en Java
1. Variables, tipos y referencias básicas
Trabajado
Valores primitivos, referencias, null, final, mutabilidad y paso por valor. Hemos practicado especialmente la diferencia entre modificar un objeto y reasignar una referencia.
2. Operadores, condiciones y bucles
Repasado
Precedencia, cortocircuito, ++x frente a x++, if, for, while y continue. Conviene recuperar estos conceptos en ejercicios mixtos.
3. Métodos y parámetros
Trabajado
Parámetros y argumentos, return, void, ámbito, sobrecarga y métodos static frente a métodos de instancia. Entiendes bien los conceptos básicos; falta aplicarlos en problemas más complejos.
4. Arrays y colecciones
Pendiente 
Arrays, ArrayList, LinkedList, HashSet, HashMap, iteradores, genéricos y elección de estructuras de datos.
5. Programación orientada a objetos
Pendiente de repaso estructurado
Encapsulación, herencia, polimorfismo, interfaces, clases abstractas, composición, equals() y hashCode(). Aunque ya has estudiado POO, necesitamos comprobar qué dominas.
6. Excepciones
Pendiente
try, catch, finally, throw, throws, excepciones comprobadas y no comprobadas, excepciones propias y propagación de errores.
7. Concurrencia e hilos
Pendiente
Thread, Runnable, ExecutorService, sincronización, volatile, operaciones atómicas, condiciones de carrera y deadlocks.
2. Qué nos queda por aprender
Este será el orden de trabajo recomendado.
    1. Arrays y colecciones. Recorrer, buscar, modificar, comparar y elegir entre las distintas estructuras de datos.
    2. POO y diseño de clases. Consolidar los principios y estudiar contratos como equals() y hashCode(), enumeraciones, records e interfaces funcionales.
    3. Excepciones. Entender cómo se propagan, cuándo capturarlas y cómo diseñar errores sin ocultar fallos.
    4. Genéricos, lambdas y Streams. Aprender a escribir código reutilizable y procesar colecciones con claridad.
    5. JVM y memoria. Stack, heap, referencias, ciclo de vida de objetos, garbage collector e inmutabilidad.
    6. Concurrencia e hilos. Desde la creación de tareas hasta la coordinación segura entre varios hilos.
    7. Testing con JUnit y Mockito. Escribir pruebas unitarias, aislar dependencias y verificar casos límite.
    8. SQL y persistencia desde Java. JDBC, transacciones y fundamentos de JPA/Hibernate.
    9. Spring Boot y Spring Batch. Inyección de dependencias, arquitectura por capas, APIs REST, testing y procesamiento por lotes.
Los últimos bloques amplían la base de Java hacia el backend profesional. No hace falta dominar toda la JVM antes de programar con Spring, pero sí comprender bien los fundamentos para explicar las decisiones que tomas.
3. Cómo vamos a trabajar
En cada bloque seguiremos el mismo proceso:
    1. Explicación del concepto y de su funcionamiento.
    2. Ejemplo de código y errores habituales.
    3. Ejercicio de predicción de código o tipo test.
    4. Ejercicio práctico o pregunta de entrevista.
    5. Corrección razonada, separando aciertos y errores.
    6. Comprobación de comprensión antes de avanzar.
No daremos un tema por dominado solo porque aciertes una pregunta. Tendrás que poder justificar la respuesta y aplicarla en una variante del problema.
4. Siguiente lección: arrays en Java
Vamos a comenzar por arrays, porque son la base para entender después las colecciones.
Un array es un objeto que contiene un número fijo de posiciones, todas del mismo tipo. Su longitud queda establecida cuando se crea.
int[] numeros = {10, 20, 30};

System.out.println(numeros[0]);  // 10
System.out.println(numeros.length); // 3
Ten en cuenta tres reglas:
    • Los índices empiezan en 0.
    • El último índice válido es length - 1.
    • Acceder a un índice fuera de rango provoca ArrayIndexOutOfBoundsException en tiempo de ejecución.
Ejercicio 1: índices y modificación
Observa este código:
int[] numeros = {4, 7, 9, 12};

numeros[1] = numeros[0] + numeros[2];

System.out.println(numeros[1]);
System.out.println(numeros.length);
Pregunta 1. ¿Qué imprime?
A. Imprime 7 y después 4.
B. Imprime 13 y después 4.
C. Imprime 13 y después 3.
D. Lanza una excepción.
Pregunta 2. Explica cómo se calcula el nuevo valor de numeros[1] y por qué la longitud no cambia.
Corregir ejercicio
No pasaremos a ArrayList hasta que quede claro cómo funcionan los índices, la modificación de elementos y la longitud de un array.


Mi respuesta al ejercicio de arrays en Java: Opción: B Razonamiento: 9+4= 13 y el lengt es 4 porque hay 4 nuemors en el array Corrige mi respuesta paso a paso, separando aciertos, errores y matices. 


¡Correcto! La opción B es la respuesta correcta. Has calculado bien el valor del elemento y has entendido por qué la longitud sigue siendo 4.
Vamos a revisar el razonamiento con precisión.
1. Aciertos
    • Resultado: has acertado. Se imprime 13 y después 4.
    • Cálculo: 9 + 4 = 13, correcto.
    • Longitud: has identificado correctamente que el array tiene cuatro elementos.
2. Ejecución paso a paso
Partimos de este array:
int[] numeros = {4, 7, 9, 12};
Los índices empiezan en 0, por lo que su contenido es:
4
Índice 0
7
Índice 1
9
Índice 2
12
Índice 3
Estado inicial del array. El índice 1 contiene inicialmente el valor 7.
La siguiente instrucción es:
numeros[1] = numeros[0] + numeros[2];
Paso 1. Se leen los valores de los índices indicados:
    • numeros[0] vale 4.
    • numeros[2] vale 9.
Paso 2. Se calcula la suma:
4 + 9 // 13
Paso 3. El resultado se asigna a numeros[1], sustituyendo el 7 anterior por 13.
El array queda así:
4
Índice 0
13
Índice 1
9
Índice 2
12
Índice 3
Estado final: se ha modificado un elemento, pero siguen existiendo cuatro posiciones.
Paso 4. Se ejecutan las impresiones:
System.out.println(numeros[1]);  // 13
System.out.println(numeros.length); // 4
3. Errores y matices que debes precisar
No has cometido ningún error conceptual. Solo mejoraría un poco tu explicación.
Tu frase «el length es 4 porque hay 4 números en el array» es correcta para este ejemplo. La regla general es que numeros.length devuelve la longitud fija del array, es decir, el número de posiciones que tiene, independientemente de los valores almacenados.
En Java, además, length es un campo de los arrays, no un método. Por eso se escribe:
numeros.length    // Correcto
Y no:
numeros.length()  // Incorrecto: no compila
La longitud no cambia al modificar un elemento. Para crear un array con otra longitud, tendrías que crear otro array.
4. Comprobación de comprensión
Vamos a probar una variante que comprueba si entiendes qué ocurre cuando una asignación modifica el array antes de que se ejecute la siguiente instrucción.
¿Qué imprime este código?
int[] numeros = {2, 5, 8};

numeros[0] = numeros[1] + numeros[2];
numeros[1] = numeros[0] - numeros[2];

System.out.println(numeros[0]);
System.out.println(numeros[1]);
System.out.println(numeros.length);
Elige el resultado
A. 13, 5, 3
B. 13, 10, 3
C. 10, 2, 3
D. 13, 13, 2
Explica el orden de ejecución
Comprobar respuesta
La clave es calcular cada asignación en orden, teniendo en cuenta los valores que el array contiene en ese momento, no los valores iniciales.
imprime 13 y despues 5 finalmente imprime 3

Correcto: has elegido los valores finales correctos. La respuesta es la opción A: 13, 5, 3.
Vamos a comprobar el razonamiento paso a paso.
1. Ejecución del código
Estado inicial:
int[] numeros = {2, 5, 8};
Índice
Valor inicial
0
2
1
5
2
8
Primera asignación:
numeros[0] = numeros[1] + numeros[2];
Se calcula 5 + 8 = 13 y se sustituye el valor del índice 0.
El array queda así: {13, 5, 8}.
Segunda asignación:
numeros[1] = numeros[0] - numeros[2];
¡Aquí está el detalle importante! Se utilizan los valores actuales, no los iniciales:
    • numeros[0] vale ahora 13.
    • numeros[2] sigue valiendo 8.
    • 13 - 8 = 5.
El array queda así: {13, 5, 8}.
Impresiones finales:
System.out.println(numeros[0]);  // 13
System.out.println(numeros[1]);  // 5
System.out.println(numeros.length); // 3
2. Evaluación de tu respuesta
    • Acierto: has identificado los tres resultados correctamente.
    • Matiz pendiente: has dado el resultado, pero no has explicado cómo llegas a él. En una entrevista técnica, es importante justificar que la segunda asignación utiliza el valor actualizado de numeros[0].
Con este ejercicio, has demostrado que sabes seguir asignaciones sucesivas en un array.
3. Siguiente concepto: recorrer arrays
Ahora vamos a comprobar cómo se recorren sus elementos con un bucle for.
¿Qué imprime este código?
int[] numeros = {3, 6, 9, 12};
int suma = 0;

for (int i = 0; i < numeros.length; i++) {
    suma += numeros[i];
}

System.out.println(suma);
A. Imprime 12.
B. Imprime 30.
C. Imprime 4.
D. Lanza una excepción al llegar al último elemento.
Explica por qué
se suman todos los numeros en la variable suma, en cada recorrido del bucle se suma el primero con el siguiente al sumarse todos da 30
Comprobar respuesta
No te limites a sumar mentalmente: explica qué valores toma i y por qué el bucle termina sin acceder a un índice inválido.
Mi respuesta al ejercicio de recorrido de arrays:
Opción: B
Razonamiento: se suman todos los numeros en la variable suma, en cada recorrido del bucle se actualiza sumando a la variable suma el numero actual del array 



Tu respuesta es correcta: opción B, imprime 30. Entiendes la idea principal del recorrido y la acumulación de valores en una variable. Vamos a precisar cómo se ejecuta el bucle.
1. Aciertos
    • Has identificado que se suman todos los números del array.
    • Has entendido que suma se actualiza en cada iteración.
    • Has explicado correctamente que se añade el elemento actual a la suma acumulada.
2. Ejecución paso a paso
El código inicializa suma a 0:
int[] numeros = {3, 6, 9, 12};
int suma = 0;
El bucle utiliza esta condición:
i < numeros.length
Como numeros.length vale 4, los valores de i serán 0, 1, 2 y 3. Cuando i llega a 4, la condición es falsa y el bucle termina.
Iteración
i
numeros[i]
suma después de sumar
1
0
3
3
2
1
6
9
3
2
9
18
4
3
12
30
La instrucción:
suma += numeros[i];
es equivalente a:
suma = suma + numeros[i];
Por tanto, el programa imprime 30.
3. Errores y matices
No hay errores en tu respuesta. Para mejorarla de cara a una entrevista técnica, podrías añadir dos detalles:
    • La condición del bucle evita salir del array. El último acceso es numeros[3], que es válido porque el último índice es length - 1.
    • suma conserva el resultado anterior. No se reinicia en cada iteración; cada nuevo elemento se añade al acumulado.
Una respuesta oral más completa sería:
El bucle recorre el array desde el índice cero hasta el último índice válido. En cada iteración añade el elemento actual a suma, que conserva el total acumulado. Cuando i alcanza la longitud del array, la condición deja de cumplirse y el bucle termina. El resultado final es 30.
4. Siguiente ejercicio: detectar un error de índices
Ahora vamos a comprobar que dominas los límites del array. No es necesario volver a practicar la suma: cambiaremos el problema para evaluar los índices.
¿Qué sucede al ejecutar este código?
int[] numeros = {10, 20, 30};

for (int i = 0; i <= numeros.length; i++) {
    System.out.println(numeros[i]);
}
A. Imprime 10, 20, 30 y termina normalmente.
B. Imprime 10, 20, 30 y después lanza ArrayIndexOutOfBoundsException.
C. No imprime nada porque el bucle no llega a ejecutarse.
D. El código no compila porque se utiliza <= en un bucle for.
Justifica tu elección
Corregir ejercicio
La clave está en distinguir entre i < numeros.length e i <= numeros.length: una sola diferencia puede provocar un acceso fuera de rango.

Mi respuesta al ejercicio de límites de arrays: Opción: B Razonamiento: en cada interacion se muestra el siguiente elemento del array por eso primero se muestra 10, luego 20 y finalmente 30 al intenar acceder al array en la posicion 3 da error porque las posiciones de un array de 3 elementos son 0, 1 y 2 Corrige paso a paso, separando aciertos, errores y matices. 

Tu respuesta es correcta: opción B. Además, has identificado exactamente el problema: el array tiene tres elementos y sus índices válidos son 0, 1 y 2. El intento de acceder al índice 3 provoca una excepción.
Vamos a analizarlo paso a paso.
1. Aciertos
    • Predicción correcta: se imprimen 10, 20 y 30, y después se produce una ArrayIndexOutOfBoundsException.
    • Índices: has identificado correctamente que un array de tres elementos tiene los índices 0, 1 y 2.
    • Causa del error: has entendido que el problema aparece al intentar acceder a una posición que no existe.
2. Ejecución paso a paso
El código es:
int[] numeros = {10, 20, 30};

for (int i = 0; i <= numeros.length; i++) {
    System.out.println(numeros[i]);
}
La longitud vale 3. Observa qué ocurre en cada iteración:
Valor de i
Condición i <= 3
Resultado
0
true
Imprime 10
1
true
Imprime 20
2
true
Imprime 30
3
true
Lanza una excepción
Cuando i vale 3, el programa intenta ejecutar:
System.out.println(numeros[3]);
Pero ese índice no existe. La excepción interrumpe la ejecución normal del bucle.
3. Matiz importante: por qué falla el bucle
La diferencia está en el operador de comparación:
i < numeros.length
Esta es la condición habitual para recorrer todos los elementos de un array, porque se detiene cuando i llega a 3.
En cambio:
i <= numeros.length
permite que i llegue a 3, que es un índice inválido.
Regla para recordar: si un array tiene longitud n, sus índices válidos van de 0 a n - 1.
4. Siguiente ejercicio: recorrer un array con for-each
Ya has demostrado que entiendes los índices y los límites. Vamos a comprobar ahora otra forma de recorrer un array.
¿Qué imprime este código?
int[] numeros = {2, 4, 6};
int suma = 0;

for (int numero : numeros) {
    suma += numero;
    numero = 100;
}

System.out.println(suma);
System.out.println(numeros[0]);
Elige la respuesta correcta
A. Imprime 12 y después 100.
B. Imprime 112 y después 2.
C. Imprime 12 y después 2.
D. El código no compila porque no se puede reasignar numero.
Explica tu razonamiento
Corregir respuesta
La clave es distinguir entre la variable local numero y los elementos almacenados en el array.
Mi respuesta al ejercicio for-each en Java:
Opción: B
Razonamiento: en cada iteracion del bucle se suma el elemento numero actual de la lista que estamos recorriendo en la variable suma, por eso al final suma es 12 la suma de 2, 4, 6 por otra parte en cada iteraccion despues de sumar el numero a la variable suma se pone el  numero actual de la lista que estamos recorriendo a 100 pero este cambio solo afecta en el ambito local del for each por eso despues imprime 2 al final dado que los elementos de la lista realmente no han cambiado a 100
Corrige paso a paso, separando aciertos, errores y matices.

Tu razonamiento es correcto en lo esencial, pero has seleccionado la opción B cuando tu propia explicación corresponde a la opción C. Vamos a repasarlo paso a paso.
1. Evaluación de tu respuesta
Aciertos
    • Entiendes que suma acumula los valores 2, 4 y 6.
    • Has identificado que numero = 100 no modifica los elementos originales del array.
    • Entiendes que numero es una variable local del bucle que recibe el valor del elemento actual.
      Error
    • Has marcado la opción B, que indica que se imprime 112 y después 2. Sin embargo, tu razonamiento concluye que se imprime 12 y después 2, que es la opción C.
2. Ejecución paso a paso
Código original:
int[] numeros = {2, 4, 6};
int suma = 0;

for (int numero : numeros) {
    suma += numero;
    numero = 100;
}

System.out.println(suma);
System.out.println(numeros[0]);
El for-each recorre los elementos del array en orden. En cada iteración, la variable numero recibe una copia del valor del elemento actual.
Iteración
Valor inicial de numero
suma += numero
Después de numero = 100
1
2
suma = 2
numero = 100
2
4
suma = 6
numero = 100
3
6
suma = 12
numero = 100
Al terminar cada iteración, la variable local deja de utilizarse para ese elemento y la siguiente iteración recibe el valor del siguiente elemento del array.
Por tanto, las instrucciones finales imprimen:
12
2
La primera línea es la suma total. La segunda es numeros[0], que sigue valiendo 2.
3. Matiz técnico importante
Has dicho que el cambio solo afecta al ámbito local del for-each. La idea es correcta, pero conviene expresarla con más precisión:
En un for-each sobre un array de tipos primitivos, la variable de iteración recibe una copia del valor de cada elemento. Reasignar esa variable no modifica el elemento almacenado en el array.
Esto es diferente de modificar directamente el array:
for (int i = 0; i < numeros.length; i++) {
    numeros[i] = 100;
}
En este segundo caso sí modificamos los elementos originales. Al terminar, el array contiene {100, 100, 100}.
Hay otro matiz para más adelante: cuando un array contiene objetos, la variable del for-each recibe una copia de la referencia al objeto. Eso permite modificar el estado del objeto a través de la referencia, aunque reasignar la variable a otro objeto tampoco sustituye el elemento del array.
4. Comprobación de comprensión
Ejercicio actual
int[] numeros = {3, 5, 7};

for (int numero : numeros) {
    numero += 10;
}

System.out.println(numeros[0]);
System.out.println(numeros[1]);
System.out.println(numeros[2]);
Recuerda que numero += 10 equivale a numero = numero + 10.
Tu tarea: responde con las tres líneas que imprime el programa y explica:
    1. ¿Qué valor recibe numero en cada iteración?

    2. ¿Qué ocurre cuando ejecutamos numero += 10?

    3. ¿Por qué los elementos de numeros cambian o permanecen iguales?

No te preocupes por la velocidad. Lo importante es que puedas justificar el resultado siguiendo la ejecución del código.
¿Qué imprime y por qué? Explica qué ocurre con numero += 10 y si cambia alguno de los elementos originales.

4. Comprobación de comprensión
Ejercicio actual
int[] numeros = {3, 5, 7};

for (int numero : numeros) {
    numero += 10;
}

System.out.println(numeros[0]);
System.out.println(numeros[1]);
System.out.println(numeros[2]);
Recuerda que numero += 10 equivale a numero = numero + 10.
Tu tarea: responde con las tres líneas que imprime el programa y explica:
    1. ¿Qué valor recibe numero en cada iteración?
El mismo valor de la posicion del array + 10 pero solo en el contexto local del bucle for
    2. ¿Qué ocurre cuando ejecutamos numero += 10?
se suma al valor de la posicion del array +10 pero solo en el contexto local del bucle for
    3. ¿Por qué los elementos de numeros cambian o permanecen iguales?
Permanecen iguales porque el cambio +10 solo ocurre en el contexto local del bucle for
No te preocupes por la velocidad. Lo importante es que puedas justificar el resultado siguiendo la ejecución del código.
¿Qué imprime y por qué? Explica qué ocurre con numero += 10 y si cambia alguno de los elementos originales.

Imprime 3,5,7 porque al modificar añadiendo 10 dentro del for each solo se esta modificando el valor de la posicion de array en el contexto local de el bucle for
Tu respuesta es correcta en el resultado y en la idea principal. Hay un matiz terminológico que conviene corregir para que tu explicación sea técnicamente precisa en una entrevista.
1. Aciertos
    • Salida correcta: el programa imprime 3, 5 y 7, cada uno en una línea.
    • Comprendes el for-each: la variable numero recibe el valor de cada elemento del array.
    • Comprendes la reasignación local: numero += 10 no modifica los elementos originales del array, porque numero es una variable local independiente que contiene una copia del valor primitivo.
2. Matiz que debes corregir
Has dicho que se modifica «el valor de la posición del array en el contexto local del bucle».
Esta expresión no es del todo precisa: no se modifica el valor de la posición del array, sino el valor de la variable local numero.
La diferencia importa porque son dos variables distintas: una almacena el elemento del array y la otra recibe una copia de su valor.
3. Ejecución paso a paso
Al comenzar, el array contiene:
3
numeros[0]
5
numeros[1]
7
numeros[2]
Iteraciones del bucle
Iteración 1
numero = 3 → numero += 10 → numero = 13
Iteración 2
numero = 5 → numero += 10 → numero = 15
Iteración 3
numero = 7 → numero += 10 → numero = 17
Array al finalizar
3
Sin cambios
5
Sin cambios
7
Sin cambios
Los valores 13, 15 y 17 solo existen en la variable local durante sus respectivas iteraciones. Por eso, las instrucciones System.out.println imprimen 3, 5 y 7.
4. Respuesta de entrevista recomendada
Podrías explicarlo así:
En un bucle for-each que recorre un array de enteros, la variable de iteración recibe una copia del valor de cada elemento. La operación numero += 10 modifica esa variable local, pero no el array original. Por eso, al imprimir sus elementos, obtenemos 3, 5 y 7.
5. Siguiente comprobación: ¿cómo modificamos el array?
Ahora cambiaremos solo el mecanismo de acceso.
int[] numeros = {3, 5, 7};

for (int i = 0; i < numeros.length; i++) {
    numeros[i] += 10;
}

System.out.println(numeros[0]);
System.out.println(numeros[1]);
System.out.println(numeros[2]);
Tu turno: ¿qué imprime ahora y cuál es la diferencia fundamental respecto al for-each anterior?
No avances por intuición: fíjate especialmente en la expresión numeros[i] += 10.


esta vez si que se esta sumando realmente 10 al valor asociado a la posicion del array en cada iteracion debido a que es un bucle for donde accedemos directamente a la direccion del array con numeros[i] en cambio antes con el for each solo obteniamos una referencia que no modifica el valor original de la posicion del array sino la referencia en local del metodo for each no se si me explico


Te explicas bien y has identificado la diferencia fundamental: ahora modificamos los elementos del array directamente, mientras que antes modificábamos una variable local. Hay un matiz técnico en tu explicación que conviene corregir para que puedas expresarlo con precisión en una entrevista.
1. Qué has entendido correctamente
En este código:
int[] numeros = {3, 5, 7};

for (int i = 0; i < numeros.length; i++) {
    numeros[i] += 10;
}
La expresión numeros[i] accede directamente al elemento del array situado en el índice i.
Por tanto, en cada iteración modificamos el propio array:
    • Primera iteración: numeros[0] pasa de 3 a 13.
    • Segunda iteración: numeros[1] pasa de 5 a 15.
    • Tercera iteración: numeros[2] pasa de 7 a 17.
El resultado es 13, 15, 17.
2. El matiz que debes corregir
Has dicho que el for-each obtiene una referencia y modifica la referencia local. Eso no es exactamente lo que sucede en este caso, porque estamos trabajando con un array de int, un tipo primitivo.
Observa el código anterior:
int[] numeros = {3, 5, 7};

for (int numero : numeros) {
    numero += 10;
}
En cada iteración, Java copia el valor del elemento en la variable local numero.
Por ejemplo, en la primera iteración ocurre conceptualmente lo siguiente:
int numero = numeros[0]; // Copia el valor 3
numero += 10;            // numero pasa a valer 13
Pero numeros[0] sigue valiendo 3, porque numero es una variable independiente.
La diferencia exacta es esta:
Expresión
Qué modifica
numero += 10
La variable local numero.
numeros[i] += 10
El elemento del array en la posición i.
No necesitas acceder a una dirección de memoria manualmente. Java gestiona ese acceso por ti.
3. Comprueba si has asimilado la diferencia
Ahora vamos a introducir una pequeña variación. No avances hasta resolverla.
int[] numeros = {2, 4, 6};

for (int i = 0; i < numeros.length; i++) {
    int numero = numeros[i];
    numero += 5;
}

System.out.println(numeros[0]);
System.out.println(numeros[1]);
System.out.println(numeros[2]);
¿Qué imprime y por qué?
Fíjate en que utilizamos un for clásico, pero dentro creamos una variable local llamada numero. ¿Eso basta para modificar los elementos del array?



al sumar 5 con una variable creada dentro del bucle he igualada al valor de la posicion del array de la iteraccion actual estamos modificando +5 solo a una copia de el valor de posicion del array que solo vive en el contexto local de el bucle for, asi que se imprime: 2, 4, 6

Correcto. Has entendido la diferencia y el resultado es exactamente 2, 4, 6.
Vamos a precisar tu razonamiento, porque es importante que sepas explicarlo técnicamente en una entrevista.
1. Qué ocurre en cada iteración
int numero = numeros[i];
numero += 5;
En la primera iteración:
    1. numeros[i] vale 2.
    2. Se copia ese valor en la variable local numero.
    3. numero += 5 cambia numero de 2 a 7.
    4. El elemento numeros[0] sigue valiendo 2, porque nunca lo hemos modificado.
Lo mismo sucede con los elementos 4 y 6.
Matiz importante: no es que el for clásico impida modificar el array ni que la variable local solo exista en el contexto del bucle. La diferencia es qué variable modificas. En este caso, numero se declara dentro del cuerpo del bucle y tiene ámbito local a ese bloque; numeros[i] permite modificar directamente el elemento del array.
2. Comprueba el último matiz
Ahora vamos a trabajar con un array de objetos, donde sí entran en juego las referencias.
class Caja {
    int valor;

    Caja(int valor) {
        this.valor = valor;
    }
}
Y este código:
Caja[] cajas = {
    new Caja(10),
    new Caja(20)
};

for (Caja caja : cajas) {
    caja.valor += 5;
}

System.out.println(cajas[0].valor);
System.out.println(cajas[1].valor);
¿Qué imprime?
Aquí quiero que distingas dos operaciones:
    • caja.valor += 5
    • caja = new Caja(100)
¿Por qué la primera puede modificar los objetos originales aunque caja sea una variable local, mientras que reasignar caja no sustituiría el elemento del array?
Porque en este caso al estar trabajando con objetos en vez de tipos de datos primitivos la variable caja del foreach esta trabajando con una referencia al objeto, asi que aunque viva en local hace referencia al mismo objeto en memoria que kas posiciones del array de cajas originales
cajas[0] y cajas[1]
Correcto. Has entendido el concepto central: la variable local caja contiene una copia de la referencia al objeto, no una copia del objeto.
Hay un matiz importante: caja no es una referencia al elemento del array, sino una copia de la referencia que contiene ese elemento. Por eso puedes modificar el objeto original, pero no sustituir directamente la posición del array reasignando caja.
1. Cómo funciona en memoria
Al ejecutar:
for (Caja caja : cajas) {
    caja.valor += 5;
}
En la primera iteración, tanto cajas[0] como caja permiten acceder al mismo objeto Caja.
Array cajas
Contiene referencias a objetos
cajas[0]
caja
Copia de la referencia
Ambas permiten acceder al mismo objeto
Objeto Caja
valor = 15
Antes valía 10
Por tanto, caja.valor += 5 modifica el estado del objeto compartido.
2. ¿Qué pasa si reasignamos caja?
Considera esta variante:
for (Caja caja : cajas) {
    caja = new Caja(100);
}
Esto no sustituye los elementos del array. Solo hace que la variable local caja pase a apuntar al objeto nuevo. Al terminar cada iteración, esa variable local deja de utilizarse.
Para sustituir realmente el primer elemento, necesitarías escribir:
cajas[0] = new Caja(100);
La diferencia fundamental es:
    • caja.valor = 100; modifica un campo del objeto al que apunta la referencia.
    • caja = new Caja(100); reasigna la variable local.
    • cajas[0] = new Caja(100); sustituye la referencia almacenada en el array.
3. Última comprobación antes de cerrar arrays
Sin ejecutar el código, dime qué imprime cada línea y explica por qué:
Caja[] cajas = {
    new Caja(10),
    new Caja(20)
};

for (Caja caja : cajas) {
    caja.valor += 5;
    caja = new Caja(100);
}

System.out.println(cajas[0].valor);
System.out.println(cajas[1].valor);
Aquí se combinan las dos operaciones que acabamos de estudiar. Si lo resuelves correctamente, pasaremos a practicar copia de referencias frente a copia de arrays.

System.out.println(cajas[0].valor);
System.out.println(cajas[1].valor);

imprimen 15 y 25 respectivamente

Correcto: imprime 15 y 25. Tu razonamiento es coherente con lo que hemos estudiado.
Vamos a repasar las dos operaciones de cada iteración para consolidar el concepto.
for (Caja caja : cajas) {
    caja.valor += 5;
    caja = new Caja(100);
}
    1. caja.valor += 5; modifica el objeto original al que apunta la referencia local. Los valores pasan de 10 a 15 y de 20 a 25.
    2. caja = new Caja(100); hace que la variable local caja apunte a un objeto nuevo. No modifica la referencia guardada en cajas[0] ni en cajas[1].
Por eso el array conserva las referencias a los objetos originales, cuyos valores ahora son 15 y 25.
Siguiente concepto: copiar un array no es lo mismo que copiar su referencia
Este matiz es importante porque conecta todo lo que acabamos de aprender sobre referencias.
Observa:
int[] original = {10, 20, 30};
int[] copia = original;

copia[0] = 99;

System.out.println(original[0]);
System.out.println(copia[0]);
Pregunta: ¿qué imprime y por qué?
No te adelantes a la solución: razona sobre si copia contiene un array nuevo o una referencia al mismo array que original.

imprimer 99 y 99

porque al igualar un array al otro ambos apuntan a la referencia de el mismo array en memoria

vamos terminando de una vez con los arrays

Correcto. Imprime 99 y 99, porque original y copia contienen referencias al mismo array. No se ha creado una copia del array, solo se ha copiado la referencia.
Vamos a cerrar el bloque de arrays con los últimos conceptos esenciales y una prueba final. No necesitamos alargarlo más de lo necesario.
1. Cómo copiar realmente un array
En Java puedes utilizar Arrays.copyOf() para crear otro array independiente.
import java.util.Arrays;

int[] original = {10, 20, 30};
int[] copia = Arrays.copyOf(original, original.length);

copia[0] = 99;

System.out.println(original[0]); // 10
System.out.println(copia[0]);    // 99
Ahora existen dos arrays diferentes. Modificar un elemento de uno no modifica el otro.
Importante: esto es una copia superficial (shallow copy). Con arrays de objetos se copian las referencias a los objetos, no los propios objetos.
2. Arrays multidimensionales
Java permite crear arrays cuyos elementos son otros arrays.
int[][] matriz = {
    {1, 2, 3},
    {4, 5, 6}
};

System.out.println(matriz[0][1]); // 2
System.out.println(matriz[1][2]); // 6
    • matriz[0] es el primer array interno.
    • matriz[1] es el segundo.
    • matriz[0][1] accede al segundo elemento del primer array.
Técnicamente, en Java un array bidimensional es un array de arrays. Las filas incluso pueden tener longitudes diferentes.
3. Operaciones útiles de Arrays
La clase java.util.Arrays proporciona utilidades habituales:
import java.util.Arrays;

int[] numeros = {3, 1, 2};

Arrays.sort(numeros);
System.out.println(Arrays.toString(numeros)); // [1, 2, 3]

int[] copia = Arrays.copyOf(numeros, numeros.length);
System.out.println(Arrays.equals(numeros, copia)); // true
Recuerda:
    • Arrays.sort(): ordena.
    • Arrays.toString(): genera una representación legible.
    • Arrays.copyOf(): crea una copia del array.
    • Arrays.equals(): compara los elementos de dos arrays; == compara sus referencias.
4. Prueba final de arrays
Responde sin ejecutar el código. Corregiremos los resultados antes de dar por terminado el bloque.
1. ¿Qué imprime?
int[] a = {2, 4, 6};
int[] b = Arrays.copyOf(a, a.length);
b[1] = 99;
System.out.println(a[1]);
99
4
Error de compilación
2. ¿Qué imprime?
int[] a = {2, 4, 6};
int[] b = a;
b[1] = 99;
System.out.println(a == b);
true
false
Error de compilación
3. ¿Qué ocurre con este bucle?
int[] a = {10, 20, 30};
for (int i = 0; i <= a.length; i++) {
    System.out.println(a[i]);
}
Imprime los tres valores y termina normalmente.
Imprime los tres valores y después lanza ArrayIndexOutOfBoundsException.
No imprime nada.
4. ¿Qué diferencia hay entre Arrays.equals(a, b) y a == b para dos arrays?
Corregir prueba
Cuando resuelvas estas cuatro cuestiones, cerraremos arrays y continuaremos con el siguiente bloque del itinerario: estructuras de datos y algoritmos, empezando por búsqueda lineal, búsqueda binaria y complejidad temporal.

Mis respuestas a la prueba final de arrays:
1. B
2. A
3. B
4. equals compara los valores de ambos arrays 1 a 1 y == solo compara la referencia, si ambos hacen referencia al mismo array


por cierto antes de cerrar arrays podrias darme un ejemplo de uso de tostring?


Las cuatro respuestas son correctas. Con esto podemos dar por terminado el bloque de arrays tras ver el ejemplo de toString() que pides.
Ejemplo práctico de Arrays.toString()
En Java, si intentas imprimir un array directamente, no obtienes una representación de sus elementos.
int[] numeros = {10, 20, 30};

System.out.println(numeros);
La salida será algo parecido a esto:
[I@5acf9800
La parte exacta después de @ puede variar. No muestra los valores del array, sino una representación basada en su tipo y su identidad.
Para mostrar los elementos de forma legible, utilizamos Arrays.toString():
import java.util.Arrays;

public class Main {
    public static void main(String[] args) {
        int[] numeros = {10, 20, 30};

        System.out.println(Arrays.toString(numeros));
    }
}
Salida:
[10, 20, 30]
Un ejemplo más realista
Imagina que estás depurando un algoritmo que modifica un array:
import java.util.Arrays;

public class Main {
    public static void main(String[] args) {
        int[] notas = {5, 7, 4, 9};

        System.out.println("Notas originales: " + Arrays.toString(notas));

        for (int i = 0; i < notas.length; i++) {
            notas[i] += 1;
        }

        System.out.println("Notas modificadas: " + Arrays.toString(notas));
    }
}
Salida:
Notas originales: [5, 7, 4, 9]
Notas modificadas: [6, 8, 5, 10]
Es especialmente útil para depurar, comprobar resultados de algoritmos y mostrar el contenido completo de un array sin escribir un bucle.
¿Y qué pasa con arrays multidimensionales?
Para un array bidimensional, utiliza Arrays.deepToString():
import java.util.Arrays;

int[][] matriz = {
    {1, 2, 3},
    {4, 5, 6}
};

System.out.println(Arrays.deepToString(matriz));
Salida:
[[1, 2, 3], [4, 5, 6]]
La diferencia importante:
    • Arrays.toString(array): representación de un array de una dimensión.
    • Arrays.deepToString(array): representación anidada de arrays multidimensionales.
Nota técnica: toString() es un método que también existe en los objetos Java, pero Arrays.toString() es un método estático de utilidad de la clase Arrays. No son la misma llamada.
Con esto cerramos arrays: declaración, índices, recorridos, for-each, mutabilidad, referencias, copias, matrices y utilidades de Arrays. El siguiente bloque será estructuras de datos y algoritmos, comenzando por búsqueda lineal y complejidad temporal.

---

Correcto. No hace falta volver a repasar las copias de arrays unidimensionales. Continuamos con el ejercicio de matrices y copias superficiales y, después, pasaremos directamente a excepciones.
1. Matrices y copias superficiales
Analiza este código:
import java.util.Arrays;

int[][] original = {
    {1, 2},
    {3, 4}
};

int[][] copia = Arrays.copyOf(original, original.length);

copia[0][0] = 99;
copia[1] = new int[]{7, 8};

System.out.println(Arrays.deepToString(original));
System.out.println(Arrays.deepToString(copia));
Sin ejecutar el código, responde:
    1. ¿Qué imprime cada println?
    2. ¿Por qué modificar copia[0][0] afecta —o no— a original?
    3. ¿Por qué asignar un array nuevo a copia[1] tiene un efecto diferente?
    4. ¿Qué diferencia hay entre una copia superficial (shallow copy) y una copia profunda (deep copy) en este caso?
La idea que debes demostrar es que una matriz bidimensional de Java es un array externo que contiene referencias a otros arrays. Arrays.copyOf() copia el array externo, pero no duplica automáticamente los arrays internos.
Cuando respondas, corregiremos el ejercicio. Si está bien resuelto, daremos por cerrado el bloque de arrays y pasaremos a 1.7. Excepciones, empezando por la jerarquía Throwable, Error y Exception, antes de estudiar try/catch/finally, throw y throws.


Imprime 

[[99, 2], [3, 4]]
[[99, 2], [7, 8]]

debido a que la primera modificacion copia[0][0] = 99; afecta a las dos matrices porque ambas hacen referencia a los mismos 2 arrays en memoria, en cambio la segunda modificacion copia[1] = new int[]{7, 8}; solo afecta a la matriz copia dado que estamos reasignando la referencia interna de la matriz[1] a un nuevo array que creamos new int[]{7, 8}

La clave está en distinguir modificar un array interno de sustituir una referencia del array externo. Vamos paso a paso.
1. ¿Qué ocurre al crear la matriz?
int[][] original = {
    {1, 2},
    {3, 4}
};

int[][] copia = Arrays.copyOf(original, original.length);
Arrays.copyOf() crea un array externo nuevo, pero copia las referencias a los arrays internos. Por tanto, ambas matrices apuntan a los mismos arrays internos.
Estado inicial
original
Fila 0 → A
Fila 1 → B
copia
Fila 0 → A
Fila 1 → B
Array interno A
1
2
Array interno B
3
4
A y B son los mismos arrays internos para ambas matrices, no duplicados.
2. Primera instrucción: modificar un elemento
copia[0][0] = 99;
Significa:
    1. copia[0]: accede al array interno A.
    2. [0]: selecciona su primer elemento.
    3. = 99: modifica ese elemento.
Como original[0] también apunta al array A, el cambio se ve desde ambas matrices.
Resultado en este momento:
original = {{99, 2}, {3, 4}}
copia    = {{99, 2}, {3, 4}}
No se han cambiado dos valores. Se ha cambiado un único valor compartido, que ambas matrices pueden ver.
3. Segunda instrucción: sustituir una referencia
copia[1] = new int[]{7, 8};
Esta vez no modificas el contenido del array B. Haces que la segunda fila de copia apunte a un array nuevo, C.
original
Fila 0 → A
Fila 1 → B
copia
Fila 0 → A
Fila 1 → C
A
99, 2
Compartido
B
3, 4
Solo original
C
7, 8
Solo copia
Por eso, el resultado final es:
[[99, 2], [3, 4]]
[[99, 2], [7, 8]]
4. Comprueba que lo has entendido
No hace falta repetir la explicación. Responde a estas dos preguntas:
A. Si después de esas instrucciones ejecutamos:
original[1][0] = 50;
¿Qué contendrá copia en ese momento?
B. Si ejecutamos:
copia[0] = new int[]{6, 6};
¿Cambiará la primera fila de original?
La distinción importante es esta: modificar un objeto compartido afecta a quienes lo referencian; cambiar una referencia para que apunte a otro objeto no cambia las referencias de las demás variables.





debido a que la primera modificacion copia[0][0] = 99; afecta a las dos matrices porque ambas hacen referencia a los mismos 2 arrays en memoria, en cambio la segunda modificacion copia[1] = new int[]{7, 8}; solo afecta a la matriz copia dado que estamos reasignando la referencia interna de la matriz[1] a un nuevo array que creamos new int[]{7, 8}

A. Si después de esas instrucciones ejecutamos:
original[1][0] = 50;
¿Qué contendrá copia en ese momento?
[[99, 2], [7, 8]] debido a que el cambio original[1][0] = 50; solo afecta a original dado que el array [1] de copy ahora hace refeerencia a un array distinto
B. Si ejecutamos:
copia[0] = new int[]{6, 6};
¿Cambiará la primera fila de original?
no seguiriamos teniendo [[99, 2], [50, 4]] en original y {6, 6}{7, 8} en copia debido a que a que estamos creando un nuevo array para ese [6,6 ] y ya no estamo haciendo referencia al mismo array que original



Las dos respuestas son correctas en cuanto al razonamiento principal. Has entendido la diferencia entre modificar un array interno compartido y reasignar una referencia. Hay un pequeño matiz de notación que conviene corregir.
Corrección
1. Primera modificación: copia[0][0] = 99
Correcto. Ambas matrices contienen referencias al mismo array interno en la fila 0, así que el cambio se observa desde las dos.
2. Segunda modificación: copia[1] = new int[]{7, 8}
Correcto. Se sustituye la referencia de la fila 1 de copia, sin cambiar la referencia de original[1]. A partir de ahí, cada matriz tiene un array diferente en esa posición.
3. Pregunta A
Correcto. Tras ejecutar original[1][0] = 50, los contenidos son:
original = {{99, 2}, {50, 4}}
copia    = {{99, 2}, {7, 8}}
El cambio afecta al array interno que sigue compartiendo original, pero que copia ya no referencia en la fila 1.
4. Pregunta B
Correcto también. Tras ejecutar copia[0] = new int[]{6, 6}, queda:
original = {{99, 2}, {50, 4}}
copia    = {{6, 6}, {7, 8}}
El matiz: copia y original son matrices distintas desde el principio, aunque inicialmente compartían sus arrays internos. No es que copia deje de ser la misma matriz; es que su fila 0 pasa a apuntar a un array diferente.
Concepto consolidado
Puedes distinguir ya estos dos comportamientos:
    • Modificar contenido: copia[0][0] = 99 modifica un elemento del array interno compartido.
    • Reasignar referencia: copia[0] = new int[]{6, 6} hace que una fila de copia apunte a un array nuevo.
Damos por cerrado este apartado de matrices y copias superficiales. Pasamos a 1.7. Excepciones en Java, empezando por su jerarquía y la diferencia entre excepciones comprobadas y no comprobadas. Después veremos propagación, try/catch/finally, throw, throws y try-with-resources.


Fase 1.7. Excepciones en Java
Vamos a empezar por la jerarquía de excepciones, porque entenderla facilita todo lo demás: cuándo Java obliga a gestionar un error, cuándo no y qué tipos puedes capturar.
1. ¿Qué es una excepción?
Una excepción es un objeto que representa una situación anómala durante la ejecución de un programa y que altera el flujo normal de ejecución.
Por ejemplo:
int resultado = 10 / 0;
La división de dos enteros entre cero provoca una ArithmeticException. Java interrumpe la ejecución normal de esa operación y busca un manejador compatible con esa excepción. Si no lo encuentra, la excepción se propaga hasta que el programa termina de forma anómala.
Otro ejemplo:
String texto = null;
System.out.println(texto.length());
Esto provoca una NullPointerException, porque intentamos invocar un método sobre una referencia null.
Importante: las excepciones no son únicamente errores de programación. También representan situaciones esperables que una aplicación debe gestionar, como no encontrar un archivo o no poder conectarse a un servicio.
2. Jerarquía de excepciones
La jerarquía principal de Java es esta:
Object
Throwable
Raíz de los objetos que pueden lanzarse
Error
Problemas graves de la JVM o del entorno
OutOfMemoryError
StackOverflowError
Exception
Situaciones que una aplicación puede gestionar
IOException
SQLException
RuntimeException
RuntimeException
Subclase de Exception
NullPointerException · IllegalArgumentException · ArithmeticException
La jerarquía se lee así:
    • Throwable: superclase de los objetos que Java permite lanzar mediante throw.
    • Error: representa problemas graves, normalmente relacionados con la JVM o los recursos del entorno. Generalmente no se intenta recuperar de ellos mediante un catch genérico.
    • Exception: representa situaciones que la aplicación puede gestionar.
    • RuntimeException: subclase de Exception que agrupa las excepciones no comprobadas más habituales.
3. Excepciones comprobadas y no comprobadas
Esta distinción es fundamental en Java.
Excepciones comprobadas (checked)
Java exige que las gestiones mediante try/catch o que se declaren para propagarlas mediante throws.
Files.readString(Path.of("datos.txt"));
Files.readString() puede lanzar IOException, que es una excepción comprobada. Si no se gestiona ni se declara, el código no compila.
Excepciones no comprobadas (unchecked)
Java no exige capturarlas ni declararlas. Son las subclases de RuntimeException y también los objetos de tipo Error y sus subclases.
int resultado = 10 / 0;
ArithmeticException es no comprobada. El código compila, aunque al ejecutarse esa división se lanza la excepción.
Una precisión importante: comprobada no significa que Java compruebe si el error sucede en tiempo de ejecución. Significa que el compilador exige gestionar o declarar ese tipo de excepción.
Tampoco significa que las excepciones no comprobadas sean siempre errores que deban ignorarse. Una IllegalArgumentException, por ejemplo, puede ser útil para indicar que un método ha recibido un argumento inválido.
4. Primera comprobación
No avancemos todavía a try/catch. Primero quiero verificar que distingues las categorías.
Clasifica cada caso como comprobada, no comprobada o Error. Además, indica si Java obliga a capturarla o declararla con throws.
Ejercicio: jerarquía de excepciones en Java
Clasifica cada tipo de excepción y determina si Java obliga a capturarla o declararla con throws.
Selecciona una categoría para cada excepción. No mostraré las soluciones hasta que envíes tus respuestas.

Recuerda la regla general: las excepciones comprobadas derivan de Exception, excluyendo RuntimeException y sus subclases. Error y RuntimeException pertenecen a las excepciones no comprobadas en el sentido de que el compilador no exige capturarlas ni declararlas; en este ejercicio las clasificamos por separado para distinguirlas.
Corrección de cada respuesta
Tipo
Clasificación
¿Java obliga a capturarla o declararla con throws?
IOException
Comprobada (checked)
Sí
NullPointerException
No comprobada (unchecked)
No
OutOfMemoryError
Error
No
SQLException
Comprobada (checked)
Sí
IllegalArgumentException
No comprobada (unchecked)
No
1. IOException
Es una excepción comprobada. Puede producirse al leer o escribir archivos, por ejemplo. El compilador exige que la gestiones con try/catch o declares que puede propagarse mediante throws IOException.
2. NullPointerException
Es una excepción no comprobada, porque hereda de RuntimeException. Puede producirse al invocar un método sobre una referencia null. No necesitas capturarla ni declararla para que el código compile.
3. OutOfMemoryError
Es una subclase de Error y representa una situación grave, como que la JVM no pueda reservar más memoria. No exige captura ni declaración. Aunque puede capturarse técnicamente, recuperarse de ella no siempre es seguro.
4. SQLException
Es una excepción comprobada utilizada en operaciones de bases de datos, por ejemplo con JDBC. Java exige capturarla o declararla con throws SQLException.
5. IllegalArgumentException
Es una excepción no comprobada que hereda de RuntimeException. Se utiliza, por ejemplo, cuando un método recibe un argumento inválido. No requiere captura ni declaración.
Regla que debes recordar
    • Checked: el compilador obliga a capturar o declarar.
    • Unchecked: el compilador no obliga a capturar ni declarar.
    • Error: rama distinta de Exception; tampoco requiere captura ni declaración.
Técnicamente, Error también forma parte de las excepciones no comprobadas en el sentido amplio de Java. Aquí lo clasificamos aparte para distinguir las dos ramas principales de Throwable.

Cuando lo resolvamos, seguiremos con try, catch y finally, y después con throw, throws, excepciones personalizadas, propagación y try-with-resources.

excepciones en Java 

Ya has acertado las cinco clasificaciones de excepciones. La siguiente pregunta es:
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public static String leer() {
    return Files.readString(Path.of("datos.txt"));
}
¿Qué ocurre al compilar este método?
    • A. Compila porque Java gestiona automáticamente IOException.
    • B. No compila porque debe capturar IOException o declarar throws IOException.
    • C. Compila, pero necesariamente falla en tiempo de ejecución.
Responde con la letra y la justificación. A partir de ahí empezaremos con try/catch, sin volver a repetir la jerarquía que ya has demostrado comprender.

B. No compila porque debe capturar IOException o declarar throws IOException. 
debido a que la excepcion IOException es una excepcion comprobada, que exige capturarse

Correcto: B. Tu explicación es correcta.
IOException es una excepción comprobada (checked exception), por lo que el compilador exige que el método la capture con try/catch o la declare mediante throws IOException.
Hay un matiz importante: esto no significa que la excepción vaya a producirse necesariamente. El error de compilación aparece porque no se ha gestionado de ninguna de las dos formas permitidas.
Pasamos a resolverlo con try/catch.
Ejercicio 1: capturar la excepción
Tenemos este método:
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public static String leer() {
    try {
        return Files.readString(Path.of("datos.txt"));
    } catch (IOException e) {
        return "No se pudo leer el archivo";
    }
}
Pregunta: si datos.txt no existe y Files.readString() lanza una IOException, ¿qué sucede?
    • A. El método devuelve el contenido del archivo como una cadena vacía.
    • B. Se ejecuta el bloque catch y el método devuelve "No se pudo leer el archivo".
    • C. La excepción siempre se propaga al método que llamó a leer(), aunque exista el bloque catch.
Responde con la letra y explica por qué.

B. Se ejecuta el bloque catch y el método devuelve "No se pudo leer el archivo". 
porque asi es como funciona el try catch cuando capturas un tipo de excepcion con catch y el codigo falla lanzando ese tipo de excepcion 
la ejceucionm del codigo salta de el bloque try al catch ejecutando lo que hay dentro de el catch, en este caso return "No se pudo leer el archivo";
catch (IOException e) {
        return "No se pudo leer el archivo";
    }

Correcto. B es la respuesta correcta, y la explicación del flujo de ejecución también es correcta.
Has identificado los dos puntos importantes:
    1. Files.readString() lanza una IOException si, por ejemplo, el archivo no existe o no puede leerse.
    2. Como el catch captura IOException, la ejecución salta desde el try al bloque catch, que devuelve el mensaje indicado.
Hay un matiz: el catch solo captura excepciones compatibles con el tipo declarado. Si se lanzase una excepción que no fuese IOException ni una de sus subclases, este bloque no la capturaría.
Ejercicio 2: declarar throws
Ahora tenemos esta versión:
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public static String leer() throws IOException {
    return Files.readString(Path.of("datos.txt"));
}
¿Qué diferencia hay respecto al ejercicio anterior?
    • A. El método captura la excepción y devuelve automáticamente un mensaje de error.
    • B. El método declara que puede propagar una IOException al código que lo invoque; no la captura aquí.
    • C. throws IOException impide que Files.readString() lance esa excepción.
Responde con la letra y explica qué responsabilidad asume el método leer() y cuál queda en manos del código que lo llama.


B. El método declara que puede propagar una IOException al código que lo invoque; no la captura aquí. 


Correcto. B es la respuesta correcta.
Con throws IOException, el método leer() declara que puede producir una excepción de ese tipo, pero no la captura ni la resuelve.
public static String leer() throws IOException {
    return Files.readString(Path.of("datos.txt"));
}
La responsabilidad se reparte así:
    • leer(): declara que puede propagar una IOException y deja que la excepción salga del método.
    • Código que llama a leer(): debe capturar la excepción con try/catch o declarar también throws IOException, si se trata de una excepción comprobada.
Por ejemplo, el siguiente método también tendría que gestionar la excepción:
public static void main(String[] args) throws IOException {
    String contenido = leer();
    System.out.println(contenido);
}
Aquí main() también declara throws IOException. Si la lectura falla, la excepción puede propagarse hasta el entorno de ejecución, sin que ninguno de estos métodos la capture.
Siguiente ejercicio: propagación de excepciones
Considera este código:
public static String leerArchivo() throws IOException {
    return Files.readString(Path.of("datos.txt"));
}

public static void procesar() throws IOException {
    String contenido = leerArchivo();
    System.out.println(contenido);
}
Suponiendo que los imports son correctos, ¿por qué compila el método procesar() aunque no tenga ningún bloque try/catch?
    • A. Porque procesar() ignora automáticamente las excepciones comprobadas.
    • B. Porque procesar() declara throws IOException y puede propagar la excepción a quien lo invoque.
    • C. Porque las excepciones de Files.readString() solo se producen en tiempo de ejecución y no las comprueba el compilador.
Responde con la letra y la explicación.

B 

Correcto. B es la respuesta correcta.
procesar() compila porque declara throws IOException. Como llama a leerArchivo(), que puede lanzar esa excepción comprobada, procesar() asume la responsabilidad de declararla y permitir que se propague al método que lo invoque.
La propagación puede encadenarse por varios métodos:
public static String leerArchivo() throws IOException {
    return Files.readString(Path.of("datos.txt"));
}

public static void procesar() throws IOException {
    String contenido = leerArchivo();
    System.out.println(contenido);
}

public static void main(String[] args) {
    try {
        procesar();
    } catch (IOException e) {
        System.err.println("Error al leer el archivo: " + e.getMessage());
    }
}
En este ejemplo, main() finalmente captura la excepción. Así, cada método puede decidir si gestiona el error o lo propaga.
Siguiente ejercicio: finally
¿Qué sucede con el bloque finally en este código?
try {
    System.out.println("A");
    throw new IOException();
} catch (IOException e) {
    System.out.println("B");
} finally {
    System.out.println("C");
}
    • A. Se imprime A, después B y finalmente C.
    • B. Se imprime A y después B; finally no se ejecuta porque hubo una excepción.
    • C. Se imprime A y después C; el catch no se ejecuta porque la excepción se lanza dentro del try.
Responde con la letra y explica el orden de ejecución.

A

Correcto. A es la respuesta correcta.
El orden de ejecución es:
    1. Se imprime A.
    2. throw new IOException() lanza la excepción.
    3. El catch (IOException e) captura la excepción y se imprime B.
    4. Se ejecuta finally y se imprime C.
La salida es:
A
B
C
Concepto clave: finally se ejecuta normalmente tanto si se produce una excepción como si no, y tanto si la excepción se captura como si se propaga. Se utiliza habitualmente para liberar recursos o realizar tareas de limpieza.
Hay una precisión: existen situaciones excepcionales en las que finally puede no ejecutarse, como cuando la JVM termina abruptamente.
Siguiente ejercicio: throw frente a throws
Observa este código:
public static void validarEdad(int edad) {
    if (edad < 18) {
        throw new IllegalArgumentException("Debe ser mayor de edad");
    }
}
¿Cuál de estas afirmaciones es correcta?
    • A. throw declara que el método puede lanzar una excepción, mientras que throws lanza la excepción.
    • B. throw lanza una excepción concreta; throws declara en la firma del método las excepciones que puede propagar.
    • C. Ambos términos hacen exactamente lo mismo.
Responde con la letra y explica la diferencia entre ambos.

B

Correcto. B es la respuesta correcta.
La diferencia fundamental es:
    • throw: lanza una instancia concreta de una excepción durante la ejecución.
    • throws: declara en la firma del método qué excepciones puede propagar.
Ejemplo de throw:
throw new IllegalArgumentException("Edad no válida");
Aquí se crea y se lanza una excepción concreta.
Ejemplo de throws:
public static String leerArchivo() throws IOException {
    return Files.readString(Path.of("datos.txt"));
}
Aquí se declara que el método puede propagar una IOException.
Matiz importante: throw puede lanzar tanto excepciones comprobadas como no comprobadas. Si lanza una excepción comprobada, el método debe capturarla o declararla mediante throws.
Siguiente ejercicio: excepción comprobada al usar throw
¿Qué ocurre al compilar este método?
public static void validar() {
    throw new IOException("Error de lectura");
}
Supongamos que IOException está importada correctamente.
    • A. Compila porque cualquier excepción se puede lanzar libremente con throw.
    • B. No compila porque IOException es comprobada y debe capturarse o declararse mediante throws.
    • C. Compila, pero la excepción se ignora automáticamente.
Responde con la letra y explica por qué.
B

Correcto. B es la respuesta correcta.
IOException es una excepción comprobada (checked exception). Por tanto, el compilador exige que se capture o se declare mediante throws.
Por ejemplo, podemos resolverlo declarando la excepción:
public static void validar() throws IOException {
    throw new IOException("Error de lectura");
}
O capturándola dentro del propio método:
public static void validar() {
    try {
        throw new IOException("Error de lectura");
    } catch (IOException e) {
        System.err.println(e.getMessage());
    }
}
En el segundo caso, el método captura la excepción y no la propaga.
Siguiente ejercicio: ¿qué ocurre si el catch no coincide?
Observa este código:
try {
    throw new IOException("Error de lectura");
} catch (NullPointerException e) {
    System.out.println("Error de referencia");
}
Supongamos que los imports son correctos.
¿Qué ocurre?
    • A. Compila y se ejecuta el catch, porque cualquier catch captura cualquier excepción.
    • B. No compila porque el catch no captura IOException.
    • C. El código no compila porque falta un bloque finally.
Responde con la letra y explica qué relación debe existir entre el tipo de excepción lanzada y el tipo declarado en catch.

B

Correcto. B es la respuesta esperada, aunque aquí hay un matiz importante de Java.
El catch (NullPointerException e) no captura una IOException, porque son tipos de excepción distintos y no existe una relación de herencia entre ellos.
Además, en este ejemplo concreto, el compilador rechaza el código: el bloque try solo lanza explícitamente una IOException comprobada, que no puede ser capturada por ese catch de NullPointerException.
La relación que debe existir es que el tipo declarado en catch sea compatible con la excepción que se puede lanzar: debe poder capturarla por tipo o por una de sus superclases.
Siguiente ejercicio: excepciones personalizadas
Queremos crear una excepción propia para indicar que una edad no es válida:
public class EdadInvalidaException extends Exception {
    public EdadInvalidaException(String mensaje) {
        super(mensaje);
    }
}
¿Qué tipo de excepción hemos creado?
    • A. Una excepción comprobada, porque hereda de Exception y no de RuntimeException.
    • B. Una excepción no comprobada, porque todas las excepciones personalizadas son unchecked.
    • C. Un Error, porque hereda indirectamente de Throwable.
Responde con la letra y explica qué implica esa elección para los métodos que lancen EdadInvalidaException.

A


Correcto. A. Es una excepción comprobada (checked exception), porque EdadInvalidaException hereda directamente de Exception, no de RuntimeException.
Esto implica que cualquier método que lance esta excepción debe capturarla con try/catch o declararla con throws.
Por ejemplo, si queremos validar una edad:
public static void validarEdad(int edad) throws EdadInvalidaException {
    if (edad < 18) {
        throw new EdadInvalidaException("La edad debe ser al menos 18");
    }
}
Aquí aparecen dos conceptos que ya has estudiado:
    • throw: lanza la instancia concreta de EdadInvalidaException.
    • throws: declara que el método puede propagar esa excepción comprobada.
El código que invoque a validarEdad() tendrá que gestionarla también:
try {
    validarEdad(16);
} catch (EdadInvalidaException e) {
    System.out.println(e.getMessage());
}
La salida será:
La edad debe ser al menos 18
Siguiente ejercicio: excepción personalizada no comprobada
Ahora cambiamos la clase para que herede de RuntimeException:
public class EdadInvalidaException extends RuntimeException {
    public EdadInvalidaException(String mensaje) {
        super(mensaje);
    }
}
¿Qué cambia respecto a la versión anterior?
    • A. Ahora es una excepción no comprobada y los métodos que la lancen no están obligados a capturarla ni declararla con throws.
    • B. Sigue siendo comprobada porque todas las excepciones personalizadas lo son.
    • C. Ahora es un Error y no puede capturarse con catch.
Responde con la letra y explica qué diferencia práctica tiene elegir Exception o RuntimeException como clase base.

A

Correcto. A. Al heredar de RuntimeException, EdadInvalidaException pasa a ser una excepción no comprobada (unchecked).
La diferencia práctica es la obligación que impone el compilador:
    • extends Exception: quien lance la excepción debe capturarla o declararla con throws.
    • extends RuntimeException: quien lance la excepción no está obligado a capturarla ni declararla.
En ambos casos puedes utilizar try/catch para capturarla. La diferencia no es si se puede capturar, sino si el compilador te obliga a gestionarla.
¿Cuándo elegir cada una?
    • Exception: cuando quieres que el código que llama al método tenga que decidir explícitamente cómo gestionar una situación recuperable, como un fallo de una operación de entrada/salida.
    • RuntimeException: cuando quieres representar situaciones como argumentos inválidos o incumplimientos de precondiciones, sin imponer esa obligación al código llamante.
No es una regla absoluta: la decisión depende del contrato de la API y de cómo se espera que el consumidor gestione el fallo.

---

Ejercicio 5 — static frente a variables de instancia
¿Qué imprime este código?
class Contador {
    static int total = 0;
    int valor = 0;

    Contador() {
        total++;
        valor++;
    }
}

Contador c1 = new Contador();
Contador c2 = new Contador();

System.out.println(Contador.total);
System.out.println(c1.valor);
System.out.println(c2.valor);
A. 2, 1, 1
B. 2, 2, 2
C. 1, 1, 1
D. 2, 1, 2
Responde con la letra y explica brevemente la diferencia entre total y valor. Después corregiremos la respuesta y seguiremos con la evaluación, sin volver a explicar los conceptos que ya tengas claros.

A

Correcto: A. Imprime 2, 1, 1.
    • total es static, por lo que existe una única variable compartida por todos los objetos de la clase. Cada constructor incrementa esa misma variable, así que termina valiendo 2.
    • valor es una variable de instancia. Cada objeto tiene su propia copia, que se incrementa una vez durante su construcción. Por eso ambos valores son 1.

---

Correcto: B. Imprime [1, 2, 3].
Tu explicación es correcta. La variable numero recibe una copia del valor primitivo de cada elemento del array. Cuando haces numero *= 2, modificas esa variable local, no el elemento original.
Por ejemplo, en la primera iteración ocurre lo siguiente:
    • numeros[0] vale 1.
    • numero recibe una copia de 1.
    • numero *= 2 cambia la variable local a 2.
    • numeros[0] sigue valiendo 1.
Matiz importante: for-each sí permite modificar el array si accedes a sus elementos mediante otra vía, por ejemplo, usando un bucle tradicional con índices. Y si recorres objetos, puedes modificar el estado del objeto a través de la referencia local, aunque reasignar esa referencia tampoco sustituye el elemento del array.
Siguiente paso: evaluación de fundamentos
Has resuelto correctamente los ejercicios de referencias, equals(), static y for-each. No tiene sentido repetirlos ahora.
Vamos a comprobar un concepto de POO que aparece con frecuencia en entrevistas: polimorfismo y despacho dinámico.
Ejercicio 7
¿Qué imprime este código?
class Animal {
    void sonido() {
        System.out.println("Animal");
    }
}

class Perro extends Animal {
    @Override
    void sonido() {
        System.out.println("Perro");
    }
}

Animal animal = new Perro();
animal.sonido();
A. Animal
B. Perro
C. Imprime ambos mensajes.
D. No compila, porque una variable de tipo Animal no puede referenciar un objeto Perro.
Responde con la letra y explica por qué se ejecuta ese método.

B
Correcto: B. Imprime Perro.
La variable animal tiene tipo declarado Animal, pero referencia un objeto cuya clase real es Perro.

Como sonido() es un método de instancia sobrescrito, Java utiliza el despacho dinámico: en tiempo de ejecución se ejecuta la implementación correspondiente a la clase real del objeto. 


---

y se podria hacer esto?

class Animal {
    void sonido() {
        System.out.println("Animal");
    }
}

class Perro extends Animal {
    @Override
    void sonido() {
        System.out.println("Perro");
    }
}

Perro animal = new Perro();
animal.sonido();


si es asi que diferencia habria?


Sí, perfectamente. Este código es válido:
class Animal {
    void sonido() {
        System.out.println("Animal");
    }
}

class Perro extends Animal {
    @Override
    void sonido() {
        System.out.println("Perro");
    }
}

Perro animal = new Perro();
animal.sonido();
Imprime Perro, igual que el ejemplo anterior. La diferencia está en el tipo de la variable y en cómo puedes utilizarla, no en el resultado de la llamada.
1. Declarar la variable como Animal
Animal animal = new Perro();

animal.sonido(); // Perro
La variable tiene tipo declarado Animal, por lo que solo puedes acceder directamente a los métodos y miembros visibles a través de ese tipo.
Sin embargo, gracias al polimorfismo, se ejecuta la implementación de sonido() de Perro.
Esto permite escribir código genérico que trabaje con distintos tipos de animales:
Animal a1 = new Perro();
Animal a2 = new Gato();

a1.sonido(); // Perro
a2.sonido(); // Gato
Siempre que Gato también extienda Animal y sobrescriba sonido().
2. Declarar la variable como Perro
Perro animal = new Perro();

animal.sonido(); // Perro
Ahora la variable tiene tipo declarado Perro. Puedes acceder tanto a los métodos heredados de Animal como a los métodos propios de Perro que sean accesibles.
Por ejemplo:
class Animal {
    void sonido() {
        System.out.println("Animal");
    }
}

class Perro extends Animal {
    @Override
    void sonido() {
        System.out.println("Perro");
    }

    void ladrar() {
        System.out.println("Guau");
    }
}

Perro animal = new Perro();
animal.ladrar(); // Guau
Si declarases la variable como Animal, no podrías llamar directamente a animal.ladrar(), porque ladrar() no está declarado en Animal.
3. ¿Cuál es la diferencia práctica?
Aspecto
Animal animal = new Perro()
Perro animal = new Perro()
Tipo declarado
Animal
Perro
Objeto creado
Perro
Perro
sonido() ejecuta
Perro.sonido()
Perro.sonido()
Acceso directo a ladrar()
No, si solo existe en Perro
Sí
Polimorfismo
Sí
También puede utilizarse polimórficamente
¿Cuándo conviene cada uno?
    • Utiliza Animal cuando quieras programar contra una abstracción y trabajar con diferentes subclases sin depender de una implementación concreta.
    • Utiliza Perro cuando necesites específicamente el comportamiento o los métodos propios de Perro.
La idea clave para una entrevista es que el polimorfismo no exige declarar la variable con el tipo padre, aunque declarar las referencias mediante el tipo abstracto o la interfaz suele facilitar un diseño más flexible.
---


Ejercicio 8 — Sobrecarga frente a sobrescritura
¿Qué imprime este código?
class Ejemplo {
    void mostrar(Object valor) {
        System.out.println("Object");
    }

    void mostrar(String valor) {
        System.out.println("String");
    }
}

Object texto = "Java";

new Ejemplo().mostrar(texto);
A. String
B. Object
C. No compila.
D. Depende del contenido de la cadena.
Responde con la letra y explica qué tiene más peso al elegir la sobrecarga: el tipo declarado de la variable o la clase real del objeto.
B
Correcto: B. Imprime Object.
La clave es que aquí tenemos sobrecarga, no sobrescritura.
Object texto = "Java";
new Ejemplo().mostrar(texto);
Aunque el objeto real sea un String, la variable texto tiene tipo declarado Object. El compilador selecciona la sobrecarga usando los tipos conocidos en tiempo de compilación, por lo que llama a mostrar(Object).
La diferencia que debes recordar para entrevistas es:
    • Sobrecarga (overloading): el compilador selecciona el método según los tipos y argumentos disponibles en tiempo de compilación.
    • Sobrescritura (overriding): para los métodos de instancia sobrescritos, la implementación se determina en tiempo de ejecución según la clase real del objeto.
Ejercicio 9 — equals() y hashCode()
Supón que una clase Usuario sobrescribe equals() para considerar iguales dos usuarios con el mismo identificador, pero no sobrescribe hashCode().
¿Qué problema puede aparecer al guardar esos usuarios en un HashSet?
A. Java no permite compilar una clase que sobrescriba equals() sin sobrescribir hashCode().
B. El HashSet siempre detectará correctamente que ambos usuarios son iguales.
C. Dos usuarios considerados iguales por equals() pueden acabar almacenados como elementos distintos en el HashSet.
D. El HashSet deja de permitir búsquedas.
Responde con la letra y explica brevemente qué contrato deben respetar equals() y hashCode().

C

Vamos a verlo desde cero, porque este concepto es importante para entender las colecciones de Java y suele aparecer en entrevistas.
1. ¿Qué hacen equals() y hashCode()?
Imagina que tienes dos objetos Usuario:
Usuario u1 = new Usuario(42, "Ana");
Usuario u2 = new Usuario(42, "Ana");
Son dos instancias diferentes en memoria. Sin embargo, queremos considerar que representan al mismo usuario porque tienen el mismo identificador: 42.
equals(): ¿son iguales lógicamente?
El método equals() permite definir cuándo dos objetos deben considerarse iguales según las reglas de nuestra clase.
Por ejemplo, si Usuario compara por identificador:
u1.equals(u2); // true
Esto depende de que hayamos sobrescrito correctamente equals().
hashCode(): ¿qué código hash les corresponde?
hashCode() devuelve un número entero que las colecciones basadas en hash utilizan para organizar y localizar objetos con eficiencia.
Por ejemplo, podríamos tener:
u1.hashCode(); // 42
u2.hashCode(); // 42
Los valores concretos dependen de la implementación. Lo importante es la relación entre ambos métodos.
2. La regla fundamental
Java exige respetar este contrato:
Si dos objetos son iguales según equals(), deben devolver el mismo hashCode().
Es decir:
u1.equals(u2) == true
implica que:
u1.hashCode() == u2.hashCode()
Pero atención: que dos objetos tengan el mismo hashCode() no significa necesariamente que sean iguales. Puede haber colisiones.
3. ¿Por qué afecta a HashSet?
Un HashSet es una colección que no permite elementos duplicados según las reglas de igualdad que utiliza.
Simplificando, cuando insertas un objeto:
    1. Utiliza su hashCode() para localizar la zona donde buscar.
    2. Compara mediante equals() con los elementos candidatos.
    3. Si encuentra uno igual, no añade un duplicado.
Si sobrescribes equals() pero dejas el hashCode() original de Object, dos usuarios que consideras iguales podrían devolver códigos hash distintos. Entonces, el HashSet puede no detectar el duplicado.
Por eso es necesario sobrescribir ambos métodos de forma coherente.
4. Ejemplo de implementación
Una forma sencilla de hacerlo en una clase Usuario sería:
@Override
public boolean equals(Object obj) {
    if (this == obj) return true;

    if (!(obj instanceof Usuario otro)) {
        return false;
    }

    return this.id == otro.id;
}

@Override
public int hashCode() {
    return Integer.hashCode(id);
}
En este ejemplo, ambos métodos utilizan el mismo criterio: el identificador id.

Los métodos originales equals() y hashCode() están definidos en la clase Object, que es la raíz de la jerarquía de clases de Java. Si tu clase no los sobrescribe, hereda esas implementaciones.


y cuales son los metodos equals y hashcode originales?
1. Implementación original de equals()
Su firma es:
public boolean equals(Object obj)
La implementación original de Object equivale conceptualmente a:
public boolean equals(Object obj) {
    return this == obj;
}
Es decir, compara la identidad de los objetos, no el contenido de sus atributos.
Por ejemplo:
Usuario u1 = new Usuario(42);
Usuario u2 = new Usuario(42);

System.out.println(u1.equals(u2)); // false
System.out.println(u1.equals(u1)); // true
Aunque u1 y u2 tengan el mismo identificador, son instancias distintas. Como no hemos sobrescrito equals(), devuelve false en el primer caso.
2. Implementación original de hashCode()
Su firma es:
public native int hashCode();
En Object, la implementación es nativa: su funcionamiento interno depende de la JVM. Por tanto, no podemos afirmar que el código fuente original sea literalmente una fórmula Java determinada.
Lo importante es que devuelve un entero que sirve como código hash del objeto.
Por defecto, no está obligado a derivarse de sus atributos. Dos objetos distintos pueden tener el mismo código hash, aunque tampoco tienen por qué tenerlo.
3. ¿Qué sucede si no sobrescribes ninguno?
Situación
Comportamiento heredado de Object
equals()
Compara identidad de referencia.
hashCode()
Devuelve un código hash asociado al objeto, sin garantizar que objetos con los mismos atributos compartan código.
Si sobrescribes equals() para comparar usuarios por su id, debes sobrescribir también hashCode() para que los usuarios iguales tengan el mismo código hash.
Qué debes recordar para la entrevista: Object.equals() compara identidad por defecto; Object.hashCode() proporciona un código hash cuyo valor no debe interpretarse como una identidad única. Si defines igualdad lógica mediante equals(), debes mantener coherente hashCode().

Comprobemos si lo has entendido
Dos objetos Producto tienen el mismo identificador y su método equals() devuelve true.
Sin embargo, sus métodos hashCode() devuelven números diferentes.
¿Qué afirmación es correcta?
A. Es válido: equals() y hashCode() no tienen relación.
B. Se incumple el contrato de Java y pueden fallar las comprobaciones de duplicados en un HashSet.
C. Java lanza automáticamente una excepción al comparar los objetos.
D. El problema solo afecta a los arrays.
Responde con la letra. No necesitas memorizar la implementación del código todavía; lo importante es entender el contrato.
B

Correcto: B. Se incumple el contrato de Java y puede fallar la detección de duplicados en un HashSet.
Ya tienes la idea fundamental: si a.equals(b) devuelve true, ambos objetos deben devolver el mismo hashCode().
No es obligatorio que dos objetos diferentes tengan códigos hash distintos; las colisiones son posibles. Lo que no puede ocurrir es que dos objetos considerados iguales tengan códigos hash diferentes.
Con esto damos por trabajado el contrato de equals() y hashCode(). No hace falta memorizar ahora todos sus detalles internos.
Ejercicio 10 — Clases abstractas e interfaces
Vamos a comprobar otro concepto de POO sin repetir el bloque entero.
¿Qué afirmación es correcta en Java?
A. Una clase puede extender varias clases, pero implementar una sola interfaz.
B. Una clase puede extender una clase e implementar varias interfaces.
C. Una interfaz puede tener constructores para inicializar sus implementaciones.
D. Una clase abstracta no puede tener métodos implementados.
Responde con la letra y una breve explicación. Después terminaremos la evaluación de fundamentos y decidiremos si hace falta reforzar algún punto antes de comenzar formalmente la Fase 2.

B


Correcto: B. Una clase puede extender una clase e implementar varias interfaces.
Por ejemplo:
class Perro extends Animal implements Comparable<Perro>, Serializable {
}
    • extends Animal: hereda de una única clase, porque Java no permite herencia múltiple de clases.
    • implements Comparable<Perro>, Serializable: implementa varias interfaces.
    • Una clase abstracta puede tener métodos implementados y métodos abstractos.
    • Las interfaces no tienen constructores, aunque pueden declarar métodos default, static y, desde Java 9, métodos private.
Este concepto queda comprobado.
Ejercicio 11 — final, referencias y mutabilidad
¿Qué ocurre al ejecutar este código?
final List<String> nombres = new ArrayList<>();

nombres.add("Ana");
nombres.add("Luis");

nombres = new ArrayList<>();
A. Compila porque final solo impide modificar el contenido de la lista.
B. No compila porque no se puede reasignar la referencia nombres.
C. No compila porque una lista final no puede recibir elementos.
D. Compila, pero la lista original se vacía automáticamente.
Responde con la letra y explica la diferencia entre modificar el objeto y reasignar la referencia.

Correcto: B. No compila porque no se puede reasignar la referencia nombres. 

La clave es que final no convierte el objeto en inmutable: impide reasignar la variable, pero permite modificar el objeto al que apunta si su clase lo permite. 


Correcto: B. No compila porque no se puede reasignar la referencia nombres.
La variable está declarada como final, por lo que solo puedes asignarle una referencia una vez.
final List<String> nombres = new ArrayList<>();

nombres.add("Ana");  // Correcto
nombres.add("Luis"); // Correcto

nombres = new ArrayList<>(); // Error de compilación
La clave es que final no convierte el objeto en inmutable: impide reasignar la variable, pero permite modificar el objeto al que apunta si su clase lo permite.
Ejercicio 12 — Excepciones en ejecución
Aunque damos por trabajado el bloque de excepciones, falta comprobar cómo aplicas el concepto en código.
¿Qué imprime este programa?
try {
    System.out.println("A");
    int resultado = 10 / 0;
    System.out.println("B");
} catch (ArithmeticException e) {
    System.out.println("C");
} finally {
    System.out.println("D");
}
A. Imprime A, B, C, D.
B. Imprime A, C, D.
C. Imprime A, C.
D. El programa no compila.
Responde con la letra y explica por qué se ejecutan o no las instrucciones B, C y D.

B






Correcto: B. Imprime A, C, D.
    • A se imprime antes de que ocurra la excepción.
    • B no se imprime porque 10 / 0 lanza una ArithmeticException y la ejecución salta directamente al catch.
    • C se imprime porque el catch captura esa excepción.
    • D se imprime porque finally se ejecuta al abandonar el bloque, incluso cuando se ha producido y capturado una excepción.
La respuesta demuestra que manejas el flujo básico de excepciones. Como decidimos, no vamos a profundizar en cada caso especial.
Evaluación de fundamentos: siguiente ejercicio
Vamos a cerrar con una comprobación breve de arrays, otro punto del itinerario que queríamos verificar antes de avanzar.
Ejercicio 13 — Copia superficial
¿Qué imprime este código?
int[][] original = {
    {1, 2},
    {3, 4}
};

int[][] copia = Arrays.copyOf(original, original.length);

copia[0][0] = 99;

System.out.println(original[0][0]);
A. 1
B. 99
C. Da un error porque Arrays.copyOf no admite matrices.
D. Depende de la implementación de la JVM.
Responde con la letra y explica si Arrays.copyOf ha copiado las filas internas o únicamente las referencias a esas filas.

Correcto: A. 1.
Arrays.copyOf(original, original.length) crea un array externo nuevo, pero copia las referencias a las filas internas, no las propias filas.
Visualmente, antes de modificar:
original ──► array externo A ──► fila 0 [1, 2]
                         └─────► fila 1 [3, 4]

copia ─────► array externo B ──► fila 0 [1, 2]
                         └─────► fila 1 [3, 4]
Los dos arrays externos son distintos, pero sus referencias a las filas apuntan a los mismos objetos. Por eso, al ejecutar copia[0][0] = 99, también cambia lo que vemos desde original[0][0].
Distinción importante:
    • copia[0] = new int[]{7, 8}; sustituye una referencia de copia y no cambia original[0].
    • copia[0][0] = 99; modifica una fila compartida y sí afecta a original.
Esto se llama copia superficial (shallow copy). Una copia profunda tendría que copiar también las filas internas.
Con esto, los fundamentos de arrays, referencias y POO están suficientemente comprobados para seguir avanzando. equals() y hashCode() necesitaron explicación, así que conviene repasarlos más adelante, especialmente al estudiar HashSet y HashMap.
Pasamos a la Fase 2: estructuras de datos y algoritmos. Empezaremos por comprobar la complejidad temporal, sin repetir toda la introducción que ya trabajaste.

---
FASE 2

Lo próximo es estructuras de datos y algoritmos, siguiendo el itinerario que acordamos. Hemos terminado el bloque de arrays básicos de Java: recorridos, modificación de elementos, for-each, referencias, copias y utilidades de Arrays.
Antes de avanzar, una precisión: no vamos a repetir arrays desde cero, pero sí los utilizaremos como base para entender las estructuras de datos siguientes.


Siguiente bloque: estructuras de datos y algoritmos
1. Búsqueda lineal y complejidad temporal
Recorrer un array para encontrar un elemento. Entenderemos qué significa \(O(1)\), \(O(n)\) y cómo analizar el número de operaciones.
Siguiente lección
2. Listas enlazadas
Nodos, referencias, inserción, eliminación y diferencias respecto a los arrays.
3. Pilas y colas
LIFO y FIFO, operaciones principales y aplicaciones prácticas.
4. Conjuntos y mapas
HashSet, HashMap, unicidad, búsqueda por clave y rendimiento.
5. Algoritmos y estructuras avanzadas
Búsqueda binaria, ordenación, recursividad, árboles y análisis de complejidad.
Cómo empezaremos
En la primera lección aprenderás a buscar un número en un array mediante un bucle, analizar cuánto trabajo necesita el algoritmo y distinguir entre el mejor, el peor y el caso promedio cuando corresponda.
Trabajaremos con ejemplos Java, ejercicios de dificultad progresiva y preguntas típicas de entrevistas. No avanzaremos a la siguiente estructura hasta que puedas explicar y aplicar la actual.

Lección 1. Búsqueda lineal y complejidad temporal
El objetivo de esta lección es aprender a analizar un algoritmo, no solamente a escribirlo. En entrevistas técnicas es importante que puedas explicar qué hace un algoritmo, cuántas operaciones necesita y cómo cambia su rendimiento cuando crece la cantidad de datos.
1. ¿Qué es la búsqueda lineal?
La búsqueda lineal (linear search) consiste en recorrer una colección de elementos, uno por uno, hasta encontrar el elemento buscado o comprobar que no existe.
Por ejemplo, queremos encontrar el número 30 en este array:
10
índice 0
20
índice 1
30
índice 2
40
índice 3
50
índice 4
El algoritmo empieza por el índice 0 y avanza hasta encontrar el valor buscado.
El proceso es:
    1. Compara 10 con 30: no coincide.
    2. Compara 20 con 30: no coincide.
    3. Compara 30 con 30: coincide, por lo que termina.
Ha realizado 3 comparaciones.
2. Implementación en Java
Observa esta implementación:
public static int buscar(int[] numeros, int objetivo) {
    for (int i = 0; i < numeros.length; i++) {
        if (numeros[i] == objetivo) {
            return i;
        }
    }

    return -1;
}
Podemos probarla así:
int[] numeros = {10, 20, 30, 40, 50};

System.out.println(buscar(numeros, 30)); // 2
System.out.println(buscar(numeros, 50)); // 4
System.out.println(buscar(numeros, 99)); // -1
Hay tres detalles importantes:
    • numeros[i] == objetivo compara el elemento actual con el valor buscado.
    • return i devuelve el índice en cuanto encuentra el elemento. No necesita seguir recorriendo el array.
    • return -1 indica que el elemento no se ha encontrado después de recorrer todo el array. Es una convención elegida para este método, no un comportamiento especial de Java.
¿Por qué devuelve el índice y no el valor? Porque el objetivo es localizar la posición del elemento. El valor buscado ya lo conocemos.
3. ¿Qué es la complejidad temporal?
La complejidad temporal describe cómo crece el trabajo que realiza un algoritmo a medida que aumenta el tamaño de la entrada.
Para expresarla, usamos habitualmente la notación Big O, como \(O(1)\) y \(O(n)\).
Aquí, \(n\) representa el número de elementos del array.
No significa necesariamente cuánto tarda el programa en segundos. Describe cómo crece el número de operaciones relevantes al aumentar los datos, ignorando constantes y términos menos significativos.
Los tres casos de la búsqueda lineal
Supongamos que tenemos un array de 1.000 elementos.
Mejor caso
\(O(1)\)
El elemento está en la primera posición. Se realiza una comparación.
Peor caso
\(O(n)\)
El elemento está en la última posición o no existe. Se realizan hasta 1.000 comparaciones.
Caso promedio
\(O(n)\)
Si el elemento buscado tiene la misma probabilidad de estar en cualquiera de las posiciones y siempre existe, se realizan en promedio unas 500,5 comparaciones para 1.000 elementos. El crecimiento sigue siendo lineal.
El caso promedio depende de los supuestos sobre la entrada. Si el elemento puede no existir, también hay que considerar esa posibilidad al calcular el promedio.
¿Cómo crece el trabajo?
Elementos (\(n\))
Mejor caso
Peor caso
10
1 comparación
10 comparaciones
100
1 comparación
100 comparaciones
1.000
1 comparación
1.000 comparaciones
1.000.000
1 comparación
1.000.000 comparaciones
El mejor caso es constante porque encontrar el primer elemento requiere una comparación, independientemente del tamaño del array. El peor caso es lineal porque puede ser necesario examinar todos los elementos.
4. Tu primer ejercicio
No te doy la solución todavía. Analiza este código como si te lo preguntaran en una entrevista técnica:
public static int buscar(int[] numeros, int objetivo) {
    int comparaciones = 0;

    for (int i = 0; i < numeros.length; i++) {
        comparaciones++;

        if (numeros[i] == objetivo) {
            System.out.println("Comparaciones: " + comparaciones);
            return i;
        }
    }

    System.out.println("Comparaciones: " + comparaciones);
    return -1;
}
Se ejecuta con:
int[] numeros = {8, 3, 15, 6, 12};

System.out.println(buscar(numeros, 6));
Responde sin ejecutar el código.
1. ¿Qué índice devuelve el método?
0
2
3
-1
2. ¿Cuántas comparaciones realiza?
3
4
5
3. ¿Cuál es su complejidad temporal en el peor caso?
\(O(1)\)
\(O(n)\)
\(O(n^2)\)
4. Explica brevemente por qué termina en esa posición y por qué la complejidad es la que has elegido.
Corregir respuestas
Cuando respondas, revisaremos cada apartado. Después pasaremos a analizar el número de operaciones con más precisión y a distinguir la complejidad temporal de la espacial.

Mis respuestas al ejercicio de búsqueda lineal:
1. Índice devuelto: 3
2. Número de comparaciones: 4
3. Complejidad en el peor caso: O(n)
4. Explicación: termina en la posicion 3 de el array porque es el que contienen el valor objetivo 6

he elegido esa complejidad pero sigo sin entener bien como fucniona lo de:


Mejor caso
\(O(1)\)

El elemento está en la primera posición. Se realiza una comparación.

Peor caso
\(O(n)\)

El elemento está en la última posición o no existe. Se realizan hasta 1.000 comparaciones.

Caso promedio
\(O(n)\)

Si el elemento buscado tiene la misma probabilidad de estar en cualquiera de las posiciones y siempre existe, se realizan en promedio unas 500,5 comparaciones para 1.000 elementos. El crecimiento sigue siendo lineal.


Tus tres respuestas son correctas. En el ejercicio, el método devuelve el índice 3, realiza 4 comparaciones y su complejidad en el peor caso es \(O(n)\).
Lo que necesitas reforzar es por qué hablamos de \(O(1)\) o \(O(n)\), y qué significan realmente el mejor caso, el peor caso y el caso promedio. Vamos a verlo desde cero, porque es un concepto fundamental para analizar algoritmos en entrevistas técnicas.
1. Primero, olvida las fórmulas por un momento
Imagina que tienes un array de 5 números:
int[] numeros = {8, 3, 15, 6, 12};
Quieres encontrar el número 6. Para encontrarlo, tienes que revisar los elementos desde el principio:
Búsqueda del número 6
8
Índice 0
3
Índice 1
15
Índice 2
6
Encontrado
12
Índice 4
Comparaciones realizadas: 
4
Has comparado 8, 3, 15 y 6. Como el número buscado está en el índice 3, el algoritmo termina después de la cuarta comparación.
Pero ¿qué pasaría si el array fuera diferente? Aquí está la clave: el trabajo que necesita el algoritmo depende de dónde esté el elemento buscado y de cuántos elementos haya.
2. El mejor caso: \(O(1)\)
Supongamos que buscas el número 8, que está en la primera posición.
int[] numeros = {8, 3, 15, 6, 12};
El algoritmo hace esto:
    1. Compara 8 con 8.
    2. Lo encuentra y termina.
Solo necesita una comparación.
Ahora imagina que el array tiene 5 elementos, 100 elementos o un millón de elementos. Si el objetivo sigue estando en la primera posición, la búsqueda necesita una sola comparación.
Eso es lo que significa \(O(1)\): el trabajo no crece con el tamaño de la entrada en este caso.
No significa que el programa tarde exactamente un segundo, ni que todos los algoritmos \(O(1)\) tarden lo mismo. Significa que la cantidad de trabajo relevante se mantiene constante respecto a \(n\).
3. El peor caso: \(O(n)\)
Ahora busca el número 12, que está en la última posición.
El algoritmo debe comprobar:
8 → 3 → 15 → 6 → 12
Necesita 5 comparaciones.
¿Y si el array tiene 100 elementos y el número buscado está al final? Necesitará 100 comparaciones.
¿Y si tiene un millón de elementos y el objetivo está al final, o ni siquiera existe? En el peor caso tendrá que examinar el millón de elementos.
Eso es \(O(n)\): el trabajo crece proporcionalmente al número de elementos.
Cómo crece el trabajo en el peor caso
Cada elemento adicional puede exigir una comparación más.
5 elementos
5
10 elementos
10
25 elementos
25
50 elementos
50
La longitud del array se multiplica por 10 y el trabajo del peor caso también se multiplica por 10. Por eso la búsqueda lineal tiene complejidad lineal.
4. El caso promedio: también \(O(n)\)
Este suele ser el más confuso.
Imagina que tienes un array de 1.000 elementos y el número buscado siempre existe. Además, suponemos que tiene la misma probabilidad de estar en cualquiera de las posiciones.
    • Si está en la posición 0, necesitas 1 comparación.
    • Si está en la posición 1, necesitas 2.
    • Si está en la posición 2, necesitas 3.
    • ...
    • Si está en la posición 999, necesitas 1.000.
Para calcular el promedio, sumamos las comparaciones posibles y dividimos entre el número de posiciones:
\[ \frac{1+2+3+\cdots+1000}{1000}=500{,}5 \]
Por tanto, en promedio, necesitamos 500,5 comparaciones.
¿Por qué sigue siendo \(O(n)\)? Porque, si multiplicamos el número de elementos por 10, el promedio también se multiplica aproximadamente por 10. Sigue creciendo de forma proporcional.
Importante: el caso promedio depende de las condiciones. Ese promedio supone que el elemento existe y todas las posiciones son igual de probables. Si también puede no existir, hay que incluir esa posibilidad en el cálculo.
5. La diferencia que debes recordar
\(O(1)\)
Constante
El tamaño del array no cambia el número de comparaciones del mejor caso: siempre es una.
\(O(n)\)
Lineal
Cuantos más elementos haya, más comparaciones puede necesitar el algoritmo. En la búsqueda lineal, el peor caso examina todos los elementos.
Como referencia visual, esta gráfica compara cómo crecen varias complejidades habituales. Para nuestra búsqueda, las dos relevantes son \(O(1)\) y \(O(n)\).
O(1)
O(log n)
O(n)
O(n log n)
O(n²)
O(2ⁿ)
10203040506050100150200Input size nOps
\(n=16:\quad (1,\log_2n,n)=(1,4,16)\)
\((n\log_2n,n^2)=(64,256)\)
\(2^n=65.536\)
\(n\)
48163264
Enviar comentarios
6. Comprueba si lo has entendido
Todavía no pasaremos a otra estructura de datos. Primero quiero comprobar que distingues los tres casos.
Tenemos este método de búsqueda lineal y un array de 100 elementos:
int[] numeros = new int[100];
Supón que el array contiene valores y que el método busca un objetivo mediante un recorrido desde el índice 0.
A. El objetivo está en la primera posición.
1 comparación; caso mejor
100 comparaciones; caso peor
B. El objetivo está en la última posición.
1 comparación; caso mejor
100 comparaciones; caso peor
C. El objetivo existe y tiene la misma probabilidad de estar en cualquiera de las 100 posiciones. ¿Cuál es el promedio de comparaciones?
1
50,5
100
D. Explícalo con tus palabras: ¿por qué el mejor caso es \(O(1)\), mientras que el peor y el promedio son \(O(n)\)?
porque el O1 constante no cambia dependeindo de el tamaño de la estructura de datos y en cambio el On es lineal ya sea el peor caso o un caso promedio, cuanto mas grande es la estructura de datos mas comparaciones hay que hacer
Enviar respuestas
No hace falta memorizar las notaciones sin entenderlas. Lo importante es que puedas razonar qué hace el algoritmo cuando el array pasa de 100 elementos a 1.000 o a un millón.


Mis respuestas sobre complejidad de búsqueda lineal:
A: 1
B: 100
C: 50.5
D: porque el O1 constante no cambia dependeindo de el tamaño de la estructura de datos y en cambio el On es lineal ya sea el peor caso o un caso promedio, cuanto mas grande es la estructura de datos mas comparaciones hay que hacer


Las cuatro respuestas son correctas. Has entendido la idea fundamental de la complejidad temporal. Antes de avanzar, voy a precisar un matiz de tu explicación para que puedas expresarlo bien en una entrevista técnica.
1. Corrección de tus respuestas
Apartado
Resultado
Evaluación
A. Objetivo en la primera posición
1 comparación
Correcto
B. Objetivo en la última posición
100 comparaciones
Correcto
C. Promedio para 100 posiciones equiprobables
50,5 comparaciones
Correcto
D. Explicación de \(O(1)\) y \(O(n)\)
Constante frente a lineal
Correcto
El matiz importante
Has dicho que, cuanto más grande es la estructura de datos, más comparaciones hay que hacer. Eso describe correctamente el peor caso de la búsqueda lineal, pero no siempre ocurre en cada ejecución.
Por ejemplo, aunque un array tenga un millón de elementos, si buscas el que está en la primera posición, solo necesitas una comparación.
La formulación precisa sería:
    • Mejor caso: el trabajo permanece constante, independientemente del tamaño del array.
    • Peor caso: el trabajo crece linealmente con el número de elementos.
    • Caso promedio: bajo el supuesto de que el objetivo existe y todas las posiciones son igualmente probables, el trabajo también crece linealmente.
2. Una respuesta válida para una entrevista
Podrías explicarlo así:
La búsqueda lineal tiene una complejidad temporal de O(1) en el mejor caso, porque el elemento puede encontrarse en la primera posición y solo necesitamos una comparación. En el peor caso tiene complejidad O(n), porque debemos recorrer todos los elementos si el objetivo está al final o no existe. Bajo una distribución uniforme de las posiciones y suponiendo que el elemento existe, el caso promedio también es O(n), porque el número de comparaciones crece proporcionalmente al tamaño del array.
No necesitas memorizar este texto literalmente. Lo importante es que puedas razonar cada afirmación.
3. Siguiente paso: calcular la complejidad de un algoritmo
Ahora vamos a comprobar si puedes aplicar el concepto a código, porque saber identificar \(O(1)\) y \(O(n)\) en una búsqueda es solo el primer paso.
Considera este método:
public static void mostrarNumeros(int[] numeros) {
    for (int i = 0; i < numeros.length; i++) {
        System.out.println(numeros[i]);
    }
}
Contesta estas tres preguntas:
    1. Si el array tiene 10 elementos, ¿cuántas veces se ejecuta System.out.println?
    2. Si tiene 1.000 elementos, ¿cuántas veces se ejecuta?
    3. ¿Cuál es la complejidad temporal del método: \(O(1)\) u \(O(n)\)? Explica por qué.
Después estudiaremos un caso distinto: dos bucles anidados, donde veremos por qué algunos algoritmos tienen complejidad \(O(n^2)\).

se ejecuta 10 veces

si tiene 1000 se ejecuta 1000 veces 

la complejidad temporal crece de forma lineal On


Correcto. Las tres respuestas son correctas.
    • 10 elementos: System.out.println se ejecuta 10 veces.
    • 1.000 elementos: se ejecuta 1.000 veces.
    • Complejidad temporal: \(O(n)\), porque el número de ejecuciones crece proporcionalmente al número de elementos.
Has identificado correctamente un algoritmo lineal. Ahora vamos a introducir una diferencia importante: un algoritmo puede tener un bucle y ser \(O(n)\), o tener dos bucles anidados y ser \(O(n^2)\).
Lección 1.2. Bucles anidados y complejidad \(O(n^2)\)
Considera este código Java:
public static void mostrarPares(int[] numeros) {
    for (int i = 0; i < numeros.length; i++) {
        for (int j = 0; j < numeros.length; j++) {
            System.out.println(numeros[i] + ", " + numeros[j]);
        }
    }
}
Tenemos dos bucles:
    • El bucle exterior recorre todos los elementos.
    • Por cada iteración del exterior, el bucle interior vuelve a recorrer todos los elementos.
1. ¿Cuántas veces se ejecuta la instrucción?
Si el array contiene 3 elementos, el funcionamiento es el siguiente:
Array: [10, 20, 30]
Cada fila representa una iteración del bucle exterior; dentro se ejecuta el bucle interior completo.
i: 10
10, 10
10, 20
10, 30
i: 20
20, 10
20, 20
20, 30
i: 30
30, 10
30, 20
30, 30
Total de ejecuciones
9
El bucle exterior se ejecuta 3 veces y, por cada una de ellas, el interior se ejecuta 3 veces:
\[ 3 \times 3 = 9 \]
Si el array tuviera 10 elementos, serían \(10 \times 10 = 100\) ejecuciones. Con 1.000 elementos, serían \(1.000 \times 1.000 = 1.000.000\).
Por eso, la complejidad temporal es:
\[ O(n^2) \]
2. Compáralo con los otros casos
Elementos \(n\)
Un bucle \(O(n)\)
Dos bucles anidados \(O(n^2)\)
10
10
100
100
100
10.000
1.000
1.000
1.000.000
La diferencia es importante: si multiplicas por 10 el tamaño de la entrada, el trabajo lineal se multiplica por 10, mientras que el cuadrático se multiplica por 100.
3. Tu turno
Sin ejecutar el código, analiza este método:
public static void procesar(int[] numeros) {
    for (int i = 0; i < numeros.length; i++) {
        System.out.println(numeros[i]);
    }

    for (int j = 0; j < numeros.length; j++) {
        System.out.println(numeros[j]);
    }
}
Responde:
    1. Si el array tiene 5 elementos, ¿cuántas veces se ejecuta System.out.println en total?
    2. ¿La complejidad es \(O(n)\) u \(O(n^2)\)?
    3. ¿Por qué tener dos bucles no implica necesariamente una complejidad \(O(n^2)\)?
No avances por intuición solamente: fíjate en si un bucle se ejecuta dentro del otro o si se ejecutan por separado.


10

la complejidad es =On


Las dos respuestas son correctas. Falta responder a la tercera pregunta, que es la más importante para entender la diferencia.
Corrección
1. Número de ejecuciones: 10.
Con 5 elementos, el primer bucle imprime 5 veces y el segundo imprime otras 5:
\[ 5+5=10 \]
2. Complejidad temporal: \(O(n)\). Correcto.
3. ¿Por qué no es \(O(n^2)\)?
Porque los bucles se ejecutan uno después del otro, no están anidados. Cada uno recorre el array completo, por lo que el trabajo total es \(n+n=2n\).
En notación Big O, ignoramos las constantes, así que \(O(2n)=O(n)\).
En cambio, con bucles anidados, el trabajo sería \(n \times n=n^2\), por lo que la complejidad sería \(O(n^2)\).
---

2.2. Búsquedas — Ejercicio 1
Tenemos este array:
int[] numeros = {4, 8, 15, 16, 23, 42};
Queremos comprobar si el número 23 está presente.
¿Cuál de estas afirmaciones sobre la búsqueda binaria es correcta?
    • A. Funciona con cualquier array, esté ordenado o no.
    • B. Necesita que los elementos estén ordenados según el criterio de búsqueda.
    • C. Siempre es más rápida que la búsqueda lineal, independientemente del tamaño del array.
    • D. Tiene una complejidad temporal de \(O(n)\) en el caso promedio.
Responde con la letra y justifica brevemente tu elección. Después avanzaremos según lo que demuestres saber, sin repasar innecesariamente lo que ya dominas.

B

Correcto: B. La búsqueda binaria necesita que los elementos estén ordenados según el criterio de búsqueda.
Funciona descartando aproximadamente la mitad de los elementos en cada paso. Por eso su complejidad temporal habitual es \(O(\log n)\), frente a \(O(n)\) de la búsqueda lineal en el peor caso.
Un matiz importante: aunque la búsqueda binaria sea asintóticamente más eficiente para colecciones grandes, no siempre compensa ordenar una colección si solo necesitas realizar una búsqueda.
Ejercicio 2 — Ejecutar una búsqueda binaria
Tenemos este array ordenado:
int[] numeros = {2, 5, 8, 12, 16, 23, 38};
Buscamos el valor 16. En la implementación habitual, calculamos el índice central así:
int medio = (izquierda + derecha) / 2;
Inicialmente, izquierda = 0 y derecha = 6.
¿Qué índice se comprueba primero y qué ocurre después?
A. Índice 3; como contiene 12, continuamos por la mitad derecha.
B. Índice 3; como contiene 12, continuamos por la mitad izquierda.
C. Índice 4; encontramos directamente el 16.
D. Índice 6; empezamos por el último elemento.
Responde con la letra y explica el siguiente paso de la búsqueda.

B


Correcto: A.
El índice central es:
\[ medio = \frac{0+6}{2}=3 \]
En el índice 3 encontramos el valor 12.
Como \(16 > 12\), descartamos la mitad izquierda y el elemento central. Continuamos buscando en los índices del 4 al 6.
El siguiente cálculo será:
\[ medio = \frac{4+6}{2}=5 \]
En el índice 5 está el valor 23. Como \(16 < 23\), continuamos por la mitad izquierda de ese intervalo y llegamos al índice 4, donde encontramos el 16.
Matiz: la búsqueda binaria no compara necesariamente con todos los elementos; reduce el intervalo en cada iteración.
Ejercicio 3 — Casos límite
Tenemos esta implementación:
public static int buscar(int[] numeros, int objetivo) {
    int izquierda = 0;
    int derecha = numeros.length - 1;

    while (izquierda <= derecha) {
        int medio = (izquierda + derecha) / 2;

        if (numeros[medio] == objetivo) {
            return medio;
        } else if (numeros[medio] < objetivo) {
            izquierda = medio + 1;
        } else {
            derecha = medio - 1;
        }
    }

    return -1;
}
¿Qué devuelve buscar(new int[]{2, 4, 6, 8}, 5)?
    • A. 0
    • B. -1
    • C. 2
    • D. Lanza una excepción porque 5 no está en el array.
Responde con la letra y explica por qué termina la búsqueda.

B

Correcto: B. Devuelve -1, que indica que el elemento no se encuentra. 


Ejercicio 4 — Elegir el algoritmo adecuado
Tienes un array de un millón de números y necesitas buscar un único valor. El array inicialmente no está ordenado.
¿Qué opción suele ser más razonable si solo necesitas hacer esa búsqueda una vez?
    • A. Ordenar el array y después usar búsqueda binaria, siempre.
    • B. Usar búsqueda lineal, porque evita el coste de ordenar.
    • C. Usar búsqueda binaria directamente, aunque el array esté desordenado.
    • D. Ninguna búsqueda puede utilizarse si el array no está ordenado.
Responde con la letra y justifica tu decisión teniendo en cuenta el coste total de la operación.
B

usar búsqueda lineal. Tu opción A puede ser correcta en otros escenarios, pero no suele ser la más eficiente cuando solo necesitas realizar una búsqueda.
La clave está en considerar el coste total.
Operación
Complejidad temporal
Buscar linealmente
\(O(n)\)
Ordenar el array
Habitualmente \(O(n\log n)\)
Buscar después con búsqueda binaria
\(O(\log n)\)
Si ordenas un millón de elementos para buscar un único valor, el coste de ordenar suele ser mucho mayor que recorrer el array una vez.
En cambio, si vas a realizar miles de búsquedas sobre el mismo array, ordenarlo una vez y utilizar búsqueda binaria repetidamente puede ser más eficiente.
La decisión depende del número de búsquedas y de si necesitas conservar el orden original.
Ejercicio 5 — Consolidación de búsquedas
Tienes un array ordenado de un millón de elementos y vas a realizar 1.000 búsquedas diferentes.
¿Qué opción es generalmente más eficiente?
    • A. Recorrer el array completo en cada búsqueda mediante búsqueda lineal.
    • B. Utilizar búsqueda binaria para cada búsqueda.
    • C. Volver a ordenar el array antes de cada búsqueda y después usar búsqueda binaria.
    • D. Ambas búsquedas tienen la misma complejidad.
Responde con la letra y explica por qué.

B binaria porque al ya estar ordenado es mas eficiente y mas si vamos a buscar varias veces aunque en este caso tambien seria mas eficiente usar busqueda binaria aunque estuviese desordenado porque se van a hacer luego 1000 busquedas

Correcto: B. Utilizar búsqueda binaria para cada búsqueda.
Tu razonamiento es correcto: el array ya está ordenado y vas a realizar muchas búsquedas, por lo que puedes aprovechar ese orden sin volver a ordenar los datos.
Hay un matiz en tu explicación: no puedes aplicar directamente la búsqueda binaria a un array desordenado. Primero tendrías que ordenarlo.
Comparemos el coste de las 1.000 búsquedas, siendo \(n\) el número de elementos:
    • Búsqueda lineal: \(O(1000n)=O(n)\), porque 1.000 es una constante.
    • Búsqueda binaria: \(O(1000\log n)=O(\log n)\), por el mismo motivo.
En ambos casos el número de búsquedas es fijo, pero la búsqueda binaria realiza muchas menos comparaciones para un array grande.
2.2. Búsquedas: evaluación
Has demostrado que entiendes los conceptos principales:
    • La búsqueda binaria requiere datos ordenados.
    • Reduce el intervalo en cada iteración.
    • Puede devolver -1 cuando no encuentra el elemento, si así lo define el método.
    • Elegir entre búsqueda lineal y binaria depende del coste de preparación y del número de búsquedas.
Podemos dar por trabajados los fundamentos de búsqueda lineal y binaria. Queda practicar más adelante la implementación y sus casos límite.

Ejercicio 2 — Acceso e inserción
Tenemos un ArrayList con 1.000 elementos:
ArrayList<Integer> numeros = new ArrayList<>();
¿Qué operación suele tener un coste temporal \(O(1)\) en un ArrayList?
    • A. Insertar un elemento al principio.
    • B. Acceder al elemento situado en el índice 500 mediante get(500).
    • C. Buscar un valor sin conocer su índice.
    • D. Eliminar el elemento situado en el índice 500.
Responde con la letra y justifica tu elección.
B

correcto

Correcto: B. Acceder al elemento mediante get(500) tiene un coste \(O(1)\), suponiendo un ArrayList convencional de Java.
ArrayList utiliza internamente un array para almacenar sus elementos. Por eso puede calcular directamente dónde está el elemento solicitado mediante su índice, sin recorrer los anteriores.
Veamos las cuatro opciones:
Operación
Complejidad habitual
A. Insertar al principio
\(O(n)\)
B. Acceder mediante get(500)
\(O(1)\)
C. Buscar un valor por su contenido
\(O(n)\)
D. Eliminar el índice 500
\(O(n)\)
¿Por qué las opciones A y D son \(O(n)\)? Porque hay que desplazar los elementos posteriores para mantenerlos contiguos. En el peor caso, ese desplazamiento afecta a una cantidad de elementos proporcional a \(n\).
Un matiz: añadir al final con add() tiene un coste amortizado \(O(1)\), aunque ocasionalmente puede requerir crear un array interno más grande y copiar los elementos.
Ejercicio 3 — Array dinámico frente a lista enlazada
Ahora comparamos ArrayList con una lista simplemente enlazada.
En una lista enlazada, cada nodo contiene un valor y una referencia al siguiente nodo.
ArrayList
10
20
30
40
Elementos almacenados en posiciones consecutivas del array interno.
Lista simplemente enlazada
10
20
30
40
Cada nodo guarda una referencia al siguiente.
Pregunta: si ya tienes una referencia al primer nodo de una lista simplemente enlazada y quieres acceder al elemento número 500, ¿cuál es la afirmación correcta?
    • A. El acceso cuesta \(O(1)\), igual que en un ArrayList.
    • B. El acceso cuesta \(O(\log n)\), porque la lista está enlazada.
    • C. El acceso cuesta \(O(n)\), porque hay que recorrer los nodos anteriores.
    • D. No es posible acceder a un elemento concreto de una lista enlazada.
Responde con la letra y explica el motivo.
C

Correcto: C. El acceso cuesta \(O(n)\) en el peor caso.
En una lista simplemente enlazada, cada nodo conoce la referencia al siguiente, pero no tiene acceso directo al nodo número 500.
Para llegar hasta él, hay que seguir las referencias sucesivamente:
Nodo actual = primero;

for (int i = 0; i < 500; i++) {
    actual = actual.siguiente;
}
Si el elemento está al final de una lista de \(n\) nodos, podrías tener que recorrer casi todos ellos. Por eso el coste es \(O(n)\).

Siguiente apartado: 2.3. Estructuras secuenciales
Empezaremos por distinguir un array tradicional de un array dinámico, antes de entrar en listas enlazadas.
Ejercicio 1
En Java, ¿cuál es la diferencia principal entre un array tradicional y un ArrayList?
    • A. Un array puede almacenar primitivos, pero un ArrayList no puede almacenar ningún tipo de dato primitivo ni sus valores.
    • B. El tamaño de un array tradicional es fijo una vez creado, mientras que un ArrayList puede crecer o reducir su tamaño.
    • C. Un ArrayList permite acceder a los elementos por índice, pero un array no.
    • D. Ambos tienen un tamaño fijo una vez creados.
Responde con la letra y explica brevemente tu elección.

B

Correcto: B. El tamaño de un array tradicional es fijo una vez creado, mientras que un ArrayList puede crecer o reducir su tamaño.
Por ejemplo:
int[] numeros = new int[3];
// Siempre tiene 3 posiciones.

ArrayList<Integer> lista = new ArrayList<>();
lista.add(10);
lista.add(20);
lista.add(30);
lista.add(40);
// Puede crecer dinámicamente.
Hay dos matices importantes:
    • Array: su longitud queda fijada al crearlo. Puedes modificar sus elementos, pero no cambiar su longitud.
    • ArrayList: su tamaño lógico cambia con operaciones como add() y remove(). Internamente utiliza un array que puede sustituir por otro de mayor capacidad cuando lo necesita.
Además, un array puede almacenar directamente tipos primitivos como int, mientras que ArrayList utiliza tipos de referencia, por lo que para almacenar enteros usamos Integer.
Ejercicio 2 — Acceso por índice
¿Cuál es la complejidad temporal habitual de acceder al elemento de un array o un ArrayList mediante un índice conocido?
Por ejemplo:
int valor = numeros[500];
o
Integer valor = lista.get(500);
    • A. \(O(1)\)
    • B. \(O(\log n)\)
    • C. \(O(n)\)
    • D. \(O(n^2)\)
Responde con la letra y explica por qué.
A

Correcto: A. \(O(1)\), complejidad constante.
Tanto numeros[500] como lista.get(500) permiten acceder directamente a una posición conocida, sin recorrer previamente los elementos anteriores.
En un ArrayList, aunque internamente pueda necesitar redimensionar su array al insertar elementos, eso no afecta a la complejidad habitual de una operación de lectura por índice: es \(O(1)\).
Ejercicio 3 — Inserción en un ArrayList
Tenemos esta lista:
ArrayList<Integer> numeros = new ArrayList<>();

numeros.add(10);
numeros.add(20);
numeros.add(30);
numeros.add(40);

numeros.add(1, 15);
La última instrucción inserta 15 en el índice 1, desplazando los elementos posteriores.
¿Cuál es la complejidad temporal de insertar un elemento en una posición intermedia de un ArrayList, en el caso habitual?
    • A. \(O(1)\)
    • B. \(O(\log n)\)
    • C. \(O(n)\)
    • D. \(O(n^2)\)
Responde con la letra y explica qué ocurre con los elementos que ya estaban en la lista.
C

Correcto: C. \(O(n)\).
Al insertar 15 en el índice 1, el ArrayList tiene que desplazar los elementos posteriores una posición hacia la derecha para dejar espacio.
Antes:
Índice:    0   1   2   3
          [10, 20, 30, 40]
Después de numeros.add(1, 15):
Índice:    0   1   2   3   4
          [10, 15, 20, 30, 40]
En el peor caso, insertar al principio requiere desplazar prácticamente todos los elementos. Por eso el coste es \(O(n)\).
Matiz importante: añadir al final mediante add(elemento) tiene un coste amortizado de \(O(1)\), aunque alguna inserción puede requerir redimensionar el array interno y copiar sus elementos.
Ejercicio 4 — Eliminar un elemento
Tenemos un ArrayList con un millón de elementos y ejecutamos:
numeros.remove(0);
¿Qué complejidad temporal tiene esta operación en el caso habitual?
    • A. \(O(1)\), porque solo elimina el primer elemento.
    • B. \(O(\log n)\), porque busca el índice mediante una búsqueda binaria.
    • C. \(O(n)\), porque debe desplazar los elementos restantes.
    • D. \(O(n^2)\), porque recorre la lista varias veces.
Responde con la letra y explica qué ocurre con los elementos que quedan después del primero.
C

Correcto: C. \(O(n)\).
Cuando ejecutas numeros.remove(0), eliminas el elemento situado en el índice 0. Como un ArrayList utiliza un array internamente, los elementos restantes deben desplazarse una posición hacia la izquierda para ocupar el hueco.
Antes:
[10, 20, 30, 40, 50]
Después de numeros.remove(0):
[20, 30, 40, 50]
En el peor caso, hay que desplazar \(n-1\) elementos. Por eso el coste es \(O(n)\).
Una precisión de Java: remove(0) elimina el elemento del índice 0, no el elemento cuyo valor sea 0.
Ejercicio 5 — Cuándo elegir una lista enlazada
Ahora comparamos ArrayList con una lista doblemente enlazada, como LinkedList de Java.
Supongamos que ya tenemos una referencia al nodo que queremos eliminar de una lista doblemente enlazada y que no necesitamos buscarlo.
¿Cuál es la complejidad temporal de eliminar ese nodo, en condiciones habituales?
    • A. \(O(1)\), porque basta con actualizar las referencias de los nodos vecinos.
    • B. \(O(\log n)\), porque hay que localizar la posición.
    • C. \(O(n)\), porque siempre hay que desplazar todos los elementos.
    • D. \(O(n^2)\), porque hay que reconstruir la lista.
Responde con la letra y explica qué diferencia hay respecto a eliminar el primer elemento de un ArrayList.
Correcto: A. \(O(1)\), siempre que ya tengamos localizada la referencia al nodo que queremos eliminar.
En una lista doblemente enlazada, cada nodo mantiene referencias al anterior y al siguiente. Para eliminarlo, basta con actualizar las referencias de sus vecinos.
Por ejemplo, antes de eliminar el nodo 30:
10 ⇄ 20 ⇄ 30 ⇄ 40 ⇄ 50
Después:
10 ⇄ 20 ⇄ 40 ⇄ 50
No necesitamos desplazar los elementos restantes ni recorrer toda la lista.
La diferencia con ArrayList es:
    • ArrayList: al eliminar un elemento intermedio, desplaza los elementos posteriores; coste \(O(n)\).
    • Lista doblemente enlazada: si ya tenemos el nodo, actualizamos unas pocas referencias; coste \(O(1)\).
Matiz importante para Java: LinkedList.remove(objeto) puede necesitar recorrer la lista para localizar el objeto, por lo que esa operación tiene coste \(O(n)\) en general. El coste \(O(1)\) corresponde a la eliminación cuando el nodo ya está localizado.
Juan, vamos a distinguir estos conceptos desde el punto de vista de Java, porque son fundamentales para las entrevistas técnicas y para comprender las estructuras de datos.

Hay que separar dos cosas:

- Array, `ArrayList` y `LinkedList`: son formas diferentes de almacenar y organizar una colección de elementos.
# 1. Array vs. ArrayList vs. LinkedList

## 1.1. Array (`array`)

Un array es una estructura de datos que almacena un número fijo de elementos de un mismo tipo. En Java, su tamaño queda establecido cuando se crea.

```
int[] numeros = new int[5];

numeros[0] = 10;
numeros[1] = 20;
numeros[2] = 30;

System.out.println(numeros[0]); // 10
System.out.println(numeros.length); // 5
```

Visualmente, podemos imaginarlo como una secuencia de posiciones:

## 10

Índice 0

## 20

Índice 1

## 30

Índice 2

## 0

Índice 3

## 0

Índice 4

Los cinco elementos tienen posiciones identificadas por índices. Los int no inicializados explícitamente valen 0.

### Características principales

- Tamaño fijo: si creas un array de cinco posiciones, no puedes convertirlo en uno de seis posiciones. Puedes crear otro array y copiar los datos.
- Acceso por índice: puedes acceder directamente a `numeros[3]`.
- Tipo definido: `int[]` almacena enteros primitivos; `String[]`, referencias a cadenas, etc.
- Rendimiento: acceder a un elemento por índice cuesta \\(O(1)\\), es decir, tiempo constante.

Su principal ventaja es su simplicidad y eficiencia. Su principal limitación es que no puede crecer o reducirse dinámicamente.

## 1.2. `ArrayList`

`ArrayList` es una implementación de la interfaz `List` de Java Collections Framework. Internamente utiliza un array que puede ampliar cuando necesita más capacidad.

```
import java.util.ArrayList;

ArrayList<Integer> numeros = new ArrayList<>();

numeros.add(10);
numeros.add(20);
numeros.add(30);

numeros.add(40); // Puede crecer dinámicamente

System.out.println(numeros.get(0)); // 10
System.out.println(numeros.size()); // 4
```

Su representación conceptual es similar a la de un array:

## 10

Índice 0

## 20

Índice 1

## 30

Índice 2

## 40

Índice 3

Es una lista indexada. El almacenamiento interno puede reservar capacidad adicional para futuras inserciones.

### Características principales

- Tamaño dinámico: puedes añadir y eliminar elementos.
- Acceso rápido por índice: `get(2)` normalmente cuesta \\(O(1)\\).
- Inserciones al final: normalmente cuestan \\(O(1)\\) amortizado; ocasionalmente debe ampliarse el array interno y copiarse.
- Inserciones o eliminaciones en medio: normalmente cuestan \\(O(n)\\), porque hay que desplazar elementos.
- No almacena tipos primitivos directamente: utiliza tipos de referencia. Para guardar enteros se usa `Integer`, no `int`, mediante autoboxing.

Por ejemplo:

```
ArrayList<String> nombres = new ArrayList<>();

nombres.add("Ana");
nombres.add("Luis");
nombres.add("Marta");

nombres.remove(1); // Elimina el elemento del índice 1
```

El resultado será `["Ana", "Marta"]`.

¿Cuándo utilizarlo? Es una excelente opción por defecto cuando necesitas una lista de elementos que crece o disminuye y accedes a ellos habitualmente por índice.

## 1.3. `LinkedList`

`LinkedList` también implementa `List`, pero su estructura interna es diferente: utiliza nodos enlazados.

Cada nodo contiene el elemento y referencias al nodo anterior y al siguiente. En Java, `LinkedList` es una lista doblemente enlazada.

Representación de una lista doblemente enlazada

### 10

Anterior: null

### 20

Anterior y siguiente

### 30

Siguiente: null

Cada nodo guarda referencias a sus vecinos; los elementos no necesitan ocupar posiciones consecutivas en memoria.

Código Java:

```
import java.util.LinkedList;

LinkedList<String> nombres = new LinkedList<>();

nombres.add("Ana");
nombres.add("Luis");
nombres.add("Marta");

nombres.addFirst("Pedro");
nombres.addLast("Carlos");

System.out.println(nombres.getFirst()); // Pedro
System.out.println(nombres.getLast());  // Carlos
```

### Características principales

- Tamaño dinámico: puedes añadir y eliminar elementos.
- Acceso por índice: es lento en comparación con `ArrayList`, ya que necesita recorrer nodos hasta alcanzar la posición solicitada. El coste es \\(O(n)\\) en el peor caso.
- Inserción y eliminación en los extremos: \\(O(1)\\).
- Inserción y eliminación en una posición conocida mediante un iterador: \\(O(1)\\) para modificar los enlaces, aunque localizar previamente esa posición puede costar \\(O(n)\\).
- Mayor sobrecarga de memoria: cada nodo necesita almacenar referencias adicionales.

Un matiz importante para una entrevista: decir que «insertar en una `LinkedList` cuesta siempre \\(O(1)\\)» es incorrecto. Solo es constante una vez que tienes localizado el nodo o la posición mediante un iterador.

# 2. Comparativa directa

















(0(n))










Los costes se refieren a las operaciones habituales, suponiendo que se trabaja con una colección de \\(n\\) elementos. En un array, modificar o desplazar elementos no es lo mismo que cambiar su tamaño.

## ¿Cuál elegiría en un proyecto real?

Mi criterio sería el siguiente:

- Array: cuando conozco el tamaño y quiero una estructura sencilla y eficiente, por ejemplo, una tabla de valores numéricos.
- `ArrayList`: para la mayoría de las listas de una aplicación Java, como usuarios, productos, tareas o resultados de consultas.
- `LinkedList`: cuando el patrón de acceso realmente favorece las operaciones en los extremos o el trabajo con iteradores y nodos ya localizados. No la elegiría simplemente porque espero insertar muchos elementos.

En la práctica, `ArrayList` suele ser más eficiente que `LinkedList` en bastantes escenarios, incluso en algunos donde ambas tienen la misma complejidad asintótica, porque aprovecha mejor la memoria caché de la CPU y evita crear un objeto por nodo.

# 3. Arrays unidimensionales y bidimensionales

Aquí cambia el concepto: ya no estamos comparando implementaciones de listas, sino cómo organizamos los datos.

## 3.1. Array unidimensional

Un array unidimensional tiene una sola dimensión: una secuencia de elementos.

```
int[] numeros = {10, 20, 30, 40};

System.out.println(numeros[2]); // 30
```

Se representa como una línea de posiciones:

10

0

20

1

30

2

40

3

Solo necesitas un índice: `numeros[2]`.

Ejemplos de uso:

- Las notas de un alumno.
- Las temperaturas registradas durante una semana.
- Los nombres de varios usuarios.
- Una lista de puntuaciones de un videojuego.

## 3.2. Array bidimensional

Un array bidimensional utiliza dos índices para organizar los elementos en filas y columnas. En Java se declara, por ejemplo, con `int[][]`.

```
int[][] matriz = {
    {1, 2, 3},
    {4, 5, 6},
    {7, 8, 9}
};

System.out.println(matriz[0][0]); // 1
System.out.println(matriz[1][2]); // 6
System.out.println(matriz[2][1]); // 8
```

Su representación sería una cuadrícula:

## 1

## 2

## 3

## 4

## 5

## 6

## 7

## 8

## 9

Para acceder al 6: `matriz[1][2]`. El primer índice identifica la fila 1 y el segundo, la columna 2. Los índices empiezan en 0.

En este ejemplo:

- `matriz[0]` devuelve la primera fila: `{1, 2, 3}`.
- `matriz[1]` devuelve la segunda fila: `{4, 5, 6}`.
- `matriz[1][2]` accede al elemento de la segunda fila y la tercera columna.

### ¿Para qué sirve?

Una matriz puede representar:

- Un tablero de ajedrez.
- Una tabla de notas de alumnos y asignaturas.
- Una imagen compuesta por píxeles.
- Una tabla de valores matemáticos.

Por ejemplo, para recorrer todos sus elementos:

```
for (int fila = 0; fila < matriz.length; fila++) {
    for (int columna = 0;
         columna < matriz[fila].length;
         columna++) {

        System.out.print(matriz[fila][columna] + " ");
    }

    System.out.println();
}
```

Se necesitan dos bucles porque hay que recorrer las filas y, dentro de cada fila, las columnas.

# 4. ¿Un array bidimensional es lo mismo que una matriz?

En el lenguaje habitual de programación se utilizan como términos equivalentes, pero conviene hacer una distinción.

Una matriz es un concepto matemático: una disposición rectangular de elementos organizados en filas y columnas, sobre los que pueden definirse operaciones como la suma, el producto o la transposición.

Un array bidimensional es una estructura de programación: una manera de almacenar y acceder a los datos utilizando dos índices.

En Java, además, `int[][]` no es necesariamente una matriz rectangular. Es realmente un array cuyos elementos son referencias a otros arrays.

Por ejemplo:

```
int[][] datos = {
    {1, 2, 3},
    {4, 5},
    {6, 7, 8, 9}
};
```

Esto es válido en Java. Las filas tienen longitudes distintas, así que hablamos de un array bidimensional irregular, también llamado jagged array.

Por eso, aunque toda matriz rectangular puede representarse con un array bidimensional, no todo array bidimensional tiene por qué representar una matriz rectangular.

# 5. ¿Qué pasa con las dimensiones superiores?

Java permite crear arrays con más de dos dimensiones:

```
int[][][] cubo = new int[3][4][5];
```

En este caso, tenemos tres índices:

```
cubo[1][2][3] = 100;
```

Podemos imaginarlo como un conjunto de matrices apiladas, es decir, un cubo de datos.

| Estructura     | Ejemplo Java | Índices |
| -------------- | ------------ | ------- |
| Unidimensional | `int[]`      | 1       |
| Bidimensional  | `int[][]`    | 2       |
| Tridimensional | `int[][][]`  | 3       |

Estas estructuras pueden utilizarse en simulaciones físicas, procesamiento de imágenes, datos espaciales y otros problemas que requieren representar varias dimensiones.

# 6. Preguntas típicas de entrevista

Test rápido · 5 preguntas

1\. ¿Cuál es la diferencia principal entre un array y un ArrayList?

El array es dinámico y ArrayList tiene tamaño fijo

El array tiene tamaño fijo y ArrayList puede crecer dinámicamente

No existe ninguna diferencia

Correcto

Un array tiene longitud fija una vez creado; ArrayList administra un almacenamiento interno que puede ampliarse.

2\. ¿Qué estructura ofrece acceso por índice en O(1) normalmente?

LinkedList

ArrayList y array

Solo LinkedList

Correcto

Los arrays y ArrayList permiten calcular directamente la posición de un elemento. LinkedList debe recorrer nodos.

3\. ¿Cuánto cuesta eliminar un nodo de LinkedList si ya tienes localizado ese nodo?

O(1) para modificar los enlaces

Siempre O(n)

Siempre O(log n)

Correcto

La modificación de enlaces es constante; encontrar primero el nodo puede requerir O(n).

4\. ¿Qué devuelve matriz[1][2] en el ejemplo anterior?

El número 4

El número 6

El número 8

Correcto

El índice 1 señala la segunda fila y el índice 2, la tercera columna. El valor es 6.

5\. ¿Puede un int[][] tener filas de diferentes longitudes en Java?

No, todas deben medir lo mismo

Sí, porque es un array de arrays

Solo si se usa ArrayList

Correcto

Cada fila es un array independiente y puede tener una longitud distinta.

Resultado: 5 / 5

Ejercicio 6 — Elegir entre ArrayList y LinkedList
Necesitas implementar una colección en la que las operaciones más frecuentes sean:
    • Acceder a elementos por índice.
    • Recorrer todos los elementos.
    • Añadir elementos al final.
¿Cuál elegirías normalmente en Java?
    • A. LinkedList, porque insertar y eliminar puede ser más barato.
    • B. ArrayList, porque ofrece acceso por índice en \(O(1)\), recorrido eficiente y adición al final en \(O(1)\) amortizado.
    • C. LinkedList, porque acceder por índice tiene complejidad \(O(1)\).
    • D. Ambas, porque sus complejidades son idénticas.
Responde con la letra y justifica brevemente tu elección.

B

Correcto: B. Elegiría ArrayList.
Las tres operaciones que indicas encajan bien con esta estructura:
Operación
Complejidad habitual
Acceder por índice (get(i))
\(O(1)\)
Recorrer todos los elementos
\(O(n)\)
Añadir al final (add(elemento))
\(O(1)\) amortizado
En cambio, LinkedList tiene acceso por índice en \(O(n)\), porque debe recorrer los nodos hasta llegar a la posición deseada.
Aunque LinkedList permite insertar y eliminar nodos en \(O(1)\) cuando ya tenemos su referencia, eso no la convierte automáticamente en la opción más eficiente. Si primero hay que localizar el nodo, la búsqueda suele costar \(O(n)\).
Conclusión: no elegimos una estructura porque sea mejor en términos absolutos, sino porque sus costes encajan con las operaciones más frecuentes de nuestro problema.
Ejercicio 7 — Listas enlazadas simples y dobles
Una lista enlazada simple tiene nodos que apuntan al siguiente. Una lista doblemente enlazada tiene nodos que apuntan tanto al siguiente como al anterior.
¿Cuál es una ventaja específica de la lista doblemente enlazada?
    • A. Permite acceder directamente a cualquier elemento por índice en \(O(1)\).
    • B. Permite recorrer la lista en ambos sentidos y facilita eliminar un nodo conocido en \(O(1)\).
    • C. Siempre consume menos memoria que una lista simple.
    • D. No necesita almacenar referencias entre nodos.
Responde con la letra y explica qué información adicional almacena cada nodo de una lista doblemente enlazada.
B

Correcto. B es la respuesta correcta.
Una lista doblemente enlazada almacena dos referencias por nodo:
    • next: referencia al siguiente nodo.
    • prev: referencia al nodo anterior.
Esto permite recorrer la lista en ambos sentidos y, si ya tenemos una referencia al nodo que queremos eliminar, actualizar los enlaces de sus vecinos en \(O(1)\).
En cambio, una lista simplemente enlazada solo almacena la referencia al siguiente nodo. Para eliminar uno, normalmente necesitamos localizar también el nodo anterior.
Ejercicio 8 — Elegir una estructura
Tienes que implementar un historial de navegación con estas operaciones:
    • Añadir una página al final.
    • Volver a la página anterior.
    • Avanzar a la página siguiente.
    • Consultar la página actual.
¿Qué estructura de datos encaja mejor como base?
    • A. Un array tradicional.
    • B. Una lista simplemente enlazada.
    • C. Una lista doblemente enlazada.
    • D. Un HashSet.
Responde con la letra y explica por qué esa estructura facilita avanzar y retroceder por el historial.
C

Correcto. C. Lista doblemente enlazada.
Cada nodo mantiene referencias al nodo siguiente (next) y al anterior (prev). Así, el historial puede avanzar y retroceder sin tener que recorrer la lista desde el principio para encontrar el nodo anterior.
Un matiz: para consultar la página actual, podemos mantener una referencia al nodo actual. Al retroceder usamos prev y al avanzar usamos next.
Ejercicio 9 — Complejidad de una lista enlazada
Tienes una lista simplemente enlazada con 10.000 nodos y quieres acceder al elemento situado en el índice 7000.
¿Qué complejidad temporal tiene esa operación en una implementación convencional?
    • A. \(O(1)\), porque conocemos el índice.
    • B. \(O(\log n)\), porque podemos descartar la mitad de los nodos.
    • C. \(O(n)\), porque debemos recorrer los nodos desde el principio hasta llegar al índice buscado.
    • D. \(O(n^2)\), porque cada nodo contiene una referencia.
Responde con la letra y explica por qué conocer el índice no permite acceder directamente al nodo.



Operación
Array
ArrayList
LinkedList
Acceder por índice
\(O(1)\)
\(O(1)\)
\(O(n)\)
Buscar por valor, sin ordenar
\(O(n)\)
\(O(n)\)
\(O(n)\)
Añadir al final
No redimensionable
\(O(1)\) amortizado
\(O(1)\)
Insertar en medio, teniendo que localizar el índice
—
\(O(n)\)
\(O(n)\)


C pero aprovechando que en linkedlist es doblemente enlazada y que 7000>5000 esta por encima de la mitad de el total 10000/2=5000 no seria mas rapido enmpezar desde el final e ir marcha atras? 


Correcto: C es la respuesta, pero tu observación es precisamente una de las ventajas de LinkedList en Java. Has detectado un detalle importante.
En Java, LinkedList es una lista doblemente enlazada y su método get(int index) aprovecha esa característica: empieza desde el principio o desde el final, según cuál esté más cerca del índice buscado.
Para una lista de 10.000 elementos, cuyos índices van del 0 al 9999:
Buscar el índice 7000
Desde el principio
7000 enlaces aprox.
Desde el final
2999 enlaces
Se compara la distancia desde ambos extremos. El índice 7000 está más cerca del final, cuyo último índice es 9999.
¿Qué complejidad tiene entonces?
Aunque se optimice la dirección del recorrido, sigue siendo \(O(n)\).
La razón es que, en el peor caso, el método debe recorrer aproximadamente la mitad de la lista. En notación Big O, ignoramos constantes:
\[ O(n/2)=O(n) \]
Por tanto, tu razonamiento es correcto: se puede ahorrar trabajo, pero la complejidad asintótica no cambia.
Matiz de Java: la implementación de LinkedList.get(index) hace precisamente esa optimización. No todas las listas doblemente enlazadas tienen por qué implementarla de esa manera.
Ejercicio 10 — Aplicación práctica
Necesitas almacenar un millón de elementos y realizar estas operaciones:
    • Consultar elementos frecuentemente por índice.
    • Recorrer la colección completa.
    • Añadir elementos al final.
¿Cuál elegirías y por qué?
    • A. LinkedList, porque cada inserción siempre cuesta \(O(1)\).
    • B. ArrayList, porque el acceso por índice es \(O(1)\) y añadir al final es \(O(1)\) amortizado.
    • C. LinkedList, porque acceder por índice es \(O(1)\).
    • D. Un array tradicional, porque puede crecer automáticamente.
Responde con la letra y justifica tu elección.
B

Correcto. B. ArrayList es la mejor opción para ese escenario.
    • Acceso por índice: \(O(1)\), porque internamente utiliza un array.
    • Recorrido completo: \(O(n)\), recorriendo los elementos secuencialmente.
    • Añadir al final: \(O(1)\) amortizado. Normalmente se añade directamente; ocasionalmente hay que ampliar el array interno y copiar sus elementos, operación que cuesta \(O(n)\).
LinkedList no sería la mejor elección porque acceder por índice cuesta \(O(n)\). Aunque no necesita desplazar elementos al insertar nodos, esa ventaja no compensa cuando predominan las consultas por índice.
Ejercicio 11 — Arrays dinámicos y redimensionamiento
Un ArrayList tiene un array interno con capacidad para 8 elementos y ya contiene esos 8 elementos. Añades un noveno.
¿Qué puede ocurrir internamente?
    • A. El array interno siempre puede crecer automáticamente sin copiar elementos.
    • B. Se crea un array interno mayor, se copian los elementos existentes y se añade el nuevo.
    • C. Se convierte automáticamente en una lista enlazada.
    • D. La operación falla porque un array tiene longitud fija.
Responde con la letra y explica la diferencia entre tamaño (size) y capacidad (capacity) de un ArrayList.
B

Correcto. B es la respuesta correcta.
La distinción importante es esta:
    • size: número de elementos que contiene actualmente el ArrayList.
    • capacity: número de elementos que puede almacenar su array interno antes de necesitar redimensionarse.
Por ejemplo:
ArrayList<Integer> numeros = new ArrayList<>(8);

numeros.add(10);
numeros.add(20);

System.out.println(numeros.size()); // 2
Aquí el tamaño es 2 y la capacidad inicial solicitada es 8. Los seis huecos restantes no son elementos de la lista y no puedes acceder a ellos mediante get(2), por ejemplo.
Cuando se agota la capacidad, Java puede crear un array interno mayor y copiar los elementos existentes. El factor de crecimiento no forma parte de una garantía contractual de la API de ArrayList, así que no conviene depender de un multiplicador concreto.
Un matiz: new ArrayList<>(8) establece una capacidad inicial, pero no crea ocho elementos.
Qué debes recordar para una entrevista de Java: el crecimiento automático de capacidad es un comportamiento de ArrayList, pero el factor concreto de crecimiento es un detalle de implementación. No confundas size, que cuenta los elementos existentes, con capacity, que representa el espacio disponible en el array interno. 

Si ya tienes una lista creada y quieres aumentar su capacidad sin modificar su número de elementos, puedes utilizar ensureCapacity():
ArrayList<Integer> numeros = new ArrayList<>(2);

numeros.add(10);
numeros.add(20);

// Preparamos espacio para 22 elementos en total.
numeros.ensureCapacity(22);

for (int i = 0; i < 20; i++) {
    numeros.add(i);
}
ensureCapacity(22) solicita capacidad suficiente para al menos 22 elementos. No añade elementos ni cambia el tamaño lógico de la lista.
3. Caso C: añadir los 20 elementos desde otra colección
Si los 20 datos ya están almacenados en otra colección, puedes utilizar addAll():
ArrayList<Integer> numeros = new ArrayList<>(2);
numeros.add(10);
numeros.add(20);

List<Integer> nuevos = new ArrayList<>();

for (int i = 0; i < 20; i++) {
    nuevos.add(i);
}

numeros.addAll(nuevos);

System.out.println(numeros.size()); // 22
Ejercicio 12 — Coste de inserción
Tienes un ArrayList con 10.000 elementos y capacidad suficiente. Insertas un elemento en el índice 100.
¿Qué complejidad temporal tiene add(100, elemento)?
    • A. \(O(1)\), porque hay capacidad suficiente.
    • B. \(O(\log n)\), porque busca el punto de inserción.
    • C. \(O(n)\), porque debe desplazar los elementos posteriores para dejar espacio.
    • D. \(O(n^2)\), porque debe copiar toda la lista dos veces.
Responde con la letra y explica qué cambia respecto a añadir el elemento al final.

C

Correcto. C es la respuesta correcta: \(O(n)\).
Aunque el ArrayList tenga capacidad suficiente, insertar en una posición intermedia requiere desplazar los elementos posteriores una posición hacia la derecha para dejar espacio.
Por ejemplo, si tenemos:
[10, 20, 30, 40, 50]
Ejecutamos:
numeros.add(2, 99);
El resultado es:
[10, 20, 99, 30, 40, 50]
Los elementos 30, 40 y 50 se desplazan hacia la derecha.
La diferencia importante es:
Operación
Complejidad
get(index)
\(O(1)\)
add(elemento) al final
\(O(1)\) amortizado
add(index, elemento) en una posición intermedia
\(O(n)\)
remove(index) en una posición intermedia
\(O(n)\)
La capacidad suficiente evita tener que crear otro array y copiar todos los elementos, pero no evita el desplazamiento.
Ejercicio 13 — Elegir entre ArrayList y LinkedList
Imagina que tienes que implementar una cola de trabajo con estas características:
    • Se añaden elementos al final.
    • Se procesan y eliminan elementos desde el principio.
    • No necesitas acceder a los elementos por índice.
¿Cuál sería una elección razonable entre ArrayList y LinkedList?
    • A. ArrayList, porque eliminar el primer elemento cuesta \(O(1)\).
    • B. LinkedList, porque añadir al final y eliminar el primer nodo cuestan \(O(1)\).
    • C. ArrayList, porque todas sus operaciones cuestan \(O(1)\).
    • D. Ambas tienen exactamente el mismo coste para todas esas operaciones.
Responde con la letra y justifica tu elección.
B

Correcto. B es la respuesta esperada, con un matiz importante: LinkedList permite añadir al final y eliminar el primer elemento en \(O(1)\), porque mantiene referencias a ambos extremos.
LinkedList<Integer> cola = new LinkedList<>();

cola.addLast(10);
cola.addLast(20);
cola.addLast(30);

int primero = cola.removeFirst(); // 10
Las operaciones addLast() y removeFirst() tienen coste \(O(1)\).
En cambio, con un ArrayList, eliminar el primer elemento cuesta \(O(n)\), porque hay que desplazar los elementos restantes hacia la izquierda.
Matiz de diseño: si lo que necesitas es específicamente una cola FIFO, en Java normalmente consideraría primero la interfaz Queue o Deque y una implementación como ArrayDeque. No necesitas elegir LinkedList solo porque sus operaciones tengan ese coste; ArrayDeque suele ser una alternativa más eficiente en memoria y localidad de caché.
Ejercicio 14 — Cola FIFO en Java
¿Cuál de estas implementaciones elegirías normalmente para una cola FIFO cuando no necesitas insertar elementos null ni acceder por índice?
    • A. ArrayList, eliminando siempre el elemento del índice 0.
    • B. ArrayDeque, usando offer() para añadir y poll() para extraer.
    • C. LinkedList, porque siempre es más rápida que ArrayDeque.
    • D. HashSet, porque evita elementos duplicados.
Responde con la letra y explica qué significan FIFO y las operaciones offer() y poll().
B
Correcto. B. ArrayDeque es la elección habitual para implementar una cola FIFO en Java.
    • FIFO (First In, First Out): el primero en entrar es el primero en salir.
    • offer(elemento): intenta añadir un elemento a la cola y devuelve true si lo consigue.
    • poll(): extrae y devuelve el elemento del principio; si la cola está vacía, devuelve null.
Queue<Integer> cola = new ArrayDeque<>();

cola.offer(10);
cola.offer(20);
cola.offer(30);

System.out.println(cola.poll()); // 10
System.out.println(cola.poll()); // 20
System.out.println(cola.poll()); // 30
ArrayDeque utiliza un array redimensionable de forma circular, por lo que añadir y extraer por los extremos tiene un coste amortizado de \(O(1)\).
No admite valores null, lo que permite que poll() utilice null para indicar que la cola está vacía.
Ejercicio 15 — Pila LIFO
Ahora necesitas implementar una pila para comprobar paréntesis en una expresión matemática. Por ejemplo, en ((2 + 3) * 4) debes poder recordar qué paréntesis se abrió el último para cerrarlo primero.
¿Qué principio debe seguir la estructura?
    • A. FIFO: el primero en entrar es el primero en salir.
    • B. LIFO: el último en entrar es el primero en salir.
    • C. Ordenar los elementos por prioridad.
    • D. Mantener los elementos ordenados por valor.
Responde con la letra y explica por qué LIFO permite comprobar correctamente los paréntesis anidados.
B

Correcto: B. LIFO (Last In, First Out).
Una pila sigue el principio de que el último elemento en entrar es el primero en salir. Es exactamente lo que necesitamos para comprobar paréntesis anidados.
Por ejemplo, en ((2 + 3) * 4):
    1. Encontramos ( → lo apilamos.
    2. Encontramos otro ( → lo apilamos también.
    3. Encontramos ) → desapilamos la última apertura.
    4. Encontramos ) → desapilamos la apertura restante.
Si aparece un cierre y la pila está vacía, hay un paréntesis de cierre sobrante. Si terminamos y quedan aperturas en la pila, faltan cierres.
Ejercicio 16 — Operaciones de una pila en Java
Observa este código:
Deque<Integer> pila = new ArrayDeque<>();

pila.push(10);
pila.push(20);
pila.push(30);

System.out.println(pila.pop());
System.out.println(pila.peek());
System.out.println(pila.pop());
¿Qué salida produce?
    • A. 10, 20, 30
    • B. 30, 20, 20
    • C. 30, 20, 20 no, porque peek() elimina el elemento.
    • D. 10, 10, 20
Elige la opción que consideres correcta y explica brevemente la diferencia entre push(), pop() y peek().
B

Correcto: B. La salida es:
30
20
20
Las tres operaciones funcionan así:
    • push(10), push(20), push(30): introduce elementos en la cima de la pila. El 30 queda arriba.
    • pop(): devuelve y elimina el elemento de la cima. Devuelve 30.
    • peek(): devuelve el elemento de la cima sin eliminarlo. Devuelve 20.
    • pop(): elimina y devuelve el 20, que seguía en la cima.
Ejercicio 17 — ¿Qué estructura elegirías?
Necesitas implementar una cola de tareas pendientes. Las tareas deben procesarse en el mismo orden en que llegan: la primera tarea recibida debe ser la primera en ejecutarse.
¿Cuál sería la opción más adecuada en Java?
    • A. Stack, porque permite recuperar el último elemento añadido.
    • B. ArrayDeque utilizado como cola FIFO.
    • C. ArrayList, eliminando siempre el elemento del índice 0.
    • D. HashSet, porque permite insertar y eliminar elementos.
Elige una opción y justifica brevemente tu decisión.
B

---
























Vamos a acelerar el ritmo. Para llegar cuanto antes a la Fase 3: Java avanzado y Spring Boot, trabajaremos los apartados 2.5–2.8 mediante explicaciones breves, diferencias importantes y preguntas de entrevista. No nos detendremos en ejercicios repetitivos de conceptos que ya dominas.
2.5. Conjuntos y mapas
1. HashSet y TreeSet
Ambos implementan Set, una colección que no admite elementos duplicados.
Característica
HashSet
TreeSet
Orden
No garantizado
Orden natural o Comparator
Operaciones habituales
O(1)
O(log n)
Uso principal
Unicidad y búsquedas rápidas
Unicidad y elementos ordenados
Set<Integer> numeros = new HashSet<>();
numeros.add(30);
numeros.add(10);
numeros.add(30); // No añade un duplicado

Set<Integer> ordenados = new TreeSet<>();
ordenados.add(30);
ordenados.add(10);
ordenados.add(20);
// Iteración: 10, 20, 30
2. HashMap y TreeMap
Ambos implementan Map, que almacena asociaciones de clave → valor. Las claves son únicas; los valores pueden repetirse.
Característica
HashMap
TreeMap
Orden por clave
No garantizado
Ordenado por clave
Operaciones habituales
O(1)
O(log n)
Clave duplicada
Sustituye el valor anterior
Sustituye el valor anterior
Map<String, Integer> edades = new HashMap<>();

edades.put("Ana", 25);
edades.put("Luis", 30);
edades.put("Ana", 26); // La edad de Ana pasa a ser 26
3. equals() y hashCode()
Esta relación es fundamental para utilizar correctamente objetos como claves de HashMap o elementos de HashSet.
La regla es:
    • Si a.equals(b) devuelve true, ambos objetos deben tener el mismo hashCode().
    • Si dos objetos tienen el mismo hashCode(), no significa necesariamente que sean iguales: puede haber una colisión.
    • Si sobrescribes equals(), normalmente debes sobrescribir también hashCode().
Las colisiones se gestionan internamente por la colección. En condiciones normales, las operaciones hash son O(1), aunque pueden degradarse en casos desfavorables.
4. ¿Qué estructura elegir?
    • Comprobar pertenencia y evitar duplicados: HashSet.
    • Mantener elementos únicos ordenados: TreeSet.
    • Buscar valores mediante claves: HashMap.
    • Consultar valores por claves manteniendo las claves ordenadas: TreeMap.
Comprobación rápida
Tienes una clase Usuario que sobrescribe equals(), pero no sobrescribe hashCode(). Dos instancias diferentes representan al mismo usuario según equals().
¿Qué problema puede aparecer al introducirlas en un HashSet?
A. El conjunto siempre las reconocerá como duplicadas.
B. El conjunto puede almacenar ambas porque sus códigos hash podrían ser diferentes.
C. HashSet ordenará automáticamente los usuarios.
D. Java impedirá compilar la clase.
Comprobar

---

2.6. Ordenación
Vamos al grano: necesitas conocer los algoritmos clásicos, sus complejidades y cómo ordenar objetos en Java. Para entrevistas, lo más importante es saber cuándo utilizar cada uno y manejar Comparator y Comparable.
1. Algoritmos clásicos
Algoritmo
Mejor caso
Caso medio
Peor caso
Memoria auxiliar
Burbuja
O(n) optimizado
O(n²)
O(n²)
O(1)
Selección
O(n²)
O(n²)
O(n²)
O(1)
Inserción
O(n)
O(n²)
O(n²)
O(1)
Merge sort
O(n log n)
O(n log n)
O(n log n)
O(n)
Quicksort
O(n log n)
O(n log n)
O(n²)
O(log n) promedio de pila
    • Burbuja: compara elementos adyacentes e intercambia los que están desordenados. Es sencillo, pero poco eficiente.
    • Selección: busca el mínimo restante y lo coloca en su posición. Hace pocos intercambios, pero siempre realiza O(n²) comparaciones.
    • Inserción: inserta cada elemento en su posición dentro de la parte ya ordenada. Es útil para conjuntos pequeños o casi ordenados.
    • Merge sort: divide, ordena las partes y las combina. Garantiza O(n log n), pero normalmente necesita memoria adicional.
    • Quicksort: divide los elementos según un pivote. Suele ser rápido, pero puede degradarse a O(n²) con particiones desfavorables.
No necesitas implementar todos de memoria ahora; debes comprender sus diferencias.
2. Ordenación en Java
Java proporciona métodos de ordenación para que normalmente no tengas que implementar estos algoritmos manualmente.
int[] numeros = {30, 10, 20};
Arrays.sort(numeros);
// [10, 20, 30]
Para colecciones:
List<Integer> numeros = new ArrayList<>(
    List.of(30, 10, 20)
);

Collections.sort(numeros);
// [10, 20, 30]
Arrays.sort() trabaja con arrays. Collections.sort() ordena listas modificables. En código moderno también es habitual:
numeros.sort(Comparator.naturalOrder());
La implementación concreta depende del tipo de datos y de la sobrecarga utilizada; no conviene asumir que todos estos métodos emplean el mismo algoritmo.
3. Comparable frente a Comparator
Esta diferencia sí es importante en Java avanzado y Spring Boot.
Comparable<T> define el orden natural de una clase mediante compareTo().
class Producto implements Comparable<Producto> {
    private final String nombre;

    Producto(String nombre) {
        this.nombre = nombre;
    }

    @Override
    public int compareTo(Producto otro) {
        return nombre.compareTo(otro.nombre);
    }
}
Comparator<T> define un criterio de ordenación externo, sin necesidad de modificar la clase.
productos.sort(
    Comparator.comparing(Producto::getPrecio)
);
Por ejemplo, puedes ordenar productos por nombre con su orden natural y, en otra operación, por precio utilizando un Comparator.
4. Estabilidad
Una ordenación es estable cuando conserva el orden relativo de los elementos que tienen la misma clave de ordenación.
Imagina tres empleados ordenados originalmente por nombre:
    • Ana, departamento A
    • Luis, departamento B
    • Marta, departamento A
Si los ordenas por departamento mediante un algoritmo estable, Ana seguirá apareciendo antes que Marta, porque ambas pertenecen al departamento A y Ana estaba primero.
Pregunta de comprobación
Tienes una clase Empleado y necesitas ordenarla por salario en una operación y por antigüedad en otra, sin modificar la clase.
¿Qué opción es la más adecuada?
A. Implementar obligatoriamente dos métodos compareTo() en Empleado.
B. Utilizar distintos Comparator<Empleado> para cada criterio.
C. Utilizar HashMap, que ordena por salario.
D. Implementar siempre burbuja para cada ordenación.
Comprobar
Correcto.
Comparator permite definir múltiples criterios externos y reutilizables. Por ejemplo, Comparator.comparing(Empleado::getSalario) para ordenar por salario.
Continuar al 2.7: Recursividad y árboles

2.7. Recursividad y árboles
Vamos a centrarnos en lo esencial para entrevistas Java. Necesitas entender la recursividad, los árboles binarios, sus recorridos y las complejidades básicas.
1. Recursividad
Una función recursiva es aquella que se llama a sí misma para resolver un problema más pequeño.
Toda recursión correcta necesita dos elementos:
    • Caso base: condición que detiene las llamadas.
    • Caso recursivo: reduce el problema y vuelve a llamar a la función.
Ejemplo: factorial de un número.
static int factorial(int n) {
    if (n <= 1) {
        return 1; // Caso base
    }

    return n * factorial(n - 1); // Caso recursivo
}
Para factorial(4):
\[ 4! = 4 \times 3 \times 2 \times 1 = 24 \]
Cada llamada queda almacenada en la pila de llamadas (call stack) hasta que se resuelve. Si hay demasiadas llamadas anidadas, Java puede lanzar StackOverflowError.
En este ejemplo, tanto el tiempo como el espacio de pila son O(n).
2. Árboles binarios
Un árbol es una estructura jerárquica formada por nodos.
Ejemplo de árbol binario de búsqueda (BST).
Conceptos básicos:
    • Raíz: nodo inicial, aquí el 8.
    • Hijo: nodo descendiente directo.
    • Hoja: nodo sin hijos, como 1, 6 y 10.
    • Altura: longitud del camino más largo desde el nodo hasta una hoja, según la convención utilizada para contar niveles o aristas.
En un árbol binario de búsqueda (BST), los valores menores que un nodo se sitúan a su izquierda y los mayores a su derecha, suponiendo esta política para los duplicados.
Con un árbol equilibrado, buscar, insertar o eliminar suele costar O(log n). Si el árbol se degenera en una cadena, puede costar O(n).
3. Recorridos de un árbol
Para el árbol del dibujo:
Recorrido
Orden
Resultado
Preorden
Nodo, izquierda, derecha
8, 3, 1, 6, 10
Inorden
Izquierda, nodo, derecha
1, 3, 6, 8, 10
Postorden
Izquierda, derecha, nodo
1, 6, 3, 10, 8
Un detalle importante: el recorrido inorden de un BST produce los valores ordenados, si se respeta la propiedad del árbol.
4. Árboles balanceados y heaps
    • Árboles balanceados, como AVL o Red-Black: mantienen la altura controlada para evitar que las operaciones se degraden a O(n). TreeMap y TreeSet se apoyan en árboles Red-Black.
    • Heap: árbol binario que satisface una propiedad de prioridad. En un min-heap, cada padre es menor o igual que sus hijos. Consultar el mínimo es O(1), insertar y extraerlo son O(log n).
Un heap no mantiene todos los elementos globalmente ordenados. Sirve para obtener eficientemente el elemento prioritario.
Pregunta de comprobación
¿Qué resultado produce el recorrido inorden de este árbol?
A. 5, 3, 2, 4, 8
B. 2, 3, 4, 5, 8
C. 2, 4, 3, 8, 5
D. 5, 8, 3, 4, 2
Comprobar
La respuesta correcta es B.
Inorden significa izquierda → nodo → derecha. Primero visitamos 2, 3, 4, después la raíz 5 y finalmente 8.
Continuar al 2.8: Resolución de problemas

2.8. Resolución de problemas
Este es el último apartado de la Fase 2. Vamos a centrarnos en las técnicas que más vas a utilizar al programar y en entrevistas técnicas.
1. Descomposición de problemas
No intentes resolver todo el problema de golpe. Divídelo en pasos pequeños.
Por ejemplo, si necesitas encontrar los usuarios duplicados en una lista:
    1. Identificar qué significa que dos usuarios sean duplicados.
    2. Elegir una estructura para registrar los usuarios ya vistos, por ejemplo, un HashSet.
    3. Recorrer la lista y comprobar cada usuario.
    4. Registrar los duplicados encontrados.
    5. Analizar los casos límite y la complejidad.
2. Elegir la estructura de datos adecuada
La elección depende de las operaciones que necesites realizar con más frecuencia.
Necesidad
Estructura habitual
Acceso por índice
ArrayList
Comprobar pertenencia rápidamente
HashSet
Buscar un valor mediante una clave
HashMap
Mantener claves ordenadas
TreeMap
Procesar elementos por orden de llegada
Queue / ArrayDeque
Deshacer la última acción
Deque usado como pila
Obtener repetidamente el mínimo o máximo
PriorityQueue
No elijas una estructura solo porque la conoces: justifica la decisión por sus operaciones y complejidad.
3. Invariantes y condiciones de terminación
Un invariante es una propiedad que debe mantenerse durante la ejecución de un algoritmo.
Ejemplo: al recorrer un array buscando el máximo, después de procesar cada elemento, la variable maximo debe contener el mayor valor visto hasta ese momento.
La condición de terminación garantiza que el algoritmo acabe. En un bucle, normalmente depende de que el índice avance o de que disminuya la cantidad de trabajo pendiente.
Un error frecuente es olvidar avanzar el índice o modificar el estado necesario para salir del bucle, provocando una ejecución infinita.
4. Casos límite
Antes de dar por terminado un algoritmo, comprueba situaciones como:
    • Colección vacía.
    • Un único elemento.
    • Elementos duplicados.
    • Valores negativos o extremos.
    • Elemento buscado inexistente.
    • Entrada null, si el método puede recibirla.
    • Tamaños suficientemente grandes para revelar problemas de rendimiento.
No todos los métodos deben aceptar null: hay que definir explícitamente su contrato.
5. Analizar la complejidad
Considera este código:
int contador = 0;

for (int i = 0; i < n; i++) {
    for (int j = 0; j < n; j++) {
        contador++;
    }
}
El bucle exterior se ejecuta \(n\) veces y el interior, \(n\) veces por cada iteración exterior. El total es \(n \times n\), así que la complejidad temporal es O(n²).
La complejidad espacial depende de la memoria adicional que utiliza el algoritmo, no del tamaño total de la entrada por sí solo.
6. Método práctico para entrevistas
Cuando te planteen un problema sin IDE:
    1. Aclara las entradas, salidas y restricciones.
    2. Explica una solución sencilla que sea correcta.
    3. Elige las estructuras de datos adecuadas.
    4. Escribe pseudocódigo o código.
    5. Comprueba manualmente casos normales y límite.
    6. Explica complejidad temporal y espacial.
    7. Propón optimizaciones si son necesarias.
Es preferible una solución sencilla y correcta que puedas explicar a otra más compleja que no controles.
Pregunta final de la Fase 2
Tienes una lista de \(n\) identificadores enteros y necesitas detectar si alguno aparece más de una vez. No necesitas conservar el orden de los identificadores ni ordenarlos.
¿Cuál es la opción más adecuada para obtener una solución eficiente en el caso habitual?
A. Comparar cada elemento con todos los demás: O(n²).
B. Introducir los identificadores en un HashSet y detectar si add() devuelve false: O(n) esperado.
C. Ordenar siempre la lista con burbuja y después recorrerla.
D. Utilizar un ArrayList y comprobar cada elemento mediante un recorrido completo adicional.
Comprobar




























Fase 3. Java avanzado y Spring Boot
El objetivo de esta fase es pasar de conocer Java y programar aplicaciones a diseñar, implementar y probar aplicaciones backend con criterios profesionales.
Como ya has trabajado Java, POO y estructuras de datos, no vamos a volver a explicar variables, bucles, herencia o polimorfismo desde cero. Nos centraremos en los conocimientos que necesitas para desarrollar con soltura y defender tus decisiones técnicas en entrevistas.
Temario de la fase
3.1. Java avanzado
Genéricos, colecciones avanzadas, lambdas, Streams, Optional, excepciones, igualdad, records, enums y características modernas de Java.
3.2. Diseño y buenas prácticas
SOLID, inyección de dependencias, interfaces, composición, separación de responsabilidades y patrones habituales.
3.3. Spring Framework y Spring Boot
IoC, beans, configuración, autoconfiguración, ciclo de vida, perfiles y configuración externa.
3.4. Spring Web y APIs REST
Controllers, DTO, validación, servicios, repositorios, códigos HTTP, errores y paginación.
3.5. Persistencia y transacciones
JPA, Hibernate, relaciones, consultas, transacciones, concurrencia y migraciones.
3.6. Testing, seguridad y producción
JUnit, Mockito, integración, Spring Security, JWT, Docker, logs y observabilidad.
El orden podrá ajustarse si un tema depende de otro. Como tu objetivo es avanzar rápido hacia Spring Boot, priorizaremos lo que realmente se utiliza en proyectos backend y entrevistas técnicas.
3.1. Java avanzado — Bloque 1: Lambdas e interfaces funcionales
Este es un buen punto de partida porque las lambdas y las interfaces funcionales aparecen constantemente en Streams, programación asíncrona y APIs de Java.
1. ¿Qué es una interfaz funcional?
Es una interfaz que tiene un único método abstracto. Puede contener también métodos default y static.
Por ejemplo:
@FunctionalInterface
interface Operacion {
    int ejecutar(int a, int b);
}
Podemos implementar esa interfaz mediante una clase anónima:
Operacion suma = new Operacion() {
    @Override
    public int ejecutar(int a, int b) {
        return a + b;
    }
};
O mediante una lambda, de forma mucho más concisa:
Operacion suma = (a, b) -> a + b;

System.out.println(suma.ejecutar(3, 5)); // 8
La lambda (a, b) -> a + b proporciona la implementación del método ejecutar. Java infiere los tipos de los parámetros a partir de la interfaz de destino.
@FunctionalInterface no es obligatorio, pero hace que el compilador compruebe que la interfaz cumple ese contrato.
2. Las cuatro interfaces funcionales que debes conocer
Java incluye interfaces funcionales genéricas en java.util.function.
Interfaz
Qué representa
Método principal
Predicate<T>
Una condición que devuelve boolean
test(T)
Function<T, R>
Una transformación de T a R
apply(T)
Consumer<T>
Una operación que recibe un valor sin devolver resultado
accept(T)
Supplier<T>
Una operación que proporciona un valor
get()
Ejemplos:
Predicate<Integer> esPar = n -> n % 2 == 0;
Function<String, Integer> longitud = s -> s.length();
Consumer<String> imprimir = s -> System.out.println(s);
Supplier<String> generar = () -> "Hola";
Observa la diferencia:
    • Predicate: pregunta algo.
    • Function: transforma algo.
    • Consumer: consume algo.
    • Supplier: proporciona algo.
Estas interfaces permiten pasar comportamiento como argumento a otros métodos, en lugar de limitarte a pasar datos.
3. ¿Por qué importan en el backend?
Imagina que tienes una lista de usuarios y quieres seleccionar los mayores de edad:
List<Usuario> mayores = usuarios.stream()
    .filter(usuario -> usuario.getEdad() >= 18)
    .toList();
La lambda dentro de filter() actúa como un Predicate<Usuario>.
No necesitas aprender todavía todos los detalles de Streams; los veremos en el siguiente bloque. Por ahora, quédate con esta idea: las lambdas permiten expresar comportamiento y las interfaces funcionales definen qué forma debe tener ese comportamiento.
Pregunta de comprobación
¿Qué interfaz funcional utilizarías para representar una operación que recibe un String y devuelve su longitud como Integer?
A. Predicate<String>
B. Consumer<String>
C. Function<String, Integer>
D. Supplier<Integer>
Comprobar

C

Correcto.
Function<String, Integer> recibe un String y devuelve un Integer. Es el patrón de transformación de un tipo a otro.


3.1. Java avanzado — Bloque 2: Streams API
La Streams API permite procesar colecciones de datos mediante una secuencia de operaciones declarativas: filtrar, transformar, ordenar, eliminar duplicados y combinar resultados.
La idea es expresar qué quieres hacer con los datos, en lugar de escribir manualmente todos los bucles y condiciones.
1. Crear un Stream
List<Integer> numeros = List.of(5, 2, 8, 2, 1);

Stream<Integer> stream = numeros.stream();
Un Stream no es una colección: es una secuencia de procesamiento de datos. Normalmente no modifica la colección original.
2. Operaciones principales
filter() — Filtrar elementos
Recibe un Predicate y conserva los elementos que cumplen la condición.
List<Integer> resultado = numeros.stream()
    .filter(n -> n > 3)
    .toList();

// [5, 8]
map() — Transformar elementos
Aplica una función a cada elemento y produce los resultados transformados.
List<Integer> cuadrados = numeros.stream()
    .map(n -> n * n)
    .toList();

// [25, 4, 64, 4, 1]
Si tienes una lista de usuarios, podrías extraer únicamente sus nombres:
List<String> nombres = usuarios.stream()
    .map(Usuario::getNombre)
    .toList();
Usuario::getNombre es una referencia a método, equivalente en este caso a usuario -> usuario.getNombre().
sorted() — Ordenar
Orden natural:
List<Integer> ordenados = numeros.stream()
    .sorted()
    .toList();

// [1, 2, 2, 5, 8]
Con un criterio personalizado:
List<Usuario> ordenados = usuarios.stream()
    .sorted(Comparator.comparing(Usuario::getEdad))
    .toList();
Para ordenar de mayor a menor edad:
.sorted(Comparator.comparing(Usuario::getEdad).reversed())
distinct() — Eliminar duplicados
Utiliza la igualdad de los elementos para conservar solo valores distintos.
List<Integer> unicos = numeros.stream()
    .distinct()
    .toList();

// [5, 2, 8, 1]
Con objetos propios, el comportamiento depende de una implementación correcta de equals() y hashCode().
3. toList() y collect()
Ambas operaciones son terminales: materializan el resultado del procesamiento.
List<Integer> pares = numeros.stream()
    .filter(n -> n % 2 == 0)
    .toList();
También puedes usar collect() con un colector:
Set<Integer> unicos = numeros.stream()
    .collect(Collectors.toSet());
O agrupar usuarios por edad:
Map<Integer, List<Usuario>> porEdad = usuarios.stream()
    .collect(Collectors.groupingBy(Usuario::getEdad));
Diferencia importante: Stream.toList(), disponible desde Java 16, devuelve una lista no modificable. Collectors.toList() no garantiza un tipo concreto ni que la lista resultante sea modificable. Si necesitas expresamente una ArrayList modificable:
List<Integer> copia = numeros.stream()
    .collect(Collectors.toCollection(ArrayList::new));
4. reduce() — Reducir a un único resultado
Combina los elementos para producir un resultado acumulado, por ejemplo, una suma.
int suma = numeros.stream()
    .reduce(0, Integer::sum);

// 18
El 0 es el valor inicial y Integer::sum combina los valores.
Para una suma de enteros, también existe una alternativa más específica:
int suma = numeros.stream()
    .mapToInt(Integer::intValue)
    .sum();
Usa reduce() cuando necesites combinar elementos en un resultado acumulado; para operaciones numéricas habituales, los métodos especializados suelen ser más claros.
5. Operaciones intermedias frente a terminales
Esta distinción es fundamental.
Tipo
Operaciones
Qué hacen
Intermedias
filter, map, sorted, distinct
Configuran el procesamiento y devuelven otro Stream
Terminales
toList, collect, reduce, count, forEach
Ejecutan el procesamiento y producen el resultado final
Los Streams son normalmente perezosos (lazy): las operaciones intermedias no se ejecutan hasta que se invoca una operación terminal.
Por ejemplo:
List<Integer> resultado = numeros.stream()
    .filter(n -> n > 3)
    .map(n -> n * 2)
    .toList();
Primero se define el filtrado, después la transformación y, al llegar a toList(), se ejecuta el procesamiento.
Un Stream no se puede reutilizar después de una operación terminal.
Pregunta de comprobación
¿Qué resultado produce este código?
List<Integer> numeros = List.of(3, 1, 3, 2, 4);

List<Integer> resultado = numeros.stream()
    .filter(n -> n % 2 == 0)
    .map(n -> n * 10)
    .distinct()
    .sorted()
    .toList();
A. [10, 20, 30, 40]
B. [20, 40]
C. [40, 20]
D. [2, 4]
Comprobar
Correcto.
filter conserva 2 y 4; map los transforma en 20 y 40; distinct no elimina nada porque ya son distintos; sorted los mantiene en orden ascendente. toList() materializa el resultado.
Continuar con Optional
3.1. Java avanzado — Bloque 3: Optional y valores ausentes
Optional<T> representa un valor que puede estar presente o ausente. Su objetivo es expresar explícitamente que una operación podría no devolver un resultado, reduciendo el riesgo de errores por null.
1. Crear y utilizar un Optional
Optional<String> nombre = Optional.of("Ana");
Hay tres formas habituales de crearlo:
Optional.of("Ana");          // Valor no nulo; falla si recibe null
Optional.ofNullable(valor);  // Admite null y lo convierte en vacío
Optional.empty();            // Sin valor
Importante: Optional.of(null) lanza NullPointerException.
2. Operaciones principales
isPresent() e isEmpty()
Permiten comprobar si hay un valor.
if (nombre.isPresent()) {
    System.out.println(nombre.get());
}
Aunque esto es válido, normalmente conviene utilizar alternativas que expresen directamente qué hacer con el valor.
orElse() y orElseGet()
Ambos proporcionan un valor alternativo si el Optional está vacío.
String nombre = optional.orElse("Desconocido");
La diferencia importante está en la evaluación:
String nombre = optional.orElse(calcularNombre());
calcularNombre() se ejecuta incluso si el valor está presente.
En cambio:
String nombre = optional.orElseGet(
    () -> calcularNombre()
);
La función solo se ejecuta cuando el Optional está vacío. Esto resulta útil si calcular el valor alternativo tiene un coste o produce efectos secundarios.
orElseThrow()
Permite lanzar una excepción si no hay valor:
Usuario usuario = repositorio.buscarPorId(id)
    .orElseThrow(() ->
        new UsuarioNoEncontradoException(id)
    );
Este patrón es frecuente en servicios Spring Boot: recuperas el usuario o comunicas explícitamente que no existe.
map() y filter()
map() transforma el valor si está presente:
Optional<String> nombre = Optional.of("Ana");

Optional<Integer> longitud = nombre.map(String::length);
// Optional con 3
filter() conserva el valor solo si cumple la condición:
Optional<String> resultado = nombre
    .filter(n -> n.length() >= 5);
// Optional.empty()
Si el Optional está vacío, ambas operaciones mantienen ese estado sin ejecutar la transformación o el predicado.
3. ¿Cuándo utilizar Optional?
Es habitual utilizarlo como tipo de retorno cuando una búsqueda puede no encontrar resultados:
Optional<Usuario> buscarPorId(Long id);
Esto obliga al consumidor a considerar la posibilidad de ausencia.
No es recomendable utilizarlo indiscriminadamente en todos los campos, parámetros o variables. En particular, en entidades JPA y DTO suele ser preferible seguir las convenciones del framework y del modelo.
Y recuerda: Optional no elimina por completo los NullPointerException. Si una API devuelve null en vez de un Optional, o se pasa una referencia nula al propio Optional, todavía pueden producirse errores.
Pregunta de comprobación
¿Cuál es la diferencia entre estas dos expresiones?
optional.orElse(calcularValor());
optional.orElseGet(() -> calcularValor());
A. Ambas ejecutan calcularValor() únicamente si el Optional está vacío.
B. orElse() evalúa el valor alternativo siempre; orElseGet() solo lo calcula si hace falta.
C. orElseGet() siempre ejecuta el cálculo y orElse() nunca.
D. orElse() devuelve un Optional y orElseGet() devuelve siempre un String.
Comprobar
Correcto.
orElse() recibe un argumento que ya se ha evaluado antes de invocar el método. orElseGet() recibe un Supplier, que se ejecuta únicamente cuando no hay valor.
Continuar con genéricos

3.1. Java avanzado — Bloque 4: Genéricos, wildcards y PECS
Los genéricos permiten escribir código reutilizable y seguro en cuanto a tipos, evitando conversiones innecesarias y errores detectables en tiempo de compilación.
1. Genéricos (Generics)
Ya los utilizas en colecciones:
List<String> nombres = new ArrayList<>();
Map<Long, Usuario> usuarios = new HashMap<>();
List<String> indica que la lista contiene cadenas. El compilador impide introducir otros tipos incompatibles.
También puedes crear clases genéricas:
public class Caja<T> {
    private T contenido;

    public void guardar(T contenido) {
        this.contenido = contenido;
    }

    public T obtener() {
        return contenido;
    }
}
T es un parámetro de tipo. Puedes utilizar la clase con distintos tipos:
Caja<String> caja = new Caja<>();
caja.guardar("Hola");

String texto = caja.obtener();
Otros nombres convencionales son E para elemento, K para clave, V para valor y N para número.
2. Bounded types: limitar los tipos permitidos
Puedes restringir un parámetro genérico para que solo acepte tipos que cumplan un requisito.
public static <T extends Number> double duplicar(T numero) {
    return numero.doubleValue() * 2;
}
Aquí T extends Number significa que T debe ser Number o un subtipo, como Integer o Double.
También puedes imponer varias restricciones:
<T extends Number & Comparable<T>>
La clase límite, si existe, debe aparecer primero; después pueden aparecer las interfaces.
¿Para qué sirve? Para permitir únicamente tipos que proporcionen las capacidades que necesita el método.
3. Wildcards: ?, ? extends y ? super
Un wildcard representa un tipo desconocido.
? extends T: límite superior
public static double sumar(List<? extends Number> numeros) {
    double total = 0;

    for (Number numero : numeros) {
        total += numero.doubleValue();
    }

    return total;
}
Acepta listas de Integer, Double y otros subtipos de Number.
Puedes leer sus elementos como Number, pero no añadir arbitrariamente un Integer o un Double: la lista podría ser, por ejemplo, una List<Double>.
? super T: límite inferior
public static void agregarEnteros(List<? super Integer> destino) {
    destino.add(10);
    destino.add(20);
}
Acepta listas de Integer, Number u Object. Puedes añadir Integer con seguridad, pero al leer elementos solo puedes tratarlos con seguridad como Object.
?: tipo desconocido
List<?> elementos;
Representa una lista de algún tipo desconocido. Puedes leer sus elementos como Object, pero no añadir un valor arbitrario (salvo null).
4. PECS: la regla que debes recordar
PECS = Producer Extends, Consumer Super.
    • Producer (extends): si una estructura te proporciona valores para leer, utiliza ? extends T.
    • Consumer (super): si una estructura recibe valores que tú produces, utiliza ? super T.
Por ejemplo, copiar elementos de una lista fuente a un destino:
public static <T> void copiar(
        List<? extends T> origen,
        List<? super T> destino) {

    for (T elemento : origen) {
        destino.add(elemento);
    }
}
El origen produce valores T; el destino consume valores T.
Un detalle importante: PECS es una regla práctica, no una obligación para todos los métodos. Si necesitas leer y escribir elementos de un tipo concreto, List<T> puede ser la elección más adecuada.
Pregunta de comprobación
Tienes este método:
public static void procesar(List<? extends Number> numeros) {
    Number n = numeros.get(0);
}
¿Por qué no puedes añadir de forma segura un Integer dentro de numeros?
A. Porque extends solo funciona con clases abstractas.
B. Porque la lista podría ser una List<Double> u otra lista de un subtipo de Number.
C. Porque Java no permite leer elementos de una lista genérica.
D. Porque Number no es una clase de Java.
Comprobar
Correcto.
List<? extends Number> podría referirse a List<Double>. Añadir un Integer rompería la seguridad de tipos. Por eso puedes leer como Number, pero no añadir arbitrariamente subtipos de Number.
Continuar con igualdad, records y enums




3.1. Java avanzado — Bloque 5: equals(), hashCode(), record, enum e inmutabilidad
Estos conceptos son importantes para trabajar con colecciones, modelar datos y diseñar servicios backend robustos.
1. equals() y hashCode()
Por defecto, Object.equals() compara identidad: comprueba si dos referencias apuntan al mismo objeto. Puedes sobrescribirlo para definir igualdad lógica.
class Usuario {
    private final Long id;

    Usuario(Long id) {
        this.id = id;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (!(obj instanceof Usuario otro)) return false;
        return Objects.equals(id, otro.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }
}
En este ejemplo, dos usuarios con el mismo id se consideran iguales.
Reglas fundamentales:
    • Si a.equals(b) es true, sus hashCode() deben coincidir.
    • Dos objetos con el mismo hash no tienen por qué ser iguales.
    • Si sobrescribes equals(), debes mantener coherente hashCode().
    • La igualdad debe ser reflexiva, simétrica, transitiva y consistente.
Esto es esencial para que HashSet y HashMap funcionen correctamente con objetos propios.
2. record: clases para transportar datos
Desde Java 16, los record permiten declarar tipos de datos de forma concisa.
public record UsuarioDTO(Long id, String nombre) {}
Java genera automáticamente:
    • Constructor canónico.
    • Accesores id() y nombre().
    • equals() y hashCode().
    • toString().
Uso:
UsuarioDTO usuario = new UsuarioDTO(1L, "Ana");

System.out.println(usuario.nombre()); // Ana
Los record son implícitamente finales y sus componentes son campos finales. Son útiles para DTO, respuestas de APIs y datos que no necesitan identidad mutable.
Matiz: un record no garantiza inmutabilidad profunda. Si un componente contiene una lista mutable, esa lista podría seguir modificándose.
3. enum: conjunto fijo de valores
Un enum representa un conjunto cerrado de constantes.
public enum EstadoPedido {
    PENDIENTE,
    PAGADO,
    ENVIADO,
    CANCELADO
}
Uso:
EstadoPedido estado = EstadoPedido.PAGADO;

if (estado == EstadoPedido.PAGADO) {
    System.out.println("Pedido pagado");
}
Puedes añadir campos, constructores y métodos a un enum:
public enum Prioridad {
    BAJA(1),
    MEDIA(2),
    ALTA(3);

    private final int nivel;

    Prioridad(int nivel) {
        this.nivel = nivel;
    }

    public int nivel() {
        return nivel;
    }
}
Son preferibles a cadenas arbitrarias cuando los valores válidos están definidos de antemano.
4. Clases inmutables
Un objeto es inmutable cuando su estado no puede cambiar después de construirse.
Ejemplo:
public final class Dinero {
    private final BigDecimal cantidad;

    public Dinero(BigDecimal cantidad) {
        this.cantidad = Objects.requireNonNull(cantidad);
    }

    public BigDecimal cantidad() {
        return cantidad;
    }
}
Para diseñar clases inmutables:
    1. Declara la clase final cuando quieras impedir subclases.
    2. Usa campos private final.
    3. Inicializa el estado en el constructor.
    4. No expongas métodos que modifiquen el estado.
    5. Si almacenas objetos mutables, realiza copias defensivas cuando sea necesario, tanto al recibirlos como al devolverlos.
La inmutabilidad simplifica el razonamiento sobre el estado y puede facilitar la concurrencia, aunque no convierte automáticamente en thread-safe cualquier objeto que la contenga.
Pregunta de comprobación
Tienes esta clase:
public record Equipo(List<String> miembros) {}
¿Cuál es la afirmación correcta?
A. El record garantiza que la lista no se pueda modificar.
B. El record genera equals() y hashCode(), pero la lista puede seguir siendo mutable.
C. Un record no puede contener referencias a objetos.
D. Es obligatorio implementar manualmente todos los métodos de Object.
Comprobar
Correcto.
El record genera métodos basados en sus componentes, pero no impide modificar el contenido de una lista mutable. Para protegerla, podrías copiarla en el constructor mediante List.copyOf(miembros), que crea una lista no modificable.
Continuar con excepciones avanzadas


Fase 3 — Java avanzado
Bloque 6: Excepciones, try-with-resources y excepciones propias
1. Excepciones en Java
Una excepción representa una situación que interrumpe el flujo normal de ejecución. Java distingue principalmente dos categorías de excepciones comprobadas y las no comprobadas.
Tipo
Característica
Ejemplo
Checked
El compilador exige capturarla o declararla con throws.
IOException
Unchecked
No exige capturarla ni declararla.
IllegalArgumentException, NullPointerException
Las excepciones no comprobadas heredan de RuntimeException; las comprobadas suelen heredar de Exception, sin contar RuntimeException y sus subclases.
try, catch y finally
try {
    int resultado = 10 / 0;
} catch (ArithmeticException e) {
    System.err.println("No se puede dividir entre cero");
} finally {
    System.out.println("Esto se ejecuta normalmente siempre");
}
    • try: contiene el código que puede lanzar una excepción.
    • catch: captura y gestiona una excepción del tipo indicado.
    • finally: se ejecuta normalmente tanto si hay excepción como si no; se utiliza para tareas de limpieza que no dependan de recursos gestionados con try-with-resources.
Puedes capturar varios tipos:
try {
    procesarArchivo();
} catch (IOException | SecurityException e) {
    System.err.println("Error procesando el archivo: " + e.getMessage());
}
Evita capturar Exception indiscriminadamente si no puedes gestionar correctamente todos los errores que incluye.
2. throw frente a throws
Son conceptos distintos:
    • throw: lanza una excepción concreta.
    • throws: declara que un método puede propagar determinadas excepciones.
public void validarEdad(int edad) {
    if (edad < 18) {
        throw new IllegalArgumentException("Debe ser mayor de edad");
    }
}

public String leerArchivo(String ruta) throws IOException {
    return Files.readString(Path.of(ruta));
}
En el primer método, el propio código lanza una excepción no comprobada. En el segundo, declara que puede producirse una IOException, que el llamador tendrá que capturar o declarar.
3. try-with-resources
Se utiliza para gestionar recursos que implementan AutoCloseable, como archivos, flujos de entrada o conexiones JDBC.
Java cierra automáticamente los recursos al salir del bloque, incluso si se produce una excepción.
import java.io.BufferedReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public String leerPrimeraLinea(Path ruta) throws IOException {
    try (BufferedReader reader = Files.newBufferedReader(ruta)) {
        return reader.readLine();
    }
}
Esto evita tener que cerrar manualmente el lector en un bloque finally.
Puedes declarar varios recursos:
try (var input = Files.newInputStream(Path.of("entrada.txt"));
     var output = Files.newOutputStream(Path.of("salida.txt"))) {

    input.transferTo(output);
}
Se cierran en orden inverso al de su declaración: primero output y después input.
4. Diseñar excepciones propias
Conviene crear una excepción específica cuando un error representa un concepto importante de tu dominio o aplicación.
Por ejemplo, en una API que gestiona tareas:
public class TareaNoEncontradaException extends RuntimeException {
    public TareaNoEncontradaException(Long id) {
        super("No se ha encontrado la tarea con ID: " + id);
    }
}
Podrías utilizarla desde un servicio:
public Tarea buscarTarea(Long id) {
    return repositorio.findById(id)
        .orElseThrow(() -> new TareaNoEncontradaException(id));
}
Así expresas claramente qué ha fallado, en lugar de devolver null o lanzar una excepción genérica.
¿Cuándo elegir una excepción comprobada o no comprobada?
    • Checked: cuando el llamador puede gestionar razonablemente el problema y quieres obligarlo a contemplarlo, como en determinadas operaciones de entrada/salida.
    • Unchecked: para errores de programación, argumentos inválidos o situaciones de dominio que se propagan hacia una capa superior para ser gestionadas centralmente. Es habitual en aplicaciones Spring.
No crees excepciones propias para cada error trivial: úsalas cuando aporten significado o permitan una gestión diferenciada.
Pregunta de comprobación
Tienes este código:
public Tarea buscar(Long id) {
    return repositorio.findById(id)
        .orElseThrow(() -> new TareaNoEncontradaException(id));
}
¿Qué afirmación es correcta?
A. orElseThrow solo puede lanzar excepciones comprobadas.
B. Si no existe la tarea, se lanza la excepción indicada; si existe, se devuelve la tarea.
C. La excepción se captura automáticamente y el método devuelve null.
D. TareaNoEncontradaException debe heredar obligatoriamente de Exception.
Comprobar
Correcto.
La respuesta es B. orElseThrow devuelve el valor si existe; si el Optional está vacío, evalúa la función suministrada y lanza la excepción resultante. Esta puede ser comprobada o no comprobada, según su tipo y la firma del método. 
Continuar al bloque 7

Fase 3 — Java avanzado
Bloque 7: Concurrencia y multithreading
La concurrencia permite que varias tareas progresen durante el mismo periodo. En Java es importante distinguir entre crear hilos, coordinar tareas y proteger los datos compartidos.
1. Thread y Runnable
Un Thread representa un hilo de ejecución. Runnable representa una tarea que puede ejecutarse en un hilo.
Runnable tarea = () -> {
    System.out.println("Ejecutando tarea");
};

Thread hilo = new Thread(tarea);
hilo.start();
Importante: start() inicia un hilo nuevo; llamar a run() directamente ejecuta el método en el hilo actual.
En aplicaciones reales, normalmente es preferible delegar la ejecución a un gestor de hilos.
2. ExecutorService
Permite ejecutar tareas mediante un pool de hilos reutilizables, sin tener que gestionar cada Thread manualmente.
import java.util.concurrent.*;

ExecutorService executor = Executors.newFixedThreadPool(4);

try {
    Future<Integer> resultado = executor.submit(() -> {
        return 10 + 20;
    });

    System.out.println(resultado.get()); // 30
} finally {
    executor.shutdown();
}
    • submit() envía una tarea y devuelve un Future.
    • Future.get() obtiene el resultado, pero bloquea hasta que esté disponible.
    • shutdown() deja de aceptar nuevas tareas y permite terminar las ya enviadas.
En código de producción también hay que considerar los límites del pool, el tiempo de espera y el tratamiento de errores.
3. Condiciones de carrera y synchronized
Una condición de carrera (race condition) ocurre cuando el resultado depende del orden impredecible en que varios hilos acceden a datos compartidos.
Por ejemplo, contador++ no es una operación atómica: implica leer, incrementar y escribir.
class Contador {
    private int valor;

    public synchronized void incrementar() {
        valor++;
    }

    public synchronized int obtener() {
        return valor;
    }
}
synchronized garantiza que solo un hilo a la vez entre en esos métodos sobre la misma instancia. Para que la protección funcione, los accesos relevantes al estado compartido deben respetar el mismo mecanismo de sincronización.
4. volatile y AtomicInteger
volatile garantiza visibilidad entre hilos para una variable: cuando un hilo escribe un valor, otros hilos que la leen pueden observar esa actualización conforme a las reglas de memoria de Java.
Pero no hace atómicas las operaciones compuestas como contador++.
Si necesitas un contador concurrente sencillo, puedes usar AtomicInteger:
import java.util.concurrent.atomic.AtomicInteger;

AtomicInteger contador = new AtomicInteger();

contador.incrementAndGet();
System.out.println(contador.get()); // 1
5. ¿Qué elegir?
Necesidad
Herramienta habitual
Ejecutar tareas concurrentes
ExecutorService
Obtener el resultado de una tarea
Future
Proteger una sección crítica
synchronized
Compartir una variable con visibilidad garantizada
volatile
Actualizar atómicamente un contador
AtomicInteger
Idea clave: utilizar varios hilos no garantiza que un programa sea más rápido. Hay costes de coordinación, bloqueos y competencia por recursos; además, el diseño debe evitar condiciones de carrera y bloqueos mutuos (deadlocks).
Pregunta de comprobación
Dos hilos ejecutan simultáneamente contador++ sobre un int compartido. ¿Cuál es la afirmación correcta?
A. Es seguro porque incrementar un int siempre es atómico.
B. Declarar el contador volatile garantiza que no se pierdan incrementos.
C. Puede haber una condición de carrera; se puede usar synchronized o AtomicInteger.
D. Java impide que dos hilos accedan a la misma variable.
Comprobar
Correcto.
La respuesta es C. El incremento implica varias operaciones y dos hilos pueden sobrescribir sus resultados. synchronized permite proteger la operación y AtomicInteger.incrementAndGet() ofrece un incremento atómico.
Continuar al bloque 8

Fase 3 — Java avanzado
Bloque 8: Colecciones concurrentes y CompletableFuture
En el bloque anterior vimos cómo ejecutar tareas con varios hilos. Ahora vamos a estudiar dos herramientas para trabajar con datos y operaciones asíncronas de forma segura.
1. Colecciones concurrentes
Las colecciones habituales, como HashMap o ArrayList, no garantizan por sí solas que las modificaciones concurrentes sean seguras.
Java ofrece alternativas:
Colección
Uso principal
ConcurrentHashMap
Mapa compartido entre varios hilos.
CopyOnWriteArrayList
Listas con muchas lecturas y pocas modificaciones.
BlockingQueue
Transferir elementos entre productores y consumidores, esperando cuando corresponda.
Ejemplo con ConcurrentHashMap:
import java.util.concurrent.ConcurrentHashMap;

ConcurrentHashMap<String, Integer> visitas =
    new ConcurrentHashMap<>();

visitas.merge("inicio", 1, Integer::sum);
visitas.merge("inicio", 1, Integer::sum);

System.out.println(visitas.get("inicio")); // 2
merge() permite actualizar el valor de una clave de forma segura frente a modificaciones concurrentes. En cambio, una secuencia de operaciones separadas sobre el mapa no se vuelve automáticamente atómica en su conjunto.
2. CompletableFuture
CompletableFuture permite ejecutar tareas asíncronas, transformar sus resultados y encadenar operaciones sin bloquear el hilo en cada paso.
import java.util.concurrent.CompletableFuture;

CompletableFuture
    .supplyAsync(() -> "Juan")
    .thenApply(nombre -> "Hola, " + nombre)
    .thenAccept(System.out::println);
Flujo:
    1. supplyAsync() ejecuta una tarea que produce un resultado.
    2. thenApply() transforma ese resultado.
    3. thenAccept() consume el resultado sin devolver otro valor.
Por defecto, estas operaciones asíncronas suelen utilizar el ForkJoinPool.commonPool(). En aplicaciones reales puedes proporcionar un Executor propio para controlar la ejecución.
3. Combinar tareas asíncronas
Si dos operaciones son independientes, puedes ejecutarlas en paralelo y combinar sus resultados:
CompletableFuture<Integer> precio =
    CompletableFuture.supplyAsync(() -> 100);

CompletableFuture<Integer> envio =
    CompletableFuture.supplyAsync(() -> 10);

CompletableFuture<Integer> total =
    precio.thenCombine(envio, Integer::sum);

System.out.println(total.join()); // 110
    • thenCombine() combina los resultados de dos futuros.
    • join() espera el resultado y propaga los errores mediante CompletionException.
    • get() también espera, pero puede lanzar excepciones comprobadas como InterruptedException y ExecutionException.
4. Gestionar errores asíncronos
Puedes recuperar un resultado alternativo si falla una operación:
CompletableFuture<Integer> resultado =
    CompletableFuture
        .supplyAsync(() -> {
            throw new IllegalStateException("Error");
        })
        .exceptionally(error -> 0);
En este ejemplo, el resultado final será 0 si la operación falla. En producción, conviene registrar el error y decidir explícitamente qué fallos se pueden recuperar.
Idea clave: las colecciones concurrentes protegen determinadas operaciones sobre datos compartidos; CompletableFuture ayuda a coordinar tareas asíncronas. Son problemas distintos, aunque pueden utilizarse juntos.
Pregunta de comprobación
Tienes dos llamadas independientes a servicios externos y quieres combinarlas cuando ambas hayan terminado. ¿Qué opción encaja mejor?
A. ConcurrentHashMap, porque ejecuta automáticamente las llamadas en paralelo.
B. CompletableFuture y thenCombine(), para combinar los resultados de ambas tareas.
C. volatile, porque hace asíncronas las llamadas.
D. Thread.sleep(), para garantizar que ambas llamadas hayan terminado.
Comprobar
Correcto.
La respuesta es B. CompletableFuture permite representar y coordinar las tareas; thenCombine() aplica una función cuando ambos futuros han completado correctamente. Para gestionar también los fallos de cualquiera de ellos, debes definir el tratamiento de errores adecuado.
Continuar al bloque 9

Fase 3 — Java avanzado
Bloque 9: Anotaciones y reflexión
Las anotaciones aportan metadatos al código. La reflexión permite inspeccionar clases, métodos, campos y constructores durante la ejecución. Ambas tecnologías son importantes en frameworks como Spring y Hibernate.
1. Anotaciones
Una anotación añade información que pueden interpretar el compilador, herramientas o frameworks.
Ejemplos habituales:
    • @Override: indica que un método sobrescribe otro.
    • @Deprecated: marca un elemento obsoleto.
    • @SuppressWarnings: suprime determinadas advertencias.
    • @Entity, @Service, @RestController: anotaciones utilizadas en aplicaciones Spring/JPA.
Puedes definir tus propias anotaciones:
import java.lang.annotation.*;

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface Auditable {
    String accion();
}
    • @Retention(RetentionPolicy.RUNTIME): permite consultar la anotación en ejecución.
    • @Target(ElementType.METHOD): limita su uso a métodos.
    • accion() define un atributo de la anotación.
Uso:
@Auditable(accion = "crear-tarea")
public void crearTarea() {
    // Crear tarea
}
2. Reflexión (Reflection)
Con reflexión puedes inspeccionar una clase en tiempo de ejecución.
Class<?> tipo = Tarea.class;

System.out.println(tipo.getName());

for (var metodo : tipo.getDeclaredMethods()) {
    System.out.println(metodo.getName());
}
También puedes leer una anotación:
var metodo = TareaService.class
    .getDeclaredMethod("crearTarea");

Auditable auditoria = metodo.getAnnotation(Auditable.class);

if (auditoria != null) {
    System.out.println(auditoria.accion());
}
Este mecanismo puede servir para crear sistemas de auditoría, serializadores o frameworks que detecten comportamientos declarados mediante anotaciones.
3. Cargar clases dinámicamente
La reflexión permite resolver una clase a partir de su nombre:
Class<?> tipo = Class.forName("com.ejemplo.Tarea");
Esto es útil cuando el tipo se determina mediante configuración. Por ejemplo, un motor genérico de procesamiento puede resolver qué entidad debe manejar sin codificar cada entidad de forma fija.
Sin embargo, Class.forName() puede lanzar ClassNotFoundException, y resolver una clase no garantiza que sea del tipo esperado. Conviene validar el tipo antes de utilizarlo.
4. Ventajas y riesgos
Ventajas
Riesgos
Permite crear mecanismos genéricos.
Los errores pueden aparecer en ejecución.
Facilita la configuración declarativa.
Puede dificultar la lectura y depuración.
Es útil para frameworks y herramientas.
El acceso reflectivo puede tener restricciones de acceso y costes adicionales.
Criterio profesional: utiliza reflexión cuando aporte flexibilidad real, especialmente en infraestructura y frameworks. Para lógica de negocio normal, suele ser preferible el acceso directo y tipado estáticamente.
Pregunta de comprobación
Estás desarrollando un framework que debe detectar en ejecución qué métodos tienen la anotación @Auditable. ¿Qué necesitas para poder leer esa anotación durante la ejecución?
A. Declarar siempre la anotación con @Retention(RetentionPolicy.SOURCE).
B. Usar @Retention(RetentionPolicy.RUNTIME) e inspeccionar los métodos mediante reflexión.
C. Heredar la anotación de RuntimeException.
D. Convertir todos los métodos en static.
Comprobar
Correcto.
La respuesta es B. RUNTIME conserva la anotación para consultarla en ejecución, y la reflexión permite localizar los métodos y leer sus metadatos.
Continuar al bloque 10
Fase 3 — Java avanzado
Bloque 10: JVM, memoria y Garbage Collector
Este bloque explica qué ocurre cuando Java ejecuta tu código: cómo organiza la memoria, cómo gestiona los objetos y por qué pueden aparecer problemas de rendimiento.
1. JVM, JDK y JRE
    • JVM (Java Virtual Machine): ejecuta el bytecode de Java.
    • JRE (Java Runtime Environment): concepto de entorno de ejecución, con la JVM y las bibliotecas necesarias.
    • JDK (Java Development Kit): herramientas para desarrollar, compilar y ejecutar programas Java.
Flujo de ejecución:
Código fuente .java
Compilador javac
Bytecode .class
JVM: interpretación y compilación JIT
Ejecución en la máquina
El compilador JIT (Just-In-Time) puede compilar partes del bytecode a código máquina durante la ejecución para mejorar el rendimiento.
2. Stack y Heap
La JVM utiliza distintas áreas de memoria con responsabilidades diferentes.
Área
Función
Stack de cada hilo
Marcos de llamadas, variables locales y datos de ejecución de los métodos.
Heap
Almacenamiento de objetos y arrays.
Metaspace
Metadatos de clases; normalmente utiliza memoria nativa.
Ejemplo:
public void procesar() {
    int cantidad = 10;
    Tarea tarea = new Tarea();
}
Conceptualmente:
    • cantidad es una variable local cuyo valor pertenece al marco de ejecución del método.
    • tarea es una variable local que contiene una referencia.
    • El objeto creado con new Tarea() normalmente se almacena en el heap.
Cuando termina el método, su marco de ejecución desaparece. El objeto puede seguir existiendo si todavía hay referencias accesibles a él.
3. Garbage Collector (GC)
El Garbage Collector recupera memoria de objetos que ya no son alcanzables desde las raíces de la JVM, como referencias activas de hilos y campos estáticos relevantes.
Tarea tarea = new Tarea();
tarea = null;
Si no queda ninguna referencia accesible al objeto, este pasa a ser candidato para la recolección.
Importante:
    • No puedes garantizar exactamente cuándo se ejecutará el GC.
    • Asignar null no obliga a liberar inmediatamente la memoria.
    • El GC gestiona memoria de objetos, pero no sustituye el cierre explícito de archivos, conexiones o sockets.
4. Fugas de memoria en Java
Aunque Java tenga GC, puedes provocar una fuga de memoria si mantienes referencias a objetos que ya no necesitas.
private static final List<byte[]> CACHE = new ArrayList<>();

public void guardarDatos() {
    CACHE.add(new byte[1_000_000]);
}
Si se llama repetidamente a guardarDatos(), la lista estática conserva las referencias a los arrays. El GC no puede recuperarlos mientras sigan siendo alcanzables.
En aplicaciones Spring, una caché sin límites, una colección estática o una suscripción que nunca se libera pueden producir problemas similares.
5. Errores de memoria habituales
    • StackOverflowError: por ejemplo, una recursión que no termina.
    • OutOfMemoryError: la JVM no puede satisfacer una solicitud de memoria.
    • Presión de GC: demasiadas asignaciones o una gran cantidad de objetos vivos pueden perjudicar el rendimiento.
Idea clave: Java automatiza la gestión de memoria, pero el desarrollador sigue siendo responsable del ciclo de vida lógico de los objetos y de evitar retener referencias innecesarias.
Pregunta de comprobación
Una aplicación Spring mantiene miles de objetos en una lista static y el consumo de memoria aumenta continuamente. ¿Por qué podría no solucionarlo el Garbage Collector?
A. Porque Java no tiene Garbage Collector en aplicaciones Spring.
B. Porque los objetos referenciados por la lista siguen siendo alcanzables y no se consideran basura.
C. Porque el GC solo libera variables locales del stack.
D. Porque asignar null a cualquier variable desactiva el GC.
Comprobar
Correcto.
La respuesta es B. La lista estática mantiene referencias a los objetos, por lo que estos siguen siendo alcanzables. Hay que revisar si se pueden eliminar elementos, limitar la caché o cambiar la estrategia de almacenamiento.
Continuar al bloque 11

Fase 3 — Java avanzado
Bloque 11: Patrones de diseño en Java
Los design patterns son soluciones reutilizables a problemas habituales de diseño de software. No son código que debas copiar siempre: son estructuras que puedes adaptar cuando el problema lo justifica.
Vamos a ver cuatro patrones especialmente útiles para entender proyectos Java y Spring Boot.
1. Strategy — intercambiar algoritmos
Permite definir distintas estrategias detrás de una misma interfaz y elegir cuál utilizar.
interface MetodoPago {
    void pagar(double importe);
}

class PagoTarjeta implements MetodoPago {
    public void pagar(double importe) {
        System.out.println("Tarjeta: " + importe);
    }
}

class PagoPayPal implements MetodoPago {
    public void pagar(double importe) {
        System.out.println("PayPal: " + importe);
    }
}

class ServicioPago {
    private final MetodoPago metodo;

    ServicioPago(MetodoPago metodo) {
        this.metodo = metodo;
    }

    void procesar(double importe) {
        metodo.pagar(importe);
    }
}
Uso:
ServicioPago servicio = new ServicioPago(new PagoTarjeta());
servicio.procesar(50);
Cuándo utilizarlo: cuando necesitas intercambiar comportamientos sin llenar una clase de if/else según el tipo de operación.
En Spring, puedes tener varias implementaciones de una interfaz e inyectar la apropiada según la configuración o el contexto.
2. Factory — centralizar la creación
Una factoría encapsula la lógica que decide qué objeto crear.
class NotificadorFactory {
    static Notificador crear(String tipo) {
        return switch (tipo) {
            case "email" -> new NotificadorEmail();
            case "sms" -> new NotificadorSMS();
            default -> throw new IllegalArgumentException(
                "Tipo desconocido: " + tipo
            );
        };
    }
}
Así, el código que necesita un notificador no tiene que conocer todos los detalles de creación.
Cuándo utilizarlo: cuando crear objetos requiere decisiones, configuración o lógica que conviene centralizar.
3. Builder — construir objetos complejos
Es útil cuando un objeto tiene muchos parámetros opcionales. Evita constructores largos y difíciles de interpretar.
Tarea tarea = Tarea.builder()
    .titulo("Estudiar Java")
    .prioridad(2)
    .completada(false)
    .build();
Este ejemplo presupone que Tarea dispone de un builder implementado manualmente o generado por una biblioteca como Lombok. Java no genera automáticamente este patrón para una clase normal.
Cuándo utilizarlo: cuando quieres crear objetos configurables de forma legible, especialmente si tienen muchos campos opcionales.
4. Observer — notificar cambios
Permite que un objeto notifique a varios observadores cuando sucede un evento.
interface Observador {
    void actualizar(String evento);
}

class RegistroLog implements Observador {
    public void actualizar(String evento) {
        System.out.println("Evento: " + evento);
    }
}
Un publicador mantendría una colección de observadores y llamaría a actualizar() cuando ocurra el evento.
Cuándo utilizarlo: para desacoplar quien produce un evento de quienes reaccionan a él. En aplicaciones Spring puede relacionarse con eventos de aplicación, aunque el mecanismo concreto es diferente.
Resumen
Patrón
Problema que resuelve
Strategy
Cambiar algoritmos o comportamientos.
Factory
Centralizar decisiones de creación.
Builder
Construir objetos complejos de forma legible.
Observer
Notificar eventos a múltiples interesados.
No necesitas aplicar patrones por obligación. Si una solución sencilla funciona y se entiende, introducir abstracciones innecesarias puede empeorar el diseño.
Pregunta de comprobación
Tienes una aplicación de facturación que debe calcular descuentos mediante distintas reglas: descuento para clientes habituales, promociones y descuentos por volumen. Quieres añadir nuevas reglas sin modificar continuamente el servicio principal.
¿Qué patrón encaja mejor?
A. Singleton, para garantizar una única instancia del servicio.
B. Strategy, para encapsular cada regla de descuento como un comportamiento intercambiable.
C. Builder, para construir cada factura campo por campo.
D. Observer, para notificar a los clientes cuando cambia el descuento.
Comprobar
Correcto.
La respuesta es B. Cada regla puede implementar una interfaz común, por ejemplo EstrategiaDescuento, y el servicio utilizar la estrategia seleccionada sin necesitar conocer sus detalles internos.
Continuar al bloque 12

Fase 3 — Java avanzado
Bloque 12: SOLID aplicado a Java
SOLID es un conjunto de cinco principios de diseño orientado a objetos que ayudan a construir software mantenible, extensible y fácil de probar. Son especialmente relevantes antes de empezar con Spring Boot y la arquitectura por capas.
1. S — Single Responsibility Principle
Principio de responsabilidad única: una clase debe tener un único motivo principal para cambiar.
Mal diseño:
class UsuarioService {
    void registrarUsuario() { /* lógica de registro */ }
    void enviarEmail() { /* envío de correo */ }
    void guardarEnBaseDeDatos() { /* persistencia */ }
}
Mejor separar responsabilidades:
class UsuarioRepository {
    void guardar(Usuario usuario) { /* persistencia */ }
}

class EmailService {
    void enviar(String email) { /* envío */ }
}

class UsuarioService {
    private final UsuarioRepository repository;
    private final EmailService emailService;

    UsuarioService(UsuarioRepository repository,
                   EmailService emailService) {
        this.repository = repository;
        this.emailService = emailService;
    }
}
El servicio coordina el caso de uso; otras clases se ocupan de persistir y enviar correos.
2. O — Open/Closed Principle
Abierto a extensión, cerrado a modificación: deberías poder añadir comportamientos sin tener que modificar constantemente el código estable existente.
interface Descuento {
    double calcular(double precio);
}

class DescuentoPremium implements Descuento {
    public double calcular(double precio) {
        return precio * 0.8;
    }
}

class DescuentoNormal implements Descuento {
    public double calcular(double precio) {
        return precio;
    }
}
Un servicio puede recibir cualquier implementación de Descuento, sin conocer todas las variantes.
3. L — Liskov Substitution Principle
Principio de sustitución de Liskov: una implementación debe poder sustituir a su tipo base sin romper las expectativas del código que la utiliza.
Por ejemplo, si un método recibe una interfaz RepositorioTareas, todas sus implementaciones deberían respetar el contrato esperado: guardar, recuperar y comunicar los errores de forma coherente.
No basta con que una clase implemente la interfaz; debe comportarse de acuerdo con sus garantías.
4. I — Interface Segregation Principle
Segregación de interfaces: es mejor disponer de interfaces pequeñas y específicas que obligar a una clase a implementar operaciones que no necesita.
Mal diseño:
interface Trabajador {
    void programar();
    void gestionarPersonal();
    void desplegar();
}
Un programador que no gestiona personal estaría obligado a implementar un método irrelevante.
Mejor:
interface Programador {
    void programar();
}

interface GestorPersonal {
    void gestionarPersonal();
}

interface ResponsableDespliegue {
    void desplegar();
}
5. D — Dependency Inversion Principle
Inversión de dependencias: las políticas de alto nivel deberían depender de abstracciones, no directamente de implementaciones concretas.
En lugar de esto:
class PedidoService {
    private final MySqlPedidoRepository repository =
        new MySqlPedidoRepository();
}
Utiliza una abstracción:
class PedidoService {
    private final PedidoRepository repository;

    PedidoService(PedidoRepository repository) {
        this.repository = repository;
    }
}
PedidoRepository sería una interfaz. Puedes inyectar distintas implementaciones sin modificar el servicio.
Esto se relaciona directamente con la inyección de dependencias (DI) que veremos en Spring: el contenedor crea los objetos y proporciona sus dependencias.
Resumen
Principio
Pregunta que debes hacerte
SRP
¿Esta clase tiene responsabilidades distintas?
OCP
¿Puedo añadir una variante sin modificar el código estable?
LSP
¿Esta implementación respeta el contrato del tipo base?
ISP
¿Estoy obligando a implementar métodos innecesarios?
DIP
¿Dependo de una abstracción o de una clase concreta?
SOLID no significa crear una interfaz para absolutamente todo. El objetivo es reducir el acoplamiento y facilitar cambios justificados, no multiplicar clases sin necesidad.
Pregunta de comprobación
Tienes un InformeService que depende directamente de MySqlInformeRepository. Quieres poder cambiar a PostgreSQL o utilizar un repositorio simulado en los tests sin modificar el servicio.
¿Qué principio SOLID aborda más directamente este problema?
A. SRP: responsabilidad única.
B. OCP: abierto/cerrado.
C. DIP: inversión de dependencias.
D. ISP: segregación de interfaces.
Comprobar
Correcto.
La respuesta es C. El servicio debe depender de una abstracción, como InformeRepository, y recibir la implementación mediante el constructor. Así puedes sustituir el repositorio real por otra implementación o un doble de prueba.
Continuar al bloque 13
Fase 3 — Java avanzado
Bloque 13: Genéricos avanzados y diseño de APIs tipadas
Ya vimos los genéricos y los comodines (? extends, ? super). Ahora vamos a aplicarlos al diseño de APIs reutilizables, algo habitual en bibliotecas Java y en código de backend.
1. Métodos genéricos
Una clase puede no ser genérica y, aun así, tener métodos genéricos.
public static <T> T primero(List<T> elementos) {
    if (elementos.isEmpty()) {
        throw new IllegalArgumentException("Lista vacía");
    }

    return elementos.get(0);
}
<T> declara el parámetro de tipo del método. El compilador suele inferirlo a partir del argumento:
String nombre = primero(List.of("Ana", "Luis"));
Integer numero = primero(List.of(10, 20));
El mismo método funciona con distintos tipos sin perder seguridad estática.
2. Límites de tipo (bounded types)
Puedes restringir qué tipos acepta un genérico mediante extends.
public static <T extends Number> double sumar(
        List<T> numeros) {

    double total = 0;

    for (T numero : numeros) {
        total += numero.doubleValue();
    }

    return total;
}
T extends Number permite Integer, Double, Long y otros subtipos de Number, pero no String.
También puedes exigir que un tipo implemente una interfaz:
public static <T extends Comparable<T>> T mayor(
        T a, T b) {

    return a.compareTo(b) >= 0 ? a : b;
}
Así, el método puede comparar valores sin conocer su clase concreta, siempre que cumplan el contrato de Comparable<T>.
3. PECS: productor y consumidor
La regla práctica para elegir comodines es PECS: Producer Extends, Consumer Super.
    • ? extends T: cuando una estructura produce valores que quieres leer como T.
    • ? super T: cuando quieres introducir valores de tipo T en una estructura.
public static double sumar(
        List<? extends Number> valores) {

    return valores.stream()
        .mapToDouble(Number::doubleValue)
        .sum();
}
Puedes pasar una List<Integer> o una List<Double>.
Para copiar elementos a un destino:
public static <T> void copiar(
        List<? extends T> origen,
        List<? super T> destino) {

    destino.addAll(origen);
}
El origen produce valores T y el destino los consume.
4. Diseñar una respuesta genérica para una API
Los genéricos también sirven para crear estructuras de respuesta reutilizables:
public record ApiResponse<T>(
    boolean correcto,
    T datos,
    String mensaje
) {}
Puedes reutilizar el mismo tipo con distintos datos:
ApiResponse<Usuario> respuestaUsuario =
    new ApiResponse<>(true, usuario, "OK");

ApiResponse<List<Tarea>> respuestaTareas =
    new ApiResponse<>(true, tareas, "OK");
El compilador conserva el tipo de datos, evitando tener que recurrir a Object y conversiones manuales.
En una API Spring Boot, este patrón puede ser útil si tu equipo adopta un formato de respuesta común. No es obligatorio: envolver todas las respuestas en una estructura propia también puede añadir complejidad innecesaria.
Pregunta de comprobación
Quieres escribir un método que reciba una lista de cualquier subtipo de Number y calcule su suma. ¿Qué firma es la más adecuada?
A. double sumar(List<Number> valores)
B. double sumar(List<? extends Number> valores)
C. double sumar(List<? super Number> valores)
D. double sumar(List<Object> valores)
Comprobar
Correcto.
La respuesta es B. List<? extends Number> permite recibir listas de Integer, Double y otros subtipos de Number. La firma List<Number> no acepta directamente una List<Integer>, porque los genéricos de Java son invariantes.
Continuar al bloque 14
Fase 3 — Java avanzado
Bloque 14: I/O, NIO.2 y gestión de archivos
En backend es habitual leer CSV, procesar ficheros de configuración, generar informes y mover datos entre sistemas. Java ofrece las APIs de java.io y java.nio.file para estas operaciones.
1. Leer y escribir archivos con Files
Para operaciones comunes, Files y Path suelen ser la opción más sencilla.
import java.nio.file.Files;
import java.nio.file.Path;
import java.io.IOException;

Path ruta = Path.of("datos.txt");

String contenido = Files.readString(ruta);
Files.writeString(Path.of("salida.txt"), contenido);
    • Path representa una ruta del sistema de archivos.
    • Files proporciona operaciones para leer, escribir, copiar y consultar archivos.
    • Estas operaciones pueden lanzar IOException.
readString() lee el archivo completo en memoria. Para archivos grandes, conviene procesarlos progresivamente.
2. Procesar archivos línea a línea
Por ejemplo, para contar las líneas de un fichero sin cargarlo entero:
long lineas;

try (var stream = Files.lines(Path.of("datos.csv"))) {
    lineas = stream.count();
}

System.out.println(lineas);
Files.lines() devuelve un stream que mantiene un recurso abierto. Por eso se utiliza try-with-resources.
Para procesar cada línea:
try (var stream = Files.lines(Path.of("datos.csv"))) {
    stream.filter(linea -> !linea.isBlank())
          .forEach(System.out::println);
}
Este ejemplo filtra líneas vacías. No es todavía un parser CSV completo: los campos CSV pueden contener comas, comillas y saltos de línea que requieren tratamiento específico.
3. Copiar y mover archivos
import java.nio.file.*;

Path origen = Path.of("entrada.txt");
Path destino = Path.of("copia.txt");

Files.copy(origen, destino);

Files.move(
    destino,
    Path.of("procesado.txt"),
    StandardCopyOption.REPLACE_EXISTING
);
La copia falla si el destino ya existe, salvo que se indique una opción compatible como REPLACE_EXISTING.
El movimiento puede depender del sistema de archivos. Si necesitas un movimiento atómico, puedes solicitar ATOMIC_MOVE, aunque el sistema puede no soportarlo.
4. Directorios y búsqueda de archivos
Puedes recorrer un directorio usando DirectoryStream:
try (DirectoryStream<Path> archivos =
         Files.newDirectoryStream(Path.of("entrada"))) {

    for (Path archivo : archivos) {
        if (Files.isRegularFile(archivo)) {
            System.out.println(archivo.getFileName());
        }
    }
}
También puedes consultar propiedades:
Path archivo = Path.of("datos.csv");

if (Files.exists(archivo) && Files.isReadable(archivo)) {
    System.out.println(Files.size(archivo));
}
Ten presente que comprobar si un archivo existe y abrirlo son operaciones distintas: el estado puede cambiar entre ambas. Debes gestionar igualmente los errores al utilizarlo.
5. Cuándo usar cada API
API
Uso típico
Files.readString()
Archivos de texto pequeños.
Files.lines()
Procesamiento de texto línea a línea.
Files.newInputStream()
Lectura mediante un flujo de bytes.
Files.copy() / Files.move()
Copiar y mover archivos.
DirectoryStream
Recorrer entradas de un directorio.
Criterio práctico: para un procesador de CSV de backend, combina Path y Files con lectura incremental, validación de datos y gestión explícita de errores. Evita cargar ficheros grandes completos en memoria sin una razón.
Pregunta de comprobación
Vas a procesar un CSV de varios gigabytes y solo necesitas examinar sus líneas una a una. ¿Qué enfoque es más apropiado?
A. Usar siempre Files.readString() y guardar todo el contenido en un String.
B. Leer progresivamente, por ejemplo con Files.lines() dentro de try-with-resources, o con un lector de búfer.
C. Utilizar Files.copy() para cargar todas las líneas en memoria.
D. Convertir primero todo el archivo en un único array de bytes.
Comprobar
Correcto.
La respuesta es B. El procesamiento incremental evita mantener todo el archivo en memoria. Files.lines() debe cerrarse porque utiliza un recurso asociado al archivo; un BufferedReader también es una alternativa válida.
Continuar al bloque 15

Fase 3 — Java avanzado
Bloque 15: JDBC y transacciones
JDBC (Java Database Connectivity) es la API estándar de Java para interactuar con bases de datos relacionales. Aunque en Spring Boot normalmente utilizarás Spring Data JPA o JdbcTemplate, entender JDBC ayuda a comprender las conexiones, las consultas SQL y las transacciones.
1. Conectarse a una base de datos
Una conexión JDBC se representa mediante Connection. Habitualmente obtienes conexiones desde un DataSource, que gestiona cómo se proporcionan las conexiones.
import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.SQLException;

public void comprobarConexion(DataSource dataSource)
        throws SQLException {

    try (Connection conexion = dataSource.getConnection()) {
        System.out.println("Conexión obtenida");
    }
}
try-with-resources cierra la conexión al terminar. Si procede de un pool, normalmente la devuelve al pool, en lugar de destruir físicamente la conexión.
2. Consultas parametrizadas con PreparedStatement
Evita construir consultas SQL concatenando directamente valores recibidos del usuario.
Incorrecto:
String sql = "SELECT * FROM usuarios WHERE nombre = '" + nombre + "'";
Correcto:
String sql = "SELECT id, nombre FROM usuarios WHERE nombre = ?";

try (Connection con = dataSource.getConnection();
     var ps = con.prepareStatement(sql)) {

    ps.setString(1, nombre);

    try (var rs = ps.executeQuery()) {
        while (rs.next()) {
            System.out.println(rs.getLong("id"));
            System.out.println(rs.getString("nombre"));
        }
    }
}
PreparedStatement permite parametrizar los valores, reduce el riesgo de inyección SQL y evita tener que escapar manualmente esos valores.
3. Operaciones de escritura
Para insertar, actualizar o eliminar registros, normalmente utilizas executeUpdate():
String sql = "UPDATE usuarios SET nombre = ? WHERE id = ?";

try (Connection con = dataSource.getConnection();
     var ps = con.prepareStatement(sql)) {

    ps.setString(1, "Ana");
    ps.setLong(2, 10L);

    int filasAfectadas = ps.executeUpdate();
    System.out.println(filasAfectadas);
}
El número devuelto indica las filas afectadas, según la operación y el controlador JDBC.
4. Transacciones
Una transacción permite agrupar operaciones para que se confirmen o se reviertan como una unidad.
try (Connection con = dataSource.getConnection()) {
    con.setAutoCommit(false);

    try {
        // Operación A
        // Operación B

        con.commit();
    } catch (SQLException e) {
        con.rollback();
        throw e;
    }
}
Con setAutoCommit(false), las operaciones no se confirman automáticamente. Si una falla, rollback() revierte los cambios pendientes de esa transacción.
En código de producción también debes considerar qué ocurre si el propio rollback() falla y preservar el error original.
5. JDBC frente a Spring Data JPA
Tecnología
Qué aporta
JDBC
Control directo de SQL, conexiones y resultados.
JdbcTemplate
Simplifica JDBC y la gestión de recursos y excepciones.
Spring Data JPA
Abstracción ORM, entidades y repositorios.
JPA no elimina SQL de la aplicación: lo genera o permite ejecutarlo explícitamente. Debes seguir entendiendo las consultas, las transacciones y el rendimiento de la base de datos.
Pregunta de comprobación
Estás transfiriendo dinero entre dos cuentas. Debes restar el importe de una y sumarlo a la otra. ¿Qué enfoque garantiza que no quede aplicada solamente una de las operaciones si la segunda falla?
A. Ejecutar ambas operaciones con autoCommit activado.
B. Agruparlas en una transacción y ejecutar rollback() si falla alguna antes de confirmar.
C. Usar dos conexiones independientes y confirmar cada operación inmediatamente.
D. Capturar la excepción e ignorarla para que la transferencia continúe.
Comprobar
Correcto.
La respuesta es B. Ambas modificaciones deben formar parte de la misma transacción: se confirman juntas mediante commit() o se revierten mediante rollback() si se produce un error, siempre que la base de datos y las operaciones implicadas permitan esa atomicidad.
Continuar al bloque 16

Fase 3 — Java avanzado
Bloque 16: Testing con JUnit 5 y Mockito
En backend Java, los tests automatizados permiten comprobar que una clase se comporta como esperas y detectar regresiones cuando modificas el código. Vamos a distinguir entre tests unitarios, mocks y tests de integración.
1. JUnit 5: pruebas unitarias
JUnit permite ejecutar pruebas y verificar resultados mediante aserciones.
Supongamos esta clase:
public class Calculadora {
    public int sumar(int a, int b) {
        return a + b;
    }
}
Un test con JUnit 5:
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class CalculadoraTest {

    @Test
    void sumaDosNumeros() {
        Calculadora calculadora = new Calculadora();

        int resultado = calculadora.sumar(2, 3);

        assertEquals(5, resultado);
    }
}
Anotaciones y aserciones frecuentes:
    • @Test: identifica un método de prueba.
    • assertEquals(esperado, actual): compara valores.
    • assertTrue(condicion): comprueba que una condición sea verdadera.
    • assertThrows(Tipo.class, accion): verifica que una operación lance una excepción.
2. Mockito: aislar dependencias
Imagina que UsuarioService depende de un repositorio. Para probar la lógica del servicio, no necesitas conectarte a una base de datos real.
class UsuarioService {
    private final UsuarioRepository repository;

    UsuarioService(UsuarioRepository repository) {
        this.repository = repository;
    }

    boolean existe(Long id) {
        return repository.findById(id).isPresent();
    }
}
Test con Mockito y JUnit 5:
@ExtendWith(MockitoExtension.class)
class UsuarioServiceTest {

    @Mock
    UsuarioRepository repository;

    @InjectMocks
    UsuarioService service;

    @Test
    void devuelveTrueSiExisteUsuario() {
        when(repository.findById(1L))
            .thenReturn(Optional.of(new Usuario()));

        assertTrue(service.existe(1L));
    }
}
Conceptos importantes:
    • @Mock: crea un doble de prueba.
    • when(...).thenReturn(...): configura el resultado esperado.
    • @InjectMocks: crea el objeto probado e intenta inyectarle los mocks.
Mockito permite aislar dependencias, pero no demuestra que la base de datos o las consultas reales funcionen correctamente.
3. Test unitario frente a test de integración
Tipo
Qué comprueba
Unitario
Una unidad de código de forma aislada.
Integración
La interacción entre componentes reales, como servicio, repositorio y base de datos.
End-to-end (E2E)
Un flujo completo desde una entrada hasta el resultado final.
Por ejemplo, probar un servicio con un repositorio simulado es un test unitario. Probar el repositorio contra una base de datos real o de pruebas es un test de integración.
En Spring Boot, herramientas como @SpringBootTest permiten cargar el contexto de la aplicación para pruebas más amplias. No es necesario usarlo en todos los tests: suele ser más lento que una prueba unitaria aislada.
4. ¿Qué deberías probar?
Una estrategia razonable incluye:
    • Casos normales: el resultado esperado con datos válidos.
    • Casos límite: listas vacías, valores extremos y entradas opcionales.
    • Errores: datos inválidos, excepciones y dependencias que fallan.
    • Reglas de negocio: permisos, transiciones de estado y restricciones.
    • Integración: persistencia, configuración y comunicación entre componentes.
Criterio profesional: escribe tests que verifiquen el comportamiento observable, no detalles internos innecesarios. Un test debe detectar un defecto real y seguir siendo útil si refactorizas la implementación.
Pregunta de comprobación
Quieres comprobar la lógica de PedidoService sin acceder a una base de datos real. El servicio depende de PedidoRepository. ¿Cuál es el enfoque más adecuado para un test unitario?
A. Ejecutar siempre el test contra la base de datos de producción.
B. Crear un mock del repositorio, configurar sus respuestas y comprobar el resultado del servicio.
C. Eliminar el repositorio del servicio para que el test no tenga dependencias.
D. Usar exclusivamente @SpringBootTest en todas las pruebas, aunque no sea necesario.
Comprobar
Correcto.
La respuesta es B. Mockito permite simular el repositorio y comprobar la lógica del servicio de forma aislada. Después puedes añadir tests de integración específicos para verificar que la persistencia funciona realmente.
Continuar al bloque 17
Fase 3 — Java avanzado
Bloque 17: Maven, dependencias y ciclo de construcción
Maven es una herramienta de construcción (build tool) muy utilizada en proyectos Java. Gestiona las dependencias, compila el código, ejecuta tests y empaqueta la aplicación.
1. El archivo pom.xml
Maven configura el proyecto mediante un archivo pom.xml.
Ejemplo mínimo:
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.ejemplo</groupId>
    <artifactId>gestion-tareas</artifactId>
    <version>1.0.0</version>

    <properties>
        <maven.compiler.release>21</maven.compiler.release>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>
</project>
Los identificadores principales son:
    • groupId: grupo u organización del proyecto.
    • artifactId: nombre del artefacto.
    • version: versión del proyecto.
    • properties: propiedades de configuración, como la versión de Java.
La versión de Java configurada debe ser compatible con el JDK utilizado para compilar.
2. Gestionar dependencias
Si necesitas JUnit 5 para las pruebas, puedes declararlo así:
<dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.12.2</version>
    <scope>test</scope>
</dependency>
Maven descarga las dependencias necesarias desde los repositorios configurados y las mantiene en su caché local.
El ámbito test significa que esa dependencia se utiliza para compilar y ejecutar las pruebas, pero no forma parte del classpath normal de producción.
En proyectos reales, es importante mantener las versiones de dependencias controladas y actualizar las que tengan vulnerabilidades.
3. Ciclo de vida de Maven
Los comandos más habituales son:
Comando
Función
mvn compile
Compila el código principal.
mvn test
Ejecuta las pruebas unitarias configuradas.
mvn package
Compila, ejecuta las fases anteriores y genera el artefacto empaquetado.
mvn verify
Ejecuta las fases previas y las verificaciones configuradas.
mvn clean
Elimina normalmente el directorio target.
Por ejemplo:
mvn clean verify
Esto limpia la salida anterior y ejecuta el ciclo hasta la fase verify. Las comprobaciones concretas dependen de los plugins configurados en el proyecto.
4. ¿Qué es un artefacto?
Tras empaquetar un proyecto Java, Maven puede generar un archivo .jar en target/.
Un JAR contiene clases compiladas y recursos. Si se configura como JAR ejecutable, puede incluir las dependencias o disponer de mecanismos para cargarlas.
En Spring Boot, el plugin de Maven permite generar un JAR ejecutable que normalmente puedes arrancar con:
java -jar target/gestion-tareas-1.0.0.jar
El nombre exacto depende de la configuración del proyecto.
5. Maven y Spring Boot
En un proyecto Spring Boot, el pom.xml suele declarar el parent o el BOM de Spring Boot para gestionar versiones compatibles de dependencias, además de los starters necesarios.
Por ejemplo, spring-boot-starter-web incorpora dependencias para desarrollar aplicaciones web. Maven resuelve también las dependencias transitivas que esas bibliotecas necesitan.
Idea clave: Maven no es solo un descargador de bibliotecas. Define un proceso de construcción reproducible que puedes integrar en CI/CD para compilar, probar y empaquetar la aplicación.
Pregunta de comprobación
En un proyecto Java, ejecutas mvn clean verify. ¿Cuál es la afirmación más precisa?
A. Solo descarga dependencias; no compila ni ejecuta pruebas.
B. Limpia la salida anterior y ejecuta las fases del ciclo hasta verify, incluidas las pruebas y las verificaciones configuradas.
C. Genera siempre un JAR ejecutable de Spring Boot, aunque el proyecto no utilice Spring Boot.
D. Elimina las dependencias del repositorio local de Maven.
Comprobar
Correcto.
La respuesta es B. clean elimina la salida generada anteriormente y verify ejecuta las fases previas del ciclo, incluidas compilación y pruebas, además de las verificaciones configuradas.
Continuar al bloque 18

Fase 3 — Java avanzado
Bloque 18: Logging y gestión de errores en backend
En una aplicación backend, no basta con capturar excepciones: necesitas registrar información útil para diagnosticar fallos sin exponer datos sensibles ni ocultar errores.
1. Logging frente a System.out.println
En lugar de imprimir mensajes directamente por consola, es habitual utilizar una biblioteca de logging, como SLF4J con Logback, que es una combinación frecuente en Spring Boot.
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PedidoService {
    private static final Logger log =
        LoggerFactory.getLogger(PedidoService.class);

    public void procesar(Long pedidoId) {
        log.info("Procesando pedido {}", pedidoId);
    }
}
{} es un marcador que permite pasar el valor como argumento, sin concatenar manualmente cadenas.
2. Niveles de logging
Nivel
Uso habitual
TRACE
Detalles muy exhaustivos.
DEBUG
Información útil durante el desarrollo o diagnóstico.
INFO
Eventos normales relevantes.
WARN
Situaciones anómalas que no impiden necesariamente continuar.
ERROR
Fallos que requieren atención.
Ejemplo:
log.debug("Validando pedido {}", pedidoId);
log.info("Pedido {} procesado", pedidoId);
log.warn("Reintento para pedido {}", pedidoId);
log.error("Falló el procesamiento del pedido {}", pedidoId, e);
El último ejemplo registra también la excepción y su stack trace.
3. Capturar excepciones correctamente
Evita capturar una excepción para ignorarla:
try {
    procesarPedido();
} catch (Exception e) {
    // No hacer nada
}
Esto oculta el fallo y puede dejar el sistema en un estado inesperado.
En su lugar, decide si puedes recuperarte o si debes propagar el error:
try {
    procesarPedido();
} catch (IOException e) {
    log.error("No se pudo leer el archivo de pedidos", e);
    throw new IllegalStateException(
        "No se pudo completar el procesamiento", e
    );
}
La excepción original se conserva como causa. No conviene registrar el mismo error en cada capa y volver a registrarlo al final: eso puede generar logs duplicados. Registra el error donde tengas contexto útil o donde se gestione definitivamente.
4. Logging en Spring Boot
Spring Boot permite configurar los niveles de logging en application.properties:
logging.level.root=INFO
logging.level.com.ejemplo=DEBUG
La segunda propiedad activa DEBUG para el paquete indicado y sus subpaquetes.
En producción, ten cuidado con registrar contraseñas, tokens JWT, cookies, datos personales o contenido sensible de las peticiones. Los logs deben ayudar a diagnosticar problemas sin convertirse en una filtración de información.
5. Buenas prácticas
    • Incluye identificadores de operación o petición cuando ayuden a seguir una ejecución.
    • Registra excepciones con contexto útil y conserva su causa.
    • No utilices ERROR para sucesos normales.
    • No captures errores que no puedes gestionar solo para continuar como si nada.
    • Ajusta los niveles por entorno: DEBUG puede ser útil en desarrollo, pero demasiado ruidoso en producción.
Idea clave: un buen sistema de logging permite entender qué ha sucedido, dónde y en qué contexto, sin ocultar errores ni registrar información sensible.
Pregunta de comprobación
Un método captura una IOException, pero no puede recuperarse del fallo. ¿Cuál es el enfoque más adecuado?
A. Ignorar la excepción para que el programa siga ejecutándose.
B. Registrar el error con contexto útil y propagarlo, conservando la excepción original como causa cuando corresponda.
C. Registrar únicamente e.getMessage() y devolver siempre un resultado exitoso.
D. Convertir cualquier excepción en null, sin documentar ese comportamiento.
Comprobar
Correcto.
La respuesta es B. Si no puedes recuperarte, debes comunicar el fallo mediante una excepción adecuada y conservar su causa. Registra el error en el punto donde aporte contexto útil, evitando duplicar el mismo stack trace en todas las capas.
Continuar al bloque 19
Fase 3 — Java avanzado
Bloque 19: Streams avanzados y Collectors
La API Stream permite procesar colecciones de forma declarativa: filtrar, transformar, ordenar y agrupar datos sin escribir bucles manuales para cada operación.
1. Encadenar operaciones
Imagina que tienes una lista de pedidos y quieres obtener los identificadores de los pedidos superiores a 100 €, ordenados por importe.
List<Pedido> pedidos = obtenerPedidos();

List<Long> resultado = pedidos.stream()
    .filter(p -> p.getImporte() > 100)
    .sorted(Comparator.comparing(Pedido::getImporte))
    .map(Pedido::getId)
    .toList();
Operaciones utilizadas:
    • filter(): selecciona los elementos que cumplen una condición.
    • sorted(): ordena los elementos.
    • map(): transforma cada elemento.
    • toList(): recopila los resultados en una lista.
Las operaciones intermedias, como filter() y map(), son lazy: no procesan los elementos hasta que se ejecuta una operación terminal.
2. Agrupar con Collectors.groupingBy()
Supón que quieres agrupar pedidos por estado:
Map<String, List<Pedido>> porEstado = pedidos.stream()
    .collect(Collectors.groupingBy(Pedido::getEstado));
El resultado podría ser:
PENDIENTE -> [pedido1, pedido2]
COMPLETADO -> [pedido3]
CANCELADO -> [pedido4, pedido5]
Es útil para generar informes, resumir datos o preparar resultados para una API.
3. Calcular agregaciones
Puedes contar elementos o calcular sumas:
long cantidad = pedidos.stream()
    .filter(p -> "COMPLETADO".equals(p.getEstado()))
    .count();

double total = pedidos.stream()
    .mapToDouble(Pedido::getImporte)
    .sum();
También puedes agrupar y contar en una sola operación:
Map<String, Long> cantidadPorEstado = pedidos.stream()
    .collect(Collectors.groupingBy(
        Pedido::getEstado,
        Collectors.counting()
    ));
4. flatMap() para aplanar estructuras
Si cada cliente tiene varios pedidos y quieres obtener todos los pedidos en una sola secuencia:
List<Pedido> todosLosPedidos = clientes.stream()
    .flatMap(cliente -> cliente.getPedidos().stream())
    .toList();
La diferencia esencial es:
    • map(): transforma cada elemento en otro elemento; puede producir una estructura anidada.
    • flatMap(): transforma cada elemento en un Stream y combina esos Streams en uno solo.
5. Errores habituales
    • Modificar colecciones externas desde un Stream: puede producir efectos secundarios y problemas de concurrencia.
    • Usar parallelStream() sin medir: el paralelismo no garantiza un mejor rendimiento y puede perjudicar tareas pequeñas o dependientes de recursos compartidos.
    • Confundir toList() con una lista modificable: en Java moderno, Stream.toList() devuelve una lista no modificable. Si necesitas modificarla, puedes usar Collectors.toCollection(ArrayList::new).
Pregunta de comprobación
Tienes una lista de clientes y cada cliente contiene una lista de pedidos. ¿Qué operación permite obtener un único Stream con todos los pedidos?
A. filter()
B. sorted()
C. flatMap()
D. count()
Comprobar
Correcto.
La respuesta es C: flatMap(). Permite convertir cada cliente en un Stream de pedidos y aplanar todos esos Streams en una única secuencia.
Continuar al bloque 20
Fase 3 — Java avanzado
Bloque 20: Inmutabilidad y diseño de objetos seguros
La inmutabilidad consiste en diseñar objetos cuyo estado no pueda cambiar después de su creación. Es especialmente útil en aplicaciones backend porque facilita el razonamiento sobre el código, reduce efectos secundarios y mejora la seguridad al compartir datos.
1. Crear una clase inmutable
Una clase convencional puede permitir modificar su estado:
public class Usuario {
    private String nombre;

    public Usuario(String nombre) {
        this.nombre = nombre;
    }

    public void setNombre(String nombre) {
        this.nombre = nombre;
    }
}
Podemos hacerla inmutable eliminando los setters y declarando el campo final:
public final class Usuario {
    private final String nombre;

    public Usuario(String nombre) {
        this.nombre = nombre;
    }

    public String getNombre() {
        return nombre;
    }
}
Aspectos importantes:
    • final class: impide que la clase sea extendida.
    • private final: el campo solo puede asignarse una vez.
    • Sin setters: no exponemos operaciones para modificar el estado.
    • Constructor: establece el estado inicial.
2. Cuidado con los objetos mutables internos
Declarar los campos como final no garantiza por sí solo que el objeto sea inmutable.
public final class Equipo {
    private final List<String> miembros;

    public Equipo(List<String> miembros) {
        this.miembros = miembros;
    }

    public List<String> getMiembros() {
        return miembros;
    }
}
Este código tiene un problema: quien creó la lista puede modificarla después, y quien recibe la lista mediante el getter también puede alterarla.
Una solución sencilla es crear una copia inmodificable:
public final class Equipo {
    private final List<String> miembros;

    public Equipo(List<String> miembros) {
        this.miembros = List.copyOf(miembros);
    }

    public List<String> getMiembros() {
        return miembros;
    }
}
List.copyOf() crea una lista no modificable independiente de los cambios posteriores en la lista original. Si sus elementos fueran objetos mutables, seguirían pudiendo modificarse esos objetos: la copia es superficial.
3. Usar record
Desde Java 16, los record ofrecen una forma concisa de definir clases destinadas principalmente a transportar datos:
public record Producto(
    Long id,
    String nombre,
    double precio
) {}
Java genera automáticamente el constructor canónico, los accesores, equals(), hashCode() y toString().
Se suelen utilizar para DTOs, respuestas de API y datos de configuración.
Matiz importante: un record no es automáticamente profundamente inmutable. Sus componentes no pueden reasignarse, pero si contienen una lista o un objeto mutable, ese contenido puede seguir cambiando salvo que se proteja.
4. ¿Cuándo conviene la inmutabilidad?
    • DTOs que representan datos de entrada o salida.
    • Valores como dinero, fechas o identificadores.
    • Configuración que no debería cambiar durante la ejecución.
    • Objetos compartidos entre hilos, cuando su estado puede mantenerse inmutable.
No todos los objetos deben ser inmutables. Una entidad de negocio puede necesitar cambiar de estado durante su ciclo de vida.
Pregunta de comprobación
¿Por qué private final List<String> nombres no garantiza por sí solo que una clase sea inmutable?
A. Porque final solo funciona con tipos primitivos.
B. Porque la referencia no puede reasignarse, pero la lista todavía puede modificarse.
C. Porque todas las listas son inmutables por defecto.
D. Porque una clase con campos final no puede tener constructor.
Comprobar
Correcto.
La respuesta es B. final impide reasignar la referencia, pero no impide llamar a métodos que modifiquen la lista. Una copia defensiva, por ejemplo con List.copyOf(), evita esa modificación a través de la lista expuesta.
Continuar al bloque 21

Tienes razón. Me he desviado de la ruta: después de concurrencia y testing, he seguido añadiendo temas de Java avanzado que no estaban en el itinerario que marcaste. Dejamos de lado ClassLoader, Streams avanzados e inmutabilidad como bloques independientes y retomamos tu temario.
La ruta que seguiremos es esta:
3.2. Concurrencia
Ya hemos trabajado Threads, pools de hilos, condiciones de carrera, visibilidad, volatile, synchronized, atomics, locks, deadlocks, Futures y CompletableFuture, además de concurrencia frente a paralelismo.
3.3. Testing en Java
JUnit y Mockito, pruebas unitarias y de integración, mocks y stubs, pruebas parametrizadas, cobertura y tests de servicios, repositorios y controladores.
Siguiente bloque
3.4. Spring Boot
IoC, beans, inyección de dependencias, arquitectura por capas, REST, validación, JPA, transacciones y seguridad.
3.5. Spring Batch
Jobs, Steps, chunks, readers, processors, writers, reinicios, transacciones, tolerancia a fallos y decisiones arquitectónicas.
Bloque 21 — 3.3. Testing en Java: pruebas parametrizadas
Ya hemos visto los fundamentos de JUnit 5 y Mockito. Continuamos con el siguiente punto del temario: pruebas parametrizadas.
1. ¿Qué son?
Permiten ejecutar el mismo test varias veces con diferentes entradas y resultados esperados, evitando duplicar código.
Por ejemplo, para comprobar un método que determina si una edad permite acceder a un servicio:
class AccesoService {

    boolean puedeAcceder(int edad) {
        return edad >= 18;
    }
}
Con JUnit 5:
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import static org.junit.jupiter.api.Assertions.*;

class AccesoServiceTest {

    private final AccesoService service = new AccesoService();

    @ParameterizedTest
    @CsvSource({
        "17, false",
        "18, true",
        "25, true"
    })
    void compruebaAcceso(int edad, boolean esperado) {
        assertEquals(esperado, service.puedeAcceder(edad));
    }
}
2. Anotaciones principales
    • @ParameterizedTest: indica que el test se ejecutará con varios conjuntos de datos.
    • @CsvSource: proporciona filas de valores separados por comas.
    • assertEquals(): compara el resultado real con el esperado.
También existen otras fuentes de datos:
    • @ValueSource: para valores simples, como varios enteros.
    • @MethodSource: para obtener datos desde un método Java.
    • @EnumSource: para probar valores de un enum.
Criterio práctico: utiliza pruebas parametrizadas cuando quieras verificar el mismo comportamiento para diferentes entradas, especialmente casos límite y datos inválidos.
Pregunta de comprobación
¿Qué ventaja principal aporta @ParameterizedTest junto con @CsvSource?
A. Permite ejecutar los tests sin comprobar resultados.
B. Permite ejecutar el mismo test con distintas entradas y resultados esperados sin duplicar el método de prueba.
C. Sustituye a Mockito y permite simular cualquier dependencia.
D. Convierte automáticamente un test unitario en un test de integración.
Comprobar
Correcto.
La respuesta es B. Las pruebas parametrizadas reutilizan la misma lógica de prueba con diferentes datos, facilitando la comprobación de casos normales y límites.
Continuar con testing

Fase 3 — Java avanzado
Bloque 23: Testing de servicios, repositorios y controladores
En una aplicación Spring Boot, cada capa tiene responsabilidades distintas. Por eso, el tipo de test y las herramientas que utilizamos dependen de qué queremos comprobar.
1. Tests de servicios
Los servicios contienen la lógica de negocio. Normalmente se prueban de forma unitaria, simulando sus dependencias con Mockito.
Supongamos que un servicio consulta un repositorio:
@Service
public class UsuarioService {

    private final UsuarioRepository repository;

    public UsuarioService(UsuarioRepository repository) {
        this.repository = repository;
    }

    public Usuario buscar(Long id) {
        return repository.findById(id)
            .orElseThrow(() ->
                new UsuarioNoEncontradoException(id));
    }
}
Podemos comprobar el comportamiento sin conectar una base de datos:
@ExtendWith(MockitoExtension.class)
class UsuarioServiceTest {

    @Mock
    private UsuarioRepository repository;

    @InjectMocks
    private UsuarioService service;

    @Test
    void devuelveUsuarioExistente() {
        Usuario usuario = new Usuario(1L, "Ana");

        when(repository.findById(1L))
            .thenReturn(Optional.of(usuario));

        Usuario resultado = service.buscar(1L);

        assertEquals("Ana", resultado.getNombre());
        verify(repository).findById(1L);
    }
}
    • @Mock: crea una dependencia simulada.
    • @InjectMocks: construye el objeto de prueba e inyecta los mocks compatibles.
    • when().thenReturn(): configura el comportamiento del mock.
    • verify(): comprueba que se produjo una interacción.
2. Tests de repositorios
Los repositorios acceden a la base de datos. Aquí interesa comprobar consultas, filtros, relaciones y persistencia real.
Con Spring Boot y Spring Data JPA se puede utilizar @DataJpaTest:
@DataJpaTest
class UsuarioRepositoryTest {

    @Autowired
    private UsuarioRepository repository;

    @Test
    void guardaYRecuperaUsuario() {
        Usuario guardado =
            repository.save(new Usuario(null, "Ana"));

        Optional<Usuario> resultado =
            repository.findById(guardado.getId());

        assertTrue(resultado.isPresent());
        assertEquals("Ana", resultado.get().getNombre());
    }
}
@DataJpaTest configura una prueba centrada en los componentes JPA. Habitualmente utiliza una base de datos embebida si está disponible y revierte las transacciones al terminar cada test.
Importante: una prueba con H2 no garantiza que las consultas funcionen igual en PostgreSQL o MySQL. Si dependes de funciones específicas de una base de datos, conviene probar también con el motor real, por ejemplo mediante Testcontainers.
3. Tests de controladores REST
Los controladores reciben peticiones HTTP y devuelven respuestas. Hay que verificar códigos HTTP, contenido y validación.
Con @WebMvcTest y MockMvc puedes probar la capa web sin levantar todo el contexto de la aplicación:
@WebMvcTest(UsuarioController.class)
class UsuarioControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private UsuarioService service;

    @Test
    void devuelveUsuarioEnFormatoJson() throws Exception {
        when(service.buscar(1L))
            .thenReturn(new Usuario(1L, "Ana"));

        mockMvc.perform(get("/usuarios/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.nombre").value("Ana"));
    }
}
@MockitoBean registra un mock dentro del contexto de Spring. En versiones anteriores de Spring Boot puede encontrarse @MockBean.
Este test comprueba el comportamiento HTTP del controlador y simula el servicio, por lo que no verifica la base de datos ni la lógica interna del servicio.
4. Diferencias entre los tres tipos
Capa
Qué comprueba
Herramienta habitual
Servicio
Reglas de negocio
JUnit + Mockito
Repositorio
Consultas y persistencia
@DataJpaTest
Controlador
HTTP, JSON y validación web
@WebMvcTest + MockMvc
La idea clave es probar cada responsabilidad por separado y añadir pruebas de integración cuando necesites verificar que varias capas funcionan correctamente juntas.
Pregunta de comprobación
Quieres verificar que un endpoint GET /usuarios/1 devuelve HTTP 200 y un JSON con el nombre del usuario, simulando la lógica del servicio. ¿Qué enfoque es el más adecuado?
A. @DataJpaTest, porque comprueba todos los endpoints REST.
B. @WebMvcTest con MockMvc y un mock del servicio.
C. Probar únicamente el servicio con Mockito, sin realizar ninguna petición HTTP.
D. Utilizar exclusivamente JaCoCo, porque mide las respuestas HTTP.
Comprobar
Correcto.
La respuesta es B. @WebMvcTest junto con MockMvc permite probar el comportamiento HTTP del controlador y simular el servicio, aislando la capa web.
Continuar con Spring Boot


























