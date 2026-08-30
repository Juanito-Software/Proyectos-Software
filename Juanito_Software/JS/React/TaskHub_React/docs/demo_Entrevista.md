
## 2. Para la entrevista

### Lo que cambia respecto a lo que llevabas preparado

En **«qué puedes ofrecer»** ahora tienes una frase que antes no podías decir:

> «Tengo una de mis aplicaciones desplegada y funcionando, con base de datos real y con integración continua. Si quieres verla mientras hablamos, es taskhub-react.onrender.com.»

Poder enseñar algo funcionando en mitad de una entrevista cambia el registro de
la conversación: dejas de pedir que se fíen de ti.

Y en **«buenas prácticas»**, donde ya respondías bien, ahora rematas con un
ejemplo que casi ningún junior tiene:

> «Le pasé una auditoría de seguridad al proyecto antes de dejarlo en producción, y escribí tests de regresión para lo que encontré. Uno de ellos destapó un fallo que la auditoría no vio.»

### Preguntas probables y qué responder

**«¿Cómo está desplegado?»**
Servicio web en Render y PostgreSQL gestionado en Neon, los dos en la región de
Frankfurt para que las consultas no crucen el Atlántico. Despliegue automático
en cada commit a `main`. Puse la base de datos en Neon y no en Render porque la
de Render caduca a los 30 días, y una demo enlazada desde el currículum tiene
que seguir viva dentro de tres meses.

**«¿Por qué tarda tanto la primera carga?»**
Dilo tú antes de que lo pregunten: el plan gratuito de Render duerme el servicio
tras 15 minutos sin tráfico y despertarlo lleva cerca de un minuto. Es una
limitación conocida del plan, no del código. Avisarlo de antemano queda mucho
mejor que justificarlo después.

**«¿Qué testeas exactamente?»**
Cuatro capas que prueban cosas distintas: unitarios de lógica pura, componentes
de React con Testing Library, la API completa contra un PostgreSQL real con
esquema aislado, y navegador real con Playwright. La última es la única que
comprueba que las tres partes encajan — de hecho encontró un desajuste que
ninguna otra podía ver: el formulario permitía contraseñas de 6 caracteres
cuando el servidor ya exigía 8.

**«¿Qué has tenido en cuenta en seguridad?»**
Aquí tienes material de sobra, elige dos o tres y no los sueltes todos:

- SQL escrito a mano y siempre parametrizado; el único elemento dinámico que no
  se puede parametrizar —qué columnas actualiza un `UPDATE`— va por lista blanca.
- El rol de administrador **solo se puede crear desde las variables de entorno
  del despliegue**. No hay ningún camino desde la API pública, y hay un test que
  manda `role: "admin"` en el registro y comprueba que no lo concede.
- El rol se consulta en la base de datos en cada petición, no se lee del token:
  si viajara dentro, quitarle el permiso a alguien tardaría siete días en
  surtir efecto.
- Una tarea ajena devuelve 404 y no 403, para no confirmar que existe. Pero en
  la zona de administración devuelvo 403, porque ahí quien pregunta ya está
  autenticado y su existencia no es un secreto. **Saber cuándo toca cada uno es
  el matiz que importa.**

**«¿Qué mejorarías del proyecto?»**
Pregunta trampa clásica, y tienes respuestas honestas:

- Los tokens duran siete días y no hay forma de revocarlos; lo suyo sería
  refresh tokens, que ya implementé en la versión de Angular.
- `PUT` y `PATCH` comparten controlador y hacen los dos actualización parcial.
  Un `PUT` estricto debería reemplazar el recurso completo.
- El cliente está cubierto al 36%: lo importante está probado, pero falta el
  contexto de sesión.

Reconocer esto tú, antes de que lo encuentren, vale más que cualquier respuesta
defensiva.

### Un fallo que merece la pena contar

Si buscas un ejemplo concreto de depuración, este es bueno porque el error era
sutil y la solución no es obvia:

> El limitador de peticiones estaba inutilizado en producción sin que se notara. Al estar detrás del proxy de Render, Express veía siempre la IP del proxy, así que contaba a todos los visitantes como un único cliente: un usuario activo podía agotar el límite para todos los demás. Se arregla diciéndole a Express en cuántos proxies confiar — pero hay que decir *uno*, no *todos*: si confías en todos, cualquiera puede falsificar la cabecera y saltarse el límite con una IP inventada en cada petición.

Funciona porque tiene las tres cosas que se buscan en una respuesta técnica:
un síntoma que no era evidente, una causa que exige entender la infraestructura,
y una solución donde la opción fácil habría sido la insegura.
