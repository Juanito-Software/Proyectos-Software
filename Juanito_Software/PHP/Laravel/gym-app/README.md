# Gym App

Aplicacion web para gestion de gimnasio, desarrollada con Laravel y Vite.

## Requisitos

- Windows 10/11
- Laragon
- PHP 8.1 o superior
- Composer
- Node.js y npm
- MySQL (incluido en Laragon)

## Instalacion

1) Clonar o copiar el proyecto en:

```powershell
C:\laragon\www\gym-app
```
2. Importar el archivo SQL:
```
gym_app_demo.sql
```

3) Abrir una terminal en la carpeta del proyecto:

```powershell
cd C:\laragon\www\gym-app
```

4) Si `php` o `composer` no son reconocidos, verificar que Laragon y Composer estén correctamente añadidos al PATH del sistema.

5) Si `composer install` falla por `zip` o `git`, aplicar este prerequisito:

- En `C:\laragon\bin\php\php-8.3.26-Win32-vs16-x64\php.ini`, activar:
  `extension=zip` (quitar el `;`).
- Usar una terminal nueva con Git en PATH:

```powershell
$env:Path = "C:\laragon\bin\php\php-8.3.26-Win32-vs16-x64;C:\laragon\bin\composer;C:\laragon\bin\git\cmd;$env:Path"
```

6) Instalar dependencias:

```powershell
composer install
npm install
```

7) Crear archivo de entorno y clave de aplicacion:

```powershell
copy .env.example .env
php artisan key:generate
```

8) Configurar base de datos en `.env`:

```env
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=gym_app
DB_USERNAME=root
DB_PASSWORD=
```

9) Iniciar servicios en Laragon (al menos MySQL).

- Si ya se importó `gym_app_demo.sql`, no es necesario ejecutar migraciones.
- Alternativamente, puede generarse la estructura de la base de datos mediante:

```powershell
php artisan migrate

## Ejecucion

Ejecutar en dos terminales distintas dentro de `C:\laragon\www\gym-app`.

Terminal 1 (backend):

```powershell
php artisan serve
```

Terminal 2 (frontend):

```powershell
npm run dev
```

Abrir en el navegador:

- Aplicacion: `http://127.0.0.1:8000`
- Assets en desarrollo (Vite): `http://localhost:5173`

## Usuarios de prueba

La aplicación tiene tres roles —administrador, entrenador y usuario— y para
recorrerla entera hacen falta los tres. **No vienen creados**: el seeder deja el
ejemplo comentado a propósito, para no meter cuentas con contraseña conocida en
ninguna base de datos que luego se despliegue por error.

Se crean en un minuto con Tinker, eligiendo tú la contraseña:

```bash
php artisan tinker
```

```php
foreach ([['admin@example.test','admin'],
          ['entrenador@example.test','coach'],
          ['usuario@example.test','client']] as [$correo, $rol]) {
    \App\Models\User::create([
        'name'     => $rol,
        'email'    => $correo,
        'password' => bcrypt('la-que-tu-elijas'),
        'role'     => $rol,
    ]);
}
```

> **Los valores de `role` son `admin`, `coach` y `client`**, en inglés. Este
> fragmento decía `entrenador` y `usuario`, que es como se llaman los roles en
> la interfaz, pero la columna es un `enum('client','coach','admin')` y esos dos
> valores no entran. MySQL en modo estricto rechaza la inserción; en modo
> permisivo guarda una cadena vacía, y entonces el usuario existe pero no encaja
> con ningún grupo de rutas.

> Usa una contraseña de usar y tirar, no una de las tuyas. Y si en algún momento
> este proyecto se despliega, que estas cuentas no viajen con él.

---

## Tests

**41 tests con PHPUnit.** No necesitan MySQL: `phpunit.xml` fija SQLite en
memoria, y eso no es solo comodidad — los tests usan `RefreshDatabase`, que
lanza `migrate:fresh`. Sin esas dos líneas arrasarían la base de desarrollo
declarada en `.env`.

```bash
npm run build     # solo la primera vez, o tras tocar los assets
php artisan test
```

> **Sí, hace falta compilar los assets.** Los layouts Blade llaman a
> `@vite(...)`, que busca `public/build/manifest.json` al renderizar. Si no
> está, la vista lanza `ViteManifestNotFoundException` y los siete tests que
> renderizan una pantalla fallan con «Expected 200 but received 500» — un
> mensaje que no menciona Vite por ninguna parte.
>
> En local no suele notarse porque `public/build/` ya existe de alguna
> compilación anterior, pero está en `.gitignore` y no viaja con el
> repositorio. En un clon limpio hay que compilar antes.

| Fichero | Tests | Qué cubre |
|---|---|---|
| `tests/Feature/RoleMiddlewareTest.php` | 7 | Que `RoleMiddleware` **decide** bien |
| `tests/Feature/RutasPorRolTest.php` | 9 | Que está **aplicado** en las rutas que toca |
| `tests/Feature/Auth/*` | 18 | Registro, login, verificación de correo, contraseñas |
| `tests/Feature/ProfileTest.php` | 5 | Perfil de usuario |
| `tests/Feature/ExampleTest.php` · `tests/Unit/ExampleTest.php` | 2 | Andamiaje de Laravel |

### Por qué dos ficheros para el control de acceso

Son dos fallos distintos y el primero no detecta el segundo. Un middleware
impecable que nadie ha puesto en la ruta deja la sección abierta igual.

`RoleMiddlewareTest` define sus **propias rutas** de usar y tirar en vez de
atacar las reales. Así, cuando falla, significa que la autorización está rota —y
no que a un controlador le faltaban datos sembrados—. Fija cuatro reglas:

- Un visitante sin autenticar es **redirigido a `/login`**, no recibe un 403. La
  diferencia importa: un 403 le confirmaría que el recurso existe.
- El rol exigido pasa; cualquiera de los listados pasa.
- Un rol que no está en la lista recibe 403.
- **Un `admin` entra en rutas que no lo mencionan.** Esta es la que más falta
  hacía tener escrita: en `routes/web.php`, `/coach/classes` dice `role:coach` y
  nada más, así que nadie deduce leyendo esa línea que un administrador también
  pasa. La regla vive en un `if` dentro del middleware.

`RutasPorRolTest` inspecciona la tabla de rutas en vez de pedir las URL: sin base
de datos, sin ejecutar controladores, en milisegundos. Incluye un barrido de
**todas** las rutas bajo `/admin`, `/coach` y `/clients` exigiendo `auth` y algún
`role:`. Ese es el que cazaría un `Route::resource` añadido por descuido fuera
del grupo, o un `withoutMiddleware()` puesto para depurar y olvidado.

> **Los otros 25 tests son de Laravel Breeze.** Los genera al instalarse y
> prueban su propio flujo de autenticación, no la lógica del gimnasio. Valen
> —comprueban que ese flujo funciona con tus migraciones y tu modelo `User`—
> pero no son cobertura de gym-app.

### En CI

El job **`PHP · tests`** de `.github/workflows/ci.yml` los ejecuta en cada push.
Genera una `APP_KEY` de usar y tirar a partir de `.env.example`, porque en un
*runner* no hay `.env` y Laravel no arranca sin ella.

Exige además un mínimo de tests ejecutados. Si el número baja, el CI falla y hay
que ajustar el mínimo a mano: quitar cobertura pasa a ser una decisión escrita en
el diff en lugar de un efecto colateral que nadie ve.

