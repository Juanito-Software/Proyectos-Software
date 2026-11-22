es posible crear una clase en javascript que no sea constante?
Sí, es perfectamente posible crear una clase en JavaScript que no sea una constante. [1]
Aunque es muy común declarar las clases utilizando const (por ejemplo, const MiClase = class { ... } o class MiClase { ... }), en JavaScript las clases se pueden asignar o reasignar utilizando otras palabras clave como let o var, e incluso se pueden definir mediante funciones constructoras tradicionales. [1, 2]
Formas de crear una clase que no sea constante
    1. Usando let con expresión de clase (reasignable en su ámbito):
       javascript
       let MiClase = class {
         constructor(nombre) {
           this.nombre = nombre;
         }
       };
       
       // Puedes reasignarla más adelante
       MiClase = class {
         constructor(nombre) {
           this.nombre = "Modificado: " + nombre;
         }
       };
       Usa el código con precaución.
    2. Usando una declaración tradicional con let o reasignación:
Si declaras una clase con class MiClase {}, por defecto actúa como un identificador de ámbito de bloque (similar a let, no se puede volver a declarar en el mismo ámbito, pero si usas expresiones o funciones constructoras puedes mutar la referencia). [1]
    3. Usando funciones constructoras (estilo clásico ES5):
Antes de ES6, las "clases" se emulaban mediante funciones que sí podían reasignarse libremente con var o let: [1, 2]
       javascript
       let MiClase = function(nombre) {
         this.nombre = nombre;
       };
       
       MiClase = function(nombre) {
         this.otroNombre = nombre;
       };
       Usa el código con precaución.
Aquí tienes una explicación detallada sobre cómo funcionan las declaraciones y expresiones de 


¿Estás intentando reasignar una clase de forma dinámica en tu código o necesitas ayuda con un patrón de diseño específico (como inyección de dependencias)?
Las respuestas de la IA pueden contener errores. Más información


diferencia entre crearla con let y con var
La diferencia principal entre usar let y var al crear una clase en JavaScript radica en el alcance (ámbito) de la variable y en cómo se comportan antes de ser declaradas (hoisting).
Aquí tienes las diferencias clave:
Característica
Con let
Con var
Ámbito (Scope)
Bloque (dentro de { })
Función o Global
Hoisting
Sí, pero entra en Temporal Dead Zone (da error si la usas antes)
Sí, se inicializa como undefined
Redeclaración
No se puede volver a declarar en el mismo ámbito
Sí se puede volver a declarar sin error

1. Ámbito de la variable (Scope)
    • Con let: La clase solo existe dentro del bloque específico (como un if, un for o una función) donde se creó.
    • Con var: La clase se escapa del bloque {} y es visible en toda la función o en el entorno global.
javascript
{
    let ClaseLet = class {};
    var ClaseVar = class {};
}

console.log(ClaseVar); // Funciona: muestra la clase
console.log(ClaseLet); // Error: ClaseLet is not defined
Usa el código con precaución.
2. Elevación (Hoisting) y Zona Muerta Temporal
    • Con var: JavaScript eleva la declaración al inicio. Si intentas usarla antes de su línea, no da error, pero vale undefined (por lo que fallará al intentar hacer un new).
    • Con let: También se eleva, pero no se inicializa. Si intentas acceder a ella antes de su línea, el código se rompe inmediatamente lanzando un ReferenceError.
javascript
console.log(ClaseVar); // Muestra: undefined
// console.log(ClaseLet); // Si la descomentas, da ReferenceError

var ClaseVar = class {};
let ClaseLet = class {};
Usa el código con precaución.
3. Redeclaración
    • Con var: Puedes volver a escribir var MiClase = ... más abajo en el mismo archivo y JavaScript lo ignorará, sobrescribiéndola.
    • Con let: Si intentas declarar dos veces let MiClase en el mismo ámbito, el navegador o Node.js lanzará un error de sintaxis antes de ejecutar el código.
¿Qué comportamiento estás buscando para tu clase? Si me cuentas el caso de uso de tu proyecto, te puedo recomendar cuál de las dos opciones se adapta mejor.
Las respuestas de la IA pueden contener errores. Más información


y ahi diferencia entre let y var al declarar tipos de datos simples?
Sí, el comportamiento es exactamente el mismo. No importa si estás declarando una clase compleja, un objeto, o un tipo de dato simple (como un número, un texto o un booleano); las reglas de let y var se aplican a la variable que los contiene, no al tipo de dato en sí.
La diferencia sigue dividiéndose en los mismos tres pilares:
1. El Ámbito (Scope)
    • Con let: Si creas un número dentro de un if o un for, al salir de ese bloque {} la variable desaparece.
    • Con var: La variable sigue existiendo fuera del bloque {}.
javascript
if (true) {
    let edadLet = 25;
    var edadVar = 30;
}

console.log(edadVar); // Muestra: 30
console.log(edadLet); // Error: edadLet is not defined
Usa el código con precaución.
2. Hoisting (Elevación)
    • Con var: Puedes intentar leer la variable antes de que exista en el código. No dará error, pero su valor será undefined.
    • Con let: Intentar usarla antes de declararla romperá tu programa con un ReferenceError.
javascript
console.log(textoVar); // Muestra: undefined
// console.log(textoLet); // Daría ReferenceError

var textoVar = "Hola";
let textoLet = "Adiós";
Usa el código con precaución.
3. Redeclaración
    • Con var: Te permite duplicar la declaración por error en el mismo sitio, lo que suele causar fallos difíciles de encontrar.
    • Con let: Protege tu código impidiéndote duplicar el nombre de la variable en el mismo ámbito.
javascript
var nota = 10;
var nota = 5; // JavaScript lo permite sin quejar se (nota ahora vale 5)

let precio = 100;
// let precio = 80; // Error de sintaxis: 'precio' has already been declared
Usa el código con precaución.
En resumen
El tipo de dato (simple o complejo) no cambia las reglas del juego. var define variables con comportamiento antiguo (y más propenso a errores), mientras que let introduce un control estricto y moderno basado en bloques de código.
Por regla general en el JavaScript moderno, siempre se recomienda usar const por defecto y let solo si el valor va a cambiar. ¿Te ha quedado alguna duda sobre cómo maneja JavaScript la memoria o el alcance con estos componentes?
Las respuestas de la IA pueden contener errores. Más información

-

Perfecto. Empezamos **JavaScript desde los fundamentos y después continuaremos con TypeScript**, siguiendo el itinerario de formación que has compartido.

Texto pegado.txt

Mantendremos el mismo método que hemos utilizado con Java: explicaciones progresivas, ejemplos de código, ejercicios prácticos, corrección rigurosa y preguntas tipo entrevista. No avanzaremos por haber leído la teoría, sino cuando demuestres que comprendes y aplicas los conceptos.

## **Fase 4 — JavaScript y TypeScript**

**Bloque 4.1 — JavaScript fundamental**

Empezamos aquí.

Tipos, coerción, `==` frente a `===`, `null`, `undefined`, variables, referencias, funciones, closures, `this`, prototipos, clases y módulos.

**Bloque 4.2 — Asincronía**

Callbacks, promesas, `async/await`, event loop, microtasks, peticiones HTTP y gestión de errores.

**Bloque 4.3 — TypeScript**

Tipos, interfaces, uniones, narrowing, genéricos, `unknown`, `never`, utility types y configuración del compilador.

## **Lección 1 — Variables y tipos en JavaScript**

JavaScript es un lenguaje de tipado dinámico. Esto significa que una variable no queda vinculada permanentemente a un tipo: puede contener un número y, posteriormente, una cadena.

```
let value = 10;
value = "hola";

console.log(value); // "hola"
```

### **1. Las tres formas de declarar variables**

|Declaración|¿Se puede reasignar?|Ámbito|
|---|---|---|
|`const`|No|Bloque|
|`let`|Sí|Bloque|
|`var`|Sí|Función, o ámbito global si se declara fuera de una función|

En JavaScript moderno, normalmente utilizarás `const` por defecto y `let` cuando necesites reasignar. Evitaremos `var` salvo cuando estudiemos su comportamiento histórico.

Un matiz importante: `const` **impide reasignar la variable, pero no hace inmutable el objeto al que apunta.**

```
const user = { name: "Ana" };

user.name = "Luis";       // Válido
// user = { name: "Eva" }; // TypeError
```

### **2. Tipos primitivos principales**

JavaScript tiene siete tipos primitivos:

- `string`: cadenas de texto.
    
- `number`: números, tanto enteros como decimales.
    
- `bigint`: enteros de gran tamaño.
    
- `boolean`: `true` y `false`.
    
- `undefined`: valor que indica, habitualmente, ausencia de asignación.
    
- `null`: ausencia intencionada de valor.
    
- `symbol`: identificadores únicos.
    

Los objetos y los arrays son tipos de referencia. Más adelante veremos cómo afecta esto a la mutabilidad y a las comparaciones.

### **3. Primera diferencia importante respecto a Java**

En Java, declarar una variable local primitiva sin inicializarla y utilizarla produce un error de compilación. En JavaScript, una variable declarada con `let` pero sin valor asignado contiene `undefined`.

```
let age;
console.log(age); // undefined

console.log(typeof age);   // "undefined"
console.log(typeof "hola"); // "string"
console.log(typeof 42);     // "number"
console.log(typeof null);   // "object"
```

Ese último resultado es una particularidad histórica de JavaScript: `typeof null` devuelve `"object"`, aunque `null` sea un valor primitivo.

## **Ejercicio 1 — Comprueba tu comprensión**

Sin ejecutar el código, predice qué imprime cada línea y responde a la pregunta final.

```
const numbers = [1, 2, 3];
numbers.push(4);

let value;
value = 5;
value = "cinco";

console.log(numbers);
console.log(value);
console.log(typeof null);
```

1. ¿Qué imprime `console.log(numbers)`?

`[1, 2, 3]`

`[1, 2, 3, 4]`

Produce un error porque `numbers` es `const`.

2. ¿Qué imprime `console.log(value)`?

`5`

`"cinco"`

`undefined`

3. ¿Qué imprime `console.log(typeof null)`?

`"null"`

`"undefined"`

`"object"`

4. Explica con tus palabras por qué se puede modificar `numbers` aunque se haya declarado con `const`.

Corregir ejercicio

Tras corregirlo, seguiremos con las diferencias entre `==` y `===`, las conversiones de tipos y los valores _truthy/falsy_, que son fundamentales para entender JavaScript antes de pasar a TypeScript.

--Corrige rigurosamente mis respuestas al ejercicio 1 de JavaScript. Mis respuestas: 1) b; 2) b; 3) c; 4) porque no se ha modificado sino que se ha añadido un numero, `const` impide cambiar esa referencia por otra pero no impide modificar las propiedades o el contenido del objeto referenciado..

Explica cada error y no avances a la siguiente lección hasta corregir las lagunas.


Juan, las cuatro respuestas son correctas. Sin embargo, quiero matizar tu explicación de la cuarta pregunta porque hay una distinción importante que conviene dominar antes de avanzar.

# **4/4**

Todas correctas

## **Corrección individual**

### **1. Modificación del array**

Correcta — B

Resultado:

```
[1, 2, 3, 4]
```

`const` impide reasignar la variable, pero no impide modificar el objeto al que hace referencia.

```
const numbers = [1, 2, 3];

numbers.push(4); // Correcto
numbers[0] = 99; // Correcto

numbers = [5, 6]; // TypeError
```

### **2. Reasignación de** `value`

Correcta — B

Resultado:

```
"cinco"
```

Has identificado correctamente el comportamiento del tipado dinámico.

```
let value = 5;
value = "cinco";
value = true;
```

Las tres asignaciones son válidas.

En Java, en cambio, una variable declarada como `int` no puede recibir posteriormente un `String`.

### **3.** `typeof null`

Correcta — C

Resultado:

```
"object"
```

Es una peculiaridad histórica del lenguaje.

Aunque `null` representa ausencia intencionada de valor, `typeof null` devuelve `"object"`.

Para comprobarlo correctamente:

```
const value = null;

console.log(value === null); // true
console.log(typeof value);   // "object"
```

No debes utilizar `typeof` como comprobación de `null`.

### **4. ¿Por qué podemos modificar** `numbers` **siendo** `const`**?**

Correcta, con un matiz conceptual

Tu explicación:

> `const` impide cambiar esa referencia por otra pero no impide modificar las propiedades o el contenido del objeto referenciado.

Es correcta.

Hay una precisión terminológica que quiero introducir:

**No estamos modificando la referencia: estamos modificando el objeto al que apunta la referencia.**

Visualmente:

**Antes de** `push(4)`

**numbers**

`[1, 2, 3]`

**Después de** `push(4)`

**numbers**

`[1, 2, 3, 4]`

La referencia permanece igual. El contenido del array cambia.

Una consecuencia importante: `const` tampoco garantiza inmutabilidad profunda de los objetos.

## **Comprobación de consolidación**

Antes de pasar a la siguiente lección, quiero comprobar que dominas la diferencia entre reasignación, mutabilidad y referencias.

Analiza este código:

