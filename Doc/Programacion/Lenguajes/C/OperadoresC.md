x = 5 (que en binario es 101)

Caso 1: Operaciones independientes (empezando siempre con \(x = 5\))
x = x & 3 (AND binario): El resultado es 1.
Compara bit a bit. Solo da 1 si ambos bits son 1.
101 (5) & 011 (3) = 001 (1).

x = x | 3 (OR binario): El resultado es 7.
Da 1 si al menos uno de los bits es 1.
101 (5) | 011 (3) = 111 (7).

x = x ^ 3 (XOR binario): El resultado es 6.
Da 1 si los bits son diferentes entre sí.
101 (5) ^ 011 (3) = 110 (6).

x = x >> 3 (Desplazamiento a la derecha): El resultado es 0.
Mueve los bits 3 posiciones a la derecha, descartando los que salen.
101 (5) desplazado resulta en 000 (0). Equivale a dividir \(5 / 2^3\).

x = x << 3 (Desplazamiento a la izquierda): El resultado es 40.
Mueve los bits 3 posiciones a la izquierda, rellenando con ceros.
101 (5) desplazado resulta en 101000 (40). Equivale a multiplicar \(5 \times 2^3\).