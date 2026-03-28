package com.example.tic_tac_toe_svoy_cod;

import java.net.URL;
import java.util.ResourceBundle;

import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.scene.control.Alert;
import javafx.scene.control.Button;
import javafx.scene.control.ButtonType;
import javafx.scene.layout.GridPane;

public class HelloController {

    @FXML
    private ResourceBundle resources;

    @FXML
    private URL location;

    private char currentPlayer = 'X';
    private final char[][] field = new char[3][3];
    private boolean gameActive = true;

    @FXML
    void buttonClick(ActionEvent event) {
        if (!gameActive) return;

        Button clickedButton = (Button) event.getSource();
        if (!clickedButton.getText().isEmpty()) return;

        Integer row = GridPane.getRowIndex(clickedButton);
        Integer col = GridPane.getColumnIndex(clickedButton);
        int rowIdx = (row == null) ? 0 : row;
        int colIdx = (col == null) ? 0 : col;

        field[rowIdx][colIdx] = currentPlayer;
        clickedButton.setText(String.valueOf(currentPlayer));

        if (checkWin(currentPlayer)) {
            gameActive = false;
            showAlert("Победитель", "Игрок " + currentPlayer + " выиграл!");
            return;
        }

        if (isDraw()) {
            gameActive = false;
            showAlert("Ничья", "Игра окончена вничью!");
            return;
        }

        currentPlayer = (currentPlayer == 'X') ? 'O' : 'X';
    }

    private boolean checkWin(char player) {
        for (int i = 0; i < 3; i++) {
            if (field[i][0] == player && field[i][1] == player && field[i][2] == player) return true;
            if (field[0][i] == player && field[1][i] == player && field[2][i] == player) return true;
        }
        if (field[0][0] == player && field[1][1] == player && field[2][2] == player) return true;
        if (field[0][2] == player && field[1][1] == player && field[2][0] == player) return true;
        return false;
    }

    private boolean isDraw() {
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                if (field[i][j] == '\0') return false;
            }
        }
        return true;
    }

    private void showAlert(String title, String message) {
        Alert alert = new Alert(Alert.AlertType.INFORMATION, message, ButtonType.OK);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.showAndWait();
    }

    @FXML
    void initialize() {
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                field[i][j] = '\0';
            }
        }
        gameActive = true;
        currentPlayer = 'X';
    }

}
