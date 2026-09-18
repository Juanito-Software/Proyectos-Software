package com.radiostack.persistence.config;

import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

/**
 * Donde vive el conocimiento JPA del proyecto: las entidades y los repositorios
 * son de ESTE modulo, y esta clase se encarga de decirlo.
 *
 * Antes vivian como anotaciones directas en RadiostackApiApplication, la clase
 * de arranque del modulo API. Eso tenia dos costes:
 *
 *   - La API conocia los paquetes internos de otro modulo: si la persistencia
 *     reorganizara sus entidades o repositorios, el arranque tendria que
 *     enterarse y cambiar.
 *   - Las anotaciones puestas en la clase raiz son las unicas que @WebMvcTest
 *     no puede apagar: el contexto rodajado detecta @EntityScan y
 *     @EnableJpaRepositories en la configuracion raiz aunque la autoconfiguracion
 *     este desactivada, y los repositorios exigen un entityManagerFactory que en
 *     una rodaja web no existe. De ahi que SecurityConfigTest tenga su propia
 *     clase raiz de prueba.
 *
 * Como configuracion normal (bean escaneable), esta clase ya puede excluirse con
 * un filtro de @ComponentScan desde cualquier rodaja que no toque la base de
 * datos.
 *
 * La autoconfiguracion de Spring Boot por paquete base (com.radiostack) ya
 * hacia este trabajo por deduccion: cuanto las anotaciones estaban puestas, esa
 * autoconfiguracion quedaba desactivada a favor de ellas; quitadas, entra ella.
 * El resultado funcional no cambia —lo comprueba EsquemaYMigracionesTest— pero
 * el conocimiento pasa a estar donde pertenece.
 */
@Configuration
@EntityScan("com.radiostack.persistence.entity")
@EnableJpaRepositories("com.radiostack.persistence.repository.jpa")
public class JpaConfig {
}