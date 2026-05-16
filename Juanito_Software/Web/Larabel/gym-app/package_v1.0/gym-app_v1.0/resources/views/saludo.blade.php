<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Saludo</title>
    @vite(['resources/css/style.css', 'resources/js/script.js'])
</head>
<body>
    <div class="container">
        <h1>Hola, {{ $nombre }} 👋 desde Blade</h1>
        <button id="boton">Haz clic</button>
    </div>
</body>
</html>
