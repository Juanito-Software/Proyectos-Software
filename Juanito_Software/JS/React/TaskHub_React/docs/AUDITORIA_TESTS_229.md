# Auditoría de los 229 tests tras la política de composición

Fecha: 3 de septiembre de 2026 · Rama `main` · Base: commit `f6443b9`

Este documento recorre **uno a uno los 229 tests** que existían antes del
cambio de política y comprueba que cada uno sigue estando alineado con la
arquitectura y el comportamiento actuales.

La distinción que importa no es «todos los tests pasan», sino «todos los tests
siguen probando algo cierto». Un test puede terminar en verde y estar
comprobando una implementación que ya no existe, o haberse aflojado hasta el
punto de no detectar ninguna regresión. Por eso cada entrada indica qué código
prueba y por qué se ha dejado como está o se ha cambiado.

## Qué cambió en la política

| | Antes | Ahora |
|---|---|---|
| Longitud mínima | 15 caracteres | 15 caracteres |
| Longitud máxima | 72 **caracteres** | 72 **bytes** |
| Mayúscula obligatoria | No | **Sí** |
| Número obligatorio | No | **Sí** |
| Símbolo obligatorio | No | **Sí** |
| Espacios | Permitidos | Permitidos (pero no cuentan como símbolo) |
| Lista de bloqueo | Sí | Sí, ampliada con patrones previsibles |

El cambio de caracteres a bytes en el máximo no es cosmético: bcrypt cuenta
bytes, y una contraseña de 72 caracteres con acentos supera los 72 bytes. Con
la comprobación anterior se aceptaba y bcrypt descartaba el sobrante sin avisar.

## Resumen

| Estado | Tests |
|---|---|
| PASS | 150 |
| UPDATED | 63 |
| BLOCKED | 20 |
| INVALID | 10 |
Los 20 tests **BLOCKED** son los de navegador: Playwright no puede descargar
Chromium en el entorno donde se ha hecho esta auditoría, así que se han
revisado por lectura pero **no se han ejecutado**. Trece de ellos están además
marcados como UPDATED y uno como INVALID, por eso las columnas suman más de 229.

No hay ningún test clasificado como **WEAK**, **REDUNDANT** ni **FAIL**: los que
fallaron durante el trabajo se corrigieron y la causa está anotada en el
apartado siguiente. Ninguno se ha desactivado, comentado ni debilitado.

## Los diez tests INVALID

Son los que afirmaban lo contrario de la política nueva. No se han borrado: cada
uno se ha sustituido por su equivalente inverso, de modo que el número de
comprobaciones no baja y la regla queda igual de fijada, solo que en el otro
sentido.

Ocho de ellos formaban el bloque `sin reglas de composición (NIST Rev 4)` de
`password-policy.test.ts`, escrito expresamente para impedir que alguien
añadiera reglas de composición más adelante. Cumplió su función: al cambiar la
política, falló y obligó a tomar la decisión de forma consciente en lugar de
dejarla pasar.

## Fallos encontrados durante la auditoría

**`P@ssword2026!!!` se colaba.** La comprobación de patrones previsibles quitaba
los caracteres que no son letras y comparaba el resto contra una lista de
palabras comunes. Con la `@` sustituyendo a la `a`, quedaba `pssword`, que no
está en la lista. Se corrigió deshaciendo las sustituciones de estilo *leet*
antes de comparar, y probando varias normalizaciones porque el relleno y la
sustitución se estorban entre sí.

**La suite de API se estrangulaba a sí misma.** Al añadir comprobaciones de las
tres reglas de composición, la suite pasó a hacer una decena de registros que
deben ser rechazados, y cada rechazo cuenta como intento fallido de
autenticación. El limitador cortaba a partir del décimo y todo lo posterior
fallaba con 429 en vez de por lo que se estaba probando. Se resolvió con
`AUTH_RATE_LIMIT`, que **se ignora cuando `NODE_ENV` es `production`**: un
límite de fuerza bruta que se puede desactivar desde el entorno no es un límite.
Hay tres tests nuevos que fijan justo eso.

## Tabla completa


### `server/src/modules/auth/auth.validation.test.ts`

