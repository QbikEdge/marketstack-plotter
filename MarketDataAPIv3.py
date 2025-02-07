#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dieses Programm lädt Finanzdaten entweder über die Marketstack-API oder aus einer lokalen JSON-Datei.
Es bietet zwei Plotbereiche:
- Standard-Plot: Zeigt per Voreinstellung den Verlauf von 'date' gegen 'close'.
- Benutzerdefinierter Plot: Hier kann der Benutzer aus den geladenen Daten die x- und y-Achse wählen
  und zusätzlich über zahlreiche Einstellmöglichkeiten den Plot anpassen.

Weitere Funktionen:
- Eine Dropdown-Liste mit den 30 gängigsten Aktien-Symbolen sowie ein Textfeld für benutzerdefinierte Symbole.
- Zusätzliche Plot-Einstellungen: Titel, Achsen-Beschriftungen, Diagrammtyp, Farbe, Legende und Colorbar.
- Menü- und ToolBar-Elemente sowie Funktionen zum Speichern des Plots und der Daten.
- Speicherung der Daten als JSON oder CSV.

Installation via pip:
    pip install PySide6 matplotlib qdarkstyle pandas requests
"""

import datetime
import json
import os
import sys
import warnings

import pandas as pd
import qdarkstyle
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QFileDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QComboBox, QSplitter, QLineEdit, QGroupBox, QCheckBox, QMenu, QMenuBar, QToolBar,
                               QFrame, QColorDialog, QStatusBar, QSizePolicy, QSpacerItem)

from DataManager import DataManager
from PlotCanvas import PlotCanvas

warnings.filterwarnings("ignore", message="Selected binding 'pyqt5' could not be found")


class MainWindow(QMainWindow):
    """
    Hauptfenster der Anwendung.
    """

    def __init__(self):
        super().__init__()
        self.status_timeout = 5000
        self.setWindowTitle("Modern Data Plotter")
        self.data_manager = DataManager()
        self.common_symbols = [
            "AAPL", "MSFT", "AMZN", "GOOGL", "FB", "TSLA", "BRK.B", "JNJ", "V", "WMT",
            "JPM", "NVDA", "PG", "MA", "HD", "UNH", "DIS", "BAC", "VZ", "ADBE",
            "NFLX", "CMCSA", "INTC", "T", "PFE", "KO", "MRK", "PEP", "ABT", "CSCO"
        ]
        self.init_ui()
        self.create_menu()

    def init_ui(self):
        """Initialisiert die Benutzeroberfläche und deren Komponenten."""
        # Zentrales Widget und Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # ToolBar-Bereich (oben)
        tool_bar_layout = QHBoxLayout()

        # Erstelle das Text-Label
        aktien_label = QLabel("Aktien Symbol:")
        tool_bar_layout.addWidget(aktien_label)

        # Dropdown für die Aktien-Symbole
        self.combo_symbols = QComboBox()
        self.combo_symbols.addItems(self.common_symbols)
        self.combo_symbols.setFixedWidth(80)
        tool_bar_layout.addWidget(self.combo_symbols)

        # Textfeld für ein eigenes Symbol
        own_symbol_label = QLabel("Oder eigenes Symbol:")
        tool_bar_layout.addWidget(own_symbol_label)
        self.lineedit_symbol = QLineEdit(placeholderText="z. B. IBM")
        tool_bar_layout.addWidget(self.lineedit_symbol)

        # API und Datei Laden Buttons mit Icons
        self.btn_load_api = QPushButton("Daten von API laden")
        self.btn_load_api.setIcon(QIcon.fromTheme("edit-find"))
        self.btn_load_api.clicked.connect(self.load_data_api)
        tool_bar_layout.addWidget(self.btn_load_api)

        self.btn_load_file = QPushButton("Daten aus Datei laden")
        self.btn_load_file.setIcon(QIcon.fromTheme("document-open"))
        self.btn_load_file.clicked.connect(self.load_data_file)
        tool_bar_layout.addWidget(self.btn_load_file)

        main_layout.addLayout(tool_bar_layout)

        # GroupBox für Plot-Einstellungen
        settings_group = QGroupBox("Plot Einstellungen")
        settings_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        settings_layout = QVBoxLayout()
        settings_group.setLayout(settings_layout)

        # Plot Titel, x- und y-Achsentitel
        titel_layout = QHBoxLayout()
        self.lineedit_title = QLineEdit()
        self.lineedit_title.setPlaceholderText("Plot Titel")
        titel_layout.addWidget(QLabel("Titel:"))
        titel_layout.addWidget(self.lineedit_title)
        settings_layout.addLayout(titel_layout)

        # UI-Komponenten für den benutzerdefinierten Plot (Achsen-Auswahl)
        ax_selection_layout = QHBoxLayout()

        ax_selection_layout.addWidget(QLabel("X-Achse auswählen:"))
        self.combo_x = QComboBox()
        ax_selection_layout.addWidget(self.combo_x)

        ax_selection_layout.addWidget(QLabel("Y-Achse auswählen:"))
        self.combo_y = QComboBox()
        ax_selection_layout.addWidget(self.combo_y)

        settings_layout.addLayout(ax_selection_layout)

        ax_titel_layout = QHBoxLayout()

        self.lineedit_xlabel = QLineEdit()
        self.lineedit_xlabel.setPlaceholderText("x-Achsentitel")
        ax_titel_layout.addWidget(QLabel("x-Achse:"))
        ax_titel_layout.addWidget(self.lineedit_xlabel)

        self.lineedit_ylabel = QLineEdit()
        self.lineedit_ylabel.setPlaceholderText("y-Achsentitel")
        ax_titel_layout.addWidget(QLabel("y-Achse:"))
        ax_titel_layout.addWidget(self.lineedit_ylabel)
        settings_layout.addLayout(ax_titel_layout)

        diagramm_settings_layout = QHBoxLayout()

        # Diagrammtyp
        self.combo_diagram_typ = QComboBox()
        self.combo_diagram_typ.addItems(["Linie", "Scatter", "Bar"])
        diagramm_settings_layout.addWidget(QLabel("Diagrammtyp:"))
        diagramm_settings_layout.addWidget(self.combo_diagram_typ)

        # Farbauswahl-Button
        def pick_color():
            self.selected_color = QColorDialog.getColor()
            if self.selected_color.isValid():
                color_indicator_frame.setStyleSheet(
                    f"background-color: {self.selected_color.name()}; border: 1px solid #000;")

        diagramm_settings_layout.addWidget(QLabel("Farbe auswählen:"))
        self.color_button = QPushButton()
        self.color_button.clicked.connect(pick_color)
        self.color_button.setIcon(QIcon.fromTheme("color-picker"))
        self.color_button.setFixedWidth(20)

        # Farbindikator: Quadrat mit Standardfarbe
        color_indicator_frame = QFrame(self.color_button)
        color_indicator_frame.setFixedSize(20, 20)
        color_indicator_frame.setStyleSheet("background-color: #ffffff; border: 1px solid #000;")

        color_button_layout = QHBoxLayout(self.color_button)
        color_button_layout.setContentsMargins(0, 0, 0, 0)
        color_button_layout.addWidget(color_indicator_frame, alignment=Qt.AlignCenter)

        self.color_button.setLayout(color_button_layout)
        diagramm_settings_layout.addWidget(self.color_button)

        # Checkboxen für Legende und Colorbar
        self.check_legend = QCheckBox("Legende")
        diagramm_settings_layout.addWidget(self.check_legend)

        self.legend_title = QLineEdit()
        self.legend_title.setPlaceholderText("Titel")
        diagramm_settings_layout.addWidget(QLabel("Legenden Titel:"))
        diagramm_settings_layout.addWidget(self.legend_title)

        self.legend_text = QLineEdit()
        self.legend_text.setPlaceholderText("Beschreibung")
        diagramm_settings_layout.addWidget(QLabel("Legenden Text:"))
        diagramm_settings_layout.addWidget(self.legend_text)

        self.check_colorbar = QCheckBox("Colorbar")
        # diagramm_settings_layout.addWidget(self.check_colorbar)

        diagramm_settings_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Button, um den Custom Plot mit den Einstellungen zu aktualisieren (mit Icon)
        self.btn_plot_custom = QPushButton("Custom Plot aktualisieren")
        self.btn_plot_custom.setIcon(QIcon.fromTheme("view-refresh"))
        self.btn_plot_custom.clicked.connect(self.update_custom_plot)
        diagramm_settings_layout.addWidget(self.btn_plot_custom)

        settings_layout.addLayout(diagramm_settings_layout)

        main_layout.addWidget(settings_group)

        # Splitter für zwei Plot-Bereiche: Standard und Custom
        splitter = QSplitter(Qt.Horizontal)

        # Standard Plot (Date vs Close)
        self.standard_plot = PlotCanvas(self, width=5, height=4)
        std_plot_container = QWidget()
        std_layout = QVBoxLayout(std_plot_container)
        std_layout.addWidget(QLabel("Standard Plot (Date vs. Close)"))
        std_layout.addWidget(self.standard_plot)
        splitter.addWidget(std_plot_container)

        # Custom Plot
        self.custom_plot = PlotCanvas(self, width=5, height=4)
        custom_plot_container = QWidget()
        custom_layout = QVBoxLayout(custom_plot_container)
        custom_layout.addWidget(QLabel("Benutzerdefinierter Plot"))
        custom_layout.addWidget(self.custom_plot)
        splitter.addWidget(custom_plot_container)

        main_layout.addWidget(splitter)
        self.resize(1300, 700)

    def create_menu(self):
        """Erstellt das Menü und die zugehörigen Aktionen."""
        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)

        # Datei Menü
        file_menu = QMenu("Datei", self)
        menu_bar.addMenu(file_menu)

        # Aktionen mit Icons
        save_plot_act = QAction(QIcon("icons/picture-filled-svgrepo-com.svg"), "Plot als Bild speichern", self)
        save_plot_act.triggered.connect(self.save_plot_image)
        save_plot_act.setShortcut("Ctrl+S")
        file_menu.addAction(save_plot_act)

        save_json_act = QAction(QIcon("icons/json-file-svgrepo-com.svg"), "Daten als JSON speichern", self)
        save_json_act.triggered.connect(self.save_data_json)
        save_json_act.setShortcut("Ctrl+J")
        file_menu.addAction(save_json_act)

        save_csv_act = QAction(QIcon("icons/csv-svgrepo-com.svg"), "Daten als CSV speichern", self)
        save_csv_act.triggered.connect(self.save_data_csv)
        save_csv_act.setShortcut("Ctrl+C")
        file_menu.addAction(save_csv_act)

        file_menu.addSeparator()
        exit_act = QAction(QIcon.fromTheme("application-exit"), "Beenden", self)
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

        # Toolbar und Statusleiste
        tool_bar = QToolBar("Hauptwerkzeuge")
        tool_bar.setIconSize(QSize(30, 30))
        tool_bar.setMovable(False)
        tool_bar.setLayoutDirection(Qt.RightToLeft)

        # Statusbar erstellen
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("color: #15ff00; font-weight: bold;")
        self.status_bar.showMessage("Bereit", self.status_timeout)
        self.setStatusBar(self.status_bar)

        self.addToolBar(Qt.BottomToolBarArea, tool_bar)

        tool_bar.addAction(save_plot_act)
        tool_bar.addAction(save_json_act)
        tool_bar.addAction(save_csv_act)
        tool_bar.addWidget(self.status_bar)

    def update_status(self, status: str, message: str, timeout: int = 5000):
        if status == "error":
            self.status_bar.setStyleSheet("color: #ff1500; font-weight: bold;")
        elif status == "success":
            self.status_bar.setStyleSheet("color: lime; font-weight: bold;")
        elif status == "info":
            self.status_bar.setStyleSheet("color: cyan; font-weight: bold;")
        elif status == "warning":
            self.status_bar.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.status_bar.setStyleSheet(f"color: {status}; font-weight: bold;")
        self.status_bar.showMessage(message, timeout)

    def load_data_api(self):
        """Lädt Daten aus der API und aktualisiert die UI-Komponenten."""
        access_key = os.getenv("API_KEY")  # Ersetze diesen Platzhalter mit deinem API-Schlüssel.

        # Bestimme das zu ladende Symbol: Wird im Textfeld etwas eingegeben, so hat dies Vorrang.
        symbol = self.lineedit_symbol.text().strip().upper()
        if not symbol:
            symbol = self.combo_symbols.currentText()

        # Optionale API-Parameter
        params = {"sort": "DESC", "limit": 100, "offset": 0}
        if self.data_manager.load_from_api(access_key, symbol, **params):
            self.populate_combos()
            self.plot_standard()
            self.update_status("success", f"{symbol} wurde erfolgreich geladen.")
        else:
            self.update_status("error", "Fehler beim Laden der API-Daten.")

    def load_data_file(self):
        """Öffnet einen Dateidialog, um eine JSON-Datei auszuwählen, und lädt die Daten."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Datei auswählen", "", "JSON Files (*.json);;CSV Files (*.csv)"
        )

        if file_path:
            try:
                if self.data_manager.load_from_file(file_path):
                    self.update_status("info", "Daten wurden erfolgreich geladen.")
                    self.populate_combos()
                    self.plot_standard()
                else:
                    self.update_status("error", "Fehler beim Laden der Datei.")
            except Exception as e:
                self.update_status("error", f"Fehler beim Laden der Datei: {e}")

    def populate_combos(self):
        """Füllt die Combo-Boxen mit den verfügbaren Keys aus den Daten."""
        keys = self.data_manager.get_available_keys()
        self.combo_x.clear()
        self.combo_y.clear()
        for key in keys:
            self.combo_x.addItem(key)
            self.combo_y.addItem(key)

    def plot_standard(self):
        """Erstellt den Standardplot: 'date' vs. 'close'."""
        dates, close_values = [], []
        if self.data_manager.data and isinstance(self.data_manager.data, list):
            dates = self.data_manager.get_column_data("date")
            close_values = self.data_manager.get_column_data("close") if self.data_manager.data else []
        if not dates or not close_values:
            self.update_status(
                "error",
                "Die Standard-Daten (date und close) sind nicht verfügbar. Daher kann kein Plot erstellt werden."
            )
            return
        try:
            x_data = [datetime.datetime.fromisoformat(d) if isinstance(d, str) else d for d in dates]
        except Exception as e:
            self.update_status("error", f"Fehler beim Konvertieren der Datumswerte: {e}")
            return

        # Standardplot: ohne weitere Anpassungen
        self.standard_plot.plot(
            x_data, close_values,
            title=f"{self.data_manager.data[0]['symbol']}  Date vs. Close",
            x_label="Date", y_label="Close",
            diagram_typ="Linie", color="lime" if self.is_growing(close_values) else "crimson", legend=False,
            colorbar=False)

        self.update_status("success", "Standard Plot wurde erfolgreich aktualisiert.")

    @staticmethod
    def is_growing(y: []) -> bool:
        """
        Überprüft, ob die Daten wachsen.

        :param y: Liste der y-Achsendaten.
        """
        return True if y[-1] < y[0] else False

    def update_custom_plot(self):
        """
        Aktualisiert den benutzerdefinierten Plot basierend auf den vom Benutzer gewählten Achsen und Einstellungen.
        """
        key_x = self.combo_x.currentText()
        key_y = self.combo_y.currentText()
        if not key_x or not key_y:
            self.update_status("warning", "Bitte wählen Sie beide Achsen aus.")
            return

        x_raw = self.data_manager.get_column_data(key_x)
        y_raw = self.data_manager.get_column_data(key_y)

        if not x_raw or not y_raw:
            self.update_status("warning", "Die ausgewählten Schlüssel sind nicht in den Daten vorhanden.")
            return

        # Versuche, die Daten zu konvertieren
        x_data = []
        for x in x_raw:
            if isinstance(x, str):
                try:
                    x_data.append(datetime.datetime.fromisoformat(x))
                    continue
                except Exception:
                    self.update_status("warning", f"Die Daten für {key_x} sind nicht plottbar.")
                    pass
            try:
                x_data.append(float(x))
            except Exception:
                self.update_status("warning", f"Die Daten für {key_x} sind nicht plottbar.")
                return

        y_data = []
        for y in y_raw:
            try:
                y_data.append(float(y))
            except Exception:
                self.update_status("warning", f"Die Daten für {key_y} sind nicht plottbar.")
                return

        # Lese weitere Plot-Einstellungen aus der UI
        title = self.lineedit_title.text().strip() if self.lineedit_title.text().strip() else f"{self.data_manager.data[0]['symbol']} {key_x} vs. {key_y}"

        # Aktualisiere den Custom Plot
        self.custom_plot.plot(
            x_data, y_data,
            title=title,
            x_label=self.lineedit_xlabel.text().strip() if self.lineedit_xlabel.text().strip() else key_x,
            y_label=self.lineedit_ylabel.text().strip() if self.lineedit_ylabel.text().strip() else key_y,
            diagram_typ=self.combo_diagram_typ.currentText(),
            color=self.selected_color.name() if hasattr(self, "selected_color") else "lime",
            legend=self.check_legend.isChecked(),
            legend_title=self.legend_title.text().strip() if self.check_legend.isChecked() else None,
            legend_text=self.legend_text.text().strip() if self.check_legend.isChecked() else None,
            colorbar=self.check_colorbar.isChecked()
        )

        self.update_status("success", f"Benutzerdefinierter Plot {title} wurde erfolgreich aktualisiert.")

    def save_plot_image(self):
        """Speichert den aktuell angezeigten Custom Plot als Bild."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Plot speichern",
            f"./Exports/{datetime.datetime.now().date()}_{self.data_manager.data[0]['symbol'] if self.data_manager.data else ''}_plot" if not self.lineedit_title.text().strip() else self.lineedit_title.text().strip(),
            "PNG Files (*.png);;JPEG Files (*.jpg)")
        if file_path:
            try:
                self.custom_plot.fig.savefig(file_path)
                self.update_status("success", "Plot wurde erfolgreich gespeichert.")
            except Exception as e:
                self.update_status("error", f"Fehler beim Speichern des Plots: {e}")

    def save_data_json(self):
        """Speichert die geladenen Daten als JSON-Datei."""
        if not self.data_manager.data:
            self.update_status("warning", "Keine Daten zum Speichern vorhanden.")
            return

        # Wenn der Export Ordner nicht existiert, wird er erstellt
        if not os.path.exists("./Exports/"):
            os.makedirs("./Exports/")

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Daten als JSON speichern",
            f"./Exports/{self.data_manager.data[0]['symbol']}_{self}_data.json" if not self.lineedit_title.text().strip() else self.lineedit_title.text().strip(),
            "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(self.data_manager.data, file, ensure_ascii=False, indent=4)
                self.update_status("success", "Daten wurden erfolgreich gespeichert.")
            except Exception as e:
                self.update_status("error", f"Fehler beim Speichern der Daten: {e}")

    def save_data_csv(self):
        """Speichert die geladenen Daten als CSV-Datei."""
        if not self.data_manager.data:
            self.update_status("warning", "Keine Daten zum Speichern vorhanden.")
            return

        # Wenn der Export Ordner nicht existiert, wird er erstellt
        if not os.path.exists("./Exports/"):
            os.makedirs("./Exports/")

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Daten als CSV speichern",
            f"./Exports/{self.data_manager.data[0]['symbol']}_{self}_data.csv" if not self.lineedit_title.text().strip() else self.lineedit_title.text().strip(),
            "CSV Files (*.csv)")
        if file_path:
            try:
                df = pd.DataFrame(self.data_manager.data)
                df.to_csv(file_path, index=False)
                self.update_status("success", "Daten wurden erfolgreich gespeichert.")
            except Exception as e:
                self.update_status("error", f"Fehler beim Speichern der Daten: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
