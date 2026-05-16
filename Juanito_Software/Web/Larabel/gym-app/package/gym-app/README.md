# Gym App - Instalacion, ejecucion y empaquetado

Guia rapida para levantar el proyecto en Windows (Laragon) y compartirlo listo para pruebas.

## 1) Requisitos

- Windows 10/11
- Laragon instalado
- Node.js y npm
- PHP 8.1+ y Composer (normalmente ya incluidos en Laragon)

## 2) Preparar entorno (PowerShell)

Ubicate en la carpeta del proyecto:

```powershell
cd C:\laragon\www\gym-app
```

Si `php` y `composer` no se reconocen en PowerShell, agrega Laragon al PATH de la sesion:

```powershell
$env:Path = "C:\laragon\bin\php\php-8.3.26-Win32-vs16-x64;C:\laragon\bin\composer;$env:Path"
```

Verifica:

```powershell
php -v
composer -V
node -v
npm -v
```

## 3) Instalar dependencias

```powershell
composer install
npm install
```

## 4) Configurar variables de entorno

Si no existe `.env`, crealo desde el ejemplo:

```powershell
copy .env.example .env
php artisan key:generate
```

Configura base de datos en `.env` (ejemplo):

```env
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=gym_app
DB_USERNAME=root
DB_PASSWORD=
```

## 5) Iniciar servicios

1. Abre Laragon.
2. Pulsa `Start All` (o inicia al menos MySQL).
3. Verifica que MySQL este activo.

## 6) Base de datos

Si no tienes una copia previa:

```powershell
php artisan migrate
```

Si te compartieron un dump `.sql`, importalo (ver seccion de empaquetado/importacion).

## 7) Ejecutar aplicacion

Abre dos terminales en la carpeta del proyecto:

Terminal 1 (backend):

```powershell
php artisan serve
```

Terminal 2 (frontend):

```powershell
npm run dev
```

Navega en:

- App: `http://127.0.0.1:8000`
- Vite (assets): normalmente `http://localhost:5173`

## 8) Usuarios de prueba

> Solo para pruebas locales/demo.

- Admin  
  - Email: `bernaldezperedaj@gmail.com`  
  - Password: `Tomate1?`

- Entrenador  
  - Email: `entrenador1@prueba.com`  
  - Password: `Tomate1?`

- Usuario  
  - Email: `prueba3@prueba.com`  
  - Password: `Tomate1?`

## 9) Empaquetar para compartir (codigo + base de datos)

### 9.1 Exportar la base de datos a SQL

Con Laragon iniciado y MySQL activo:

```powershell
C:\laragon\bin\mysql\mysql-8.4.3-winx64\bin\mysqldump.exe -u root -p --databases gym_app > gym_app.sql
```

Si tu `root` no tiene password, presiona Enter cuando la pida.

Si tu version de MySQL en Laragon tiene otra carpeta, ajusta la ruta de `mysqldump.exe`.

### 9.2 Crear carpeta de entrega

En una ruta temporal (ejemplo):

```powershell
mkdir C:\temp\gym-app-entrega
```

Copia a esa carpeta:

- Todo el proyecto `gym-app` (sin `node_modules` ni `vendor` si quieres un zip mas liviano)
- El archivo `gym_app.sql`

Recomendado excluir:

- `node_modules`
- `vendor`
- `.git`
- `storage/logs/*.log`

### 9.3 Comprimir en ZIP

```powershell
Compress-Archive -Path C:\temp\gym-app-entrega\* -DestinationPath C:\temp\gym-app-entrega.zip -Force
```

## 10) Como lo instala otra persona con tu paquete

1. Descomprimir ZIP en `C:\laragon\www\gym-app`.
2. Crear/configurar `.env`.
3. Ejecutar:

```powershell
composer install
npm install
```

4. Crear la base `gym_app` en MySQL y luego importar:

```powershell
C:\laragon\bin\mysql\mysql-8.4.3-winx64\bin\mysql.exe -u root -p gym_app < C:\ruta\gym_app.sql
```

5. Levantar app:

```powershell
php artisan serve
npm run dev
```

## 11) Problemas comunes