| # | Test | Tipo | Estado | Código probado | Acción realizada | Motivo |
|---|------|------|--------|----------------|------------------|--------|
| 1 | registerValidator: acepta una frase larga sin mayúsculas, números ni símbolos | Unitario | **INVALID** | registerValidator → validarPassword | Sustituido por su equivalente inverso | Afirmaba exactamente lo contrario de la política nueva |
| 2 | registerValidator: acepta también una contraseña compleja tradicional | Unitario | **UPDATED** | registerValidator | Fixture/aserción actualizada | La contraseña de ejemplo pasó a ser el caso normal, no la excepción |
| 3 | registerValidator: exige al menos 15 caracteres | Unitario | **UPDATED** | registerValidator | Fixture/aserción actualizada | El fixture de 14 ahora cumple composición, para aislar la longitud |
| 4 | registerValidator: rechaza por encima de 72 | Unitario | **UPDATED** | registerValidator | Fixture/aserción actualizada | El límite pasó de caracteres a bytes |
| 5 | registerValidator: rechaza una contraseña de la lista de bloqueo | Unitario | **PASS** | BLOQUEADAS | Ninguna | Sin relación con la política; sigue alineado |
| 6 | registerValidator: rechaza que la contraseña contenga el nombre de usuario | Unitario | **UPDATED** | comprobación de username | Fixture/aserción actualizada | Fixture adaptado a la composición |
| 7 | registerValidator: permite espacios en la contraseña | Unitario | **UPDATED** | validarPassword | Fixture/aserción actualizada | Fixture adaptado; el espacio sigue permitido pero ya no basta |
| 8 | registerValidator: exige al menos 3 caracteres de usuario | Unitario | **UPDATED** | MIN_USERNAME_LENGTH | Fixture/aserción actualizada | Depende de la constante de contraseña válida |
| 9 | registerValidator: rechaza nombres de usuario de más de 32 | Unitario | **UPDATED** | MAX_USERNAME_LENGTH | Fixture/aserción actualizada | Depende de la constante de contraseña válida |
| 10 | registerValidator rechaza: sin usuario | Unitario | **UPDATED** | registerValidator | Fixture/aserción actualizada | Depende de la constante de contraseña válida |
| 11 | registerValidator rechaza: sin contraseña | Unitario | **UPDATED** | registerValidator | Fixture/aserción actualizada | Depende de la constante de contraseña válida |
| 12 | registerValidator rechaza: usuario en blanco | Unitario | **UPDATED** | registerValidator | Fixture/aserción actualizada | Depende de la constante de contraseña válida |
| 13 | registerValidator rechaza: usuario numérico | Unitario | **UPDATED** | registerValidator | Fixture/aserción actualizada | Depende de la constante de contraseña válida |
| 14 | registerValidator rechaza: contraseña numérica | Unitario | **UPDATED** | registerValidator | Fixture/aserción actualizada | Depende de la constante de contraseña válida |
| 15 | registerValidator rechaza: cuerpo vacío | Unitario | **UPDATED** | registerValidator | Fixture/aserción actualizada | Depende de la constante de contraseña válida |
| 16 | registerValidator: no repite el mismo mensaje dos veces | Unitario | **PASS** | deduplicación de errores | Ninguna | Sin relación con la política; sigue alineado |
| 17 | registerValidator: no se rompe con el cuerpo indefinido | Unitario | **PASS** | req.body ?? {} | Ninguna | Sin relación con la política; sigue alineado |
| 18 | loginValidator: acepta usuario y contraseña presentes | Unitario | **PASS** | loginValidator | Ninguna | Sin relación con la política; sigue alineado |
| 19 | loginValidator: NO aplica la política de contraseñas al entrar | Unitario | **PASS** | loginValidator | Ninguna | Sin relación con la política; sigue alineado |
| 20 | loginValidator: tampoco rechaza una contraseña de la lista de bloqueo | Unitario | **PASS** | loginValidator | Ninguna | Sin relación con la política; sigue alineado |
| 21 | loginValidator: no acepta el campo de confirmación | Unitario | **PASS** | contrato de login | Ninguna | Sin relación con la política; sigue alineado |
| 22 | loginValidator rechaza: sin usuario | Unitario | **PASS** | loginValidator | Ninguna | Sin relación con la política; sigue alineado |
| 23 | loginValidator rechaza: sin contraseña | Unitario | **PASS** | loginValidator | Ninguna | Sin relación con la política; sigue alineado |
| 24 | loginValidator rechaza: ambos vacíos | Unitario | **PASS** | loginValidator | Ninguna | Sin relación con la política; sigue alineado |

### `server/src/modules/auth/password-policy.test.ts`

