import crypto from 'node:crypto';
import { test, expect } from '@playwright/test';

/**
 * Recorrido completo por la aplicación, en un navegador real.
 *
 * Cada test se registra con un usuario nuevo: así no dependen unos de otros
 * ni del estado que haya dejado una ejecución anterior, y el aislamiento por
 * usuario los mantiene separados aunque compartan base de datos.
 */

/**
 * Nombre de usuario único para cada test.
 *
 * Con `crypto.randomUUID()` y no con `Math.random()` por dos motivos. El
 * práctico: `Date.now()` más un número de tres cifras colisiona de verdad
 * cuando varios tests arrancan dentro del mismo milisegundo, y dos usuarios con
 * el mismo nombre hacen fallar el registro por conflicto. El otro: CodeQL marca
 * cualquier `Math.random()` como «insecure randomness» sin poder saber que aquí
 * no se genera ninguna credencial, y silenciar el aviso caso por caso enseña a
 * ignorarlos.
 */
const nuevoUsuario = () => `e2e-${crypto.randomUUID().slice(0, 12)}`;

// Cumple los cuatro requisitos: 15+ caracteres, mayúscula, número y símbolo.
const PASSWORD = 'Frase larga de prueba e2e 7!';

async function registrarse(page, username = nuevoUsuario()) {
  await page.goto('/');

  // La pantalla de acceso arranca en modo "iniciar sesión"; hay que cambiar
  // al de registro.
  const enlaceRegistro = page.getByRole('button', { name: /regístrate/i });
  if (await enlaceRegistro.isVisible().catch(() => false)) {
    await enlaceRegistro.click();
  }

  await page.getByPlaceholder('Usuario', { exact: true }).fill(username);
  // Placeholders exactos: /contraseña/i casaría con los dos campos del
  // registro, "Contraseña" y "Repite la contraseña".
  await page.getByPlaceholder('Contraseña', { exact: true }).fill(PASSWORD);
  await page.getByPlaceholder('Repite la contraseña').fill(PASSWORD);
  await page.getByRole('button', { name: /registrarse|crear cuenta/i }).click();

  // La cabecera con el nombre solo aparece cuando hay sesión.
  await expect(page.getByText(username)).toBeVisible({ timeout: 15_000 });
  return username;
}

