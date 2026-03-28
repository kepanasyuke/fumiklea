module com.example.tic_tac_toe_svoy_cod {
    requires javafx.controls;
    requires javafx.fxml;
    requires javafx.web;

    requires org.controlsfx.controls;
    requires com.dlsc.formsfx;
    requires validatorfx;
    requires org.kordamp.ikonli.javafx;
    requires org.kordamp.bootstrapfx.core;
    requires eu.hansolo.tilesfx;
    requires com.almasb.fxgl.all;

    opens com.example.tic_tac_toe_svoy_cod to javafx.fxml;
    exports com.example.tic_tac_toe_svoy_cod;
}