| # | Test | Tipo | Estado | Código probado | Acción realizada | Motivo |
|---|------|------|--------|----------------|------------------|--------|
| 25 | longitud: rechaza por debajo de 15 caracteres | Unitario | **UPDATED** | MIN_PASSWORD_LENGTH | Fixture/aserción actualizada | El fixture de 14 ahora cumple composición, para aislar la longitud |
| 26 | longitud: acepta justo en el límite de 15 | Unitario | **UPDATED** | MIN_PASSWORD_LENGTH | Fixture/aserción actualizada | Fixture cambiado a uno que cumple los cuatro requisitos |
| 27 | longitud: acepta contraseñas mucho más largas | Unitario | **UPDATED** | validarPassword | Fixture/aserción actualizada | Fixture adaptado a la composición |
| 28 | longitud: rechaza por encima de 72, sin recortar en silencio | Unitario | **UPDATED** | MAX_PASSWORD_BYTES | Fixture/aserción actualizada | El límite pasó de caracteres a bytes |
| 29 | longitud: acepta justo en el límite de 72 | Unitario | **UPDATED** | MAX_PASSWORD_BYTES | Fixture/aserción actualizada | El límite pasó de caracteres a bytes |
| 30 | sin composición: acepta una frase solo en minúsculas | Unitario | **INVALID** | validarPassword | Sustituido por su equivalente inverso | Existía para impedir la composición, que ahora es requisito |
| 31 | sin composición: acepta una frase con acentos y eñes | Unitario | **UPDATED** | clases Unicode | Fixture/aserción actualizada | Reformulado como "acepta una mayúscula acentuada": el objetivo real era no romper con Unicode |
| 32 | sin composición: acepta una contraseña compleja al estilo tradicional | Unitario | **UPDATED** | validarPassword | Fixture/aserción actualizada | Movido al bloque de contraseñas válidas: ahora es la norma |
| 33 | sin composición: acepta solo dígitos si la longitud es suficiente | Unitario | **INVALID** | validarPassword | Sustituido por su equivalente inverso | Sin mayúscula ni símbolo, ya no puede aceptarse |
| 34 | sin composición: acepta espacios, que NIST exige permitir | Unitario | **UPDATED** | validarPassword | Fixture/aserción actualizada | Se mantiene el espacio permitido, pero el fixture añade composición |
| 35 | sin composición: NO rechaza por faltar mayúsculas | Unitario | **INVALID** | validarPassword | Sustituido por su equivalente inverso | Invertido: ahora rechaza por faltar mayúscula |
| 36 | sin composición: NO rechaza por faltar números | Unitario | **INVALID** | validarPassword | Sustituido por su equivalente inverso | Invertido: ahora rechaza por faltar número |
| 37 | sin composición: NO rechaza por faltar símbolos | Unitario | **INVALID** | validarPassword | Sustituido por su equivalente inverso | Invertido: ahora rechaza por faltar símbolo |
| 38 | lista de bloqueo: rechaza una contraseña común | Unitario | **PASS** | BLOQUEADAS | Ninguna | Sin relación con la política; sigue alineado |
| 39 | lista de bloqueo: la comparación ignora mayúsculas y espacios | Unitario | **PASS** | normalización | Ninguna | Sin relación con la política; sigue alineado |
| 40 | lista de bloqueo: rechaza un único carácter repetido | Unitario | **PASS** | esUnCaracterRepetido | Ninguna | Sin relación con la política; sigue alineado |
| 41 | lista de bloqueo: rechaza secuencias de teclado | Unitario | **PASS** | esSecuencia | Ninguna | Sin relación con la política; sigue alineado |
| 42 | lista de bloqueo: rechaza que contenga el nombre de usuario | Unitario | **UPDATED** | comprobación de username | Fixture/aserción actualizada | Fixture adaptado a la composición |
| 43 | lista de bloqueo: no compara con usuarios de menos de 4 caracteres | Unitario | **UPDATED** | MIN_USERNAME_PARA_COMPARAR | Fixture/aserción actualizada | Fixture adaptado a la composición |
| 44 | lista de bloqueo: sí compara a partir de 4 caracteres | Unitario | **UPDATED** | MIN_USERNAME_PARA_COMPARAR | Fixture/aserción actualizada | Fixture adaptado a la composición |
| 45 | entradas inválidas: rechaza una contraseña indefinida | Unitario | **PASS** | guarda de tipo | Ninguna | Sin relación con la política; sigue alineado |
| 46 | entradas inválidas: rechaza una contraseña nula | Unitario | **PASS** | guarda de tipo | Ninguna | Sin relación con la política; sigue alineado |
| 47 | entradas inválidas: rechaza una contraseña numérica | Unitario | **PASS** | guarda de tipo | Ninguna | Sin relación con la política; sigue alineado |
| 48 | entradas inválidas: rechaza una contraseña vacía | Unitario | **PASS** | guarda de tipo | Ninguna | Sin relación con la política; sigue alineado |

### `server/src/modules/tasks/tasks.validation.test.ts`

| # | Test | Tipo | Estado | Código probado | Acción realizada | Motivo |
|---|------|------|--------|----------------|------------------|--------|
| 49 | acepta una tarea con solo el título | Unitario | **PASS** | validadores de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 50 | acepta todos los campos válidos a la vez | Unitario | **PASS** | validadores de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 51 | rechaza: sin título | Unitario | **PASS** | validadores de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 52 | rechaza: título vacío | Unitario | **PASS** | validadores de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 53 | rechaza: título de solo espacios | Unitario | **PASS** | validadores de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 54 | rechaza: título que no es texto | Unitario | **PASS** | validadores de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 55 | rechaza: título nulo | Unitario | **PASS** | validadores de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 56 | rechaza un estado que no existe | Unitario | **PASS** | validadores de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 57 | rechaza una prioridad que no existe | Unitario | **PASS** | validadores de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 58 | acepta el estado válido pending | Unitario | **PASS** | validadores de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 59 | acepta el estado válido in-progress | Unitario | **PASS** | validadores de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 60 | acepta el estado válido completed | Unitario | **PASS** | validadores de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 61 | acepta la prioridad válida low | Unitario | **PASS** | validadores de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 62 | acepta la prioridad válida medium | Unitario | **PASS** | validadores de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 63 | acepta la prioridad válida high | Unitario | **PASS** | validadores de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 64 | no se rompe si el cuerpo llega indefinido | Unitario | **PASS** | validadores de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 65 | acepta una actualización parcial de un solo campo | Unitario | **PASS** | validadores de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 66 | acepta el campo completed del cliente antiguo | Unitario | **PASS** | validadores de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 67 | rechaza un título vacío si se manda explícitamente | Unitario | **PASS** | validadores de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 68 | rechaza un estado inválido igual que al crear | Unitario | **PASS** | validadores de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 69 | acepta que no haya ningún filtro | Unitario | **PASS** | validadores de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 70 | acepta los tres filtros a la vez | Unitario | **PASS** | validadores de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 71 | rechaza un estado inventado en la cadena de consulta | Unitario | **PASS** | validadores de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 72 | rechaza una prioridad inventada en la cadena de consulta | Unitario | **PASS** | validadores de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 73 | acepta cualquier texto de búsqueda, incluidos caracteres SQL | Unitario | **PASS** | validadores de tareas | Ninguna | Sin relación con la política; sigue alineado |

### `server/src/modules/tasks/tasks.repository.test.ts`