```
const user = {
    name: "Juan",
    skills: ["Java", "Spring"]
};

const anotherUser = user;

anotherUser.name = "Pedro";
anotherUser.skills.push("JavaScript");

console.log(user.name);
console.log(user.skills);

anotherUser = {}; // ¿Qué sucede?
```

**1. ¿Qué imprime** `console.log(user.name)`**?**

`"Juan"`

`"Pedro"`

`undefined`

**2. ¿Qué imprime** `console.log(user.skills)`**?**

`["Java", "Spring"]`

`["Java", "Spring", "JavaScript"]`

Produce un error porque `skills` es una propiedad de `const`.

**3. ¿Qué sucede al ejecutar** `anotherUser = {}`**?**

`anotherUser` pasa a apuntar al nuevo objeto.

`user` también pasa a apuntar al nuevo objeto.

Se produce un `TypeError` porque `anotherUser` es `const`.

**4. Explica por qué las dos primeras modificaciones afectan a** `user`**, pero la última asignación no está permitida.**

Enviar respuestas

**Objetivo:** que puedas razonar sobre referencias compartidas sin depender de memorizar qué hace `const`. Si resuelves este ejercicio y justificas correctamente el comportamiento, daremos por consolidado este primer concepto.


--Corrige rigurosamente mi comprobación de consolidación de JavaScript. Respuestas: 1) b; 2) b; 3) c; explicación: las primeraws 2 afectan porque ambos hacen referencia al mismo objeto en memoria y la ultima daa error porque intenta reasigna una variable declarada con const. No avances de lección hasta resolver cualquier laguna.

Las tres respuestas son correctas. Tu explicación también es correcta y demuestra que has comprendido la distinción fundamental entre **modificar un objeto y reasignar una variable declarada con** `const`.

Vamos a comprobar cada punto con precisión.

## **Corrección**

**1.** `console.log(user.name)`

Correcto: B

Resultado:

```
"Pedro"
```

`user` y `anotherUser` contienen referencias al mismo objeto. Cuando ejecutamos:

```
anotherUser.name = "Pedro";
```

Modificamos la propiedad `name` del objeto compartido. Por tanto, acceder a esa propiedad desde `user` devuelve `"Pedro"`.

**2.** `console.log(user.skills)`

Correcto: B

Resultado:

```
["Java", "Spring", "JavaScript"]
```

La instrucción:

```
anotherUser.skills.push("JavaScript");
```

Modifica el array al que apunta la propiedad `skills` del objeto compartido.

No estamos reasignando `anotherUser.skills`, sino modificando el contenido del array existente.

**3.** `anotherUser = {}`

Correcto: C

Se produce un `TypeError` porque `anotherUser` se declaró con `const`.

Esta instrucción intenta cambiar la referencia almacenada en la variable:

```
anotherUser = {};
```

`const` impide esa reasignación.

Importante: el error se produce al ejecutar esa última instrucción. Los dos `console.log()` anteriores sí se habrán ejecutado.

## **Evaluación de tu explicación**

Has escrito:

> Las primeras dos afectan porque ambos hacen referencia al mismo objeto en memoria y la última da error porque intenta reasignar una variable declarada con const.

Concepto consolidado

Tu razonamiento es correcto. Solo quiero afinar la terminología para una entrevista técnica:

- **Referencia compartida:** dos variables pueden apuntar al mismo objeto.
    
- **Mutación:** modificar el estado interno de ese objeto, por ejemplo, cambiar una propiedad o añadir un elemento a un array.
    
- **Reasignación:** hacer que una variable apunte a otro valor u objeto.
    
- `const`**:** impide reasignar el enlace de la variable, pero no garantiza que el objeto referenciado sea inmutable.
    

Una precisión adicional: decir que ambos apuntan al mismo objeto en memoria es una explicación válida a este nivel. No obstante, técnicamente, JavaScript especifica el comportamiento observable de las referencias sin obligar a una implementación concreta a utilizar una determinada organización física de memoria.

## **Prueba adicional de consolidación**

Antes de continuar, quiero comprobar que puedes distinguir entre mutación y reasignación en una situación ligeramente diferente.

Considera este código:

```
const user = {
    name: "Juan",
    skills: ["Java", "Spring"]
};

const skills = user.skills;

skills = ["Python"];

user.skills = ["JavaScript"];

skills.push("PHP");

console.log(user.skills);
```

**¿Qué sucede al ejecutar el código?**

**1. ¿Se ejecuta** `skills = ["Python"]`**?**

Sí, porque `skills` apunta a un array.

No, produce un `TypeError` porque `skills` se declaró con `const`.

Sí, pero modifica también `user.skills`.

**2. ¿Qué ocurre con** `user.skills = ["JavaScript"]`**?**

Esta pregunta se responderá en la explicación.

**3. Explica qué relación existe entre** `skills` **y** `user.skills` **después de ejecutar las asignaciones que sean válidas.**

Enviar respuesta

No avanzaremos a coerción de tipos ni a `==` frente a `===` hasta resolver esta distinción.

--user.skills = ["JavaScript"] esta funciona sin problema

```
skills = ["Python"]; esta no porque skills es const
```

```
skills.push("PHP"); esta si funciona porque no reasigna sino que modifica
```

Tu razonamiento es correcto en los tres casos. Has identificado bien la diferencia entre **reasignar una referencia** y **mutar un objeto**. Hay un matiz importante en el orden de ejecución que quiero explicarte.

## **1. Análisis de cada instrucción**

Partimos de:

```
const user = {
    name: "Juan",
    skills: ["Java", "Spring"]
};

const skills = user.skills;
```

En este momento, tanto `skills` como `user.skills` hacen referencia al mismo array.

**Estado inicial**

**Array compartido**

`["Java", "Spring"]`

`skills`

Mismo array

`user.skills`

Mismo array

### **A.** `skills = ["Python"]`

TypeError

Correcto: no se permite porque `skills` está declarada con `const`.

Intenta reasignar la variable a un array diferente.

### **B.** `user.skills = ["JavaScript"]`

Permitido

Correcto: `user` es una constante que referencia un objeto, pero sus propiedades pueden modificarse.

Esta instrucción sustituye el array al que apunta la propiedad `user.skills`.

Ahora tenemos dos arrays diferentes:

- `skills` sigue apuntando al array original: `["Java", "Spring"]`.
    
- `user.skills` apunta al nuevo array: `["JavaScript"]`.
    

### **C.** `skills.push("PHP")`

Permitido

Correcto: modifica el array original, que sigue referenciado por `skills`.

Su contenido pasa a ser:

```
["Java", "Spring", "PHP"]
```

## **2. Pero hay un detalle fundamental: el orden de ejecución**

El código original era:

```
const user = {
    name: "Juan",
    skills: ["Java", "Spring"]
};

const skills = user.skills;

skills = ["Python"]; // TypeError

user.skills = ["JavaScript"];

skills.push("PHP");

console.log(user.skills);
```

**El programa se detiene en** `skills = ["Python"]`**.**

Por tanto, las dos instrucciones posteriores no llegan a ejecutarse y no se imprime nada.

Si eliminamos la instrucción que provoca el error:

```
const user = {
    name: "Juan",
    skills: ["Java", "Spring"]
};

const skills = user.skills;

user.skills = ["JavaScript"];

skills.push("PHP");

console.log(user.skills);
console.log(skills);
```

Resultado:

```
["JavaScript"]
["Java", "Spring", "PHP"]
```

Esto demuestra que, aunque inicialmente ambas variables apuntaban al mismo array, sustituir la propiedad `user.skills` no modifica la referencia almacenada en `skills`.

## **Evaluación**

Concepto consolidado

Has demostrado que comprendes:

- La diferencia entre referencias y objetos.
    
- La mutabilidad de arrays y objetos.
    
- La reasignación de variables.
    
- Las limitaciones de `const`.
    
- La diferencia entre sustituir una propiedad y modificar el objeto al que apuntaba anteriormente.
    

No veo ninguna laguna conceptual que justifique seguir haciendo ejercicios sobre referencias y `const`.

**Siguiente contenido: coerción de tipos en JavaScript**, empezando por conversiones implícitas y explícitas. Después abordaremos `==` frente a `===`, y posteriormente `truthy`, `falsy`, `null` y `undefined`.

--okey

## **JavaScript — Lección 2: coerción de tipos**

Empezamos con un concepto fundamental de JavaScript: **la conversión de tipos (****_type coercion_****)**.

JavaScript permite operar con valores de distintos tipos. En determinadas situaciones convierte automáticamente un valor para que la operación pueda realizarse.

Existen dos tipos de conversión:

1. **Conversión implícita:** JavaScript convierte automáticamente un valor.
    
2. **Conversión explícita:** el programador convierte el valor deliberadamente.
    

### **1. Conversión implícita**

Observa estos ejemplos:

```
console.log("5" + 2); // "52"
console.log("5" - 2); // 3
console.log("5" * 2); // 10
console.log("5" / 2); // 2.5
```

¿Por qué sucede esto?

El operador `+` tiene dos comportamientos:

- Suma números.
    
- Concatena cadenas cuando interviene una cadena de texto.
    

En cambio, los operadores `-`, `*` y `/` realizan operaciones aritméticas y convierten las cadenas numéricas a números.

Por tanto:

```
"5" + 2 // "52"
"5" - 2 // 3
```

Esta diferencia es especialmente importante porque puede producir errores difíciles de detectar.

### **2. Conversión explícita**

JavaScript proporciona funciones para convertir valores manualmente.

|Función|Conversión|
|---|---|
|`Number()`|Convierte a número|
|`String()`|Convierte a cadena|
|`Boolean()`|Convierte a booleano|
|`parseInt()`|Extrae un número entero|
|`parseFloat()`|Extrae un número decimal|

Ejemplos:

```
Number("42");       // 42
String(42);         // "42"
Boolean(1);         // true
parseInt("42px");   // 42
parseFloat("3.14"); // 3.14
```

Un detalle importante:

```
Number("42px"); // NaN
parseInt("42px"); // 42
```

`Number()` intenta convertir toda la cadena. `parseInt()` puede extraer el componente entero inicial.

### **3. NaN: Not a Number**

`NaN` representa un resultado numérico inválido.

```
const result = Number("hola");

console.log(result); // NaN
console.log(typeof result); // "number"
```

Aunque se llame _Not a Number_, su tipo es `number`.

Para comprobarlo correctamente:

```
Number.isNaN(result); // true
```

## **Ejercicio 1 — Comprobación de conocimientos**

Analiza este código sin ejecutarlo:

```
const a = "10";
const b = 5;

console.log(a + b);
console.log(a - b);
console.log(a * b);
console.log(Number(a) + b);
console.log(Boolean("0"));
console.log(Number("hola"));
console.log(parseInt("25.8px"));
```

**Test de coerción de tipos**

0/7 respondidas

**1. ¿Qué devuelve a + b?**

15

"105"

"10 5"

**2. ¿Qué devuelve a - b?**

"105"

5

NaN

**3. ¿Qué devuelve a * b?**

50

"105"

NaN

**4. ¿Qué devuelve Number(a) + b?**

"105"

15

NaN

**5. ¿Qué devuelve Boolean("0")?**

false

true

0

**6. ¿Qué devuelve Number("hola")?**

0

undefined

NaN

**7. ¿Qué devuelve parseInt("25.8px")?**

25

25.8

NaN

Corregir respuestas

No avanzaremos todavía a `==` y `===`. Primero quiero comprobar que dominas estas conversiones y que puedes razonar sobre sus resultados.

--

## **JavaScript — Lección 3: igualdad (**`==` **frente a** `===`**)**

Este es uno de los conceptos más importantes de JavaScript. La diferencia entre ambos operadores está en cómo comparan los valores y si permiten conversiones automáticas de tipos.

### **1. Igualdad no estricta:** `==`

El operador `==` compara dos valores permitiendo, cuando corresponde, **conversión implícita de tipos** (_type coercion_).

Ejemplos:

```
console.log(5 == "5");       // true
console.log(10 == "10");     // true
console.log(0 == false);     // true
console.log(1 == true);      // true
console.log(null == undefined); // true
```

¿Por qué?

Porque JavaScript convierte determinados valores antes de compararlos.

Por ejemplo:

```
5 == "5"
```

JavaScript convierte la cadena `"5"` en el número `5` y después compara:

```
5 == 5 // true
```

### **2. Igualdad estricta:** `===`

El operador `===` compara los valores **sin realizar coerción de tipos**.

Para que la comparación sea verdadera, ambos operandos deben tener el mismo tipo y el mismo valor.

```
console.log(5 === "5");   // false
console.log(10 === "10"); // false
console.log(0 === false); // false
console.log(1 === true);  // false
console.log(5 === 5);     // true
```

Por ejemplo:

```
5 === "5"
```

- Primer operando: `number`.
    
- Segundo operando: `string`.
    
- Tipos diferentes.
    
- Resultado: `false`.
    

### **3. Comparación directa**

