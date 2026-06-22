package com.example.soccer.service;

import org.springframework.stereotype.Service;

import java.util.ArrayList;

@Service
public class PrimosService{
    // Metodo principal que recibe un número n
    public ArrayList<Integer> encontrarPrimosConSumandos(int n) {
        ArrayList<Integer> primos = generarPrimosMenoresQue(n); //genera un ArrayList con todos los numeros primos menores que el numero proporcionado;
        ArrayList<Integer> resultado = new ArrayList<>(); //crea un ArryList para guardar el resultado
        int maxLongitud = 0; //variable para almacenar la longitud máxima de las cadenas de sumandos consecutivos que suman al número primo (en el contexto global).

        for (int primo : primos) {//itera sobre el ArrayList de primos
            int longitud = encontrarCadenaMasLarga(primo);//variable para guardar la cadena mas larga de sumandos consecutivos que suman el numero primo (en el contexto de este primo que estamos iterando).
            if (longitud > maxLongitud) {//si la longitud de la cadena mas larga extraida para este primo es superior a la almacenada previamente
                maxLongitud = longitud;//toma su lugar
                resultado.clear(); // Limpiar el ArrayList anterior
                resultado.add(primo); // Agregar el nuevo primo con la cadena más larga
            } else if (longitud == maxLongitud) {
                resultado.add(primo); // Agregar también si tiene la misma longitud
            }
        }

        return resultado; // Devolver la lista de primos
    }

    // Metodo para generar números primos menores que n
    private ArrayList<Integer> generarPrimosMenoresQue(int n) {
        ArrayList<Integer> primos = new ArrayList<>();//crea un ArrayList para los numeros primos
        for (int i = 2; i < n; i++) {//itera desde 2 hasta el numero proporcionado
            if (esPrimo(i)) {
                primos.add(i);//si el numero es primo se añade a el ArrayList
            }
        }
        return primos;
    }

    // Verificar si un número es primo (mejorado)
    private boolean esPrimo(int n) {
        if (n <= 1) return false; // Los números menores o iguales a 1 no son primos
        if (n == 2) return true;  // El 2 es el único número par primo
        if (n % 2 == 0) return false; // Los números pares mayores que 2 no son primos
        for (int i = 3; i * i <= n; i += 2) {
            if (n % i == 0) {
                return false; // Si es divisible por cualquier número impar, no es primo
            }
        }
        return true; // Si no se encontró ningún divisor, es primo
    }

    // Metodo para encontrar la cadena más larga de sumandos consecutivos que suman al primo
    private int encontrarCadenaMasLarga(int primo) {
        int maxLongitud = 0;

        for (int inicio = 1; inicio < primo; inicio++) {//Bucle exterior (inicio): Explora todas las posibles posiciones desde donde puede comenzar una secuencia de sumandos consecutivos. Cada posición puede producir una secuencia diferente.
            int suma = 0;
            int longitud = 0;
            for (int fin = inicio; suma < primo; fin++) {//Bucle interior (fin): Extiende la secuencia de sumandos consecutivos para cada valor de inicio y verifica si la suma resultante es igual al número primo. Este bucle construye la secuencia actual y va sumando hasta encontrar una suma que sea igual o mayor al número primo.
                if (esPrimo(fin)) { // Verifica si el número actual es primo antes de sumarlo.
                    suma += fin;
                    longitud++; // Incrementa la longitud solo si el número es primo.
                    if (suma == primo) {//Verifica si la secuencia de números consecutivos suma exactamente al número primo.
                        maxLongitud = Math.max(maxLongitud, longitud);//Si se encuentra una secuencia que suma al número primo, calcula su longitud y actualiza la longitud máxima encontrada si la nueva secuencia es más larga que las anteriores.
                        break; // Rompe el bucle porque ya encontramos una secuencia que suma al primo.
                    }
                }

            }
        }
        return maxLongitud; // Devolver la longitud máxima encontrada
    }


    /**
     * // Metodo para generar números primos menores que n
     *     private static ArrayList<Integer> generarPrimosMenoresQue(int n) {
     *         ArrayList<Integer> primos = new ArrayList<>(); // crea un ArrayList para los numeros primos
     *         for (int i = 2; i < n; i++) { // itera desde 2 hasta el numero proporcionado
     *             if (esPrimo(i)) {
     *                 primos.add(i); // si el numero es primo se añade al ArrayList
     *             }
     *         }
     *         return primos;
     *     }
     *
     *     // Metodo para verificar si un número es primo
     *     private static boolean esPrimo(int num) {
     *         if (num <= 1) return false; // 0 y 1 no son primos
     *         for (int i = 2; i <= Math.sqrt(num); i++) { // verifica hasta la raíz cuadrada del número
     *             if (num % i == 0) return false; // si es divisible, no es primo
     *         }
     *         return true; // es primo
     *     }
     *
     *     // Metodo para encontrar los primos con la cadena más larga de sumandos consecutivos
     *     public ArrayList<Integer> encontrarPrimosConSumaConsecutiva(int n) {
     *         ArrayList<Integer> primos = generarPrimosMenoresQue(n);
     *         int maxLongitud = 0;
     *         ArrayList<Integer> resultado = new ArrayList<>();
     *
     *         for (int i = 0; i < primos.size(); i++) {
     *             for (int j = i; j < primos.size(); j++) {
     *                 int suma = 0;
     *                 for (int k = i; k <= j; k++) {
     *                     suma += primos.get(k);
     *                 }
     *
     *                 if (suma < n && esPrimo(suma)) {
     *                     int longitud = j - i + 1;
     *                     if (longitud > maxLongitud) {
     *                         maxLongitud = longitud;
     *                         resultado.clear();
     *                         resultado.add(suma);
     *                     } else if (longitud == maxLongitud) {
     *                         resultado.add(suma);
     *                     }
     *                 }
     *             }
     *         }
     *
     *         resultado.sort(Integer::compareTo);
     *         return resultado;
     *     }
     */

}
