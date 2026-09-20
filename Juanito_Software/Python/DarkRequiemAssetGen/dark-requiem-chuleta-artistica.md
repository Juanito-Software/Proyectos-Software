# DARK REQUIEM — Chuleta de dirección artística

> Documento de consulta rápida. No es un ensayo: es lo que abres cuando tienes que decidir
> qué suena en una sala, qué aspecto tiene un enemigo o cómo se llama un ítem.

---

## 0. La frase que gobierna todo

> **Una aventura de estilo Zelda construida sobre la iconografía medieval del Juicio Final,
> el Réquiem y la Danza de la Muerte.**

Esto no es "Zelda oscuro". La diferencia es que el juego tiene una **teología propia**:
hay un juicio, hay condenados, hay salvados, y el jugador está dentro del proceso.

**Test de coherencia** — cualquier asset, mecánica o línea de diálogo debe pasar al menos dos de tres:

1. ¿Habla de muerte, juicio, penitencia o condena?
2. ¿Podría existir en un manuscrito, retablo o misa de difuntos del s. XIV–XVI?
3. ¿Añade solemnidad en lugar de "molar"?

Si solo pasa el 3, es edginess genérico. Fuera.

---

## 1. Los cinco movimientos — el esqueleto conceptual

Estructura vertebral del juego. Cada movimiento es a la vez **tema musical, zona, emoción y mecánica**.
Es el sistema de leitmotiv que hace que todo lo demás encaje.

| Movimiento | Significado | Emoción | Dónde vive | Pieza ancla | Referencia visual |
|---|---|---|---|---|---|
| **Requiem** | Descanso eterno / la muerte ya ocurrida | Calma fúnebre | Hub, santuarios, guardado | Mozart — *Introitus / Lacrimosa* (suave) | Memling, ala central |
| **Dies Irae** | El día de la ira, llega el juicio | Terror, cataclismo | Umbral de acto, revelación del lore | Verdi — *Dies Irae* | Miguel Ángel, *Juicio Final* |
| **Rex Tremendae** | Aparece algo infinitamente superior | Sobrecogimiento | Entidad divina, dios muerto, juez | Verdi — *Rex Tremendae* | Rubens, *Gran Juicio Final* |
| **Confutatis** | Los condenados frente a los elegidos | Angustia moral | Bifurcaciones, elecciones irreversibles | Verdi — *Confutatis* | Bosch, panel infernal |
| **Lacrimosa** | Las consecuencias, el duelo | Tristeza | Muerte de NPC, finales, ruinas | Mozart — *Lacrimosa* | Bruegel, *El triunfo de la muerte* |

**Cómo usarlo en la práctica:** cada acto del juego debería *tocar* los cinco en algún orden.
Y cada uno tiene su propia paleta, su propio tipo de enemigo y su propio sonido de UI.

---

## 2. Biblioteca musical

Escala de intensidad: **1 = casi silencio · 5 = cataclismo**.
Regla: no más de **una pieza de intensidad 5 por hora de juego**. Si suena siempre el coro, deja de significar nada.

### 2.1 Núcleo melancólico (base, exploración, respiro)

| Pieza | Función | Int. | Uso concreto |
|---|---|:--:|---|
| Beethoven — *Moonlight Sonata*, I | Melancolía, soledad | 1 | Hub, refugio, menú de pausa |
| Chopin — *Preludio Op. 28 nº 4* | Resignación absoluta | 1 | Muerte del jugador, epitafios, tumbas |
| Rachmaninoff — *Vocalise* | Duelo, recuerdo | 1 | Pueblos abandonados, flashbacks, post-batalla |
| Mozart — *Lacrimosa* | Dolor, consecuencia | 3 | Muerte de personajes, ciudades caídas, final |

### 2.2 Núcleo litúrgico (juicio, lore, entidades)

| Pieza | Función | Int. | Uso concreto |
|---|---|:--:|---|
| Mozart — *Dies Irae* | Condena religiosa, "espera tu sentencia" | 3 | Iglesias, criptas, cementerios, NPCs religiosos |
| Verdi — *Confutatis* | Condenados vs. elegidos | 4 | Zonas de decisión moral, tribunales |
| Verdi — *Rex Tremendae* | Poder divino | 4 | Aparición de entidad superior, antesala de boss |
| Verdi — *Dies Irae* | Apocalipsis, juicio general | 5 | Boss final, revelación del verdadero lore, endgame |

### 2.3 Núcleo demoníaco y bélico (combate, mazmorra, caos)

