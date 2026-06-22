package com.example.BatchProcessor.service;

import jakarta.annotation.PostConstruct;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class BatchTablesCreate {


    private final JdbcTemplate jdbcTemplate;

    public BatchTablesCreate(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @PostConstruct
    public void init() {
        createBatchJobTablesIfNotExists();
    }

    public void createBatchJobTablesIfNotExists() {
        try {
            System.out.println("Creando tablas si no existen...");

            // SQL para crear las tablas
            String[] CreateTableSql = {
                    "CREATE TABLE IF NOT EXISTS BATCH_JOB_INSTANCE (" +
                            "JOB_INSTANCE_ID BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY, " +
                            "VERSION BIGINT, " +
                            "JOB_NAME VARCHAR(100) NOT NULL, " +
                            "JOB_KEY VARCHAR(32) NOT NULL, " +
                            "CONSTRAINT JOB_INST_UN UNIQUE (JOB_NAME, JOB_KEY));",

                    "CREATE TABLE IF NOT EXISTS BATCH_JOB_EXECUTION (" +
                            "JOB_EXECUTION_ID BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY, " +
                            "VERSION BIGINT, " +
                            "JOB_INSTANCE_ID BIGINT NOT NULL, " +
                            "CREATE_TIME TIMESTAMP(6) NOT NULL, " +
                            "START_TIME TIMESTAMP(6) DEFAULT NULL, " +
                            "END_TIME TIMESTAMP(6) DEFAULT NULL, " +
                            "STATUS VARCHAR(10), " +
                            "EXIT_CODE VARCHAR(2500), " +
                            "EXIT_MESSAGE VARCHAR(2500), " +
                            "LAST_UPDATED TIMESTAMP(6), " +
                            "CONSTRAINT JOB_INST_EXEC_FK FOREIGN KEY (JOB_INSTANCE_ID) " +
                            "REFERENCES BATCH_JOB_INSTANCE(JOB_INSTANCE_ID));",

                    "CREATE TABLE IF NOT EXISTS BATCH_JOB_EXECUTION_PARAMS (" +
                            "JOB_EXECUTION_ID BIGINT NOT NULL, " +
                            "PARAMETER_NAME VARCHAR(100) NOT NULL, " +
                            "PARAMETER_TYPE VARCHAR(100) NOT NULL, " +
                            "PARAMETER_VALUE VARCHAR(2500), " +
                            "IDENTIFYING CHAR(1) NOT NULL, " +
                            "CONSTRAINT JOB_EXEC_PARAMS_FK FOREIGN KEY (JOB_EXECUTION_ID) " +
                            "REFERENCES BATCH_JOB_EXECUTION(JOB_EXECUTION_ID));",

                    "CREATE TABLE IF NOT EXISTS BATCH_STEP_EXECUTION (" +
                            "STEP_EXECUTION_ID BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY, " +
                            "VERSION BIGINT NOT NULL, " +
                            "STEP_NAME VARCHAR(100) NOT NULL, " +
                            "JOB_EXECUTION_ID BIGINT NOT NULL, " +
                            "CREATE_TIME TIMESTAMP(6) NOT NULL, " +
                            "START_TIME TIMESTAMP(6) DEFAULT NULL, " +
                            "END_TIME TIMESTAMP(6) DEFAULT NULL, " +
                            "STATUS VARCHAR(10), " +
                            "COMMIT_COUNT BIGINT, " +
                            "READ_COUNT BIGINT, " +
                            "FILTER_COUNT BIGINT, " +
                            "WRITE_COUNT BIGINT, " +
                            "READ_SKIP_COUNT BIGINT, " +
                            "WRITE_SKIP_COUNT BIGINT, " +
                            "PROCESS_SKIP_COUNT BIGINT, " +
                            "ROLLBACK_COUNT BIGINT, " +
                            "EXIT_CODE VARCHAR(2500), " +
                            "EXIT_MESSAGE VARCHAR(2500), " +
                            "LAST_UPDATED TIMESTAMP(6), " +
                            "CONSTRAINT JOB_EXEC_STEP_FK FOREIGN KEY (JOB_EXECUTION_ID) " +
                            "REFERENCES BATCH_JOB_EXECUTION(JOB_EXECUTION_ID));",

                    "CREATE TABLE IF NOT EXISTS BATCH_STEP_EXECUTION_CONTEXT (" +
                            "STEP_EXECUTION_ID BIGINT NOT NULL PRIMARY KEY, " +
                            "SHORT_CONTEXT VARCHAR(2500) NOT NULL, " +
                            "SERIALIZED_CONTEXT TEXT, " +
                            "CONSTRAINT STEP_EXEC_CTX_FK FOREIGN KEY (STEP_EXECUTION_ID) " +
                            "REFERENCES BATCH_STEP_EXECUTION(STEP_EXECUTION_ID));",

                    "CREATE TABLE IF NOT EXISTS BATCH_JOB_EXECUTION_CONTEXT (" +
                            "JOB_EXECUTION_ID BIGINT NOT NULL PRIMARY KEY, " +
                            "SHORT_CONTEXT VARCHAR(2500) NOT NULL, " +
                            "SERIALIZED_CONTEXT TEXT, " +
                            "CONSTRAINT JOB_EXEC_CTX_FK FOREIGN KEY (JOB_EXECUTION_ID) " +
                            "REFERENCES BATCH_JOB_EXECUTION(JOB_EXECUTION_ID));",

                    "CREATE TABLE IF NOT EXISTS BATCH_STEP_EXECUTION_SEQ (ID BIGINT NOT NULL) ENGINE=InnoDB; ",

                    "CREATE TABLE IF NOT EXISTS BATCH_JOB_EXECUTION_SEQ (ID BIGINT NOT NULL) ENGINE=InnoDB; ",

                    "CREATE TABLE IF NOT EXISTS BATCH_JOB_SEQ (ID BIGINT NOT NULL) ENGINE=InnoDB; "
            };

            // Ejecutar cada sentencia SQL
            for (String sql : CreateTableSql) {
                jdbcTemplate.update(sql);
            }

            // Sentencias SQL para insertar valores en las secuencias
            String[] insertSql = {
                    "INSERT INTO BATCH_STEP_EXECUTION_SEQ values(0);",
                    "INSERT INTO BATCH_JOB_EXECUTION_SEQ values(0);",
                    "INSERT INTO BATCH_JOB_SEQ values(0);"
            };

            // Ejecutar las sentencias de inserción
            jdbcTemplate.batchUpdate(insertSql);

            System.out.println("Tablas creadas o ya existentes.");
        } catch (Exception e) {
            System.err.println("Error al crear las tablas: " + e.getMessage());
        }
    }
}