| # | Test | Tipo | Estado | Código probado | Acción realizada | Motivo |
|---|------|------|--------|----------------|------------------|--------|
| 74 | escapeLikePattern: deja intacto el texto normal | Unitario | **PASS** | repositorio de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 75 | escapeLikePattern: escapa el comodín % | Unitario | **PASS** | repositorio de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 76 | escapeLikePattern: escapa el comodín _ | Unitario | **PASS** | repositorio de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 77 | escapeLikePattern: escapa la barra invertida ANTES que los comodines | Unitario | **PASS** | repositorio de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 78 | escapeLikePattern: escapa varios comodines a la vez | Unitario | **PASS** | repositorio de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 79 | escapeLikePattern: una búsqueda de solo % deja de significar "todo" | Unitario | **PASS** | repositorio de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 80 | escapeLikePattern: no altera comillas ni punto y coma | Unitario | **PASS** | repositorio de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 81 | escapeLikePattern: devuelve cadena vacía tal cual | Unitario | **PASS** | repositorio de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 82 | toDto: completed es true solo cuando el estado es completed | Unitario | **PASS** | repositorio de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 83 | toDto: pending da completed false | Unitario | **PASS** | repositorio de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 84 | toDto: in-progress da completed false | Unitario | **PASS** | repositorio de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 85 | toDto: conserva todos los campos originales | Unitario | **PASS** | repositorio de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 86 | toDto: no añade nada más que completed | Unitario | **PASS** | repositorio de tareas | Ninguna | Sin relación con la política; sigue alineado |

### `client/src/components/AuthForm.test.jsx`

| # | Test | Tipo | Estado | Código probado | Acción realizada | Motivo |
|---|------|------|--------|----------------|------------------|--------|
| 87 | modo login: no muestra el campo de confirmación | Componente | **PASS** | AuthForm (login) | Ninguna | Sin relación con la política; sigue alineado |
| 88 | modo login: no impone longitud mínima | Componente | **PASS** | AuthForm (login) | Ninguna | Sin relación con la política; sigue alineado |
| 89 | modo login: entrega usuario y contraseña al enviar | Componente | **PASS** | AuthForm.handleSubmit | Ninguna | Sin relación con la política; sigue alineado |
| 90 | modo registro: muestra el campo de confirmación | Componente | **PASS** | AuthForm (registro) | Ninguna | Sin relación con la política; sigue alineado |
| 91 | modo registro: exige la longitud mínima de 15 | Componente | **UPDATED** | atributo minLength | Fixture/aserción actualizada | La constante se movió de constants.js a passwordPolicy.js |
| 92 | modo registro: limita al máximo técnico de 72 | Componente | **UPDATED** | atributo maxLength | Fixture/aserción actualizada | La constante se movió de constants.js a passwordPolicy.js |
| 93 | modo registro: NO usa pattern | Componente | **INVALID** | atributo pattern | Sustituido por su equivalente inverso | Existía para impedir la composición; ahora el pattern es obligatorio |
| 94 | modo registro: sugiere usar una frase | Componente | **UPDATED** | texto de ayuda | Fixture/aserción actualizada | El consejo cambió: una frase sola ya no vale, hay que retocarla |
| 95 | modo registro: entrega SOLO usuario y contraseña | Componente | **UPDATED** | AuthForm.handleSubmit | Fixture/aserción actualizada | Fixture adaptado; la aserción de 2 argumentos se mantiene intacta |
| 96 | modo registro: acepta una frase sin mayúsculas, números ni símbolos | Componente | **INVALID** | AuthForm.handleSubmit | Sustituido por su equivalente inverso | Esa frase ya no supera la validación del campo |
| 97 | confirmación: avisa en cuanto dejan de coincidir | Componente | **UPDATED** | estado mismatch | Fixture/aserción actualizada | Fixture adaptado a la composición; la lógica probada no cambia |
| 98 | confirmación: no avisa mientras el segundo campo está vacío | Componente | **UPDATED** | estado mismatch | Fixture/aserción actualizada | Fixture adaptado a la composición; la lógica probada no cambia |
| 99 | confirmación: deshabilita el botón mientras no coincidan | Componente | **UPDATED** | estado mismatch | Fixture/aserción actualizada | Fixture adaptado a la composición; la lógica probada no cambia |
| 100 | confirmación: no llama a onSubmit si no coinciden | Componente | **UPDATED** | estado mismatch | Fixture/aserción actualizada | Fixture adaptado a la composición; la lógica probada no cambia |
| 101 | confirmación: vuelve a habilitar el botón cuando se corrige | Componente | **UPDATED** | estado mismatch | Fixture/aserción actualizada | Fixture adaptado a la composición; la lógica probada no cambia |
| 102 | confirmación: marca el campo como inválido para lectores de pantalla | Componente | **UPDATED** | estado mismatch | Fixture/aserción actualizada | Fixture adaptado a la composición; la lógica probada no cambia |
| 103 | errores del servidor: muestra el error recibido por props | Componente | **PASS** | prop error | Ninguna | Sin relación con la política; sigue alineado |
| 104 | errores del servidor: una contraseña corta no llega a enviarse | Componente | **UPDATED** | validación del campo | Fixture/aserción actualizada | Ampliado a it.each con los cuatro incumplimientos |

### `client/src/components/TaskForm.test.jsx`