test.describe('Autenticación', () => {
  test('un usuario nuevo puede registrarse y entra directamente', async ({ page }) => {
    const username = await registrarse(page);
    await expect(page.getByRole('heading', { name: 'TaskHub' })).toBeVisible();
    await expect(page.getByText(username)).toBeVisible();
  });

  test('la sesión sobrevive a recargar la página', async ({ page }) => {
    const username = await registrarse(page);
    await page.reload();
    // El token está en localStorage: tras recargar no debe pedir credenciales.
    await expect(page.getByText(username)).toBeVisible();
  });

  test('salir devuelve a la pantalla de acceso', async ({ page }) => {
    await registrarse(page);
    await page.getByRole('button', { name: /salir/i }).click();

    await expect(page.getByPlaceholder('Usuario', { exact: true })).toBeVisible();

    // Y vuelve en modo "iniciar sesión", no en el que estuviera. Quien acaba de
    // registrarse y sale casi siempre quiere entrar, no crear otra cuenta.
    await expect(page.getByRole('button', { name: 'Entrar' })).toBeVisible();
    await expect(page.getByPlaceholder('Repite la contraseña')).not.toBeVisible();
  });

  test('la confirmación que no coincide impide registrarse', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /regístrate/i }).click();

    await page.getByPlaceholder('Usuario', { exact: true }).fill(nuevoUsuario());
    await page.getByPlaceholder('Contraseña', { exact: true }).fill(PASSWORD);
    await page.getByPlaceholder('Repite la contraseña').fill('otra cosa completamente');

    await expect(page.getByText(/no coinciden/i)).toBeVisible();
    // El botón se deshabilita: la petición no llega a salir.
    await expect(page.getByRole('button', { name: /registrarse/i })).toBeDisabled();
  });

  test('el campo de confirmación solo existe en el registro', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByPlaceholder('Repite la contraseña')).not.toBeVisible();

    await page.getByRole('button', { name: /regístrate/i }).click();
    await expect(page.getByPlaceholder('Repite la contraseña')).toBeVisible();
  });

  // Las cuatro reglas, cada una con su test. La longitud viene de NIST; la
  // mayúscula, el número y el símbolo son decisión propia de TaskHub, más
  // estricta que la norma.
  const INVALIDAS = [
    ['demasiado corta', 'Corto-Horse12!'],
    ['sin mayúscula', 'cafe con leche y 2 tostadas!'],
    ['sin número', 'Cafe con leche y tostadas!'],
    ['sin símbolo', 'Cafe con leche y 2 tostadas'],
  ];

  for (const [caso, password] of INVALIDAS) {
    test(`una contraseña ${caso} no permite registrarse`, async ({ page }) => {
      await page.goto('/');
      await page.getByRole('button', { name: /regístrate/i }).click();

      await page.getByPlaceholder('Usuario', { exact: true }).fill(nuevoUsuario());
      await page.getByPlaceholder('Contraseña', { exact: true }).fill(password);
      await page.getByPlaceholder('Repite la contraseña').fill(password);
      await page.getByRole('button', { name: /registrarse/i }).click();

      // No se entra: sigue viéndose el formulario de registro. Lo para la
      // validación del navegador (minLength o pattern) antes de que la
      // petición llegue a salir.
      await expect(page.getByPlaceholder('Usuario', { exact: true })).toBeVisible();
      await expect(page.getByPlaceholder('Repite la contraseña')).toBeVisible();
    });
  }

  test('la lista de requisitos se va marcando al escribir', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /regístrate/i }).click();

    const campo = page.getByPlaceholder('Contraseña', { exact: true });
    const cumplidos = page.locator('[data-cumplido="si"]');

    await expect(cumplidos).toHaveCount(0);

    await campo.fill('cafeconlecheytostadas'); // solo longitud
    await expect(cumplidos).toHaveCount(1);

    await campo.fill('Cafeconlecheytostadas'); // + mayúscula
    await expect(cumplidos).toHaveCount(2);

    await campo.fill('Cafeconlecheytostadas2'); // + número
    await expect(cumplidos).toHaveCount(3);

    await campo.fill('Cafe con leche y 2 tostadas!'); // + símbolo
    await expect(cumplidos).toHaveCount(4);
  });

  test('una contraseña de exactamente 15 caracteres es válida', async ({ page }) => {
    const username = nuevoUsuario();
    await page.goto('/');
    await page.getByRole('button', { name: /regístrate/i }).click();

    const quince = 'Correct-Horse2!'; // justo en el mínimo
    await page.getByPlaceholder('Usuario', { exact: true }).fill(username);
    await page.getByPlaceholder('Contraseña', { exact: true }).fill(quince);
    await page.getByPlaceholder('Repite la contraseña').fill(quince);
    await page.getByRole('button', { name: /registrarse/i }).click();

    await expect(page.getByText(username)).toBeVisible({ timeout: 15_000 });
  });

  test('una contraseña larga y válida deja registrarse y volver a entrar', async ({ page }) => {
    const username = nuevoUsuario();
    await page.goto('/');
    await page.getByRole('button', { name: /regístrate/i }).click();

    const larga = 'Una frase larga de paso que recuerdo sin esfuerzo 2026!';
    await page.getByPlaceholder('Usuario', { exact: true }).fill(username);
    await page.getByPlaceholder('Contraseña', { exact: true }).fill(larga);
    await page.getByPlaceholder('Repite la contraseña').fill(larga);
    await page.getByRole('button', { name: /registrarse/i }).click();

    await expect(page.getByText(username)).toBeVisible({ timeout: 15_000 });

    // Y se puede volver a entrar con ella. Al salir, el formulario vuelve solo
    // a modo "iniciar sesión", así que no hay que cambiarlo a mano.
    await page.getByRole('button', { name: /salir/i }).click();

    await page.getByPlaceholder('Usuario', { exact: true }).fill(username);
    await page.getByPlaceholder('Contraseña', { exact: true }).fill(larga);
    await page.getByRole('button', { name: /entrar/i }).click();
    await expect(page.getByText(username)).toBeVisible({ timeout: 15_000 });
  });

  test('el token de refresco no es accesible desde JavaScript', async ({ page }) => {
    // Es el motivo de haberlo movido a una cookie HttpOnly: un XSS puede
    // llevarse el token de acceso y disponer de quince minutos, pero no la
    // credencial que renueva la sesión durante días.
    await registrarse(page);

    const cookiesVisibles = await page.evaluate(() => document.cookie);
    expect(cookiesVisibles).not.toContain('taskhub_refresh');

    // Y en el almacenamiento tampoco: allí solo va el token de acceso.
    const guardado = await page.evaluate(() => localStorage.getItem('taskhub_auth'));
    expect(guardado).not.toContain('refresh');

    // Pero el navegador sí la tiene, marcada como HttpOnly.
    const cookies = await page.context().cookies();
    const refresco = cookies.find((c) => c.name === 'taskhub_refresh');
    expect(refresco).toBeDefined();
    expect(refresco.httpOnly).toBe(true);
    expect(refresco.sameSite).toBe('Strict');
  });

  test('con el token de acceso caducado, la sesión se renueva sola', async ({ page }) => {
    // Simula la caducidad borrando el token de acceso del almacenamiento y
    // dejando intacta la cookie de refresco, que es exactamente el estado en
    // que queda el navegador pasados quince minutos. La aplicación debe
    // renovar por su cuenta y seguir dentro, sin pedir credenciales.
    const username = await registrarse(page);

    await page.evaluate(() => {
      const auth = JSON.parse(localStorage.getItem('taskhub_auth'));
      auth.token = 'token-caducado-a-proposito';
      localStorage.setItem('taskhub_auth', JSON.stringify(auth));
    });

    await page.reload();

    // Sigue dentro: no ha aparecido el formulario.
    await expect(page.getByText(username)).toBeVisible({ timeout: 15_000 });
    await expect(page.getByPlaceholder('Usuario', { exact: true })).not.toBeVisible();

    // Y el token guardado ya no es el inventado: se ha renovado de verdad.
    const tokenActual = await page.evaluate(
      () => JSON.parse(localStorage.getItem('taskhub_auth')).token,
    );
    expect(tokenActual).not.toBe('token-caducado-a-proposito');
  });

  test('la renovación rota el token: la cookie cambia', async ({ page }) => {
    await registrarse(page);

    const antes = (await page.context().cookies()).find((c) => c.name === 'taskhub_refresh').value;

    // Fuerza una renovación caducando el token de acceso.
    await page.evaluate(() => {
      const auth = JSON.parse(localStorage.getItem('taskhub_auth'));
      auth.token = 'caducado';
      localStorage.setItem('taskhub_auth', JSON.stringify(auth));
    });
    await page.reload();
    await expect(page.getByRole('heading', { name: 'TaskHub' })).toBeVisible({ timeout: 15_000 });

    const despues = (await page.context().cookies()).find((c) => c.name === 'taskhub_refresh').value;
    expect(despues).not.toBe(antes);
  });

  test('tras cerrar sesión, el servidor no acepta renovar aunque se conserve la cookie', async ({
    page,
  }) => {
    // La diferencia con la implementación anterior: el logout revoca en el
    // servidor. Antes bastaba con recuperar el token del navegador para seguir
    // dentro; ahora el refresco está revocado y no hay vuelta atrás.
    const username = await registrarse(page);
    const guardado = await page.evaluate(() => localStorage.getItem('taskhub_auth'));

    await page.getByRole('button', { name: /salir/i }).click();
    await expect(page.getByPlaceholder('Usuario', { exact: true })).toBeVisible();

    // Se restaura a mano lo que había, imitando a quien copia el localStorage.
    await page.evaluate((valor) => localStorage.setItem('taskhub_auth', valor), guardado);
    await page.reload();

    // La renovación al arrancar falla y vuelve al formulario.
    await expect(page.getByPlaceholder('Usuario', { exact: true })).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText(username)).not.toBeVisible();
  });

  test('el refresco pide credenciales nuevas al servidor y no solo mira el almacenamiento', async ({
    page,
  }) => {
    // Comprueba que la renovación es una llamada real a la API, no un apaño
    // del cliente para no enseñar el formulario.
    const llamadas = [];
    page.on('request', (req) => {
      if (req.url().includes('/api/auth/refresh')) llamadas.push(req.method());
    });

    await registrarse(page);
    await page.reload();
    await expect(page.getByRole('heading', { name: 'TaskHub' })).toBeVisible({ timeout: 15_000 });

    expect(llamadas).toContain('POST');
  });

  test('unas credenciales incorrectas muestran error y no dejan entrar', async ({ page }) => {
    await page.goto('/');
    await page.getByPlaceholder('Usuario', { exact: true }).fill('usuario-que-no-existe-jamas');
    await page.getByPlaceholder('Contraseña', { exact: true }).fill('credenciales que no existen');
    await page.getByRole('button', { name: /entrar/i }).click();

    await expect(page.getByText(/incorrect/i)).toBeVisible({ timeout: 10_000 });
    await expect(page.getByRole('button', { name: /entrar/i })).toBeVisible();
  });
});

