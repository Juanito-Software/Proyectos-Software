package com.example.soccer.service;

import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class NumerosAmigablesService {

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

    //metodo para obtener la suma de los divisores de un numero
    public int getSumDivisors(int n){
        List<Integer> sumDivisors = new ArrayList<>();  // lista para alamcenar los divisores del numero
        sumDivisors = getDivisors(n);
        int sum = 0;
        for(int i=0;i<sumDivisors.size();i++){//se itera desde 0, hasta el tamaño de la lista de divisores, de 1 en 1
            sum+=sumDivisors.get(i);// se van sumando los divisores en cada iteracion
        }
        return sum;
    }

    //metodo para comprobar si dos numeros son amigables entre si
    public boolean isFriendly(int a, int b) {
        int aSum;
        int bSum;
        aSum=getSumDivisors(a);//asignamos a la variable aSum el valor correspondiente a la suma de los divisores de a
        bSum=getSumDivisors(b);//asignamos a la variable bSum el valor correspondiente a la suma de los divisores de b
        // si a es igual la suma de los divisores de b o viceversa devuelve true
        if(a==bSum && b==aSum){
            return true;
        }else{
            return false;
        }
    }
}