| # | Test | Tipo | Estado | Código probado | Acción realizada | Motivo |
|---|------|------|--------|----------------|------------------|--------|
| 105 | al crear: empieza en pendiente y prioridad media | Componente | **PASS** | TaskForm | Ninguna | Sin relación con la política; sigue alineado |
| 106 | al crear: entrega título, descripción, estado y prioridad | Componente | **PASS** | TaskForm | Ninguna | Sin relación con la política; sigue alineado |
| 107 | al crear: recorta los espacios | Componente | **PASS** | TaskForm | Ninguna | Sin relación con la política; sigue alineado |
| 108 | al crear: no envía si el título está en blanco | Componente | **PASS** | TaskForm | Ninguna | Sin relación con la política; sigue alineado |
| 109 | al crear: vacía el formulario tras crear | Componente | **PASS** | TaskForm | Ninguna | Sin relación con la política; sigue alineado |
| 110 | al editar: carga los valores actuales | Componente | **PASS** | TaskForm | Ninguna | Sin relación con la política; sigue alineado |
| 111 | al editar: el botón dice Guardar y aparece Cancelar | Componente | **PASS** | TaskForm | Ninguna | Sin relación con la política; sigue alineado |
| 112 | al editar: NO vacía el formulario tras guardar | Componente | **PASS** | TaskForm | Ninguna | Sin relación con la política; sigue alineado |
| 113 | al editar: cancelar avisa al componente padre | Componente | **PASS** | TaskForm | Ninguna | Sin relación con la política; sigue alineado |

### `client/src/components/TaskItem.test.jsx`

| # | Test | Tipo | Estado | Código probado | Acción realizada | Motivo |
|---|------|------|--------|----------------|------------------|--------|
| 114 | presentación: muestra título, descripción y distintivos | Componente | **PASS** | TaskItem | Ninguna | Sin relación con la política; sigue alineado |
| 115 | presentación: traduce los valores de la API a castellano | Componente | **PASS** | TaskItem | Ninguna | Sin relación con la política; sigue alineado |
| 116 | presentación: el checkbox refleja si está completada | Componente | **PASS** | TaskItem | Ninguna | Sin relación con la política; sigue alineado |
| 117 | presentación: no rompe sin descripción | Componente | **PASS** | TaskItem | Ninguna | Sin relación con la política; sigue alineado |
| 118 | acciones: el checkbox manda el valor contrario | Componente | **PASS** | TaskItem | Ninguna | Sin relación con la política; sigue alineado |
| 119 | acciones: eliminar pide confirmación y respeta un "no" | Componente | **PASS** | TaskItem | Ninguna | Sin relación con la política; sigue alineado |
| 120 | acciones: eliminar borra cuando se confirma | Componente | **PASS** | TaskItem | Ninguna | Sin relación con la política; sigue alineado |
| 121 | acciones: editar abre el formulario | Componente | **PASS** | TaskItem | Ninguna | Sin relación con la política; sigue alineado |
| 122 | acciones: guardar la edición envía y cierra | Componente | **PASS** | TaskItem | Ninguna | Sin relación con la política; sigue alineado |
| 123 | acciones: un fallo de la API al borrar no elimina la tarea | Componente | **PASS** | TaskItem | Ninguna | Sin relación con la política; sigue alineado |

### `client/src/services/api.test.js`

| # | Test | Tipo | Estado | Código probado | Acción realizada | Motivo |
|---|------|------|--------|----------------|------------------|--------|
| 124 | envoltorio: devuelve data directamente | Componente | **PASS** | services/api.js | Ninguna | Sin relación con la política; sigue alineado |
| 125 | envoltorio: devuelve un array cuando lista tareas | Componente | **PASS** | services/api.js | Ninguna | Sin relación con la política; sigue alineado |
| 126 | filtros: no añade parámetros cuando no hay filtros | Componente | **PASS** | services/api.js | Ninguna | Sin relación con la política; sigue alineado |
| 127 | filtros: omite los filtros vacíos | Componente | **PASS** | services/api.js | Ninguna | Sin relación con la política; sigue alineado |
| 128 | filtros: manda status, priority y search | Componente | **PASS** | services/api.js | Ninguna | Sin relación con la política; sigue alineado |
| 129 | filtros: codifica los caracteres especiales | Componente | **PASS** | services/api.js | Ninguna | Sin relación con la política; sigue alineado |
| 130 | errores: lanza el mensaje que devuelve la API | Componente | **PASS** | services/api.js | Ninguna | Sin relación con la política; sigue alineado |
| 131 | errores: convierte un 401 en "Sesión expirada" | Componente | **PASS** | services/api.js | Ninguna | Sin relación con la política; sigue alineado |
| 132 | errores: usa un mensaje por defecto | Componente | **PASS** | services/api.js | Ninguna | Sin relación con la política; sigue alineado |
| 133 | errores: no se rompe si la respuesta no es JSON | Componente | **PASS** | services/api.js | Ninguna | Sin relación con la política; sigue alineado |
| 134 | autorización: incluye el token cuando está establecido | Componente | **PASS** | services/api.js | Ninguna | Sin relación con la política; sigue alineado |
| 135 | autorización: no incluye la cabecera si no hay token | Componente | **PASS** | services/api.js | Ninguna | Sin relación con la política; sigue alineado |
| 136 | verbos: createTask hace POST | Componente | **PASS** | services/api.js | Ninguna | Sin relación con la política; sigue alineado |
| 137 | verbos: updateTask hace PATCH al id | Componente | **PASS** | services/api.js | Ninguna | Sin relación con la política; sigue alineado |
| 138 | verbos: deleteTask hace DELETE al id | Componente | **PASS** | services/api.js | Ninguna | Sin relación con la política; sigue alineado |
| 139 | verbos: toggleCompleted manda completed | Componente | **PASS** | services/api.js | Ninguna | Sin relación con la política; sigue alineado |

### `client/src/services/authApi.test.js`

