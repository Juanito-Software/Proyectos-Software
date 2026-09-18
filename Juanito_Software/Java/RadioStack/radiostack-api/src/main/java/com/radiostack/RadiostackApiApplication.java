package com.radiostack;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Arranque de la API REST de RadioStack.
 *
 * La configuracion de JPA (entidades y repositorios) NO esta aqui: vive en
 * com.radiostack.persistence.config.JpaConfig, dentro del modulo de persistencia
 * que la posee. El escaneo de componentes de este @SpringBootApplication, cuyo
 * paquete base es com.radiostack, la descubre como a cualquier otro bean, y con
 * la misma regla vale para toda rodaja que quiera excluirla.
 */
@SpringBootApplication
public class RadiostackApiApplication {

    public static void main(String[] args) {
        SpringApplication.run(RadiostackApiApplication.class, args);
    }
}

