Uno de los errores más comunes cuando se habla de IA actualmente: mucha gente usa "Machine Learning" para referirse casi exclusivamente a Deep Learning porque ChatGPT, Gemini, Claude, Midjourney, etc. están basados en redes neuronales profundas. Pero **Machine Learning es muchísimo más grande que Deep Learning**.

La realidad es que si estudias Machine Learning de forma seria, probablemente dedicarás más tiempo a modelos clásicos que a redes neuronales durante bastante tiempo.

La estructura correcta sería:

```text
Inteligencia Artificial
│
├── Sistemas expertos
├── Búsqueda y planificación
├── Lógica
├── Machine Learning
│   │
│   ├── Regresión
│   ├── Árboles de decisión
│   ├── Random Forest
│   ├── Gradient Boosting
│   ├── SVM
│   ├── KNN
│   ├── Naive Bayes
│   ├── Clustering
│   ├── PCA
│   ├── Aprendizaje por refuerzo
│   │
│   └── Deep Learning
│       ├── MLP
│       ├── CNN
│       ├── RNN
│       ├── LSTM
│       └── Transformers
│
└── Otros enfoques
```

---

# Lo que realmente es Machine Learning

Machine Learning es un conjunto enorme de técnicas para aprender patrones a partir de datos.

El objetivo no es construir redes neuronales.

El objetivo es:

```text
Datos
↓
Aprender relaciones
↓
Generalizar
↓
Predecir
```

Una red neuronal es solo una de las muchas herramientas que existen para lograrlo.

---

# Los grandes bloques del Machine Learning clásico

## 1. Regresión

Problema:

```text
Predecir un valor numérico
```

Ejemplos:

- Precio de una vivienda
    
- Temperatura mañana
    
- Ventas del mes
    
- Consumo energético
    

Modelo más simple:

### Regresión lineal

Busca una recta:

```text
y = mx + b
```

Por ejemplo:

```text
Precio = 50000 + 2000 × metros_cuadrados
```

Esto ya es Machine Learning.

Sin neuronas.

Sin IA generativa.

Sin GPUs.

---

## 2. Clasificación

Problema:

```text
Asignar categorías
```

Ejemplos:

```text
Spam / No spam

Fraude / No fraude

Cliente abandona / No abandona

Enfermo / Sano
```

Modelos típicos:

- Regresión logística
    
- Árboles
    
- Random Forest
    
- SVM
    
- Redes neuronales
    

---

# 3. Árboles de decisión

Uno de los algoritmos más importantes.

Funcionan como un árbol de preguntas.

```text
¿Edad > 30?
│
├─ Sí
│   ├─ Salario > 40000?
│   │   ├─ Sí → Comprar
│   │   └─ No → No comprar
│
└─ No
    └─ No comprar
```

Ventajas:

- Muy interpretables
    
- Fáciles de visualizar
    
- Rápidos
    

Problema:

```text
Sobreajustan fácilmente
```

---

# 4. Random Forest

Uno de los algoritmos más útiles de toda la historia del ML.

Idea:

```text
Un árbol → puede equivocarse

100 árboles → votan
```

```text
Árbol 1 → Gato
Árbol 2 → Gato
Árbol 3 → Perro
...
```

La mayoría decide.

Ventajas:

- Muy robusto
    
- Funciona bien con pocos datos
    
- Requiere poco ajuste
    

Por eso sigue siendo extremadamente utilizado en empresas.

---

# 5. Gradient Boosting

Aquí están los modelos que dominaron Kaggle durante años.

Ejemplos:

- XGBoost
    
- LightGBM
    
- CatBoost
    

Idea:

```text
Modelo 1 → se equivoca
Modelo 2 → corrige errores
Modelo 3 → corrige errores
Modelo 4 → corrige errores
...
```

Cada modelo aprende de los errores del anterior.

Actualmente son de los mejores algoritmos para:

```text
Datos tabulares
```

Es decir:

```text
Excel
CSV
Bases de datos
ERP
CRM
```

En muchos problemas empresariales superan a las redes neuronales.

---

# 6. Support Vector Machines (SVM)

Uno de los algoritmos más elegantes matemáticamente.

Imagina:

```text
Perros
xxxxxxxx

Gatos
oooooooo
```

SVM busca:

```text
La línea que mejor separa ambas clases
```

