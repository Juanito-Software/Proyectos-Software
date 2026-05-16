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

4) Si PowerShell no reconoce `php` o `composer`, agregar Laragon al PATH de la sesion:

```powershell
$env:Path = "C:\laragon\bin\php\php-8.3.26-Win32-vs16-x64;C:\laragon\bin\composer;$env:Path"
```

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

9) Iniciar servicios en Laragon (al menos MySQL) y ejecutar migraciones:

```powershell
php artisan migrate
```

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

### Administrador
- Email: `bernaldezperedaj@gmail.com`
- Password: `Tomate1?`

### Entrenador
- Email: `entrenador1@prueba.com`
- Password: `Tomate1?`

### Usuario
- Email: `prueba3@prueba.com`
- Password: `Tomate1?`

