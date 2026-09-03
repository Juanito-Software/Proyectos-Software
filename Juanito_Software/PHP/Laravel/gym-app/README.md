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
          ['entrenador@example.test','entrenador'],
          ['usuario@example.test','usuario']] as [$correo, $rol]) {
    \App\Models\User::create([
        'name'     => $rol,
        'email'    => $correo,
        'password' => bcrypt('la-que-tu-elijas'),
        'role'     => $rol,
    ]);
}
```

> Usa una contraseña de usar y tirar, no una de las tuyas. Y si en algún momento
> este proyecto se despliega, que estas cuentas no viajen con él.

