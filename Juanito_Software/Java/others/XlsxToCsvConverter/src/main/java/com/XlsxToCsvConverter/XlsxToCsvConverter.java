package com.XlsxToCsvConverter;

import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

import java.io.*;

public class XlsxToCsvConverter {

    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("Uso: java XlsxToCsvConverter <ruta-del-archivo-xlsx> <ruta-del-archivo-csv>");
            return;
        }

        String xlsxFilePath = args[0];
        String csvFilePath = args[1];

        try {
            convertXlsxToCsv(xlsxFilePath, csvFilePath);
            System.out.println("Archivo convertido exitosamente: " + csvFilePath);
        } catch (IOException e) {
            System.err.println("Error al convertir el archivo: " + e.getMessage());
        }
    }

    public static void convertXlsxToCsv(String xlsxFilePath, String csvFilePath) throws IOException {
        try (FileInputStream fis = new FileInputStream(new File(xlsxFilePath));
             Workbook workbook = new XSSFWorkbook(fis);
             PrintWriter writer = new PrintWriter(new File(csvFilePath))) {

            Sheet sheet = workbook.getSheetAt(0); // Usamos la primera hoja del Excel

            for (Row row : sheet) {
                StringBuilder rowBuilder = new StringBuilder();

                for (Cell cell : row) {
                    switch (cell.getCellType()) {
                        case STRING:
                            rowBuilder.append(cell.getStringCellValue());
                            break;
                        case NUMERIC:
                            if (DateUtil.isCellDateFormatted(cell)) {
                                rowBuilder.append(cell.getDateCellValue());
                            } else {
                                rowBuilder.append(cell.getNumericCellValue());
                            }
                            break;
                        case BOOLEAN:
                            rowBuilder.append(cell.getBooleanCellValue());
                            break;
                        case FORMULA:
                            rowBuilder.append(cell.getCellFormula());
                            break;
                        case BLANK:
                            rowBuilder.append("");
                            break;
                        default:
                            rowBuilder.append("");
                            break;
                    }
                    rowBuilder.append(","); // Separador CSV
                }

                // Eliminamos el último separador y escribimos la línea
                if (rowBuilder.length() > 0) {
                    rowBuilder.setLength(rowBuilder.length() - 1);
                }
                writer.println(rowBuilder);
            }
        }
    }
}