- Error 500 al login con `SQLSTATE[HY000] [2002]`: MySQL no esta iniciado o puerto/credenciales en `.env` no coinciden.
- `php` o `composer` no reconocido: falta agregar rutas de Laragon al PATH de la sesion.
- Advertencia de Browserslist en Vite: no bloquea la ejecucion; opcionalmente ejecutar `npx update-browserslist-db@latest`.

<p align="center"><a href="https://laravel.com" target="_blank"><img src="https://raw.githubusercontent.com/laravel/art/master/logo-lockup/5%20SVG/2%20CMYK/1%20Full%20Color/laravel-logolockup-cmyk-red.svg" width="400" alt="Laravel Logo"></a></p>

<p align="center">
<a href="https://github.com/laravel/framework/actions"><img src="https://github.com/laravel/framework/workflows/tests/badge.svg" alt="Build Status"></a>
<a href="https://packagist.org/packages/laravel/framework"><img src="https://img.shields.io/packagist/dt/laravel/framework" alt="Total Downloads"></a>
<a href="https://packagist.org/packages/laravel/framework"><img src="https://img.shields.io/packagist/v/laravel/framework" alt="Latest Stable Version"></a>
<a href="https://packagist.org/packages/laravel/framework"><img src="https://img.shields.io/packagist/l/laravel/framework" alt="License"></a>
</p>

## About Laravel

Laravel is a web application framework with expressive, elegant syntax. We believe development must be an enjoyable and creative experience to be truly fulfilling. Laravel takes the pain out of development by easing common tasks used in many web projects, such as:

- [Simple, fast routing engine](https://laravel.com/docs/routing).
- [Powerful dependency injection container](https://laravel.com/docs/container).
- Multiple back-ends for [session](https://laravel.com/docs/session) and [cache](https://laravel.com/docs/cache) storage.
- Expressive, intuitive [database ORM](https://laravel.com/docs/eloquent).
- Database agnostic [schema migrations](https://laravel.com/docs/migrations).
- [Robust background job processing](https://laravel.com/docs/queues).
- [Real-time event broadcasting](https://laravel.com/docs/broadcasting).

Laravel is accessible, powerful, and provides tools required for large, robust applications.

## Learning Laravel

Laravel has the most extensive and thorough [documentation](https://laravel.com/docs) and video tutorial library of all modern web application frameworks, making it a breeze to get started with the framework.

You may also try the [Laravel Bootcamp](https://bootcamp.laravel.com), where you will be guided through building a modern Laravel application from scratch.

If you don't feel like reading, [Laracasts](https://laracasts.com) can help. Laracasts contains over 2000 video tutorials on a range of topics including Laravel, modern PHP, unit testing, and JavaScript. Boost your skills by digging into our comprehensive video library.

## Laravel Sponsors

We would like to extend our thanks to the following sponsors for funding Laravel development. If you are interested in becoming a sponsor, please visit the Laravel [Patreon page](https://patreon.com/taylorotwell).

### Premium Partners

- **[Vehikl](https://vehikl.com/)**
- **[Tighten Co.](https://tighten.co)**
- **[Kirschbaum Development Group](https://kirschbaumdevelopment.com)**
- **[64 Robots](https://64robots.com)**
- **[Cubet Techno Labs](https://cubettech.com)**
- **[Cyber-Duck](https://cyber-duck.co.uk)**
- **[Many](https://www.many.co.uk)**
- **[Webdock, Fast VPS Hosting](https://www.webdock.io/en)**
- **[DevSquad](https://devsquad.com)**
- **[Curotec](https://www.curotec.com/services/technologies/laravel/)**
- **[OP.GG](https://op.gg)**
- **[WebReinvent](https://webreinvent.com/?utm_source=laravel&utm_medium=github&utm_campaign=patreon-sponsors)**
- **[Lendio](https://lendio.com)**

## Contributing

Thank you for considering contributing to the Laravel framework! The contribution guide can be found in the [Laravel documentation](https://laravel.com/docs/contributions).

## Code of Conduct

In order to ensure that the Laravel community is welcoming to all, please review and abide by the [Code of Conduct](https://laravel.com/docs/contributions#code-of-conduct).

## Security Vulnerabilities

If you discover a security vulnerability within Laravel, please send an e-mail to Taylor Otwell via [taylor@laravel.com](mailto:taylor@laravel.com). All security vulnerabilities will be promptly addressed.

## License

The Laravel framework is open-sourced software licensed under the [MIT license](https://opensource.org/licenses/MIT).
