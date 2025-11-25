# ⏱️ Cuenta Atrás Personalizada para OBS

Un temporizador de cuenta atrás web personalizable diseñado para usar como fuente de navegador en OBS Studio.

## 🚀 Características

- ✅ Temporizador de cuenta atrás personalizable
- ✅ Configuración de colores (fondo y texto)
- ✅ Tamaño de fuente ajustable
- ✅ Texto superior opcional
- ✅ Interfaz web moderna y responsiva
- ✅ Accesible desde la red local
- ✅ Perfecto para usar en OBS como fuente de navegador

## 📋 Requisitos

- Python 3.8 o superior
- Flask

## 🛠️ Instalación

1. Instala las dependencias:

```bash
pip install -r requirements.txt
```

## ▶️ Uso

1. Inicia el servidor:

```bash
python app.py
```

2. Abre tu navegador en: `http://localhost:5000`

3. Configura tu temporizador:
   - Establece el tiempo (horas, minutos, segundos)
   - Personaliza el color del texto (el fondo es transparente)
   - Añade texto superior opcional
   - Ajusta el tamaño de fuente

4. Haz clic en "Iniciar Temporizador"

5. Se abrirá una nueva ventana con el temporizador activo

## 🎬 Configurar en OBS

1. Abre OBS Studio
2. Añade una nueva fuente "Navegador de Escena"
3. Copia la URL que se mostró al iniciar el temporizador
4. Pega la URL en OBS
5. Establece el tamaño personalizado (recomendado: 1920x1080)
6. **Importante**: En las propiedades de la fuente, asegúrate de que "Shutdown source when not visible" esté desactivado
7. ¡Listo! El temporizador aparecerá en tu escena con fondo transparente

## 🌐 Acceso desde la red local

Para acceder desde otra computadora en la misma red:

1. Descubre tu IP local (ejecuta `ipconfig` en Windows o `ifconfig` en Linux/Mac)
2. Accede desde `http://TU_IP_LOCAL:5000`
3. Esto te permite controlar el temporizador desde otro dispositivo

## 📝 Notas

- El temporizador se actualiza cada segundo
- El fondo es **transparente** para usarlo como overlay en OBS
- El color del texto se puede personalizar con códigos hexadecimales
- El temporizador funciona de forma continua hasta llegar a 00:00:00
- La página es completamente responsive

## 🎨 Personalización

- **Tiempo**: Configura horas, minutos y segundos
- **Color del texto**: Personaliza el color del texto (fondo transparente)
- **Texto**: Añade un mensaje que aparecerá encima del temporizador
- **Fuente**: Ajusta el tamaño del texto del temporizador

## 📄 Estructura del Proyecto

```
BackCount/
├── app.py              # Servidor Flask principal
├── templates/
│   ├── index.html      # Página de configuración
│   └── timer.html      # Página del temporizador
├── requirements.txt    # Dependencias
└── README.md          # Este archivo
```

## 💡 Tips

- El fondo transparente permite usar el temporizador como overlay
- Elige un color de texto que contraste bien con tu fondo en OBS
- El tamaño de fuente recomendado para OBS es 72px o superior
- Puedes tener múltiples temporizadores activos con diferentes IDs
- Recarga la página del temporizador para reiniciarlo

## 🐛 Solución de Problemas

Si el temporizador no se actualiza:
- Verifica que el servidor esté corriendo
- Revisa la consola del navegador (F12) para errores
- Asegúrate de que no hay un firewall bloqueando el puerto 5000

## 📜 Licencia

Este proyecto es de código abierto y está disponible para uso personal y comercial.

