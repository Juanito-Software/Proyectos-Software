
### Fase 1

Instalar:

- Python
    
- CUDA
    
- Git
    
- ComfyUI
    

y generar:

- imágenes
    
- Flux
    
- algún workflow sencillo
    

para familiarizarte con nodos.

---

### Fase 2

Añadir:

- Wan2.2
    
- Text-to-Video
    
- Image-to-Video
    

---

### Fase 3

Cuando controles ComfyUI:

- HunyuanVideo
    
- LoRAs para vídeo
    
- Control de movimiento
    
- Workflows personalizados
    

---

### Fase 4 (la más interesante para ti)

Montar una arquitectura propia:

```text
Frontend
      ↓
FastAPI
      ↓
Cola (Redis)
      ↓
Worker GPU
      ↓
Wan2.2
      ↓
MP4 generado
      ↓
Almacenamiento
```

Porque ahí es donde empiezas a unir:

- programación backend,
    
- IA,
    
- DevOps,
    
- automatización,
    

que son áreas que te interesan profesionalmente.

Mi recomendación sería: **antes de instalar nada, comprueba si tu 4060 Ti es la de 8 GB o la de 16 GB**. Esa única información determina si te recomiendo ir directamente a Wan2.2 14B o empezar por configuraciones más ligeras.