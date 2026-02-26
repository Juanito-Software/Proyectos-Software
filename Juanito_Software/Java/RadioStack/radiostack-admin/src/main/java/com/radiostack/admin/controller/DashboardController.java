package com.radiostack.admin.controller;

import com.radiostack.admin.RadiostackAdminApp;
import com.radiostack.admin.client.ApiClient;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Label;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;

import java.io.IOException;

public class DashboardController {

    @FXML private Label welcomeLabel;
    @FXML private VBox contentArea;

    private ApiClient apiClient;
    private String token;

    public void setToken(String token) {
        this.token = token;
        this.apiClient = new ApiClient(RadiostackAdminApp.getBaseUrl());
        this.apiClient.setToken(token);
        welcomeLabel.setText("Bienvenido a RadioStack Admin");
    }

    @FXML
    private void verParrilla() {
        welcomeLabel.setText("Parrilla semanal — (vista en construcción)");
    }

    @FXML
    private void verProgramas() {
        welcomeLabel.setText("Gestión de programas — (vista en construcción)");
    }

    @FXML
    private void abrirChat() {
        try {
            Stage stage = (Stage) welcomeLabel.getScene().getWindow();
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/fxml/chat.fxml"));
            Parent root = loader.load();
            ChatController chat = loader.getController();
            chat.setToken(token);
            Scene scene = new Scene(root, 700, 500);
            scene.getStylesheets().add(getClass().getResource("/css/theme.css").toExternalForm());
            stage.setTitle("RadioStack Admin — Chat en directo");
            stage.setScene(scene);
        } catch (IOException e) {
            welcomeLabel.setText("No se pudo abrir el chat.");
        }
    }

    @FXML
    private void cerrarSesion() {
        try {
            Stage stage = (Stage) welcomeLabel.getScene().getWindow();
            Parent root = FXMLLoader.load(getClass().getResource("/fxml/login.fxml"));
            Scene scene = new Scene(root, 420, 320);
            scene.getStylesheets().add(getClass().getResource("/css/theme.css").toExternalForm());
            stage.setTitle("RadioStack Admin");
            stage.setScene(scene);
            stage.setResizable(false);
        } catch (IOException e) {
            welcomeLabel.setText("Error al cerrar sesión.");
        }
    }
}
