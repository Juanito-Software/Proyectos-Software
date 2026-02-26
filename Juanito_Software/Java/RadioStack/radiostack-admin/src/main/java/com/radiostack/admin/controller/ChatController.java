package com.radiostack.admin.controller;

import com.radiostack.admin.RadiostackAdminApp;
import com.radiostack.admin.client.StompClient;
import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Label;
import javafx.scene.control.ListView;
import javafx.scene.control.TextField;
import javafx.stage.Stage;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class ChatController {

    @FXML private TextField emisionIdField;
    @FXML private TextField aliasField;
    @FXML private TextField mensajeField;
    @FXML private ListView<String> mensajesList;
    @FXML private Label estadoLabel;

    private StompClient stompClient;
    private String token;
    private final ExecutorService executor = Executors.newSingleThreadExecutor(r -> {
        Thread t = new Thread(r, "stomp-client");
        t.setDaemon(true);
        return t;
    });

    public void setToken(String token) {
        this.token = token;
    }

    @FXML
    private void conectar() {
        String idStr = emisionIdField.getText();
        if (idStr == null || idStr.isBlank()) {
            estadoLabel.setText("Escribe el ID de la emisión.");
            return;
        }
        long emisionId;
        try {
            emisionId = Long.parseLong(idStr.trim());
        } catch (NumberFormatException e) {
            estadoLabel.setText("ID de emisión no válido.");
            return;
        }
        estadoLabel.setText("Conectando...");
        executor.submit(() -> {
            try {
                stompClient = StompClient.create(RadiostackAdminApp.getBaseUrl());
                final long emisionIdFinal = emisionId;
                stompClient.setOnConnected(() -> Platform.runLater(() -> {
                    estadoLabel.setText("Conectado a emisión " + emisionIdFinal);
                    stompClient.subscribe(emisionIdFinal);
                }));
                stompClient.setOnDisconnected(() -> Platform.runLater(() -> estadoLabel.setText("Desconectado")));
                stompClient.setOnMessage(msg -> Platform.runLater(() -> {
                    String line = "[" + (msg.timestamp != null ? msg.timestamp : "") + "] " + msg.alias + ": " + msg.contenido;
                    mensajesList.getItems().add(line);
                }));
                stompClient.connectBlocking();
            } catch (Exception e) {
                Platform.runLater(() -> estadoLabel.setText("Error: " + (e.getMessage() != null ? e.getMessage() : "conexión")));
            }
        });
    }

    @FXML
    private void desconectar() {
        if (stompClient != null) {
            stompClient.disconnectStomp();
            stompClient = null;
        }
        estadoLabel.setText("Desconectado");
    }

    @FXML
    private void enviar() {
        String idStr = emisionIdField.getText();
        if (idStr == null || idStr.isBlank()) {
            estadoLabel.setText("Indica ID de emisión y conecta primero.");
            return;
        }
        if (stompClient == null || !stompClient.isStompConnected()) {
            estadoLabel.setText("Conecta antes de enviar.");
            return;
        }
        long emisionId;
        try {
            emisionId = Long.parseLong(idStr.trim());
        } catch (NumberFormatException e) {
            return;
        }
        String alias = aliasField.getText();
        if (alias == null) alias = "Anónimo";
        String contenido = mensajeField.getText();
        if (contenido == null || contenido.isBlank()) return;
        stompClient.send(emisionId, alias, contenido);
        mensajeField.clear();
    }

    @FXML
    private void volver() {
        desconectar();
        try {
            Stage stage = (Stage) estadoLabel.getScene().getWindow();
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/fxml/dashboard.fxml"));
            Parent root = loader.load();
            DashboardController dashboard = loader.getController();
            dashboard.setToken(token);
            Scene scene = new Scene(root, 900, 560);
            scene.getStylesheets().add(getClass().getResource("/css/theme.css").toExternalForm());
            stage.setTitle("RadioStack Admin — Dashboard");
            stage.setScene(scene);
        } catch (Exception e) {
            estadoLabel.setText("Error al volver.");
        }
    }
}
