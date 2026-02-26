package com.radiostack;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

@SpringBootApplication
@EntityScan("com.radiostack.persistence.entity")
@EnableJpaRepositories("com.radiostack.persistence.repository.jpa")
public class RadiostackApiApplication {

    public static void main(String[] args) {
        SpringApplication.run(RadiostackApiApplication.class, args);
    }
}