|Expresión|`==`|`===`|
|---|---|---|
|`5` y `"5"`|`true`|`false`|
|`0` y `false`|`true`|`false`|
|`1` y `true`|`true`|`false`|
|`null` y `undefined`|`true`|`false`|
|`10` y `10`|`true`|`true`|
|`"hola"` y `"hola"`|`true`|`true`|

### **4. Un caso especial:** `null` **y** `undefined`

JavaScript tiene un comportamiento particular:

```
null == undefined;  // true
null === undefined; // false
```

Esto se debe a una regla específica del algoritmo de igualdad abstracta de JavaScript.

Sin embargo:

```
null == 0;  // false
null == ""; // false
null == false; // false
```

No debes asumir que `null` se convierte siempre en cero o en un booleano.

### **5. ¿Cuál deberías utilizar?**

Mi recomendación para desarrollo profesional es utilizar `===` y `!==` como norma general.

¿Por qué?

- Evitas conversiones implícitas inesperadas.
    
- El código resulta más predecible.
    
- Reduces errores en condiciones.
    
- Facilitas el mantenimiento y la revisión del código.
    

Ejemplo:

```
const age = "18";

if (age === 18) {
    console.log("Mayor de edad");
} else {
    console.log("Los tipos no coinciden");
}
```

Esto imprime:

```
Los tipos no coinciden
```

Si necesitas comparar el valor numérico, conviértelo explícitamente:

```
if (Number(age) === 18) {
    console.log("La edad es 18");
}
```

## **Ejercicio 1 — Igualdad y coerción**

Analiza el siguiente código sin ejecutarlo.

```
console.log(5 == "5");
console.log(5 === "5");

console.log(0 == false);
console.log(0 === false);

console.log(null == undefined);
console.log(null === undefined);

console.log("0" == false);
console.log("0" === false);

console.log([] == false);
console.log([] === false);
```

**Test de igualdad**

0/10

**1. ¿Qué devuelve 5 == "5"?**

true

false

**2. ¿Qué devuelve 5 === "5"?**

true

false

**3. ¿Qué devuelve 0 == false?**

true

false

**4. ¿Qué devuelve 0 === false?**

true

false

**5. ¿Qué devuelve null == undefined?**

true

false

**6. ¿Qué devuelve null === undefined?**

true

false

**7. ¿Qué devuelve "0" == false?**

true

false

**8. ¿Qué devuelve "0" === false?**

true

false

**9. ¿Qué devuelve [] == false?**

true

false

**10. ¿Qué devuelve [] === false?**

true

false

**Explica con tus palabras:** ¿Por qué `[] == false` devuelve `true`, pero `[] === false` devuelve `false`?

Corregir ejercicio

**Importante:** no memorices únicamente los resultados. Quiero que entiendas las conversiones que intervienen, especialmente en los casos de arrays y booleanos. No avanzaremos a `null`, `undefined` y los operadores lógicos hasta consolidar esta parte.

--

Continuamos con el siguiente apartado del temario: `null`**,** `undefined` **y operadores lógicos**.

Antes, una precisión didáctica: todavía no has enviado las respuestas del ejercicio anterior sobre `==` y `===`. Por tanto, no puedo dar esa materia por evaluada. Podemos continuar, pero mantendremos pendiente su comprobación.

# **JavaScript — Lección 4:** `null`**,** `undefined` **y operadores lógicos**

## **1. Diferencia entre** `undefined` **y** `null`

Ambos representan ausencia de un valor, pero tienen significados diferentes.

### `undefined`

Indica que una variable ha sido declarada, pero todavía no tiene asignado ningún valor.

```
let username;

console.log(username); // undefined
```

También aparece cuando intentamos acceder a una propiedad inexistente:

```
const user = {
    name: "Juan"
};

console.log(user.age); // undefined
```

Y cuando una función no devuelve explícitamente ningún valor:

```
function greet() {
    console.log("Hola");
}

const result = greet();

console.log(result); // undefined
```

### `null`

Representa una ausencia de valor intencionada. Es decir, el programador establece explícitamente que una variable no contiene ningún objeto o valor.

```
let selectedUser = null;

console.log(selectedUser); // null
```

Podemos interpretar la diferencia así:

- `undefined`: todavía no se ha asignado un valor.
    
- `null`: se ha asignado explícitamente la ausencia de valor.
    

Una peculiaridad histórica de JavaScript:

```
console.log(typeof undefined); // "undefined"
console.log(typeof null);      // "object"
```

Esto último es un comportamiento histórico del lenguaje. No significa que `null` sea realmente un objeto.

## **2. Comprobar si un valor es** `null` **o** `undefined`

Para comprobarlos, lo más seguro es utilizar igualdad estricta:

```
const user = null;

if (user === null) {
    console.log("No existe usuario");
}
```

También podemos comprobar `undefined`:

```
let username;

if (username === undefined) {
    console.log("Nombre no definido");
}
```

Existe una comprobación interesante:

```
const value = null;

console.log(value == null); // true
console.log(value === null); // true
```

Con `== null` podemos comprobar conjuntamente `null` y `undefined`:

```
null == null;       // true
undefined == null;  // true
undefined == undefined; // true
```

Es una de las pocas situaciones en las que algunos desarrolladores utilizan deliberadamente `==`.

## **3. Operadores lógicos**

JavaScript dispone de tres operadores lógicos fundamentales.

|Operador|Nombre|Función|
|---|---|---|
|`&&`|AND|Ambas condiciones deben ser verdaderas.|
|`\\|\\|`|OR|Al menos una condición debe ser verdadera.|
|`!`|NOT|Invierte el valor lógico.|

### **AND (**`&&`**)**

Devuelve verdadero cuando ambos operandos son verdaderos.

```
const age = 25;
const hasLicense = true;

console.log(age >= 18 && hasLicense); // true
```

Si cualquiera de las condiciones es falsa, el resultado lógico es falso.

### **OR (**`||`**)**

Devuelve verdadero cuando al menos uno de los operandos es verdadero.

```
const isAdmin = false;
const isModerator = true;

console.log(isAdmin || isModerator); // true
```

### **NOT (**`!`**)**

Invierte el valor booleano:

```
const isLogged = false;

console.log(!isLogged); // true
```

También convierte valores a booleanos antes de invertirlos:

```
console.log(!0);     // true
console.log(!1);     // false
console.log(!"");    // true
console.log(!"Hola");// false
```

## **4. Short-circuit evaluation**

Este concepto es especialmente importante en JavaScript.

Los operadores `&&` y `||` no siempre devuelven un booleano. Pueden devolver directamente uno de los operandos.

### **AND (**`&&`**)**

Si el primer operando es falsy, JavaScript no necesita evaluar el segundo.

```
console.log(0 && "Hola"); // 0
console.log(5 && "Hola"); // "Hola"
```

### **OR (**`||`**)**

Si el primer operando es truthy, JavaScript no necesita evaluar el segundo.

```
console.log("Juan" || "Invitado"); // "Juan"
console.log("" || "Invitado");     // "Invitado"
```

Esto se utiliza mucho para asignar valores predeterminados:

```
const username = inputName || "Invitado";
```

Si `inputName` está vacío, será falsy y se utilizará `"Invitado"`.

Sin embargo, tiene una limitación: también sustituye valores válidos como `0` o `false`.

Para resolverlo existe el operador `??`.

## **5. Nullish coalescing (**`??`**)**

El operador `??` devuelve el operando de la derecha únicamente cuando el de la izquierda es `null` o `undefined`.

```
const age = 0;

console.log(age || 18); // 18
console.log(age ?? 18); // 0
```

¿Por qué?

- `||` comprueba si el valor es falsy.
    
- `??` comprueba si el valor es `null` o `undefined`.
    

Comparación:

| Valor | `valor || "Default"` | `valor ?? "Default"` |  
|---|---|---|  
| `null` | `"Default"` | `"Default"` |  
| `undefined` | `"Default"` | `"Default"` |  
| `0` | `"Default"` | `0` |  
| `false` | `"Default"` | `false` |  
| `""` | `"Default"` | `""` |  
| `"Juan"` | `"Juan"` | `"Juan"` |

Mi recomendación: cuando quieras proporcionar un valor predeterminado porque una variable puede no estar definida, `??` suele ser más preciso que `||`.

# **Ejercicio 1 — Evaluación**

Analiza el siguiente código:

```
const username = null;
const age = 0;
const isAdmin = false;

console.log(username ?? "Invitado");
console.log(username || "Invitado");

console.log(age ?? 18);
console.log(age || 18);

console.log(isAdmin ?? true);
console.log(isAdmin || true);

console.log(null == undefined);
console.log(null === undefined);

console.log(5 && "JavaScript");
console.log(0 || "Fallback");
console.log(!"");
```

**Cuestionario**

0/11

**1. username ?? "Invitado"**

null

"Invitado"

undefined

**2. username || "Invitado"**

null

"Invitado"

false

**3. age ?? 18**

0

18

undefined

**4. age || 18**

0

18

false

**5. isAdmin ?? true**

true

false

null

**6. isAdmin || true**

true

false

undefined

**7. null == undefined**

true

false

**8. null === undefined**

true

false

**9. 5 && "JavaScript"**

true

5

"JavaScript"

**10. 0 || "Fallback"**

0

true

"Fallback"

**11. !" "**

true

false

**Explicación:** ¿Cuál es la diferencia fundamental entre `||` y `??`? Pon un ejemplo donde su comportamiento sea diferente.

--con || se devuelve el valor de la derecha cuando el de la izquierda es falsy, null o undefined, en cambio con ?? solo se devuelve el valor de la derecha si el de la izquierda es null o undefined

**Estos operadores devuelven el valor del último operando evaluado, no necesariamente el último operando escrito en la expresión.**

Corregir respuestas

**Nota:** este ejercicio incluye también una comprobación de `==` y `===` que dejamos pendiente. La pregunta 11 utiliza `!" "` (una cadena con un espacio), que es `false` porque la cadena no está vacía.

No avanzaremos hasta revisar tus respuestas y corregir cualquier laguna.

--1 b, 2 b, 3 a, 4 b, 5 b, 6 a, 7 a, 8 b, 9 c, 10 c, 11 b


Sí, Juan. **La afirmación es esencialmente correcta**, pero necesita un par de matices para ser técnicamente precisa, especialmente en la segunda parte.

Estás describiendo los operadores de cortocircuito (_short-circuit operators_) de JavaScript:

- `||` — OR lógico.
    
- `&&` — AND lógico.
    
- `??` — Nullish coalescing (coalescencia de nulos).
    

La diferencia fundamental es que **estos operadores no devuelven necesariamente un booleano (**`true` **o** `false`**), sino uno de los valores de sus operandos**.

## **1. Diferencias entre los operadores**

Tu primera afirmación es correcta, aunque conviene definir exactamente qué significa _falsy_.

### `||` **— OR lógico**

Devuelve el operando de la derecha cuando el de la izquierda es _falsy_. Si es _truthy_, devuelve el de la izquierda.

En JavaScript, los valores falsy son:

- `false`
    
- `0`
    
- `-0`
    
- `0n`
    
- `""` (cadena vacía)
    
- `null`
    
- `undefined`
    
- `NaN`
    

```
console.log(0 || 10);          // 10
console.log("" || "Default"); // "Default"
console.log(false || true);   // true
console.log(25 || 10);        // 25
console.log(null || "Hola");  // "Hola"
```

### `??` **— Nullish coalescing**

Devuelve el operando de la derecha exclusivamente cuando el de la izquierda es `null` o `undefined`.

```
console.log(0 ?? 10);          // 0
console.log("" ?? "Default");  // ""
console.log(false ?? true);    // false
console.log(null ?? "Hola");   // "Hola"
console.log(undefined ?? 10);  // 10
```

La diferencia es importante cuando `0`, `false` o `""` son valores válidos que queremos conservar.

MDN+1

## **2. ¿Qué devuelve** `&&`**,** `||` **y** `??`**?**

Tu segunda afirmación también es correcta en esencia, pero cambiaría la expresión «último que se haya llegado a procesar».

La regla es:

**Estos operadores devuelven el valor del último operando evaluado, no necesariamente el último operando escrito en la expresión.**

Veamos cada uno:

### `&&` **— AND lógico**

- Si el operando izquierdo es falsy, devuelve el izquierdo sin evaluar el derecho.
    
- Si es truthy, evalúa el derecho y devuelve su valor.
    

```
console.log(0 && "Hola");          // 0
console.log("Hola" && "Mundo");    // "Mundo"
console.log(true && false);        // false
console.log(true && 25);           // 25
```

### `||` **— OR lógico**

- Si el izquierdo es truthy, devuelve el izquierdo sin evaluar el derecho.
    
- Si es falsy, evalúa el derecho y devuelve su valor.
    

```
console.log("Hola" || "Mundo"); // "Hola"
console.log(0 || "Mundo");      // "Mundo"
console.log(false || 25);      // 25
```

### `??` **— Nullish coalescing**

- Si el izquierdo no es `null` ni `undefined`, devuelve el izquierdo sin evaluar el derecho.
    
- Si es `null` o `undefined`, evalúa el derecho y devuelve su valor.
    