/**
 * Cambio de contraseña.
 *
 * Las otras tres capas de tests ya comprueban las piezas: el servicio revoca y
 * vuelve a abrir sesión, el controlador responde, el formulario valida. Pero
 * ninguna puede comprobar lo que de verdad promete esta función, porque la
 * promesa es sobre **dos navegadores a la vez**: cambiar la contraseña en un
 * dispositivo tiene que expulsar a los demás. Eso solo se ve aquí.
 */
const PASSWORD_NUEVA = 'Otra frase distinta y larga 9!';

async function entrar(page, username, password) {
  await page.goto('/');
  await page.getByPlaceholder('Usuario', { exact: true }).fill(username);
  await page.getByPlaceholder('Contraseña', { exact: true }).fill(password);
  await page.getByRole('button', { name: /entrar/i }).click();
  await expect(page.getByText(username)).toBeVisible({ timeout: 15_000 });
}

async function cambiarPassword(page, actual, nueva) {
  // `exact` en casi todo, y no por costumbre: estos selectores casan por
  // subcadena, y aquí hay tres nombres que se contienen unos a otros. El botón
  // «Contraseña» de la cabecera está dentro de «Cambiar contraseña», y la
  // etiqueta «Contraseña nueva» está dentro de «Repite la contraseña nueva».
  // Sin `exact` cada uno de esos dos selectores encuentra dos elementos.
  await page.getByRole('button', { name: 'Contraseña', exact: true }).click();
  await page.getByLabel('Contraseña actual', { exact: true }).fill(actual);
  await page.getByLabel('Contraseña nueva', { exact: true }).fill(nueva);
  await page.getByLabel('Repite la contraseña nueva', { exact: true }).fill(nueva);
  await page.getByRole('button', { name: /cambiar contraseña/i }).click();
}