| Pieza | Función | Int. | Uso concreto |
|---|---|:--:|---|
| Saint-Saëns — *Danse Macabre* | La muerte **bailando** | 2 | Tema de identidad, títulos, enemigo recurrente |
| Beethoven — Sinfonía VII, II (*Allegretto*) | Marcha, destino inevitable | 2 | Avance de ejército, travesía larga, cuenta atrás |
| Liszt — *Totentanz* | Danza de la muerte, versión agresiva | 4 | Combate de mazmorra, aparición de demonio |
| Mussorgsky — *Una noche en el Monte Pelado* | Caos sobrenatural | 4 | Los muertos salen de las tumbas, oleadas |
| Berlioz — *Sinfonía fantástica*, V (*Aquelarre*) | Pesadilla, brujería, grotesco | 4 | Aquelarre, zona onírica, enemigo brujo |
| Holst — *Los planetas*: *Marte* | Guerra, invasión, destrucción | 5 | Ejército de muertos, boss militar, asedio |

### 2.4 Reglas de uso musical

- **El silencio es un instrumento.** Un pasillo sin música antes del *Rex Tremendae* multiplica su efecto.
- **Contraste, no acumulación.** Melancolía → tensión → estallido → melancolía. Nunca dos estallidos seguidos.
- **Una pieza = un significado.** Si *Totentanz* suena en tres contextos distintos, deja de comunicar.
- **Danse Macabre y Totentanz son familia.** Úsalas como dos caras del mismo enemigo o concepto.
- **Berlioz y Mussorgsky también son familia** (aquelarre / noche de los muertos). Misma zona, no mismas salas.

---

## 3. El leitmotiv *Dies Irae* — la mina de oro

La secuencia medieval *Dies Irae* se reduce a un **motivo de cuatro notas descendentes**, y está
citada literalmente en Berlioz, Liszt, Rachmaninoff, Saint-Saëns y en medio siglo de bandas sonoras
de cine. Es reconocible incluso por quien no sabe qué es.

**Esto es lo que te da identidad propia**, más que cualquier lista de piezas prestadas:

| Variación del motivo | Instrumento | Dónde |
|---|---|---|
| Caja de música desafinada | Celesta / carillón | Menú, guardado, recuerdo de infancia |
| Campana solitaria | Campana tubular | Al entrar en una zona nueva |
| Violonchelo solo | Cuerda grave | Muerte de un NPC |
| Marcha de percusión | Timbal + bombo | Persecución, oleada |
| Coro completo | Coro + órgano | Boss final |

Un solo motivo, cinco arreglos, y el jugador reconoce el juego en tres segundos. **Prioridad alta.**

---

## 4. Nota práctica de licencias (léela antes de meter un `.mp3`)

Esto no aparecía en las notas originales y es lo que más te puede morder:

- **La composición** de todo lo listado está en **dominio público** (Verdi, Mozart, Liszt, etc.). Sin problema.
- **La grabación concreta, no.** Una interpretación de la Filarmónica de Berlín de 1998 tiene copyright
  de sello e intérpretes. Meterla en tu build es infracción, aunque la pieza tenga 200 años.

**Vías limpias, de menor a mayor coste:**

1. Grabaciones en dominio público o CC0 (Musopen y similares). Calidad irregular, pero gratis y legal.
2. Partituras libres (IMSLP) + **arreglo propio**: reducción a piano, órgano, cuarteto o coro pequeño.
   Grabado por un músico de confianza sale mucho más barato de lo que parece y te da derechos limpios.
3. **Composición original sobre el motivo *Dies Irae***. El motivo es de dominio público; lo que
   compongas encima es tuyo. Es la opción que más identidad da y la que mejor se adapta a bucles,
   transiciones y capas dinámicas de Unity.

> Opinión: la opción 2 + 3 combinadas son el camino. Las piezas originales completas úsalas como
> **referencia de mood para el compositor**, no necesariamente como assets finales.

---

## 5. Biblioteca visual