| # | Test | Tipo | Estado | Código probado | Acción realizada | Motivo |
|---|------|------|--------|----------------|------------------|--------|
| 140 | login: devuelve { user, token } desenvuelto | Componente | **UPDATED** | services/authApi.js | Fixture/aserción actualizada | Cosmético: la contraseña del mock se alineó con la política. Nunca se valida aquí |
| 141 | login: manda usuario y contraseña como JSON | Componente | **UPDATED** | services/authApi.js | Fixture/aserción actualizada | Cosmético: la contraseña del mock se alineó con la política. Nunca se valida aquí |
| 142 | login: propaga el mensaje del servidor | Componente | **PASS** | services/authApi.js | Ninguna | Sin relación con la política; sigue alineado |
| 143 | login: no manda la cabecera de autorización | Componente | **UPDATED** | services/authApi.js | Fixture/aserción actualizada | Cosmético: la contraseña del mock se alineó con la política. Nunca se valida aquí |
| 144 | register: devuelve el usuario creado con su rol | Componente | **UPDATED** | services/authApi.js | Fixture/aserción actualizada | Cosmético: la contraseña del mock se alineó con la política. Nunca se valida aquí |
| 145 | register: llama al endpoint de registro | Componente | **UPDATED** | services/authApi.js | Fixture/aserción actualizada | Cosmético: la contraseña del mock se alineó con la política. Nunca se valida aquí |
| 146 | register: propaga el 409 de usuario ya existente | Componente | **UPDATED** | services/authApi.js | Fixture/aserción actualizada | Cosmético: la contraseña del mock se alineó con la política. Nunca se valida aquí |
| 147 | register: usa un mensaje por defecto | Componente | **UPDATED** | services/authApi.js | Fixture/aserción actualizada | Cosmético: la contraseña del mock se alineó con la política. Nunca se valida aquí |

### `server/src/verify.ts` — suite de API contra PostgreSQL