test.describe('Cambio de contraseña', () => {
  test('expulsa al otro dispositivo y deja dentro a este', async ({ page, browser }) => {
    // Es la razón de ser de toda la función. Si la revocación global se
    // rompiera —por ejemplo invirtiendo el orden y abriendo la sesión nueva
    // antes de revocar— los tres niveles de tests de abajo seguirían en verde:
    // el servicio llamaría a las dos funciones, el controlador respondería 200
    // y el formulario enseñaría su confirmación. Solo un segundo navegador
    // delata que el dispositivo ajeno sigue dentro.
    const username = await registrarse(page);

    // Segundo dispositivo: contexto aparte, con sus propias cookies.
    const otroDispositivo = await browser.newContext();
    const otraPagina = await otroDispositivo.newPage();
    await entrar(otraPagina, username, PASSWORD);

    await cambiarPassword(page, PASSWORD, PASSWORD_NUEVA);
    await expect(page.getByText(/contraseña cambiada/i)).toBeVisible({ timeout: 15_000 });

    // Este sigue dentro aunque recargue: al terminar, el servidor le abrió una
    // sesión limpia y el navegador se quedó con la cookie nueva.
    await page.reload();
    await expect(page.getByText(username)).toBeVisible({ timeout: 15_000 });

    // El otro no. Conviene ser preciso sobre cuándo: lo que se revoca es el
    // token de refresco, no el de acceso, que sigue vivo hasta que caduque. Por
    // eso hace falta la recarga, que es cuando la aplicación pide credenciales
    // nuevas al servidor y se encuentra con la familia revocada. Ese hueco de
    // quince minutos es el precio conocido de no consultar la base de datos en
    // cada petición.
    await otraPagina.reload();
    await expect(otraPagina.getByPlaceholder('Usuario', { exact: true })).toBeVisible({
      timeout: 15_000,
    });
    await expect(otraPagina.getByText(username)).not.toBeVisible();

    await otroDispositivo.close();
  });

  test('la contraseña vieja deja de valer y la nueva entra', async ({ page }) => {
    const username = await registrarse(page);

    await cambiarPassword(page, PASSWORD, PASSWORD_NUEVA);
    await expect(page.getByText(/contraseña cambiada/i)).toBeVisible({ timeout: 15_000 });

    await page.getByRole('button', { name: /salir/i }).click();
    await expect(page.getByPlaceholder('Usuario', { exact: true })).toBeVisible();

    // La vieja ya no abre nada.
    await page.getByPlaceholder('Usuario', { exact: true }).fill(username);
    await page.getByPlaceholder('Contraseña', { exact: true }).fill(PASSWORD);
    await page.getByRole('button', { name: /entrar/i }).click();
    await expect(page.getByText(/incorrect/i)).toBeVisible({ timeout: 10_000 });

    // La nueva sí. Sin esta segunda mitad, el test pasaría igual con un cambio
    // que hubiera dejado la cuenta inaccesible con las dos contraseñas.
    await page.getByPlaceholder('Contraseña', { exact: true }).fill(PASSWORD_NUEVA);
    await page.getByRole('button', { name: /entrar/i }).click();
    await expect(page.getByText(username)).toBeVisible({ timeout: 15_000 });
  });

  test('con la contraseña actual equivocada no cambia nada', async ({ page }) => {
    // Exigir la actual es lo que impide que un token de acceso robado se
    // convierta en la pérdida definitiva de la cuenta. Aquí se comprueba que
    // el rechazo llega del servidor y que no tiene efectos colaterales: ni
    // cambia la contraseña ni cierra la sesión en curso.
    const username = await registrarse(page);

    await cambiarPassword(page, 'Esta no es la de antes 9!', PASSWORD_NUEVA);
    await expect(page.getByText('La contraseña actual no es correcta')).toBeVisible({
      timeout: 10_000,
    });

    // La sesión sigue viva tras recargar: no se ha revocado nada.
    await page.reload();
    await expect(page.getByText(username)).toBeVisible({ timeout: 15_000 });

    // Y la contraseña original sigue siendo la buena.
    await page.getByRole('button', { name: /salir/i }).click();
    await entrar(page, username, PASSWORD);
  });
});