```
console.log(0 ?? 10);          // 0
console.log(null ?? 10);       // 10
console.log(undefined ?? 10);  // 10
```

GitHub+1

## **3. Tabla comparativa**

| Operador | Condición para devolver el izquierdo | Si no se cumple     |     |     |     |
| -------- | ------------------------------------ | ------------------- | --- | --- | --- |
| \|\|     | Es truthy                            | Devuelve el derecho |     |     |     |
| &&       | Es Falsy                             | Devuelve el derecho |     |     |     |
| `??`     | No es nullish                        | Devuelve el derecho |     |     |     |

## **4. Ejemplo práctico: evaluación y cortocircuito**

Una característica importante es que el cortocircuito evita ejecutar el segundo operando cuando ya se puede determinar el resultado.

```
function ejecutar() {
    console.log("Función ejecutada");
    return "Resultado";
}

console.log(false && ejecutar());
// false
// No ejecuta la función.

console.log(true || ejecutar());
// true
// No ejecuta la función.

console.log(null ?? ejecutar());
// "Función ejecutada"
// "Resultado"
```

Esto no es solamente una optimización: también afecta al comportamiento del programa, porque evita efectos secundarios de las expresiones que no llegan a evaluarse.

## **5. Tu afirmación corregida**

Esta sería mi versión, técnicamente más precisa y adecuada para tus apuntes de JavaScript:

**Operadores de cortocircuito (**`&&`**,** `||` **y** `??`**)**

- Con `||` se devuelve el operando de la derecha cuando el de la izquierda es _falsy_. En caso contrario, se devuelve el izquierdo.
    
- Con `??` se devuelve el operando de la derecha únicamente cuando el de la izquierda es `null` o `undefined`. En caso contrario, se devuelve el izquierdo.
    
- Con `&&` se devuelve el operando de la derecha cuando el de la izquierda es _truthy_. En caso contrario, se devuelve el izquierdo.
    

**Evaluación de cortocircuito:**

Los tres operadores evalúan sus operandos de izquierda a derecha y devuelven el valor del último operando evaluado. Cuando el valor del operando izquierdo permite determinar el resultado, se produce un cortocircuito y el operando derecho no llega a evaluarse.

**Mi recomendación:** quédate especialmente con esta última regla. Es la propiedad que comparten los tres operadores y una de las características más importantes de JavaScript para escribir expresiones condicionales, asignaciones por defecto y evaluaciones perezosas.

Documentación oficial:

- [MDN – Logical OR (||)](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Logical_OR?utm_source=chatgpt.com).
    
- [MDN – Nullish coalescing (??)](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Nullish_coalescing?utm_source=chatgpt.com).
    
- [MDN – Expressions and operators](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Expressions_and_operators?utm_source=chatgpt.com).



Perfecto. Seguimos con el temario de JavaScript.

Una precisión: no puedo ver qué opciones has seleccionado en el cuestionario anterior, así que no voy a atribuirte una puntuación ni dar por verificadas respuestas que no puedo consultar. Mantendremos esos conceptos como materia pendiente de evaluación.

# **JavaScript — Lección 5: variables, ámbito y hoisting**

Vamos a estudiar tres conceptos fundamentales para comprender cómo JavaScript gestiona las variables:

1. `var`, `let` y `const`.
    
2. Scope (ámbito de las variables).
    
3. Hoisting y Temporal Dead Zone (TDZ).
    

## **1.** `var`**,** `let` **y** `const`

Ya hemos visto sus diferencias básicas, pero ahora vamos a profundizar en su comportamiento.

|Característica|`var`|`let`|`const`|
|---|---|---|---|
|Reasignación|Sí|Sí|No|
|Redeclaración en el mismo ámbito|Sí|No|No|
|Scope de bloque|No|Sí|Sí|
|Hoisting|Sí|Sí|Sí|
|Inicialización automática|`undefined`|No|No|

### **Redeclaración**

Con `var` podemos declarar varias veces una variable dentro del mismo ámbito:

```
var username = "Juan";
var username = "Pedro";

console.log(username); // Pedro
```

Con `let` y `const` esto produce un error:

```
let username = "Juan";
let username = "Pedro"; // SyntaxError
```

No obstante, podemos reasignar una variable declarada con `let`:

```
let username = "Juan";
username = "Pedro"; // Correcto
```

## **2. Scope: ámbito de las variables**

El _scope_ determina desde qué partes del código podemos acceder a una variable.

JavaScript tiene varios tipos de ámbito. Vamos a centrarnos inicialmente en los tres principales.

### **A. Global scope**

Una variable declarada fuera de cualquier función o bloque tiene ámbito global dentro de su contexto de ejecución.

```
const username = "Juan";

function greet() {
    console.log(username);
}

greet(); // Juan
```

La función puede acceder a la variable porque está declarada en un ámbito exterior.

### **B. Function scope**

Las variables declaradas con `var` tienen ámbito de función.

```
function example() {
    var message = "Hola";
    console.log(message);
}

example(); // Hola

console.log(message); // ReferenceError
```

La variable existe dentro de la función, pero no es accesible desde fuera.

### **C. Block scope**

`let` y `const` tienen ámbito de bloque.

Un bloque se delimita mediante llaves `{}`.

```
if (true) {
    let age = 25;
    const username = "Juan";
}

console.log(age);      // ReferenceError
console.log(username); // ReferenceError
```

Sin embargo, `var` no respeta ese ámbito:

```
if (true) {
    var age = 25;
}

console.log(age); // 25
```

**Recomendación profesional:** utiliza `const` por defecto y `let` cuando necesites reasignar. Evita `var` en código moderno salvo que estés trabajando con código heredado.

## **3. Hoisting**

El _hoisting_ es el comportamiento por el que las declaraciones se procesan antes de ejecutar el código de su ámbito.

Esto puede producir comportamientos que parecen extraños inicialmente.

### **Hoisting con** `var`

```
console.log(username);

var username = "Juan";
```

Resultado:

```
undefined
```

Conceptualmente, podemos entenderlo como si JavaScript procesase el código así:

```
var username;

console.log(username);

username = "Juan";
```

La declaración se procesa antes, pero la asignación permanece en su posición original.

### **Hoisting con** `let` **y** `const`

```
console.log(username);

let username = "Juan";
```

Resultado:

```
ReferenceError
```

Aunque sus declaraciones también participan en el hoisting, no podemos acceder a ellas antes de su inicialización.

## **4. Temporal Dead Zone (TDZ)**

La _Temporal Dead Zone_ es el intervalo entre el inicio del ámbito de una variable `let` o `const` y el momento en que se inicializa.

Durante ese intervalo, intentar acceder a la variable produce un `ReferenceError`.

```
{
    // Temporal Dead Zone

    console.log(age); // ReferenceError

    let age = 25;
}
```

La TDZ evita que utilicemos accidentalmente variables antes de que hayan sido inicializadas.

## **Ejercicio 1 — Scope y hoisting**

Analiza este código:

```
console.log(a);

var a = 10;

function test() {
    var b = 20;
    let c = 30;

    if (true) {
        var d = 40;
        let e = 50;
    }

    console.log(b);
    console.log(c);
    console.log(d);
    console.log(e);
}

test();
```

**Cuestionario**

6/6

**1. ¿Qué imprime el primer console.log(a)?**

10

undefined

ReferenceError

Correcto

**2. ¿Qué imprime console.log(b) dentro de test()?**

20

undefined

ReferenceError

Correcto

**3. ¿Qué imprime console.log(c)?**

30

undefined

ReferenceError

Correcto

**4. ¿Qué imprime console.log(d)?**

40

undefined

ReferenceError

Correcto

**5. ¿Qué sucede con console.log(e)?**

Imprime 50

Imprime undefined

ReferenceError

Correcto

**6. ¿Se ejecuta alguna instrucción posterior a console.log(e) dentro de test()?**

Sí

No, la excepción interrumpe la ejecución de la función

Correcto

**Pregunta de razonamiento:** ¿Por qué `d` es accesible fuera del bloque `if`, mientras que `e` no lo es?

--1 b, 2 a, 3 a, 4 a, 5 c, 6 b

--porque var es accesible fuera del bloque a diferencia de let y const

# **6****/6**

Repetir ejercicio

**Objetivo:** que puedas explicar no solo qué imprime JavaScript, sino por qué. Después abordaremos closures y funciones de orden superior, siguiendo el orden del temario.


--var tiene ambito de funcion lo cual quiere decir que una variable declarada dentro de una funcion con var solo puede ser leida dentro de esa funcion, 

por otra parte una variable declarada con let y const tiene ambito de bloque es decir: 
o solo vive dentro de la funcion, 
o solo vive dentro de los bloques que pueden existir dentro de una funcion ej if, for o while 

por otra parte Una variable declarada fuera de cualquier función o bloque tiene ámbito global dentro de su contexto de ejecución.

- **Ámbito de función (`var`):** Es correcto. Si declaras una variable con `var` dentro de una función, solo existe ahí dentro (incluyendo bloques internos como `if`, while o `for`), y no se puede leer desde afuera.
-
- **Ámbito de bloque (`let` y `const`):** Es exacto. Las llaves `{ }` definen el límite de estas variables, lo que aplica tanto para estructuras de control (`if`, `while`) como para el cuerpo de una función.
-
- **Ámbito global:** También es correcto. Cualquier variable declarada fuera de funciones o bloques queda disponible en todo el contexto de ejecución (por ejemplo, todo el archivo o el objeto global `window` en el navegador).
  
  1. Ámbito de función (`var`) — La casa entera

Cuando declaras algo con `var`, la variable pertenece a toda la casa (`function`). No le importan las paredes de las habitaciones (`if`, `for`), puede atravesarlas libremente.

javascript

```
function miCasa() {
  if (true) { // <--- Una habitación
    var televisor = "Encendido";
  }
  
  // Estoy fuera del 'if' (en el pasillo), pero sigo dentro de 'miCasa'
  console.log(televisor); // ✅ Funciona: imprime "Encendido"
}

// Estoy fuera de 'miCasa' (en la calle)
console.log(televisor); // ❌ Error: televisor no existe aquí afuera
```

Usa el código con precaución.

2. Ámbito de bloque (`let` y `const`) — La habitación exacta

Cuando declaras algo con `let` o `const`, la variable queda encerrada en las llaves `{ }` exactas donde nació, ya sean las llaves de una habitación (`if`) o las llaves de toda la casa (`function`).

javascript

```
function miCasa() {
  let sofa = "Cómodo"; // Nació en las llaves de la función (toda la casa)

  if (true) { // <--- Una habitación con sus propias llaves { }
    let diarioSecreto = "Privado";
    console.log(sofa); // ✅ Funciona: el sofá está en la casa
  }
  
  // Salí de la habitación 'if'
  console.log(diarioSecreto); // ❌ Error: no puede salir de sus llaves { }
}
```


Perfecto. Damos por superados los conceptos de `var`, `let`, `const`, scope, hoisting y Temporal Dead Zone.

Seguimos con el siguiente apartado del temario: **closures y funciones de orden superior (Higher-Order Functions)**. Son conceptos fundamentales de JavaScript y aparecen constantemente en React, programación funcional y desarrollo backend con Node.js.

# **JavaScript — Lección 6: funciones y closures**

## **1. Funciones como ciudadanos de primera clase**

JavaScript trata las funciones como _first-class citizens_ (ciudadanos de primera clase).

Esto significa que podemos:

- Asignar funciones a variables.
    
- Pasar funciones como argumentos de otras funciones.
    
- Devolver funciones desde otras funciones.
    
- Almacenar funciones en objetos y arrays.
    

Por ejemplo:

```
function greet() {
    return "Hola";
}

const message = greet;

console.log(message()); // "Hola"
```

Fíjate en la diferencia:

```
greet(); // Ejecuta la función.
greet;   // Hace referencia a la función.
```

Cuando asignamos `greet` a `message`, no estamos ejecutando la función: estamos copiando su referencia.

## **2. Funciones de orden superior (Higher-Order Functions)**

Una función de orden superior es aquella que cumple al menos una de estas condiciones:

1. Recibe otra función como argumento.
    
2. Devuelve otra función como resultado.
    

Ejemplo:

```
function executeOperation(a, b, operation) {
    return operation(a, b);
}

function sum(a, b) {
    return a + b;
}

function multiply(a, b) {
    return a * b;
}

console.log(executeOperation(5, 3, sum));      // 8
console.log(executeOperation(5, 3, multiply)); // 15
```

`executeOperation` es una función de orden superior porque recibe otra función como argumento.

### **Callbacks**

Una función que se pasa como argumento a otra función se denomina _callback_.

```
function greet(name, callback) {
    console.log("Hola " + name);
    callback();
}

function sayGoodbye() {
    console.log("Hasta luego");
}

greet("Juan", sayGoodbye);
```

Resultado:

```
Hola Juan
Hasta luego
```

Los callbacks son especialmente importantes en JavaScript porque permiten gestionar operaciones asíncronas, eventos y procesamiento de datos.

## **3. Closures (clausuras)**

Este es uno de los conceptos más importantes de JavaScript.

