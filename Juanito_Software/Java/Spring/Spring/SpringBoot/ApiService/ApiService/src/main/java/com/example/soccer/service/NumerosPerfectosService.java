package com.example.soccer.service;

import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class NumerosPerfectosService {
    int sumaDivisors;

    // metodo para comprobar si un numero es perfecto
    public boolean isPerfect(int n) {
        List<Integer> divisores = getDivisors(n);// lista para almacenar los divisores de un numero
        sumaDivisors=0;
        for (int t = 0; t <= divisores.size()-1; t++) {// bucle para sumar todos los divisores de un numero
            sumaDivisors+=divisores.get(t);
        }
        if(n==sumaDivisors){// si la suma de los divisores de un numero es igual a ese numero, return true
            return true;
        }else{
            return false;
        }
    }

    // metodo que retorna una lista con todos los divisores de un numero
    public List<Integer> getDivisors(int n) {
        List<Integer> divisors = new ArrayList<>();// lista para almacenar los divisores de un numero
        for (int l = 1; l < n; l++) {// iteramos con l, desde 1 hasta el numero, de 1 en 1
            if (n % l == 0) {// si el resto de la dvision del numero entre l da 0 significa que es divisible
                divisors.add(l);
            }
        }
        return divisors;
    }

    //metodo que devuelve una lista de perfectos desde n hasta m (solo si n es perfecto), sino desde 0 hasta m
    public ArrayList<Integer> getPerfects(int n, int m) {
        ArrayList<Integer> perfects = new ArrayList<>();// lista para guardar los numeros perfectos
        if(isPerfect(n)){// si n es perfecto
            for(int k=n;k<m;k++){
                if (isPerfect(k)) {
                    perfects.add(k);
                }
            }
        }else{
            for(int k=1;k<m;k++){
                if (isPerfect(k)) {
                    perfects.add(k);
                }
            }
        }
        return perfects;
    }
}