test.describe('Ciclo de vida de una tarea', () => {
  test('crear, ver, completar y eliminar', async ({ page }) => {
    await registrarse(page);
    const titulo = `Tarea E2E ${Date.now()}`;

    // Todo acotado al formulario de creación: los selectores globales chocan
    // con los filtros, que tienen las mismas etiquetas y las mismas opciones.
    const formulario = page.locator('form.task-form').first();
    await formulario.getByPlaceholder(/título de la tarea/i).fill(titulo);
    await formulario.getByPlaceholder('Descripción (opcional)').fill('Creada desde Playwright');
    await formulario.getByLabel(/prioridad/i).selectOption('high');
    await formulario.getByRole('button', { name: /agregar tarea/i }).click();

    // Los distintivos se localizan por su clase, no por su texto: "Alta" y
    // "Pendiente" también aparecen dentro de las opciones de los desplegables.
    const tarjeta = page.locator('li.task-item').filter({ hasText: titulo });
    await expect(tarjeta).toBeVisible();
    await expect(tarjeta.locator('.badge--priority-high')).toHaveText('Alta');
    await expect(tarjeta.locator('.badge--status-pending')).toHaveText('Pendiente');

    // Completar con el checkbox.
    //
    // Se usa click() y no check(): el checkbox es un componente controlado
    // cuyo valor viene del estado de React, y ese estado no cambia hasta que
    // la API responde. check() comprueba el cambio inmediatamente después del
    // clic y fallaría siempre. La confirmación real es que aparezca el
    // distintivo de completada, que solo se pinta con la respuesta del
    // servidor: es una aserción más fuerte que mirar el propio checkbox.
    await tarjeta.getByRole('checkbox').click();
    await expect(tarjeta.locator('.badge--status-completed')).toHaveText('Completada');
    await expect(tarjeta.getByRole('checkbox')).toBeChecked();

    // Eliminar, aceptando la confirmación del navegador
    page.on('dialog', (dialog) => dialog.accept());
    await page.getByRole('button', { name: /eliminar/i }).first().click();
    await expect(page.getByText(titulo)).not.toBeVisible();
  });

  test('editar cambia título, estado y prioridad', async ({ page }) => {
    await registrarse(page);
    const titulo = `Editable ${Date.now()}`;

    await page.getByPlaceholder(/título de la tarea/i).fill(titulo);
    await page.getByRole('button', { name: /agregar tarea/i }).click();
    await expect(page.getByText(titulo)).toBeVisible();

    await page.getByRole('button', { name: /^editar$/i }).first().click();

    // Al abrir la edición hay dos formularios en pantalla: el de crear, arriba,
    // y el de la tarea. Se acota al <li> que se está editando en lugar de usar
    // selectores globales, que cogerían el de crear.
    const tarjeta = page.locator('li.task-item--editing');
    await tarjeta.getByPlaceholder(/título de la tarea/i).fill(`${titulo} (editada)`);
    await tarjeta.getByLabel(/estado/i).selectOption('in-progress');
    await tarjeta.getByRole('button', { name: /guardar/i }).click();

    // Igual que antes: "En progreso" también es el texto de una opción en dos
    // desplegables, así que se busca el distintivo dentro de la tarjeta.
    const editada = page.locator('li.task-item').filter({ hasText: `${titulo} (editada)` });
    await expect(editada).toBeVisible();
    await expect(editada.locator('.badge--status-in-progress')).toHaveText('En progreso');
  });

  test('no deja crear dos tareas con el mismo título', async ({ page }) => {
    await registrarse(page);
    const titulo = `Duplicada ${Date.now()}`;

    for (let i = 0; i < 2; i++) {
      await page.getByPlaceholder(/título de la tarea/i).fill(titulo);
      await page.getByRole('button', { name: /agregar tarea/i }).click();
      await page.waitForTimeout(500);
    }

    await expect(page.getByText(/ya tienes una tarea con este título/i)).toBeVisible();
  });
});

