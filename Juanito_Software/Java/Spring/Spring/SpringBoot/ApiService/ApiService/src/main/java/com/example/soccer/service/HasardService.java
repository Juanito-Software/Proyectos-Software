package com.example.soccer.service;

import org.springframework.stereotype.Service;

import java.util.ArrayList;

@Service
public class HasardService {

    // Metodo auxiliar para calcular la suma de los dígitos de un número
    private int sumaDigitos(int n){
        int suma=0;
        // Ciclo que suma cada dígito del número
        while(n>0){
            suma+=n%10; // añadir el ultimo digito a la suma
            n /= 10; //Eliminar el ultimo digito
        }
        return suma; // Devolver la suma de los dígitos
    }

    // Verifica si n es un número Harshad (también llamado número Niven)
    // Un número es Harshad si es divisible por la suma de sus dígitos
    public boolean isValid(int n) {
        int sumDigitos = sumaDigitos(n);
        // Retorna true si n es divisible por la suma de sus dígitos y dicha suma no es 0
        return sumDigitos != 0 && n % sumDigitos == 0; // Verifica si n es divisible por la suma de sus dígitos
    }

    // Obtiene el siguiente número Harshad después de n
    public int getNext(int n){
        n++; // Incrementa n en 1
        // Sigue incrementando n hasta que se encuentre un número válido (Harshad)
        while(!isValid(n)){
            n++;
        }
        return n;// Devuelve el siguiente número Harshad
    }

    // Genera una serie de números Harshad, comenzando desde un número dado
    public ArrayList<Integer> getSerie(int start, int cantidad){
        ArrayList<Integer> serie = new ArrayList<>();// Lista para almacenar la serie
        int numero = start+1;// Inicia la búsqueda desde el siguiente número después de start

        // Añadir números Harshad a la lista hasta alcanzar la cantidad deseada
        while(serie.size()<cantidad){
            if(isValid(numero)){
                serie.add(numero);// Añadir a la serie si es un número Harshad
            }
            numero++;// Incrementa el número en 1
        }
        return serie;// Devuelve la serie completa
    }
    // Sobrecarga del metodo getSerie que genera una serie de números Harshad, comenzando desde 0
    public ArrayList<Integer> getSerie(int cantidad){
        return getSerie(0, cantidad);// Llama al metodo anterior con start = 0
    }
}
