package com.example.soccer.service;

import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class LenguajeAmistosoService {

        // Constantes para los segundos en cada unidad de tiempo
        private static final int SECONDS_IN_A_MINUTE = 60;
        private static final int SECONDS_IN_AN_HOUR = 60^2;
        private static final int SECONDS_IN_A_DAY = 60^2*24;
        private static final int SECONDS_IN_A_YEAR = 60^2*24*365; // 365 días

        public String formatDuration(int seconds) {
            if (seconds == 0) {
                return "ahora"; // Si es 0, devolver "ahora"
            }

            // Calcular los valores de cada unidad de tiempo respetando el orden de mayor a menor
            int years = seconds / SECONDS_IN_A_YEAR; //se dividen los segundos por la cantidad de segundos que hay en un año
            seconds %= SECONDS_IN_A_YEAR; //se dividen de nuevo para asignar el resto a la variable "seconds"

            int days = seconds / SECONDS_IN_A_DAY;
            seconds %= SECONDS_IN_A_DAY;

            int hours = seconds / SECONDS_IN_AN_HOUR;
            seconds %= SECONDS_IN_AN_HOUR;

            int minutes = seconds / SECONDS_IN_A_MINUTE;
            seconds %= SECONDS_IN_A_MINUTE;

            // Crear una lista para almacenar los componentes de la duracion
            List<String> components = new ArrayList();

            // Añadir los componentes que no hayan quedado vacios
            if (years > 0) {
                components.add(formatUnit(years, "año"));// formatear los años si es que ha habido
            }
            if (days > 0) {
                components.add(formatUnit(days, "día"));
            }
            if (hours > 0) {
                components.add(formatUnit(hours, "hora"));
            }
            if (minutes > 0) {
                components.add(formatUnit(minutes, "minuto"));
            }
            if (seconds > 0) {
                components.add(formatUnit(seconds, "segundo"));
            }

            // Formatear la lista de componentes en una cadena
            return joinComponents(components);
        }

        // Metodo auxiliar para formatear la unidad con singular/plural según corresponda
        private static String formatUnit(int value, String unit) {
            return value + " " + (value > 1 ? unit + "s" : unit); //se retorna el valor coorespondiente, un espacio y luego se compara: si el valor es mayor que 1 se le añade una "s" a la unidad
        }

        // Metodo auxiliar para unir los componentes con ", " y " y " antes del último
        private static String joinComponents(List<String> components) {
            if (components.size() == 1) {//si la lista de componentes es igual a 1, este componente se devuelve
                return components.get(0);
            }

            String lastComponent = components.remove(components.size() - 1);//se asigna a "lastComponent" y a la vez se elimina el ultimo componente de la lista
            return String.join(", ", components) + " y " + lastComponent;//se devuelven los componentes separados por "," y se añade "y" antes del ultimo
        }
}