test.describe('Filtros', () => {
  test('filtrar por estado y por texto, y limpiar', async ({ page }) => {
    await registrarse(page);
    const sello = Date.now();

    // Acotado al formulario en lugar de usar .first(): así no depende del
    // orden en que estén los elementos en el DOM.
    const formulario = page.locator('form.task-form').first();

    for (const [titulo, estado] of [
      [`Pendiente ${sello}`, 'pending'],
      [`Completada ${sello}`, 'completed'],
    ]) {
      await formulario.getByPlaceholder(/título de la tarea/i).fill(titulo);
      await formulario.getByLabel(/estado/i).selectOption(estado);
      await formulario.getByRole('button', { name: /agregar tarea/i }).click();
      // La lista se recarga con 300 ms de espera tras cambiar los filtros.
      await expect(page.locator('li.task-item').filter({ hasText: titulo })).toBeVisible();
    }

    // Filtrar por estado: solo debe quedar una
    await page.getByLabel(/filtrar por estado/i).selectOption('completed');
    await expect(page.getByText(`Completada ${sello}`)).toBeVisible();
    await expect(page.getByText(`Pendiente ${sello}`)).not.toBeVisible();

    // Limpiar y buscar por texto
    await page.getByRole('button', { name: /limpiar/i }).click();
    await page.getByLabel(/buscar tareas/i).fill(`Pendiente ${sello}`);
    await expect(page.getByText(`Pendiente ${sello}`)).toBeVisible();
    await expect(page.getByText(`Completada ${sello}`)).not.toBeVisible();
  });

  test('una búsqueda sin resultados muestra el mensaje correspondiente', async ({ page }) => {
    await registrarse(page);
    await page.getByLabel(/buscar tareas/i).fill('texto-que-no-existe-en-ninguna-tarea');
    await expect(page.getByText(/ninguna tarea coincide/i)).toBeVisible();
  });
});

test.describe('Aislamiento entre usuarios', () => {
  test('un usuario no ve las tareas de otro', async ({ page, browser }) => {
    await registrarse(page);
    const titulo = `Privada ${Date.now()}`;
    await page.getByPlaceholder(/título de la tarea/i).fill(titulo);
    await page.getByRole('button', { name: /agregar tarea/i }).click();
    await expect(page.getByText(titulo)).toBeVisible();

    // Un contexto nuevo, no una pestaña nueva: las pestañas del mismo contexto
    // comparten localStorage, así que la segunda heredaría la sesión de la
    // primera y no habría dos usuarios distintos. Además, una pestaña recién
    // creada está en about:blank, donde el navegador ni siquiera permite leer
    // localStorage.
    const contextoAjeno = await browser.newContext();
    const otraPagina = await contextoAjeno.newPage();
    await registrarse(otraPagina);

    await expect(otraPagina.getByText(/todavía no tienes tareas/i)).toBeVisible();
    await expect(otraPagina.getByText(titulo)).not.toBeVisible();

    await contextoAjeno.close();
  });
});

