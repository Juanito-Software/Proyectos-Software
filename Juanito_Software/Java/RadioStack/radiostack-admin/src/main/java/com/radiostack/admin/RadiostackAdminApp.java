package com.radiostack.admin;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;

import java.io.IOException;
import java.net.URL;

public class RadiostackAdminApp extends Application {

    private static final String BASE_URL = "http://localhost:8080";

    public static String getBaseUrl() {
        return BASE_URL;
    }

    @Override
    public void start(Stage stage) throws IOException {
        URL fxml = getClass().getResource("/fxml/login.fxml");
        Parent root = FXMLLoader.load(fxml);
        Scene scene = new Scene(root, 420, 320);
        scene.getStylesheets().add(getClass().getResource("/css/theme.css").toExternalForm());
        stage.setTitle("RadioStack Admin");
        stage.setScene(scene);
        stage.setResizable(false);
        stage.show();
    }

    public static void main(String[] args) {
        launch(args);
    }
}