y además intenta maximizar la distancia entre ellas.

Concepto clave:

```text
Margen máximo
```

Durante años fue uno de los mejores clasificadores existentes.

---

# 7. K-Nearest Neighbors (KNN)

Extremadamente intuitivo.

Para clasificar algo nuevo:

```text
Busca los vecinos más cercanos
```

Ejemplo:

```text
5 vecinos

4 son gatos
1 es perro

Resultado:
Gato
```

No aprende una función explícita.

Simplemente memoriza ejemplos.

---

# 8. Naive Bayes

Basado en probabilidad.

Utiliza el teorema de Bayes.

genui{"math_block_widget_always_prefetch_v2":{"content":"P(A|B)=\frac{P(B|A)P(A)}{P(B)}"}}

Fue uno de los algoritmos clásicos para:

- Filtros de spam
    
- Clasificación de texto
    
- Sistemas de recomendación simples
    

---

# Machine Learning No Supervisado

Aquí no existen etiquetas.

No sabes las respuestas correctas.

Solo tienes datos.

---

## Clustering

Objetivo:

```text
Agrupar elementos parecidos
```

Ejemplo:

Clientes de una tienda.

El algoritmo descubre:

```text
Grupo 1 → estudiantes
Grupo 2 → familias
Grupo 3 → jubilados
```

sin que nadie se lo diga.

---

### K-Means

El algoritmo de clustering más famoso.

Funciona así:

```text
1. Crear K centroides
2. Asignar puntos
3. Recalcular centroides
4. Repetir
```

Hasta que los grupos se estabilizan.

---

# Reducción de dimensionalidad

Problema:

```text
100 variables
200 variables
1000 variables
```

Muchas son redundantes.

---

## PCA

Principal Component Analysis.

Busca nuevas variables que concentran la mayor información posible.

Permite:

- Visualizar datos
    
- Eliminar ruido
    
- Acelerar modelos
    

---

# Detección de anomalías

Objetivo:

```text
Encontrar cosas raras
```

Ejemplos:

- Fraudes bancarios
    
- Fallos industriales
    
- Ataques informáticos
    

El modelo aprende:

```text
Qué es normal
```

y detecta desviaciones.

---

# Aprendizaje por Refuerzo

Muy diferente al resto.

No aprende de ejemplos etiquetados.

Aprende interactuando.

```text
Estado
↓
Acción
↓
Recompensa
↓
Aprendizaje
```

Ejemplos:

- AlphaGo
    
- Robots
    
- Sistemas de control
    
- Videojuegos
    

---

# Entonces ¿dónde entra Deep Learning?

Después de todo lo anterior.

Históricamente:

```text
1950-2010
=
ML clásico
```

dominó la industria.

Luego aparecieron:

- GPUs
    
- Big Data
    
- Redes profundas
    

y nació el boom del Deep Learning.

---

# Lo que usan realmente las empresas

Esto suele sorprender.

La mayoría de problemas empresariales son:

```text
Predicción de ventas
Fraude
Churn
Scoring
Marketing
Logística
Forecasting
```

Y para ellos suelen utilizarse:

- Random Forest
    
- XGBoost
    
- LightGBM
    
- Regresión logística
    

mucho más que Transformers o LLMs.

Los Transformers dominan cuando trabajas con:

- Texto
    
- Imagen
    
- Audio
    
- Vídeo
    
- IA generativa
    

---

# Si fueras a aprender ML desde cero

Yo seguiría este orden:

```text
1. Python
2. Numpy
3. Pandas
4. Estadística
5. Probabilidad
6. Regresión lineal
7. Regresión logística
8. Árboles
9. Random Forest
10. Gradient Boosting
11. SVM
12. Clustering
13. PCA
14. Evaluación de modelos
15. Scikit-Learn
16. Deep Learning
17. PyTorch
18. CNN
19. RNN
20. Transformers
21. LLMs
22. MLOps
```

De hecho, para alguien con tu perfil de desarrollador Full Stack, entender profundamente **Scikit-Learn, árboles, Random Forest, XGBoost, métricas, validación cruzada y feature engineering** te dará una base mucho más sólida que lanzarte directamente a estudiar Transformers. Los LLMs son la punta visible del iceberg; el Machine Learning clásico es gran parte de la ingeniería que hay debajo.