| Obra | Qué robar exactamente | Aplicación directa |
|---|---|---|
| **Miguel Ángel — *Juicio Final*** | Composición vertical: ascenso / juez / caída. Cuerpos musculosos y pesados | Portada, pantalla de título, estructura del acto final |
| **Bosch — *Juicio Final*** | Criaturas híbridas, cuerpos deformados, máquinas de tortura, arquitectura imposible | **Diseño de enemigos.** Es tu bestiario |
| **Memling — *Juicio Final*** | Estructura tríptica: Cielo ↑ / Juicio → / Infierno ↓ | **Arquitectura de mazmorra.** Un dungeon de tres alturas |
| **Bruegel — *El triunfo de la muerte*** | La muerte como **ejército**, no como personaje. Horizonte quemado, multitud | Diseño de mundo, zona overworld, hordas |
| **Dürer — *Los cuatro jinetes*** | Cuatro siluetas, cuatro atributos claros | **Cuatro bosses**: Conquista, Guerra, Hambre, Muerte |
| **Dürer — *El Apocalipsis* (serie)** | Grabado en blanco y negro, línea densa, ángeles y trompetas | Iconografía, UI, mapas, ilustración de lore |
| **Signorelli — *Juicio Final*** | Anatomía retorcida, resurrección de la carne, esqueletos levantándose | **Animación**: cómo se levanta un muerto, cómo se contorsiona |
| **Rubens — *Gran Juicio Final*** | Escala imposible, masas de cuerpos en diagonal | Boss gigantesco, plano de cámara del clímax |
| **Blake — *El gran dragón rojo*** | Entidad sobrehumana, color saturado y antinatural | Entidades cósmicas, ángeles hostiles |
| **Doré — *La Divina Comedia*** | Luz teatral, silueta contra niebla, profundidad de abismo | **Lenguaje de iluminación y silueta.** Cómo se lee una escena |

### 5.1 Jerarquía (importante: no uses las diez a la vez)

- **Fuentes primarias (el 80 % del juego):** Bruegel (mundo) + Doré (luz y silueta).
- **Fuentes secundarias:** Bosch (enemigos) + Dürer (iconografía y UI).
- **Fuentes de clímax, dosis única:** Miguel Ángel, Rubens, Blake.

Mezclar Bosch, Rubens y Blake en la misma sala produce ruido visual, no atmósfera.

### 5.2 Paleta derivada

| Color | Uso | Origen |
|---|---|---|
| Negro humo / carbón | Fondo, sombra, vacío | Doré |
| Ocre y tierra quemada | Mundo, ruina, hueso viejo | Bruegel |
| Rojo bermellón | **Solo** condena, sangre, entidad hostil | Blake |
| Oro pálido | **Solo** salvación, divinidad, ítem clave | Miguel Ángel |
| Blanco hueso | Esqueletos, texto, iconografía | Dürer |

Regla dura: **rojo y oro son moneda escasa.** Si aparecen en una sala normal, pierdes el lenguaje.

---

## 6. Estructura narrativa: la vía dantesca

| Acto | Espacio | Mecánica dominante | Movimiento musical | Referencia visual |
|:--:|---|---|---|---|
| **I** | Mundo de los vivos | Exploración, tiempo real | Requiem (calma) | Bruegel |
| **II** | Purgatorio | Puzzle, penitencia, elección | Confutatis | Memling |
| **III** | Infierno | Combate duro, mazmorra | Dies Irae / Totentanz | Bosch + Doré |
| **IV** | El Juicio | Turnos puros, boss | Rex Tremendae | Miguel Ángel / Rubens |
| **V** | Sentencia | Final ramificado | Lacrimosa | Bruegel / Signorelli |

Ventaja: **es una progresión que el jugador ya intuye culturalmente.** No necesitas explicarla.

---

## 7. Mecánica = tema (la parte que evita que esto sea decoración)

Aquí es donde el concepto deja de ser un moodboard y se convierte en diseño de juego:

| Sistema | Lectura temática |
|---|---|
| **Combate en tiempo real** | Instinto, reflejo, supervivencia. El cuerpo. |
| **Combate por turnos** | Juicio, cálculo, deliberación. El alma. |
| **Alternancia entre ambos** | El jugador oscila entre *actuar* y *ser juzgado* |
| **Cada run del roguelite** | Un juicio completo: entras, decides, combates, mueres, el mundo registra |
| **Muerte del jugador** | No es "Game Over": es **sentencia**. Cambia el copy en pantalla |
| **Leaderboard mundial** | **Tabla de Condenados**, no un ranking genérico |
| **Guardado** | Un "descanso" (*requiescat*), en santuario, con vela |

### Ideas derivadas que merecen prototipo

- **Sistema de pecados y virtudes acumulados durante la run.** No lo ves como barra; lo ves cuando
  el juez, al final, **te lee tus propias acciones**. Es un final ramificado que no requiere árboles
  de diálogo, solo contadores.
- **La Tabla de Condenados muestra la causa de muerte**, no solo la puntuación. "Cayó ante el Segundo
  Jinete, en el piso VII" es más memorable que "puntuación: 14.320".
- **La muerte de otro jugador deja rastro en tu mundo** (un cadáver, un epitafio). Barato de
  implementar, enorme en atmósfera, y encaja literalmente con "el mundo registra tu resultado".

---

## 8. Diseño de enemigos por fuente