Un _closure_ se produce cuando una función conserva acceso a las variables de su ámbito léxico exterior, incluso después de que la función exterior haya terminado de ejecutarse.

Vamos a verlo paso a paso.

```
function createCounter() {
    let count = 0;

    return function() {
        count++;
        return count;
    };
}

const counter = createCounter();

console.log(counter()); // 1
console.log(counter()); // 2
console.log(counter()); // 3
```

¿Qué está pasando?

1. Ejecutamos `createCounter()`.
    
2. Se crea la variable `count`, inicialmente con valor `0`.
    
3. La función exterior devuelve una función interna.
    
4. La función exterior termina.
    
5. La función interna sigue teniendo acceso a `count`.
    
6. Cada ejecución incrementa el mismo contador.
    

Normalmente, podrías pensar que `count` debería desaparecer al finalizar `createCounter()`. Sin embargo, como la función devuelta todavía necesita acceder a esa variable, JavaScript conserva el entorno léxico necesario.

### **¿Para qué sirven los closures?**

Son útiles para:

- Encapsular variables privadas.
    
- Mantener estado entre ejecuciones.
    
- Crear funciones configurables.
    
- Implementar patrones como factories y módulos.
    
- Gestionar callbacks y eventos.
    

### **Ejemplo: encapsulación**

```
function createBankAccount(initialBalance) {
    let balance = initialBalance;

    return {
        deposit(amount) {
            balance += amount;
        },

        withdraw(amount) {
            if (amount > balance) {
                return false;
            }

            balance -= amount;
            return true;
        },

        getBalance() {
            return balance;
        }
    };
}

const account = createBankAccount(100);

account.deposit(50);

console.log(account.getBalance()); // 150

console.log(account.balance); // undefined
```

La variable `balance` no es accesible directamente desde fuera de la función. Solo podemos interactuar con ella a través de los métodos proporcionados.

Es una forma de encapsulación basada en closures.

## **4. Métodos de arrays:** `map`**,** `filter` **y** `reduce`

Estos tres métodos son fundamentales en JavaScript moderno.