test.describe('Playground', () => {
  test('se sirve y comparte la sesión con la aplicación', async ({ page }) => {
    const username = await registrarse(page);

    await page.goto('/playground');
    await expect(page.getByRole('heading', { name: 'TaskHub' })).toBeVisible();
    // Comparte el token por localStorage: no debe volver a pedir credenciales.
    await expect(page.getByText(username)).toBeVisible({ timeout: 10_000 });
  });

  test('sin sesión, el playground pide entrar', async ({ page }) => {
    await page.goto('/playground');
    await page.evaluate(() => localStorage.clear());
    await page.reload();
    await expect(page.getByRole('button', { name: /entrar/i })).toBeVisible();
  });

  test('el panel de administración no aparece para un usuario normal', async ({ page }) => {
    await registrarse(page);
    await page.goto('/playground');
    await expect(page.getByText('Administración')).not.toBeVisible();
  });

  /**
   * Los tres tests de arriba pasarían con TODOS los botones muertos: ninguno
   * pulsa nada. Y ese es justamente el modo de fallo de una CSP estricta —la
   * página carga, se ve entera, y lo único que no ocurre es nada—. Los tres de
   * abajo existen por eso.
   */

  test('los botones responden: abrir y cerrar el formulario de tarea', async ({ page }) => {
    await registrarse(page);
    await page.goto('/playground');

    const modal = page.locator('#task-modal');
    await expect(modal).not.toHaveClass(/active/);

    await page.locator('[data-accion="abrir-crear"]').first().click();
    await expect(modal).toHaveClass(/active/);

    await page.locator('[data-accion="cerrar-modal"]').first().click();
    await expect(modal).not.toHaveClass(/active/);
  });

  test('una tarjeta de endpoint responde aunque se pulse en un elemento hijo', async ({ page }) => {
    // Con los atributos onclick, el clic en un hijo subía por burbujeo hasta el
    // div que llevaba el manejador. Al pasar a un único oyente delegado, quien
    // reproduce ese comportamiento es `closest`. Si se hubiera escrito
    // comparando `event.target` en vez de subir por el árbol, pulsar en el
    // texto de la tarjeta no haría nada y pulsar justo en el borde sí — un
    // fallo desesperante de diagnosticar.
    await registrarse(page);
    await page.goto('/playground');

    const terminal = page.locator('#terminal');
    const inicial = await terminal.innerText();

    const tarjeta = page.locator('[data-accion="simular"][data-url="/api/tasks"]');
    await tarjeta.locator('span').first().click();

    await expect(terminal).not.toHaveText(inicial, { timeout: 10_000 });
  });

  test('el navegador no rechaza nada por la política de seguridad', async ({ page }) => {
    // La red de seguridad de verdad. Cualquier manejador en atributo o bloque
    // en línea que se colara en el futuro haría que el navegador escribiera
    // "Refused to execute…" en la consola, y ninguna comprobación del lado del
    // servidor puede verlo.
    const rechazos = [];
    page.on('console', (msg) => {
      const texto = msg.text();
      if (/Content Security Policy|Refused to/i.test(texto)) rechazos.push(texto);
    });

    await registrarse(page);
    await page.goto('/playground');
    await page.locator('[data-accion="abrir-crear"]').first().click();
    await page.locator('[data-accion="cerrar-modal"]').first().click();

    expect(rechazos).toEqual([]);
  });
});

test.describe('API', () => {
  test('las rutas de tareas exigen token', async ({ request }) => {
    const res = await request.get('/api/tasks');
    expect(res.status()).toBe(401);
  });

  test('la comprobación de salud responde sin autenticar', async ({ request }) => {
    const res = await request.get('/api/health');
    expect(res.ok()).toBeTruthy();
    expect((await res.json()).success).toBe(true);
  });

  test('las cabeceras de seguridad están presentes', async ({ request }) => {
    const res = await request.get('/api/health');
    const cabeceras = res.headers();
    // Las pone helmet: si alguien lo quita, este test lo detecta.
    expect(cabeceras['x-content-type-options']).toBe('nosniff');
    expect(cabeceras['content-security-policy']).toBeTruthy();
    expect(cabeceras['x-frame-options']?.toLowerCase()).toBe('sameorigin');
  });
});