| Fuente | Tipo de enemigo | Nota de diseño |
|---|---|---|
| Bosch | Híbridos, deformes, absurdos-terroríficos | Enemigos comunes de mazmorra. Silueta rara, legible |
| Signorelli | Muertos que resucitan, cuerpos retorcidos | Animaciones de aparición y muerte |
| Bruegel | Hordas de esqueletos con herramientas y armas caseras | Enemigos de overworld, en grupo |
| Dürer | Los cuatro jinetes | Cuatro bosses principales, atributo único cada uno |
| Blake | Entidad cósmica, dragón, ángel hostil | Boss final o entidad no combatible |
| Berlioz / Mussorgsky | Brujas, aquelarre, espíritus | Una zona entera, no enemigos sueltos |

**Regla de silueta:** todo enemigo debe ser reconocible en negro puro sobre fondo claro.
Bosch es genial de referencia pero ilegible si lo copias literal. Simplifica hasta la silueta.

---

## 9. Mini-glosario latino (nombres de zonas, ítems y bosses)

| Término | Significado | Uso sugerido |
|---|---|---|
| *Requiem* | Descanso | Nombre del hub o del santuario |
| *Dies Irae* | Día de la ira | Acto o evento de mundo |
| *Tuba Mirum* | La trompeta que despierta a los muertos | Objeto clave, evento de oleada |
| *Rex Tremendae* | Rey de tremenda majestad | Boss final |
| *Confutatis* | Los confundidos / condenados | Zona de bifurcación |
| *Lacrimosa* | Llorosa | Final, o zona de duelo |
| *Libera Me* | Líbrame | Ítem de resurrección o escape |
| *Kyrie Eleison* | Señor, ten piedad | Mecánica de súplica / perdón |
| *Agnus Dei* | Cordero de Dios | Sacrificio, ítem consumible caro |
| *Memento Mori* | Recuerda que morirás | Tutorial, o mensaje al morir |
| *Ars Moriendi* | El arte de morir bien | Menú de progresión meta del roguelite |
| *Vanitas* | Vanidad, lo efímero | Objetos de coleccionismo |
| *Totentanz* | Danza de la muerte | Enemigo recurrente o modo desafío |

---

## 10. Reglas de oro

1. **Solemnidad antes que espectáculo.** Si algo "mola" pero no pesa, se cae.
2. **Un significado por pieza musical.** Reutilizar es diluir.
3. **El silencio precede al coro.** Siempre.
4. **Rojo y oro son sagrados.** Escasez absoluta.
5. **Dos fuentes visuales primarias, no diez.** Bruegel + Doré.
6. **Toda silueta debe leerse en negro.**
7. **El motivo de cuatro notas aparece en cada acto**, transformado.
8. **La muerte nunca es un fallo: es una sentencia.** Cuida el copy.
9. **Latín para nombrar, castellano para hablar.** El latín pierde fuerza si lo usas para todo.
10. **Si dudas de si una idea encaja, aplica el test de la sección 0.**

---

## 11. Trampas a evitar

- **Sobredosis de coro.** El error más común. Verdi a todo volumen durante veinte minutos anestesia.
- **Moodboard sin traducción mecánica.** Si el Juicio Final no cambia *cómo se juega*, es solo un skin.
- **Copiar a Bosch literalmente.** Precioso en un cuadro de 2 m, ilegible en un sprite de 64 px.
- **Incoherencia por acumulación de referencias.** Diez maestros a la vez = ningún estilo.
- **Alcance.** Cinco actos, cuatro bosses jinetes, híbrido tiempo real/turnos, roguelite y leaderboard
  online es un juego de estudio, no de un dev en solitario. **Elige un acto y un jinete como vertical
  slice** y demuestra el concepto ahí antes de expandir.

---

## 12. Decisiones pendientes

- [ ] ¿El motivo *Dies Irae* se compone original o se usan grabaciones libres? (ver sección 4)
- [ ] ¿Cuántos actos reales tendrá la v1? *(recomendación: uno, completo y pulido)*
- [ ] ¿El híbrido tiempo real / turnos es por zona, por enemigo o a elección del jugador?
- [ ] ¿El roguelite es el modo principal o un modo secundario sobre una campaña lineal?
- [ ] ¿Qué resolución y estilo de arte final? (pixel art, 2D pintado, 3D con shader de grabado)
- [ ] ¿La Tabla de Condenados es online real o local con datos sembrados?
- [ ] ¿Sistema de pecados/virtudes en v1 o se pospone?
- [ ] Vertical slice elegido: acto ____ , boss ____ , duración objetivo ____ min
