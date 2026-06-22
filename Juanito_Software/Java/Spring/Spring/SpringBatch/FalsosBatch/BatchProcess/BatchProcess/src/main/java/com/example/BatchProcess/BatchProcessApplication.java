package com.example.BatchProcess;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

@SpringBootApplication
@EnableJpaRepositories(basePackages = "com.example.soccer.repository")
public class BatchProcessApplication {

	public static void main(String[] args) {
		SpringApplication.run(BatchProcessApplication.class, args);
	}

}