[JavaScript Array Methods You Must Know - DEV Community](https://images.openai.com/static-rsc-4/e8WqSDg_tlamKRvNzO8QxNLTL8CV1t6_zgPMK45zlkl4LrAxBddbrFk0cdubaMVQpvWiiUO6uKEcFo5sgii3s-rzoAgmmkc3_NuEcEO_H727MZuHUyDSCT91p06EWJs4kztCke0qW6RokHRd8F9bhcLXV3Tvn41R-h3ZBO001lE?purpose=inline)

`map()`

Transforma cada elemento de un array y devuelve un nuevo array con los resultados.

```
const numbers = [1, 2, 3];

const doubled = numbers.map(n => n * 2);

console.log(doubled); // [2, 4, 6]
```

[JavaScript Array Methods You Must Know - DEV Community](https://images.openai.com/static-rsc-4/eLqRxgF3Ce86fAriGEzYaQn9l3P6nhm314cDZqEd2Yr06lmhz5trBXMlIdr2royzKvGKB9TNMrGeToLle_gowDmshqrJyOkpi7DKsFA9uwD67C4--A_IxWhPSrOJ1KyfvdTTUvwb7tMF4IBIPBSoondBWdWoJ1ZIwekeM_tV4As?purpose=inline)

`filter()`

Selecciona los elementos que cumplen una condición y devuelve un nuevo array.

```
const numbers = [1, 2, 3, 4, 5];

const even = numbers.filter(n => n % 2 === 0);

console.log(even); // [2, 4]
```

[Array Methods in JavaScript You Must Know | by Sumedh Barsagade | Mar, 2026 | Medium](https://images.openai.com/static-rsc-4/1KnJ_W2X8T3VmFFsF1XKo7fJt36gBJbvFELQ2s_rkD7i3CKXcOLKhMHqLZqMwO31cJRFeF0bVlshRFBqfMfSoXWbdZwKhACXWb8VLKO0SAF8jvStgQQFe4Z_izVpw0MTtwQcGBctBA_FMSRJ4F-32EM4U-55hxtyHD1QUDmBd2w?purpose=inline)

`reduce()`

Recorre el array acumulando sus elementos en un único resultado, que puede ser un número, un objeto, otro array, etc.

```
const numbers = [1, 2, 3, 4];

const total = numbers.reduce(
    (accumulator, current) => accumulator + current,
    0
);

console.log(total); // 10
```

En `reduce()`:

- `accumulator`: resultado acumulado hasta el momento.
    
- `current`: elemento que se está procesando.
    
- `0`: valor inicial del acumulador.
    

## **5. Diferencia entre** `map`**,** `filter` **y** `reduce`

|Método|Objetivo|Resultado|
|---|---|---|
|`map()`|Transformar|Array|
|`filter()`|Filtrar|Array|
|`reduce()`|Acumular|Cualquier tipo de valor|

Una observación importante: ninguno de estos métodos modifica el array original por sí mismo, aunque las funciones callback podrían modificar objetos que reciban como argumentos.

# **Ejercicio 1 — Higher-Order Functions y Closures**

Vamos a comprobar primero que comprendes los fundamentos antes de pasar a los métodos de arrays.

Analiza este código:

```
function createMultiplier(multiplier) {
    return function(number) {
        return number * multiplier;
    };
}

const double = createMultiplier(2);
const triple = createMultiplier(3);

console.log(double(5));
console.log(triple(5));
console.log(double(10));
```

**Evaluación de closures**

5/5

**1. ¿Qué devuelve double(5)?**

5

10

15

Correcto

**2. ¿Qué devuelve triple(5)?**

10

15

25

Correcto

**3. ¿Qué devuelve double(10)?**

10

20

30

Correcto

**4. ¿Por qué double sigue teniendo acceso a multiplier?**

Porque multiplier es global

Porque se conserva mediante un closure

Porque createMultiplier sigue ejecutándose

Correcto

**5. ¿double y triple comparten la misma variable multiplier?**

Sí, siempre comparten el mismo estado

No, cada llamada a createMultiplier crea su propio entorno léxico

Sí, porque ambas funciones se declaran en el mismo archivo

Correcto

**Pregunta de razonamiento:** Explica qué es un closure y por qué `double` y `triple` pueden conservar multiplicadores diferentes.

el closure permite que una funcion interna obtenga el argumento de la funcion externa

# **5****/5**

Repetir ejercicio

**Siguiente paso:** cuando consolidemos closures, profundizaremos en `map()`, `filter()`, `reduce()`, `forEach()` y funciones flecha. Después veremos `this`, `bind`, `call` y `apply`, siguiendo el orden del temario.

-1 b, 2 b, 3 c, 4 b, 5 b

todo correcto, seguimos

Perfecto. Damos por consolidados los fundamentos de **closures, funciones de orden superior y callbacks**.

Continuamos con los métodos de arrays, especialmente importantes en JavaScript moderno y en el desarrollo con React.

# **JavaScript — Lección 7: métodos de arrays**

Vamos a estudiar cinco métodos:

1. `forEach()`
    
2. `map()`
    
3. `filter()`
    
4. `find()`
    
5. `reduce()`
    

Todos reciben una función callback, pero tienen objetivos diferentes.

## **1.** `forEach()`**: iterar sobre un array**

Ejecuta una función para cada elemento del array.

```
const numbers = [1, 2, 3, 4];

numbers.forEach(number => {
    console.log(number);
});
```

Resultado:

```
1
2
3
4
```

Una característica importante: `forEach()` devuelve `undefined`.

```
const result = numbers.forEach(n => n * 2);

console.log(result); // undefined
```

No sirve para transformar y obtener un nuevo array. Para eso utilizamos `map()`.

## **2.** `map()`**: transformar elementos**

Ejecuta una función sobre cada elemento y devuelve un nuevo array con los resultados.

```
const prices = [10, 20, 30];

const pricesWithTax = prices.map(price => price * 1.21);

console.log(pricesWithTax);
// [12.1, 24.2, 36.3]
```

El array original permanece intacto:

```
console.log(prices);
// [10, 20, 30]
```

Es especialmente útil para transformar datos recibidos desde una API.

Por ejemplo:

```
const users = [
    { id: 1, name: "Juan" },
    { id: 2, name: "Pedro" },
    { id: 3, name: "Ana" }
];

const usernames = users.map(user => user.name);

console.log(usernames);
// ["Juan", "Pedro", "Ana"]
```

## **3.** `filter()`**: filtrar elementos**

Devuelve un nuevo array con los elementos que cumplen una condición.

```
const numbers = [1, 2, 3, 4, 5, 6];

const evenNumbers = numbers.filter(number => number % 2 === 0);

console.log(evenNumbers);
// [2, 4, 6]
```

La función callback debe devolver un valor que JavaScript interprete como verdadero o falso.

Otro ejemplo:

```
const users = [
    { name: "Juan", age: 25 },
    { name: "Pedro", age: 16 },
    { name: "Ana", age: 30 }
];

const adults = users.filter(user => user.age >= 18);

console.log(adults);
```

Resultado: Juan y Ana.

## **4.** `find()`**: buscar un elemento**

Devuelve el primer elemento que cumple una condición.

```
const users = [
    { id: 1, name: "Juan" },
    { id: 2, name: "Pedro" },
    { id: 3, name: "Ana" }
];

const user = users.find(user => user.id === 2);

console.log(user);
// { id: 2, name: "Pedro" }
```

Si no encuentra ningún elemento, devuelve `undefined`.

La diferencia con `filter()`:

```
const numbers = [2, 4, 6, 8];

const result1 = numbers.find(n => n > 3);
const result2 = numbers.filter(n => n > 3);

console.log(result1); // 4
console.log(result2); // [4, 6, 8]
```

## **5.** `reduce()`**: acumular resultados**

Es probablemente el método más versátil de los cinco.

Permite recorrer un array y acumular un resultado.

Su sintaxis:

```
array.reduce((accumulator, currentValue) => {
    // Operación
}, initialValue);
```

Ejemplo: sumar todos los números.

```
const numbers = [10, 20, 30, 40];

const total = numbers.reduce((acc, current) => {
    return acc + current;
}, 0);

console.log(total); // 100
```

Podemos representar su funcionamiento así:

**Evolución del acumulador**

|   |   |   |
|---|---|---|
|**Iteración**|**Elemento**|**Acumulador**|
|1|10|**10**|
|2|20|**30**|
|3|30|**60**|
|4|40|**100**|

Valor inicial del acumulador: 0.

`reduce()` también permite construir objetos:

```
const products = [
    { category: "Hardware", price: 100 },
    { category: "Software", price: 50 },
    { category: "Hardware", price: 200 }
];

const totals = products.reduce((acc, product) => {
    acc[product.category] = (acc[product.category] || 0) + product.price;

    return acc;
}, {});

console.log(totals);

// {
//   Hardware: 300,
//   Software: 50
// }
```

Aquí el acumulador es un objeto, no un número.

## **6. Comparativa general**

|Método|Devuelve|Utilidad|
|---|---|---|
|`forEach()`|`undefined`|Ejecutar una operación por elemento|
|`map()`|Array|Transformar elementos|
|`filter()`|Array|Seleccionar elementos|
|`find()`|Elemento o `undefined`|Buscar el primero que cumple|
|`reduce()`|Cualquier valor|Acumular o construir resultados|

**Consejo de desarrollo:** no utilices `reduce()` para absolutamente todo. Aunque permite resolver muchos problemas, `map()`, `filter()` y `find()` suelen expresar mejor la intención del código cuando su funcionalidad encaja.

# **Ejercicio 1 — Procesamiento de datos**

Imagina que estás desarrollando una API para gestionar usuarios.

Disponemos de este array:

```
const users = [
    { id: 1, name: "Juan", age: 25, active: true, salary: 2500 },
    { id: 2, name: "Pedro", age: 17, active: false, salary: 1200 },
    { id: 3, name: "Ana", age: 30, active: true, salary: 3000 },
    { id: 4, name: "Laura", age: 22, active: true, salary: 2200 },
    { id: 5, name: "Carlos", age: 16, active: false, salary: 1000 }
];
```

**Evaluación**

6/6

**1. ¿Qué método utilizarías para obtener un array con los nombres de todos los usuarios?**

forEach()

map()*

find()

Incorrecto: map()

map transforma cada usuario en su nombre y devuelve un nuevo array.

**2. ¿Qué método utilizarías para obtener exclusivamente los usuarios activos?**

filter()*

map()

reduce()

Correcto

filter selecciona todos los elementos que cumplen la condición active === true.

**3. ¿Qué método utilizarías para encontrar al usuario con id 3?**

filter()

find()*

forEach()

Correcto

find devuelve el primer elemento que cumple la condición.

**4. ¿Qué método utilizarías para calcular la suma de todos los salarios?**

map()

find()

reduce()*

Correcto

reduce permite acumular todos los salarios en un único número.

**5. ¿Qué devuelve forEach()?**

Un nuevo array

El último elemento

undefined*

Correcto

forEach ejecuta el callback, pero su valor de retorno es undefined.

**6. ¿Qué devuelve find() si no encuentra coincidencias?**

Un array vacío

undefined*

null

Correcto

find devuelve undefined cuando no existe ningún elemento que cumpla la condición.

**Pregunta práctica:** ¿Cómo escribirías una expresión utilizando `filter()` para obtener los usuarios activos y mayores de edad?

No hace falta que escribas todo el array; basta con la expresión que obtiene el resultado.

const adults = users.filter(user => user.age >= 18 && user.active = true);

# **5****/6**

Repetir ejercicio

Cuando dominemos estos métodos, pasaremos a `this`, `bind()`, `call()` y `apply()`, que son los siguientes conceptos de JavaScript en nuestro itinerario.


Perfecto. Damos por superados `forEach()`, `map()`, `filter()`, `find()` y `reduce()`, incluyendo su aplicación al procesamiento de datos.

El siguiente bloque de nuestro itinerario es especialmente importante para entender JavaScript orientado a objetos, eventos, callbacks y frameworks como React y Angular.

# **JavaScript — Lección 8:** `this`**,** `call()`**,** `apply()` **y** `bind()`

## **1. ¿Qué es** `this`**?**

`this` es una referencia al contexto de ejecución de una función.

Su valor depende principalmente de **cómo se invoca la función**, no de dónde se declara.

Esta distinción es fundamental.

### **A.** `this` **dentro de un objeto**

Cuando invocamos un método a través de un objeto, `this` normalmente hace referencia al objeto que realiza la llamada.

```
const user = {
    name: "Juan",

    greet() {
        console.log(`Hola, soy ${this.name}`);
    }
};

user.greet(); // Hola, soy Juan
```

En este caso:

```
this === user; // true, dentro de greet()
```

### **B.** `this` **en una función independiente**

En una función normal, `this` depende del modo de ejecución.

```
function showThis() {
    console.log(this);
}

showThis();
```

En JavaScript moderno:

- En modo estricto (`"use strict"`), `this` es `undefined`.
    
- En modo no estricto, normalmente apunta al objeto global (`globalThis`).
    

Los módulos JavaScript y las clases utilizan modo estricto.

### **C. Las arrow functions y** `this`

Las funciones flecha tienen un comportamiento especial: **no crean su propio** `this`.

Heredan el `this` léxico del contexto en el que fueron definidas.

Observa:

```
const user = {
    name: "Juan",

    greet: () => {
        console.log(this.name);
    }
};

user.greet();
```

Esto no devuelve `"Juan"`.

¿Por qué? Porque la función flecha no obtiene `this` del objeto `user`. Hereda el contexto exterior.

Por eso, como regla general, es preferible utilizar métodos normales para los métodos de objetos cuando necesitas acceder a sus propiedades mediante `this`.

Un caso donde las arrow functions son muy útiles:

```
const user = {
    name: "Juan",

    greet() {
        const callback = () => {
            console.log(this.name);
        };

        callback();
    }
};

user.greet(); // Juan
```

La arrow function hereda el `this` del método `greet()`.

## **2.** `call()`**: invocar una función con un** `this` **determinado**

`call()` permite ejecutar una función indicando explícitamente qué objeto debe utilizar como `this`.

Sintaxis:

```
functionName.call(thisArg, arg1, arg2, ...);
```

Ejemplo:

```
function greet(city, country) {
    console.log(
        `Hola, soy ${this.name}, de ${city}, ${country}`
    );
}

const user = {
    name: "Juan"
};

greet.call(user, "Santander", "España");
```

Resultado:

```
Hola, soy Juan, de Santander, España
```

La función `greet` no pertenece al objeto `user`, pero `call()` permite ejecutarla utilizando ese objeto como contexto.

## **3.** `apply()`**: parecido a** `call()`**, pero con arrays**

`apply()` hace prácticamente lo mismo que `call()`, pero recibe los argumentos de la función agrupados en un array.

```
function greet(city, country) {
    console.log(`${this.name} vive en ${city}, ${country}`);
}

const user = {
    name: "Juan"
};

greet.apply(user, ["Santander", "España"]);
```

Comparación:

```
greet.call(user, "Santander", "España");

greet.apply(user, ["Santander", "España"]);
```

Ambas llamadas producen el mismo resultado.

|Método|Argumentos|
|---|---|
|`call()`|Individuales|
|`apply()`|En un array|

## **4.** `bind()`**: crear una función con un** `this` **permanente**

A diferencia de `call()` y `apply()`, `bind()` no ejecuta inmediatamente la función.

Devuelve una nueva función con el `this` asociado al objeto indicado.

```
function greet() {
    console.log(`Hola, soy ${this.name}`);
}

const user = {
    name: "Juan"
};

const boundGreet = greet.bind(user);

boundGreet(); // Hola, soy Juan
```

La función original no se ha modificado.

`boundGreet` es una nueva función que conserva el contexto establecido mediante `bind()`.

También podemos fijar argumentos:

```
function greet(city) {
    console.log(`Hola, soy ${this.name} y vivo en ${city}`);
}

const user = {
    name: "Juan"
};

const greetFromSantander = greet.bind(user, "Santander");

greetFromSantander();
```

Esto se conoce como _partial application_: fijamos algunos argumentos de una función para reutilizarla posteriormente.

## **5. Comparación de los tres métodos**

|Característica|`call()`|`apply()`|`bind()`|
|---|---|---|---|
|Establece `this`|Sí|Sí|Sí|
|Ejecuta inmediatamente|Sí|Sí|No|
|Devuelve una función nueva|No|No|Sí|
|Argumentos|Individuales|Array|Individuales|

Una limitación importante: estos métodos no pueden cambiar el `this` propio de una arrow function, porque su contexto es léxico.

## **6. Aplicación práctica: pérdida de contexto**

Este es un problema bastante habitual en JavaScript.

```
const user = {
    name: "Juan",

    greet() {
        console.log(`Hola, soy ${this.name}`);
    }
};

const greetFunction = user.greet;

greetFunction();
```

¿Por qué puede fallar?

Porque hemos extraído el método del objeto y después lo ejecutamos como una función independiente.

La llamada original era:

```
user.greet();
```

Pero ahora es:

```
greetFunction();
```

Ya no existe una referencia a `user` en la llamada.

Podemos solucionarlo utilizando `bind()`:

```
const greetFunction = user.greet.bind(user);

greetFunction(); // Hola, soy Juan
```

Este problema aparece frecuentemente al pasar métodos como callbacks o manejadores de eventos.

# **Ejercicio 1 — Evaluación de** `this`

Analiza este código:

```
const user = {
    name: "Juan",

    greet() {
        return `Hola, ${this.name}`;
    }
};

const anotherUser = {
    name: "Pedro"
};

console.log(user.greet());

console.log(user.greet.call(anotherUser));

const greet = user.greet.bind(anotherUser);

console.log(greet());
```

**Cuestionario**

5/5

**1. ¿Qué devuelve user.greet()?**

"Hola, Juan"

"Hola, Pedro"

undefined

Correcto

**2. ¿Qué devuelve user.greet.call(anotherUser)?**

"Hola, Juan"

"Hola, Pedro"

TypeError

Correcto

**3. ¿Qué hace bind() en este ejemplo?**

Ejecuta inmediatamente greet

Crea una nueva función asociada a anotherUser

Modifica permanentemente user.greet

Correcto

**4. ¿Qué devuelve greet()?**

"Hola, Juan"

"Hola, Pedro"

undefined

Correcto

**5. ¿Qué diferencia principal existe entre call() y bind()?**

No existe ninguna

call ejecuta inmediatamente; bind devuelve una nueva función

bind ejecuta inmediatamente; call devuelve una función

Correcto

**Pregunta de razonamiento:** ¿Por qué `user.greet()` funciona correctamente, pero al extraer el método en `const greet = user.greet`, podemos perder el contexto de `this`?

porque estamos sacanado el metodo del objeto user, si no queremos pereder contexto al usar this hay que usar call, apply o bind

# **5****/5**

Repetir ejercicio

Cuando dominemos esto, continuaremos con **prototipos, herencia prototípica y clases ES6**, antes de terminar los fundamentos de JavaScript.

Perfecto. Damos por superados `forEach()`, `map()`, `filter()`, `find()` y `reduce()`, incluyendo su aplicación al procesamiento de datos.

El siguiente bloque de nuestro itinerario es especialmente importante para entender JavaScript orientado a objetos, eventos, callbacks y frameworks como React y Angular.

# **JavaScript — Lección 8:** `this`**,** `call()`**,** `apply()` **y** `bind()`

## **1. ¿Qué es** `this`**?**

`this` es una referencia al contexto de ejecución de una función.

Su valor depende principalmente de **cómo se invoca la función**, no de dónde se declara.

Esta distinción es fundamental.

### **A.** `this` **dentro de un objeto**

Cuando invocamos un método a través de un objeto, `this` normalmente hace referencia al objeto que realiza la llamada.

```
const user = {
    name: "Juan",

    greet() {
        console.log(`Hola, soy ${this.name}`);
    }
};

user.greet(); // Hola, soy Juan
```

En este caso:

```
this === user; // true, dentro de greet()
```

### **B.** `this` **en una función independiente**

En una función normal, `this` depende del modo de ejecución.

```
function showThis() {
    console.log(this);
}

showThis();
```

En JavaScript moderno:

- En modo estricto (`"use strict"`), `this` es `undefined`.
    
- En modo no estricto, normalmente apunta al objeto global (`globalThis`).
    

Los módulos JavaScript y las clases utilizan modo estricto.

### **C. Las arrow functions y** `this`

Las funciones flecha tienen un comportamiento especial: **no crean su propio** `this`.

Heredan el `this` léxico del contexto en el que fueron definidas.

Observa:

```
const user = {
    name: "Juan",

    greet: () => {
        console.log(this.name);
    }
};

user.greet();
```

Esto no devuelve `"Juan"`.

¿Por qué? Porque la función flecha no obtiene `this` del objeto `user`. Hereda el contexto exterior.

Por eso, como regla general, es preferible utilizar métodos normales para los métodos de objetos cuando necesitas acceder a sus propiedades mediante `this`.

Un caso donde las arrow functions son muy útiles:

```
const user = {
    name: "Juan",

    greet() {
        const callback = () => {
            console.log(this.name);
        };

        callback();
    }
};

user.greet(); // Juan
```

La arrow function hereda el `this` del método `greet()`.

## **2.** `call()`**: invocar una función con un** `this` **determinado**

`call()` permite ejecutar una función indicando explícitamente qué objeto debe utilizar como `this`.

Sintaxis:

```
functionName.call(thisArg, arg1, arg2, ...);
```

Ejemplo:

```
function greet(city, country) {
    console.log(
        `Hola, soy ${this.name}, de ${city}, ${country}`
    );
}

const user = {
    name: "Juan"
};

greet.call(user, "Santander", "España");
```

Resultado:

```
Hola, soy Juan, de Santander, España
```

La función `greet` no pertenece al objeto `user`, pero `call()` permite ejecutarla utilizando ese objeto como contexto.

## **3.** `apply()`**: parecido a** `call()`**, pero con arrays**

`apply()` hace prácticamente lo mismo que `call()`, pero recibe los argumentos de la función agrupados en un array.

```
function greet(city, country) {
    console.log(`${this.name} vive en ${city}, ${country}`);
}

const user = {
    name: "Juan"
};

greet.apply(user, ["Santander", "España"]);
```

Comparación:

```
greet.call(user, "Santander", "España");

greet.apply(user, ["Santander", "España"]);
```

Ambas llamadas producen el mismo resultado.

|Método|Argumentos|
|---|---|
|`call()`|Individuales|
|`apply()`|En un array|

## **4.** `bind()`**: crear una función con un** `this` **permanente**

A diferencia de `call()` y `apply()`, `bind()` no ejecuta inmediatamente la función.

Devuelve una nueva función con el `this` asociado al objeto indicado.

```
function greet() {
    console.log(`Hola, soy ${this.name}`);
}

const user = {
    name: "Juan"
};

const boundGreet = greet.bind(user);

boundGreet(); // Hola, soy Juan
```

La función original no se ha modificado.

`boundGreet` es una nueva función que conserva el contexto establecido mediante `bind()`.

También podemos fijar argumentos:

```
function greet(city) {
    console.log(`Hola, soy ${this.name} y vivo en ${city}`);
}

const user = {
    name: "Juan"
};

const greetFromSantander = greet.bind(user, "Santander");

greetFromSantander();
```

Esto se conoce como _partial application_: fijamos algunos argumentos de una función para reutilizarla posteriormente.

## **5. Comparación de los tres métodos**

|Característica|`call()`|`apply()`|`bind()`|
|---|---|---|---|
|Establece `this`|Sí|Sí|Sí|
|Ejecuta inmediatamente|Sí|Sí|No|
|Devuelve una función nueva|No|No|Sí|
|Argumentos|Individuales|Array|Individuales|

Una limitación importante: estos métodos no pueden cambiar el `this` propio de una arrow function, porque su contexto es léxico.

## **6. Aplicación práctica: pérdida de contexto**

Este es un problema bastante habitual en JavaScript.

```
const user = {
    name: "Juan",

    greet() {
        console.log(`Hola, soy ${this.name}`);
    }
};

const greetFunction = user.greet;

greetFunction();
```

¿Por qué puede fallar?

Porque hemos extraído el método del objeto y después lo ejecutamos como una función independiente.

La llamada original era:

```
user.greet();
```

Pero ahora es:

```
greetFunction();
```

Ya no existe una referencia a `user` en la llamada.

Podemos solucionarlo utilizando `bind()`:

```
const greetFunction = user.greet.bind(user);

greetFunction(); // Hola, soy Juan
```

Este problema aparece frecuentemente al pasar métodos como callbacks o manejadores de eventos.

# **Ejercicio 1 — Evaluación de** `this`

Analiza este código:

```
const user = {
    name: "Juan",

    greet() {
        return `Hola, ${this.name}`;
    }
};

const anotherUser = {
    name: "Pedro"
};

console.log(user.greet());

console.log(user.greet.call(anotherUser));

const greet = user.greet.bind(anotherUser);

console.log(greet());
```

**Cuestionario**

5/5

**1. ¿Qué devuelve user.greet()?**

"Hola, Juan"

"Hola, Pedro"

undefined

Correcto

**2. ¿Qué devuelve user.greet.call(anotherUser)?**

"Hola, Juan"

"Hola, Pedro"

TypeError

Correcto

**3. ¿Qué hace bind() en este ejemplo?**

Ejecuta inmediatamente greet

Crea una nueva función asociada a anotherUser

Modifica permanentemente user.greet

Correcto

**4. ¿Qué devuelve greet()?**

"Hola, Juan"

"Hola, Pedro"

undefined

Correcto

**5. ¿Qué diferencia principal existe entre call() y bind()?**

No existe ninguna

call ejecuta inmediatamente; bind devuelve una nueva función

bind ejecuta inmediatamente; call devuelve una función

Correcto

**Pregunta de razonamiento:** ¿Por qué `user.greet()` funciona correctamente, pero al extraer el método en `const greet = user.greet`, podemos perder el contexto de `this`?

porque estamos sacanado el metodo del objeto user, si no queremos pereder contexto al usar this hay que usar call, apply o bind

# **5****/5**

Repetir ejercicio

Cuando dominemos esto, continuaremos con **prototipos, herencia prototípica y clases ES6**, antes de terminar los fundamentos de JavaScript.

---


La confusión viene de mezclar dos conceptos que son independientes: **el modo estricto (**`strict mode`**) y el contexto de ejecución de** `this`. Vamos a separarlos, porque cuando entiendas esa diferencia, el comportamiento del código será mucho más intuitivo.

## **1. ¿Cómo se activa y desactiva el modo estricto?**

En JavaScript puedes activar el modo estricto escribiendo:

```
"use strict";
```

Debe aparecer al principio del archivo o de una función, antes de cualquier otra instrucción ejecutable.

**Ejemplo sin modo estricto:**

```
function showThis() {
    console.log(this);
}

showThis();
```

En un entorno JavaScript tradicional (script clásico) sin modo estricto, `this` dentro de esa función será el objeto global (`window` en un navegador).

**Ejemplo con modo estricto:**

```
"use strict";

function showThis() {
    console.log(this);
}

showThis();
```

Ahora `this` será `undefined`.

La diferencia es importante: el modo estricto evita que JavaScript convierta automáticamente un `this` inexistente en el objeto global.

### **¿Y cómo se desactiva?**

No necesitas escribir ninguna instrucción para desactivarlo. Simplemente no incluyes `"use strict"` en un script clásico que no esté ya en modo estricto.

Hay una particularidad importante:

|Contexto|¿Modo estricto?|
|---|---|
|Script clásico sin `"use strict"`|No|
|Script clásico con `"use strict"`|Sí|
|Módulo JavaScript (`import` / `export`)|Sí, automáticamente|
|Código de una clase (`class`)|Sí, automáticamente|

Por tanto, en un proyecto moderno que utiliza módulos ES6, normalmente ya estás trabajando en modo estricto sin tener que declararlo.

## **2. ¿Por qué** `user.greet()` **devuelve Juan?**

Aquí está la clave: **el valor de** `this` **no depende de que hayas creado el objeto con** `const`**, sino de cómo invocas la función.**

Analicemos tu código:

```
const user = {
    name: "Juan",

    greet() {
        console.log(`Hola, soy ${this.name}`);
    }
};

user.greet();
```

Primero:

```
const user = { ... };
```

Esto crea un objeto y asigna su referencia a la constante `user`.

Después:

```
user.greet();
```

Estás invocando `greet()` como un método del objeto `user`.

En esta llamada, JavaScript establece que:

```
this === user; // true
```

Por tanto:

```
this.name
```

equivale a:

```
user.name
```

Y el resultado es:

```
Hola, soy Juan
```

**Esto funciona exactamente igual con modo estricto activado.** El modo estricto no impide que `this` haga referencia a un objeto. Lo que cambia es el comportamiento cuando una función se ejecuta sin un contexto de objeto.

## **3. La diferencia importante: invocar un método o extraer su función**

Vamos a modificar ligeramente tu ejemplo.

**Caso A: invocación como método**

```
const user = {
    name: "Juan",
    greet() {
        console.log(this.name);
    }
};

user.greet();
```

Resultado: Juan

`this` apunta a `user`, porque la llamada se realiza mediante `user.greet()`.

**Caso B: extraer la función**

```
"use strict";

const user = {
    name: "Juan",
    greet() {
        console.log(this.name);
    }
};

const greetFunction = user.greet;

greetFunction();
```

Resultado: TypeError

`this` es `undefined`. Intentar acceder a `this.name` produce un error.

¿Por qué ocurre?

En el segundo caso:

```
const greetFunction = user.greet;
```

No estás creando una copia del objeto ni una función diferente. Estás guardando una referencia a la misma función.

Pero cuando haces:

```
greetFunction();
```

Ya no estás invocándola a través de `user`.

JavaScript no recuerda automáticamente que esa función pertenecía originalmente a `user`.

Por eso pierde el contexto de llamada.

## **4. ¿Cómo podemos conservar el contexto?**

Para eso existen `call`, `apply` y `bind`.

Por ejemplo:

```
const greetFunction = user.greet.bind(user);

greetFunction(); // Juan
```

`bind(user)` crea una nueva función cuyo `this` queda asociado a `user`.

También puedes cambiar el contexto temporalmente:

```
const anotherUser = {
    name: "Pedro"
};

user.greet.call(anotherUser); // Pedro
```

Aquí `call` ejecuta inmediatamente la función utilizando `anotherUser` como `this`.

## **5. Qué debes recordar**

|Situación|Valor de `this`|
|---|---|
|`user.greet()`|`user`|
|`anotherUser.greet()`|`anotherUser`|
|`greetFunction()` en modo estricto|`undefined`|
|`greetFunction.call(user)`|`user`|
|`greetFunction.bind(user)()`|`user`|
|Método definido con una arrow function|No tiene `this` propio|

La regla fundamental es:

**En las funciones normales,** `this` **depende principalmente de cómo se llama a la función, no de dónde se ha declarado.**

## **6. Comprobemos que ha quedado claro**

No quiero que memorices una tabla sin entender el mecanismo. Vamos a utilizar un ejemplo muy parecido al tuyo.

```
"use strict";

const user = {
    name: "Juan",

    greet() {
        return this.name;
    }
};

const anotherUser = {
    name: "Pedro"
};

const greet = user.greet;

console.log(user.greet());
console.log(greet.call(anotherUser));
console.log(greet());
```

**Responde las tres preguntas**

**1****.** **¿Qué devuelve `user.greet()`?**

undefined

Juan

Pedro

**Correcto**

La llamada se realiza mediante user, por lo que this apunta a user.

**2****.** **¿Qué devuelve `greet.call(anotherUser)`?**

Juan

Pedro

undefined

**Correcto**

call ejecuta la función estableciendo anotherUser como this.

**3****.** **¿Qué sucede con `greet()`?**

Devuelve Juan

Devuelve Pedro

Produce un TypeError

**Correcto**

greet es una llamada independiente. En modo estricto, this es undefined y acceder a this.name produce un TypeError.

Comprobar respuestas

## **3****/3 correctas**

Cuando resolvamos esto, seguiremos con las arrow functions y su comportamiento particular con `this`, que es precisamente otra de las fuentes habituales de confusión en JavaScript.

---

Perfecto. Damos por entendido el bloque de `this`, `call()`, `apply()` y `bind()`. Continuamos con el siguiente apartado de nuestro itinerario.

Ahora entramos en **programación orientada a objetos (OOP)**, un concepto especialmente importante para trabajar con JavaScript, TypeScript, Angular y muchos frameworks y bibliotecas.

# **JavaScript — Lección 9: Prototipos, herencia y clases ES6**

Vamos a dividir esta lección en tres partes:

1. Qué son los prototipos y cómo funciona la herencia prototípica.
    
2. Cómo crear objetos que heredan propiedades y métodos.
    
3. Cómo funcionan las clases ES6, los constructores y `extends`/`super`.
    

## **1. ¿Qué es la programación orientada a objetos?**

La programación orientada a objetos es un paradigma que organiza el código utilizando objetos que contienen:

- **Propiedades:** datos que describen un objeto.
    
- **Métodos:** funciones que representan comportamientos del objeto.
    

Por ejemplo, imagina que estamos desarrollando un videojuego:

```
const player = {
    name: "Juan",
    health: 100,
    level: 5,

    attack() {
        console.log(`${this.name} está atacando`);
    },

    heal(amount) {
        this.health += amount;
    }
};
```

Este objeto representa a un jugador.

Podemos consultar sus propiedades:

```
console.log(player.name);   // Juan
console.log(player.health); // 100
```

Y ejecutar sus métodos:

```
player.attack();
player.heal(20);
```

Esto ya lo conoces: no es más que un objeto con propiedades y funciones.

Pero imagina que nuestro videojuego tiene 100 jugadores.

¿Tendríamos que escribir los mismos métodos 100 veces?

No. Aquí es donde entran los prototipos y la herencia.

## **2. ¿Qué son los prototipos?**

JavaScript utiliza un mecanismo de herencia denominado **herencia prototípica** (_prototypal inheritance_).

La idea es que un objeto puede heredar propiedades y métodos de otro objeto.

Imagina estos dos objetos:

```
const animal = {
    eat() {
        console.log("El animal está comiendo");
    }
};

const dog = {
    bark() {
        console.log("Guau");
    }
};
```

Tenemos:

- `animal`, que tiene el método `eat()`.
    
- `dog`, que tiene el método `bark()`.
    

Pero queremos que `dog` también pueda utilizar `eat()`.

Podemos establecer que el prototipo de `dog` sea `animal`:

```
Object.setPrototypeOf(dog, animal);
```

Ahora podemos hacer:

```
dog.bark(); // Guau
dog.eat();  // El animal está comiendo
```

¡Y no hemos añadido `eat()` directamente a `dog`!

El objeto `dog` busca el método en su propio objeto. Como no lo encuentra, JavaScript busca en su prototipo.

**Cómo funciona la cadena de prototipos**

**dog**

Método propio: bark()

Su prototipo es

**animal**

Método heredado: eat()

Su propio prototipo

**Object.prototype**

Métodos comunes como toString()

Este mecanismo se conoce como **prototype chain** (cadena de prototipos).

Cuando JavaScript intenta acceder a una propiedad, sigue este orden:

1. Busca la propiedad en el propio objeto.
    
2. Si no existe, busca en su prototipo.
    
3. Si tampoco existe, continúa buscando en la cadena.
    
4. Si llega al final sin encontrarla, devuelve `undefined`.
    

Por ejemplo:

```
console.log(dog.bark);     // Función
console.log(dog.eat);      // Función heredada
console.log(dog.toString); // Función heredada
console.log(dog.fly);      // undefined
```

### **¿Cómo podemos consultar el prototipo?**

JavaScript proporciona:

```
Object.getPrototypeOf(dog);
```

Y para comprobar si un objeto hereda de otro:

```
animal.isPrototypeOf(dog); // true
```

`Object.setPrototypeOf()` sirve para modificar el prototipo, aunque normalmente es preferible establecerlo al crear el objeto, porque cambiarlo posteriormente puede perjudicar el rendimiento.

## **3. Crear objetos mediante** `Object.create()`

Existe otra forma de crear objetos indicando directamente su prototipo:

```
const animal = {
    eat() {
        console.log("Comiendo");
    }
};

const dog = Object.create(animal);

dog.bark = function () {
    console.log("Guau");
};
```

Ahora:

```
dog.eat();  // Comiendo
dog.bark(); // Guau
```

La diferencia es que `Object.create(animal)` crea un objeto nuevo cuyo prototipo es `animal`.

Es una herramienta útil para entender la herencia prototípica, aunque en aplicaciones modernas normalmente encontrarás clases ES6.

## **4. ¿Qué son las clases ES6?**

Las clases se introdujeron en ES6 (ECMAScript 2015).

Permiten definir una estructura reutilizable para crear objetos.

Por ejemplo, vamos a crear una clase `Player`:

```
class Player {
    constructor(name, health) {
        this.name = name;
        this.health = health;
    }

    attack() {
        console.log(`${this.name} está atacando`);
    }

    heal(amount) {
        this.health += amount;
    }
}
```

Vamos a entender sus partes.

`class Player`

Declara una clase llamada `Player`.

`constructor()`

Es un método especial que se ejecuta cuando creamos una instancia de la clase mediante `new`.

`this.name = name`

Guarda el nombre recibido en la propiedad del nuevo objeto.

`attack()` **y** `heal()`

Son métodos que estarán disponibles para las instancias de la clase mediante su prototipo.

### **Crear instancias**

Para crear un jugador:

```
const player1 = new Player("Juan", 100);
const player2 = new Player("Pedro", 150);
```

Ahora tenemos dos objetos diferentes:

```
console.log(player1.name);   // Juan
console.log(player1.health); // 100

console.log(player2.name);   // Pedro
console.log(player2.health); // 150
```

Y ambos pueden utilizar los mismos métodos:

```
player1.attack();
player2.attack();
```

**Relación entre la clase y sus instancias**

**Player**

Clase: constructor(), attack(), heal()

**player1**

Juan · 100 HP

**player2**

Pedro · 150 HP

Ambas instancias tienen sus propios datos y comparten los métodos definidos en Player.prototype.

Una cuestión importante: los métodos definidos en una clase no se copian individualmente en cada instancia. Se encuentran en el prototipo de la clase.

Podemos comprobarlo:

```
console.log(
    Object.getPrototypeOf(player1) === Player.prototype
); // true
```

Esto conecta directamente las clases ES6 con lo que acabamos de aprender sobre prototipos.

## **5. Herencia mediante** `extends`

Supongamos que nuestro videojuego tiene diferentes tipos de personajes:

- Jugadores.
    
- Enemigos.
    
- Jefes finales.
    

Todos tienen nombre y salud, pero cada tipo tiene comportamientos particulares.

Podemos crear una clase general y hacer que otras clases hereden de ella.

```
class Character {
    constructor(name, health) {
        this.name = name;
        this.health = health;
    }

    attack() {
        console.log(`${this.name} ataca`);
    }
}
```

Ahora creamos un enemigo:

```
class Enemy extends Character {
    constructor(name, health, damage) {
        super(name, health);
        this.damage = damage;
    }

    specialAttack() {
        console.log(`${this.name} causa ${this.damage} de daño`);
    }
}
```

Observa estas dos palabras:

`extends`

Indica que `Enemy` hereda de `Character`.

`super()`

Llama al constructor de la clase padre para inicializar las propiedades que comparte con ella.

Ahora podemos crear un enemigo:

```
const enemy = new Enemy("Slime", 200, 35);
```

Y utilizar sus métodos:

```
enemy.attack();
enemy.specialAttack();
```

Resultado:

```
Slime ataca
Slime causa 35 de daño
```

El enemigo dispone de `attack()` porque lo hereda de `Character`, y de `specialAttack()` porque lo define él mismo.

### **¿Qué ocurre si no utilizamos** `super()`**?**

En un constructor de una clase derivada (`extends`), debemos llamar a `super()` antes de utilizar `this`.

Esto es incorrecto:

```
class Enemy extends Character {
    constructor(name, health, damage) {
        this.damage = damage;
        super(name, health);
    }
}
```

Produce un `ReferenceError`.

Primero debe inicializarse la parte heredada del objeto mediante `super()`.

## **6. Sobrescribir métodos (****_method overriding_****)**

Una clase hija puede sustituir el comportamiento de un método heredado.

Por ejemplo:

```
class Character {
    attack() {
        console.log("Ataque normal");
    }
}

class Enemy extends Character {
    attack() {
        console.log("Ataque del enemigo");
    }
}
```

Ahora:

```
const enemy = new Enemy();

enemy.attack(); // Ataque del enemigo
```

Aunque `Character` tiene un método `attack()`, `Enemy` proporciona su propia implementación.

Esto se conoce como sobrescritura de métodos.

También podemos llamar al método original utilizando `super`:

```
class Enemy extends Character {
    attack() {
        super.attack();
        console.log("Ataque adicional");
    }
}
```

## **7. Métodos y propiedades estáticas**

Las clases también permiten declarar miembros estáticos utilizando `static`.

Un método estático pertenece a la propia clase, no a sus instancias.

```
class MathUtils {
    static sum(a, b) {
        return a + b;
    }
}
```

Podemos utilizarlo así:

```
console.log(MathUtils.sum(5, 3)); // 8
```

Pero no así:

```
const utils = new MathUtils();

utils.sum(5, 3); // TypeError
```

Esto sucede porque `sum()` pertenece a `MathUtils`, no a los objetos creados a partir de ella.

Un ejemplo real es:

```
Array.isArray([1, 2, 3]); // true
```

`isArray()` es un método estático de `Array`.

## **8. Resumen de los conceptos**

|Concepto|Función|
|---|---|
|Prototipo|Objeto del que otro objeto puede heredar|
|Prototype chain|Cadena de búsqueda de propiedades y métodos|
|`Object.create()`|Crea un objeto con un prototipo determinado|
|`class`|Define una estructura para crear objetos|
|`constructor()`|Inicializa una nueva instancia|
|`new`|Crea una instancia de una clase|
|`extends`|Establece herencia entre clases|
|`super()`|Invoca el constructor de la clase padre|
|`super.metodo()`|Invoca un método de la clase padre|
|`static`|Define miembros asociados a la clase|
|Overriding|Sobrescribe un método heredado|

Una precisión importante para entrevistas: **las clases ES6 no sustituyen el sistema de prototipos de JavaScript**. Son una sintaxis más cómoda para trabajar con él. La herencia sigue funcionando mediante la cadena de prototipos.

# **Ejercicio 1 — Prototipos y herencia**

Vamos a comprobar primero que entiendes la herencia prototípica antes de pasar a las clases.

Analiza:

```
const animal = {
    eat() {
        return "Comiendo";
    }
};

const dog = Object.create(animal);

dog.bark = function () {
    return "Guau";
};

console.log(dog.bark());
console.log(dog.eat());
console.log(dog.fly);
console.log(Object.getPrototypeOf(dog) === animal);
```

## **Cuestionario**

4 preguntas · Una respuesta por pregunta

**1****.** **¿Qué devuelve `dog.bark()`?**

undefined

Guau

Comiendo

**Correcto**

bark() está definido directamente en dog.

**2****.** **¿Qué devuelve `dog.eat()`?**

Comiendo

undefined

TypeError

**Correcto**

dog no tiene eat() directamente, pero lo hereda de animal.

**3****.** **¿Qué devuelve `dog.fly`?**

false

null

undefined

**Correcto**

JavaScript busca fly en dog y en toda su cadena de prototipos. Como no existe, devuelve undefined.

**4****.** **¿Qué devuelve `Object.getPrototypeOf(dog) === animal`?**

true

false

undefined

**Correcto**

Object.create(animal) establece animal como prototipo directo de dog.

Corregir respuestas

## **4****/4 correctas**

**Importante:** no pasaremos a destructuring, spread, rest y módulos hasta que tengas clara la diferencia entre un objeto, su prototipo y la herencia. Después haremos un segundo ejercicio con `class`, `constructor`, `extends` y `super`.

---


Perfecto. He comprobado las respuestas que seleccionaste en el ejercicio anterior: **4/4 correctas**.

Has demostrado que entiendes:

- Cómo se buscan propiedades y métodos en la cadena de prototipos.
    
- Cómo un objeto puede heredar métodos de otro.
    
- Qué ocurre cuando una propiedad no existe (`undefined`).
    
- Cómo comprobar el prototipo de un objeto con `Object.getPrototypeOf()`.
    

Pasamos a la segunda parte de la lección: **clases ES6 y herencia entre clases**.

# **JavaScript — Lección 9.2: Clases, instancias y herencia**

## **1. Crear una clase**

Recordemos este ejemplo:

```
class Player {
    constructor(name, health) {
        this.name = name;
        this.health = health;
    }

    attack() {
        console.log(`${this.name} está atacando`);
    }
}
```

Una clase es una estructura que permite crear múltiples objetos con propiedades y comportamientos comunes.

Para crear un objeto utilizamos `new`:

```
const player1 = new Player("Juan", 100);
const player2 = new Player("Pedro", 150);
```

Cada objeto es una **instancia** de `Player`.

**La clase y sus instancias**

**Player**

Plantilla: constructor() y attack()

**player1**

Juan

100 HP

**player2**

Pedro

150 HP

Son objetos independientes, pero comparten los métodos del prototipo Player.prototype.

Podemos comprobar si un objeto es una instancia de una clase mediante `instanceof`:

```
console.log(player1 instanceof Player); // true
console.log(player2 instanceof Player); // true
```

`instanceof` comprueba si el prototipo de la clase aparece en la cadena de prototipos del objeto.

## **2. El constructor y** `new`

El constructor es un método especial que inicializa las nuevas instancias.

```
class Player {
    constructor(name, health) {
        this.name = name;
        this.health = health;
    }
}
```

Cuando ejecutamos:

```
const player = new Player("Juan", 100);
```

JavaScript realiza, conceptualmente, estas operaciones:

1. Crea un objeto nuevo.
    
2. Establece su prototipo como `Player.prototype`.
    
3. Ejecuta el constructor con `this` haciendo referencia al nuevo objeto.
    
4. Devuelve ese objeto, salvo que el constructor devuelva explícitamente otro objeto.
    

Por eso podemos utilizar `this.name` y `this.health` dentro del constructor.

## **3. Herencia con** `extends`

Ahora imaginemos que queremos crear enemigos que también tengan nombre y salud.

Podríamos repetir las propiedades y métodos de `Player`, pero sería innecesario.

Podemos crear una clase general:

```
class Character {
    constructor(name, health) {
        this.name = name;
        this.health = health;
    }

    attack() {
        console.log(`${this.name} ataca`);
    }
}
```

Y hacer que `Enemy` herede de ella:

```
class Enemy extends Character {
    constructor(name, health, damage) {
        super(name, health);
        this.damage = damage;
    }

    specialAttack() {
        console.log(`${this.name} causa ${this.damage} de daño`);
    }
}
```

Ahora:

```
const enemy = new Enemy("Slime", 200, 35);

enemy.attack();
enemy.specialAttack();
```

Resultado:

```
Slime ataca
Slime causa 35 de daño
```

La clase `Enemy` hereda `attack()` de `Character`, pero incorpora su propio método `specialAttack()`.

## **4. Diferencia entre** `extends` **y** `super`

Es importante no confundirlos:

|Elemento|Función|
|---|---|
|`extends`|Declara que una clase hereda de otra.|
|`super()`|Ejecuta el constructor de la clase padre.|
|`super.attack()`|Ejecuta el método `attack()` de la clase padre.|

Por ejemplo:

```
class Enemy extends Character {
    constructor(name, health, damage) {
        super(name, health);
        this.damage = damage;
    }

    attack() {
        super.attack();
        console.log("El enemigo prepara otro ataque");
    }
}
```

Aquí sobrescribimos `attack()`, pero reutilizamos la implementación original mediante `super.attack()`.

## **5. Ejercicio práctico: clases y herencia**

Vamos a comprobar que sabes interpretar código orientado a objetos.

```
class Vehicle {
    constructor(brand) {
        this.brand = brand;
    }

    start() {
        return `${this.brand} está arrancando`;
    }
}

class Car extends Vehicle {
    constructor(brand, doors) {
        super(brand);
        this.doors = doors;
    }

    showDoors() {
        return this.doors;
    }
}

const car = new Car("Toyota", 5);
```

## **Evaluación: clases ES6**

5 preguntas · Selecciona una respuesta en cada una.

**1****.** **¿Qué devuelve `car.brand`?**

undefined

Toyota

Car

**Correcto**

super(brand) ejecuta el constructor de Vehicle, que asigna this.brand.

**2****.** **¿Qué devuelve `car.start()`?**

TypeError

Toyota está arrancando

undefined

**Correcto**

Car hereda start() de Vehicle.

**3****.** **¿Qué devuelve `car.showDoors()`?**

5

Toyota

undefined

**Correcto**

showDoors() devuelve la propiedad doors, inicializada en el constructor de Car.

**4****.** **¿Qué devuelve `car instanceof Vehicle`?**

false

undefined

true

**Correcto**

Vehicle está en la cadena de prototipos de la instancia car.

**5****.** **¿Para qué sirve `super(brand)`?**

Para crear una instancia independiente de Vehicle

Para llamar al constructor de la clase padre

Para sobrescribir todos los métodos del padre

**Correcto**

En un constructor derivado, super() inicializa la parte heredada del objeto y debe ejecutarse antes de utilizar this.

Corregir respuestas

## **5****/5 correctas**

Cuando superemos este ejercicio, cerraremos el bloque de orientación a objetos y pasaremos a **destructuring, spread y rest**, que son herramientas muy utilizadas en JavaScript moderno y especialmente importantes en React.