| # | Test | Tipo | Estado | Código probado | Acción realizada | Motivo |
|---|------|------|--------|----------------|------------------|--------|
| 148 | POST /api/auth/register | API | **UPDATED** | registro | Fixture/aserción actualizada | La contraseña de la cuenta de prueba cambió para cumplir la política |
| 149 | POST /api/auth/login | API | **UPDATED** | login | Fixture/aserción actualizada | La contraseña de la cuenta de prueba cambió para cumplir la política |
| 150 | GET /api/tasks sin token -> 401 con success:false | API | **PASS** | auth.middleware | Ninguna | Sin relación con la política; sigue alineado |
| 151 | GET /api/tasks (usuario nuevo, vacío) | API | **PASS** | listado de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 152 | POST /api/tasks (válida) -> 201 | API | **PASS** | creación de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 153 | La tarea nace pending/high y completed:false | API | **PASS** | valores por defecto | Ninguna | Sin relación con la política; sigue alineado |
| 154 | POST /api/tasks (título vacío) -> 400 | API | **PASS** | validación de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 155 | POST /api/tasks (status inválido) -> 400 | API | **PASS** | validación de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 156 | POST /api/tasks (título duplicado) -> 409 | API | **PASS** | índice único + 23505 | Ninguna | Sin relación con la política; sigue alineado |
| 157 | GET /api/tasks/:id | API | **PASS** | lectura por id | Ninguna | Sin relación con la política; sigue alineado |
| 158 | PATCH completed:true traduce a status:completed | API | **PASS** | compatibilidad completed | Ninguna | Sin relación con la política; sigue alineado |
| 159 | PATCH status:in-progress deja completed:false | API | **PASS** | compatibilidad completed | Ninguna | Sin relación con la política; sigue alineado |
| 160 | GET /api/tasks?status=in-progress | API | **PASS** | filtros en SQL | Ninguna | Sin relación con la política; sigue alineado |
| 161 | GET /api/tasks?priority=low | API | **PASS** | filtros en SQL | Ninguna | Sin relación con la política; sigue alineado |
| 162 | GET /api/tasks?search= (en descripción, sin distinguir mayúsculas) | API | **PASS** | filtros en SQL | Ninguna | Sin relación con la política; sigue alineado |
| 163 | GET /api/tasks?status=inventado -> 400 | API | **PASS** | validación de filtros | Ninguna | Sin relación con la política; sigue alineado |
| 164 | GET /api/tasks/stats | API | **PASS** | resumen del usuario | Ninguna | Sin relación con la política; sigue alineado |
| 165 | GET /api/system/stats | API | **PASS** | contador de peticiones | Ninguna | Sin relación con la política; sigue alineado |
| 166 | GET /playground sirve el playground HTML | API | **PASS** | estáticos | Ninguna | Sin relación con la política; sigue alineado |
| 167 | Una ruta inexistente de /api/ devuelve 404 en JSON | API | **PASS** | fallback SPA | Ninguna | Sin relación con la política; sigue alineado |
| 168 | Aislamiento: el otro usuario no ve las tareas | API | **PASS** | filtro por user_id | Ninguna | Sin relación con la política; sigue alineado |
| 169 | Aislamiento: 404 al leer una tarea ajena | API | **PASS** | filtro por user_id | Ninguna | Sin relación con la política; sigue alineado |
| 170 | El título duplicado se comprueba por usuario, no globalmente | API | **PASS** | índice único compuesto | Ninguna | Sin relación con la política; sigue alineado |
| 171 | Registro con contraseña de 14 caracteres -> 400 | API | **UPDATED** | MIN_PASSWORD_LENGTH | Fixture/aserción actualizada | El fixture de 14 ahora cumple composición, para aislar la longitud |
| 172 | Registro con frase sin mayúsculas, números ni símbolos -> 201 | API | **INVALID** | validarPassword | Sustituido por su equivalente inverso | Sustituido por su inverso: esa frase ahora devuelve 400 |
| 173 | Se puede iniciar sesión con la frase de paso | API | **UPDATED** | login | Fixture/aserción actualizada | Renombrado a "después de registrarse"; el fixture cumple la política |
| 174 | Registro con contraseña de la lista de bloqueo -> 400 | API | **PASS** | BLOQUEADAS | Ninguna | Sin relación con la política; sigue alineado |
| 175 | Registro con la contraseña conteniendo el usuario -> 400 | API | **UPDATED** | comprobación de username | Fixture/aserción actualizada | Fixture adaptado a la composición |
| 176 | Registro con más de 72 caracteres -> 400 | API | **UPDATED** | MAX_PASSWORD_BYTES | Fixture/aserción actualizada | El límite pasó de caracteres a bytes |
| 177 | Un registro rechazado por la política no crea el usuario | API | **PASS** | transaccionalidad del registro | Ninguna | Sin relación con la política; sigue alineado |
| 178 | Una cuenta anterior a la política entra con su contraseña de siempre | API | **PASS** | loginValidator | Ninguna | Sin relación con la política; sigue alineado |
| 179 | La API ignora passwordConfirmation | API | **UPDATED** | contrato de registro | Fixture/aserción actualizada | Fixture adaptado a la composición |
| 180 | La CSP está presente y restringe el origen por defecto | API | **PASS** | helmet | Ninguna | Sin relación con la política; sigue alineado |
| 181 | La CSP no bloquea los manejadores onclick del playground | API | **PASS** | scriptSrcAttr | Ninguna | Sin relación con la política; sigue alineado |
| 182 | La CSP impide cargar la página en un iframe ajeno | API | **PASS** | frameAncestors | Ninguna | Sin relación con la política; sigue alineado |
| 183 | Se envía X-Content-Type-Options: nosniff | API | **PASS** | helmet | Ninguna | Sin relación con la política; sigue alineado |
| 184 | Una petición del mismo origen no la bloquea CORS | API | **PASS** | delegado de CORS | Ninguna | Sin relación con la política; sigue alineado |
| 185 | Un origen desconocido no recibe la cabecera | API | **PASS** | delegado de CORS | Ninguna | Sin relación con la política; sigue alineado |
| 186 | Token firmado con otro secreto -> 401 | API | **PASS** | verificación JWT | Ninguna | Sin relación con la política; sigue alineado |
| 187 | Token caducado -> 401 | API | **PASS** | verificación JWT | Ninguna | Sin relación con la política; sigue alineado |
| 188 | Token sin firmar con alg:none -> 401 | API | **PASS** | algoritmo explícito | Ninguna | Sin relación con la política; sigue alineado |
| 189 | Token válido pero sin userId -> 401 | API | **PASS** | auth.middleware | Ninguna | Sin relación con la política; sigue alineado |
| 190 | Token de un usuario inexistente no devuelve datos ajenos | API | **PASS** | auth.middleware | Ninguna | Sin relación con la política; sigue alineado |
| 191 | Token con formato inválido -> 401 | API | **PASS** | verificación JWT | Ninguna | Sin relación con la política; sigue alineado |
| 192 | Cargas de inyección SQL se tratan como texto | API | **PASS** | SQL parametrizado | Ninguna | Sin relación con la política; sigue alineado |
| 193 | Buscar "50%" encuentra ese texto y no todas las tareas | API | **PASS** | escapeLikePattern | Ninguna | Sin relación con la política; sigue alineado |
| 194 | La tabla tasks sigue intacta tras las cargas de inyección | API | **PASS** | SQL parametrizado | Ninguna | Sin relación con la política; sigue alineado |
| 195 | Un título con sintaxis SQL se almacena literalmente | API | **PASS** | SQL parametrizado | Ninguna | Sin relación con la política; sigue alineado |
| 196 | El índice único rechaza el duplicado con mayúsculas y espacios | API | **PASS** | índice LOWER(TRIM()) | Ninguna | Sin relación con la política; sigue alineado |
| 197 | Registrarse crea un usuario con rol "user", nunca admin | API | **PASS** | auth.service | Ninguna | Sin relación con la política; sigue alineado |
| 198 | Mandar role:"admin" al registrarse no concede el rol | API | **PASS** | auth.service | Ninguna | Sin relación con la política; sigue alineado |
| 199 | Un usuario normal recibe 403 en /api/admin | API | **PASS** | requireAdmin | Ninguna | Sin relación con la política; sigue alineado |
| 200 | Sin token, /api/admin devuelve 401 y no 403 | API | **PASS** | orden de middlewares | Ninguna | Sin relación con la política; sigue alineado |
| 201 | El administrador de la semilla existe y entra con rol admin | API | **UPDATED** | seedAdmin | Fixture/aserción actualizada | ADMIN_PASSWORD de prueba adaptada a la política |
| 202 | GET /api/admin/users lista a todos con su número de tareas | API | **PASS** | admin.service | Ninguna | Sin relación con la política; sigue alineado |
| 203 | El listado de administración no expone ningún hash | API | **PASS** | admin.service | Ninguna | Sin relación con la política; sigue alineado |
| 204 | Un administrador no puede borrarse a sí mismo | API | **PASS** | admin.service | Ninguna | Sin relación con la política; sigue alineado |
| 205 | GET /api/admin/stats devuelve el resumen global | API | **PASS** | admin.service | Ninguna | Sin relación con la política; sigue alineado |
| 206 | El administrador borra a otro usuario | API | **PASS** | admin.service | Ninguna | Sin relación con la política; sigue alineado |
| 207 | DELETE /api/tasks/:id -> 200 con success:true | API | **PASS** | borrado de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 208 | GET tras borrar -> 404 | API | **PASS** | borrado de tareas | Ninguna | Sin relación con la política; sigue alineado |
| 209 | Borrar un usuario arrastra sus tareas (CASCADE) | API | **PASS** | clave foránea | Ninguna | Sin relación con la política; sigue alineado |

