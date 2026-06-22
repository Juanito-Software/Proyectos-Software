package com.example.BatchProcessor.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;

@Controller

public class FileUploadController {

    @GetMapping("/upload_web_FileExplorer")
    @ResponseBody
    public String showUploadForm() {
        return """
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Subir archivo CSV</title>
                </head>
                <body>
                    <h1>Subir archivo CSV</h1>
                    <form method="POST" action="/batch/upload_file" enctype="multipart/form-data">
                        <label for="file">Selecciona un archivo CSV:</label>
                        <input type="file" id="file" name="file" accept=".csv" required />
                        <button type="submit">Subir archivo</button>
                    </form>
                </body>
                </html>
                """;
    }
}
