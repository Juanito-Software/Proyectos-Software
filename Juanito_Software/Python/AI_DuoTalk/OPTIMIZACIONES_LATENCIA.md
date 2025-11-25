# 🚀 Optimizaciones de Latencia - AI_DuoTalk

Este documento explica las optimizaciones implementadas para reducir la latencia del sistema, inspiradas en las técnicas utilizadas por OpenAI y otros sistemas de LLM modernos.

## 📊 Problema Original

- **Latencia anterior**: ~60 segundos por respuesta
- **Cuellos de botella identificados**:
  1. Generación secuencial: STT → LLM → TTS (uno tras otro)
  2. Sin caché: cada pregunta requiere generación completa
  3. Sin streaming: espera a que termine toda la generación antes de TTS
  4. Prompts largos: más tokens = más tiempo de procesamiento

## ✅ Optimizaciones Implementadas

### 1. **Streaming del LLM con Paralelización de TTS**

**Qué hace**: Genera tokens incrementalmente y empieza a convertir a voz mientras aún se genera texto.

**Cómo funciona**:
- El LLM genera tokens uno por uno (streaming)
- Cuando se completa una oración (detecta `.`, `!`, `?`), la envía al TTS
- El TTS procesa y reproduce mientras el LLM sigue generando
- Reduce la latencia percibida significativamente

**Beneficio**: En lugar de esperar 30s de generación + 20s de TTS = 50s total, ahora:
- Empiezas a oír la respuesta en ~5-10 segundos
- El resto se reproduce mientras se genera

**Código**: `agents/agent_A.py` y `agents/agent_B.py` con `use_streaming=True`

### 2. **Caché Semántico**

**Qué hace**: Guarda respuestas de preguntas similares para reutilizarlas sin generar de nuevo.

**Cómo funciona**:
- Normaliza el texto de entrada (minúsculas, sin puntuación)
- Calcula un hash MD5 del texto normalizado
- Compara similitud semántica (70% de palabras en común)
- Si encuentra una respuesta similar, la reutiliza inmediatamente
- Guarda nuevas respuestas para futuras consultas

**Beneficio**: 
- Preguntas similares responden en <1 segundo (solo TTS)
- Reduce carga del LLM
- Mejora consistencia en respuestas

**Código**: `modules/cache_semantico.py`

**Archivo de caché**: `cache_semantico.json` (se crea automáticamente)

### 3. **Prompts Optimizados**

**Qué hace**: Reduce la longitud de los prompts para minimizar tokens de entrada.

**Cómo funciona**:
- Personalidades más concisas
- Elimina redundancias
- Mantiene la esencia pero con menos tokens

**Beneficio**: Menos tokens = menos tiempo de procesamiento

**Ejemplo**:
- Antes: ~150 tokens de prompt
- Ahora: ~80 tokens de prompt
- Ahorro: ~50% menos tokens de entrada

### 4. **Paralelización Inteligente**

**Qué hace**: Procesa múltiples chunks de texto en paralelo cuando es posible.

**Cómo funciona**:
- Divide el texto generado en oraciones
- Procesa chunks de TTS en paralelo con threading
- Concatena audios de forma fluida

**Beneficio**: Mejor aprovechamiento de recursos del sistema

## 📈 Mejoras Esperadas

### Latencia Percibida

| Escenario | Antes | Después | Mejora |
|-----------|-------|---------|--------|
| Primera pregunta | ~60s | ~10-15s | **75% más rápido** |
| Pregunta similar (caché) | ~60s | ~2-3s | **95% más rápido** |
| Streaming activo | N/A | Empieza en ~5s | **Latencia percibida mínima** |

### Uso de Recursos

- **CPU/GPU**: Mejor aprovechamiento con paralelización
- **Memoria**: Caché ocupa ~1-5MB (mínimo)
- **Disco**: Archivo de caché ~100KB-1MB

## 🔧 Configuración

### Activar/Desactivar Optimizaciones

En `agents/agent_A.py` y `agents/agent_B.py`:

```python
# Con todas las optimizaciones (recomendado)
response = agentA_process_text(text, use_cache=True, use_streaming=True)

# Solo caché, sin streaming
response = agentA_process_text(text, use_cache=True, use_streaming=False)

# Sin optimizaciones (modo original)
response = agentA_process_text(text, use_cache=False, use_streaming=False)
```

### Limpiar Caché

```python
from modules.cache_semantico import clear_cache
clear_cache()
```

O simplemente elimina el archivo `cache_semantico.json`

## 🎯 Próximas Optimizaciones Posibles

1. **Modelo más pequeño**: Usar un modelo más ligero para respuestas rápidas
2. **GPU acceleration**: Asegurar que PyTorch use GPU si está disponible
3. **Batch processing**: Procesar múltiples preguntas a la vez
4. **Embeddings avanzados**: Usar embeddings semánticos reales (sentence-transformers)
5. **Compresión de caché**: Comprimir respuestas largas en caché

## 📝 Notas Técnicas

- El streaming requiere que GPT4All soporte `streaming=True` (ya implementado)
- El caché semántico usa comparación básica de palabras; para mejor precisión, considerar embeddings
- La paralelización de TTS funciona mejor con textos largos (>200 caracteres)
- El caché expira después de 7 días automáticamente

## 🐛 Solución de Problemas

**Problema**: Streaming no funciona
- Verificar que GPT4All soporte streaming
- Revisar logs para errores de threading

**Problema**: Caché no encuentra respuestas similares
- Ajustar umbral de similitud en `cache_semantico.py` (línea ~50)
- Verificar que el archivo de caché existe y es válido

**Problema**: Latencia aún alta
- Verificar que GPU esté siendo usada (si disponible)
- Considerar reducir `max_tokens` aún más
- Revisar si hay otros procesos consumiendo recursos

---

**Última actualización**: Implementación completa de optimizaciones de latencia
**Versión**: 1.0