### `e2e/taskhub.spec.js` — navegador con Playwright

| # | Test | Tipo | Estado | Código probado | Acción realizada | Motivo |
|---|------|------|--------|----------------|------------------|--------|
| 210 | un usuario nuevo puede registrarse y entra directamente | E2E | **UPDATED · BLOCKED** | flujo de registro | Fixture actualizada | Usa la constante PASSWORD, que cambió para cumplir la composición. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin acceso de red. Revisado por lectura |
| 211 | la sesión sobrevive a recargar la página | E2E | **UPDATED · BLOCKED** | token en localStorage | Fixture actualizada | Usa la constante PASSWORD, que cambió para cumplir la composición. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin acceso de red. Revisado por lectura |
| 212 | salir devuelve a la pantalla de acceso | E2E | **UPDATED · BLOCKED** | cierre de sesión | Fixture actualizada | Usa la constante PASSWORD, que cambió para cumplir la composición. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin acceso de red. Revisado por lectura |
| 213 | la confirmación que no coincide impide registrarse | E2E | **UPDATED · BLOCKED** | estado mismatch | Fixture actualizada | Usa la constante PASSWORD, que cambió para cumplir la composición. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin acceso de red. Revisado por lectura |
| 214 | el campo de confirmación solo existe en el registro | E2E | **BLOCKED** | AuthForm por modo | Ninguna | Sin relación con la política. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin acceso de red. Revisado por lectura |
| 215 | una contraseña demasiado corta no permite registrarse | E2E | **UPDATED · BLOCKED** | validación del navegador | Ampliado a un bucle de cuatro casos | Ahora cubre también sin mayúscula, sin número y sin símbolo. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin acceso de red. Revisado por lectura |
| 216 | una frase larga sin números ni símbolos es válida | E2E | **INVALID · BLOCKED** | validación del navegador | Sustituido por su equivalente inverso | Esa frase ya no supera la validación del campo. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin acceso de red. Revisado por lectura |
| 217 | unas credenciales incorrectas muestran error | E2E | **BLOCKED** | login fallido | Ninguna | Sin relación con la política. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin acceso de red. Revisado por lectura |
| 218 | crear, ver, completar y eliminar | E2E | **UPDATED · BLOCKED** | ciclo de vida de tarea | Fixture actualizada | Usa la constante PASSWORD, que cambió para cumplir la composición. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin acceso de red. Revisado por lectura |
| 219 | editar cambia título, estado y prioridad | E2E | **UPDATED · BLOCKED** | edición en línea | Fixture actualizada | Usa la constante PASSWORD, que cambió para cumplir la composición. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin acceso de red. Revisado por lectura |
| 220 | no deja crear dos tareas con el mismo título | E2E | **UPDATED · BLOCKED** | conflicto 409 | Fixture actualizada | Usa la constante PASSWORD, que cambió para cumplir la composición. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin acceso de red. Revisado por lectura |
| 221 | filtrar por estado y por texto, y limpiar | E2E | **UPDATED · BLOCKED** | filtros del cliente | Fixture actualizada | Usa la constante PASSWORD, que cambió para cumplir la composición. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin acceso de red. Revisado por lectura |
| 222 | una búsqueda sin resultados muestra el mensaje | E2E | **UPDATED · BLOCKED** | estado vacío | Fixture actualizada | Usa la constante PASSWORD, que cambió para cumplir la composición. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin acceso de red. Revisado por lectura |
| 223 | un usuario no ve las tareas de otro | E2E | **UPDATED · BLOCKED** | aislamiento por contexto | Fixture actualizada | Usa la constante PASSWORD, que cambió para cumplir la composición. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin acceso de red. Revisado por lectura |
| 224 | se sirve y comparte la sesión con la aplicación | E2E | **UPDATED · BLOCKED** | playground | Fixture actualizada | Usa la constante PASSWORD, que cambió para cumplir la composición. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin acceso de red. Revisado por lectura |
| 225 | sin sesión, el playground pide entrar | E2E | **BLOCKED** | playground | Ninguna | Sin relación con la política. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin acceso de red. Revisado por lectura |
| 226 | el panel de administración no aparece para un usuario normal | E2E | **UPDATED · BLOCKED** | render condicional | Fixture actualizada | Usa la constante PASSWORD, que cambió para cumplir la composición. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin acceso de red. Revisado por lectura |
| 227 | las rutas de tareas exigen token | E2E | **BLOCKED** | auth.middleware | Ninguna | Sin relación con la política. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin acceso de red. Revisado por lectura |
| 228 | la comprobación de salud responde sin autenticar | E2E | **BLOCKED** | /api/health | Ninguna | Sin relación con la política. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin acceso de red. Revisado por lectura |
| 229 | las cabeceras de seguridad están presentes | E2E | **BLOCKED** | helmet | Ninguna | Sin relación con la política. NO EJECUTADO en este entorno: Playwright no puede descargar Chromium sin acceso de red. Revisado por lectura |