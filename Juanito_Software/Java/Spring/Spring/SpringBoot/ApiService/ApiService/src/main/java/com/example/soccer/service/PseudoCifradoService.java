package com.example.soccer.service;
import org.springframework.stereotype.Service;


@Service // Anotación que indica que esta clase es un servicio de Spring
public class PseudoCifradoService {

    public String encrypt(String cadenaEncriptar, int numeroEncriptaciones) {
        if (cadenaEncriptar == null || cadenaEncriptar == "" || numeroEncriptaciones <= 0) {// si la cadena de texto esta vacia o el numero de veces a encriptar es menor de 0
            return "la cadena esta vacia o el numero de Encriptaciones es menor o igual que 0";
        }

        for (int l = 0; l < numeroEncriptaciones; l++) {//iteramos por el numero de de veces a encriptar
            String pares = "";
            String impares = "";

            // Recorre la cadena y separa en pares e impares
            for (int i = 0; i < cadenaEncriptar.length(); i++) {//iteramos por el tamaño de la cadena
                char caracter = cadenaEncriptar.charAt(i);// se almacena en una variable el caracter correspondiente al indice, en el cual estamos iterando
                if (esPar(i)) {// si el indice es par
                    pares += caracter; // almacena el caracter en pares
                } else {
                    impares += caracter; // almacena el caracter en impares
                }
            }

            // Combina los pares e impares y reasigna a S
            cadenaEncriptar = pares + impares;
        }

        return cadenaEncriptar;
    }

    public String decrypted(String cadenaDesencriptar, int Desencriptaciones) {
        if (cadenaDesencriptar == null || cadenaDesencriptar == ""  || Desencriptaciones <= 0) {// si la cadena de texto esta vacia o el numero de veces a encriptar es menor de 0
            return "la cadena esta vacia o el numero de Encriptaciones es menor o igual que 0";
        }

        for (int l = 0; l < Desencriptaciones; l++) {//iteramos por el numero de de veces a desencriptar
            int mitad = cadenaDesencriptar.length() / 2;  // Encuentra el punto medio
            String pares = cadenaDesencriptar.substring(0, mitad); // Los primeros caracteres hasta la mitad son los pares
            String impares = cadenaDesencriptar.substring(mitad);  // Los últimos caracteres desde la mitad son los impares
            StringBuilder resultado = new StringBuilder();

            // Combina los caracteres de las mitades
            for (int i = 0; i < mitad; i++) {//iteramos hasta la mitad de la cadena de texto(pares)
                resultado.append(pares.charAt(i)); // Añadir el par a un nuevo String
                if (i < impares.length()) {// si la iteracion es menor al numero de impares
                    resultado.append(impares.charAt(i)); // Añadir el impar al nuevo String
                }
            }

            // Si la longitud de la cadena es impar, añadir el último caracter par
            if (cadenaDesencriptar.length() % 2 != 0) {
                resultado.append(impares.charAt(impares.length() - 1));
            }

            cadenaDesencriptar = resultado.toString(); // Actualiza cadenaDesencriptar con la nueva cadena reconstruida
        }

        return cadenaDesencriptar;
    }


    public boolean esPar(int num){//metodo para comprobar si un numero es par
        return (num % 2 == 0);
    }
}
