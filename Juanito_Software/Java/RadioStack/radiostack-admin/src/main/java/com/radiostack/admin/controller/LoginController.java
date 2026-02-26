package com.radiostack.admin.controller;

import com.radiostack.admin.RadiostackAdminApp;
import com.radiostack.admin.client.ApiClient;
import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Label;
import javafx.scene.control.PasswordField;
import javafx.scene.control.TextField;
import javafx.stage.Stage;

import java.io.IOException;

public class LoginController {

    @FXML private TextField emailField;
    @FXML private PasswordField passwordField;
    @FXML private Label errorLabel;

    private final ApiClient apiClient = new ApiClient(RadiostackAdminApp.getBaseUrl());

    @FXML
    private void login() {
        String email = emailField.getText();
        String password = passwordField.getText();
        errorLabel.setText("");
        errorLabel.setVisible(false);
        errorLabel.setManaged(false);
        if (email == null || email.isBlank() || password == null || password.isBlank()) {
            errorLabel.setText("Introduce email y contraseña.");
            errorLabel.setVisible(true);
            errorLabel.setManaged(true);
            return;
        }
        new Thread(() -> {
            try {
                ApiClient.LoginResult result = apiClient.login(email, password);
                apiClient.setToken(result.token);
                Platform.runLater(() -> openDashboard(result.token));
            } catch (Exception e) {
                String msg = e.getMessage() != null && e.getMessage().contains("401") ? "Credenciales incorrectas." : e.getMessage();
                Platform.runLater(() -> {
                    errorLabel.setText(msg != null ? msg : "Error de conexión.");
                    errorLabel.setVisible(true);
                    errorLabel.setManaged(true);
                });
            }
        }).start();
    }

    private void openDashboard(String token) {
        try {
            Stage stage = (Stage) emailField.getScene().getWindow();
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/fxml/dashboard.fxml"));
            Parent root = loader.load();
            DashboardController dashboard = loader.getController();
            dashboard.setToken(token);
            Scene scene = new Scene(root, 900, 560);
            scene.getStylesheets().add(getClass().getResource("/css/theme.css").toExternalForm());
            stage.setTitle("RadioStack Admin — Dashboard");
            stage.setScene(scene);
            stage.setResizable(true);
        } catch (IOException e) {
            errorLabel.setText("No se pudo cargar el panel.");
        }
    }
}
