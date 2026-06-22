package com.example.soccer.service;

import org.springframework.stereotype.Service;

@Service
public class CaminandoService {

    // Metodo para calcular tiempo y el camino tomado
    public boolean CalcularTiempoyCamino(int minutos, String[] direcciones) {
        // Validación de minutos
        if (minutos <= 0) { // Validar que minutos sea mayor a 0
            throw new IllegalArgumentException("Los minutos deben ser mayores a cero.");
        }

        // Validación de direcciones
        if (direcciones == null || direcciones.length == 0) { // Comprobar si las direcciones son nulas o vacías
            throw new IllegalArgumentException("Las direcciones no pueden ser nulas o vacías.");
        }

        // Comprobar si el número de direcciones es distinto de los minutos
        if (direcciones.length != minutos) {
            return false; // No llegaremos a tiempo, devuelve false
        }

        int norteSur = 0; // Inicializamos las variables a 0
        int esteOeste = 0;

        for (String direccion : direcciones) { // Iteramos sobre el array de direcciones
            switch (direccion.toLowerCase()) { // Se espera en minúscula, así que se convierte para evitar errores
                // Dependiendo del caso se aumenta o disminuye las variables
                case "n":
                    norteSur++;
                    break;
                case "s":
                    norteSur--;
                    break;
                case "e":
                    esteOeste++;
                    break;
                case "w":
                    esteOeste--;
                    break;
                default:
                    return false; // Si se introduce una dirección inválida, devuelve false
            }
        }

        return norteSur == 0 && esteOeste == 0; // En el return se compara que las variables han vuelto al punto inicial, si es así, devuelve true
    }
}
