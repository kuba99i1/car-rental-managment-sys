from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, \
     QLineEdit, QPushButton, QComboBox, QMainWindow, QTableWidget, QTableWidgetItem, \
    QDialog, QVBoxLayout
from PyQt6.QtGui import QAction
import sqlite3
import sys
from brands_models import brands_models


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Car Rental Management System")

        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        add_car_action = QAction("Add car", self)
        add_car_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_car_action)
        
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.setMenuRole(QAction.MenuRole.NoRole)

        search_action = QAction("Search",self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "id_samochodu", "marka", "model", "rocznik",
            "cena_za_dobe", "dostepny"])
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

    def load_data(self):
        connection = sqlite3.connect("wypozyczalnia.sqlite")
        result = connection.execute("SELECT * FROM Samochody")
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Car Data")
        self.setFixedWidth(300)
        self.setFixedHeight(400)  # Zwiększamy szerokość dla nowych pól

        layout = QVBoxLayout()

        self.car_brand = QComboBox()
        # Słownik, który przypisuje marki samochodów do modeli
        self.car_brand.addItem("Select a brand...")
        self.car_brand.addItems(brands_models.keys())  # Dodaj dostępne marki
        self.car_brand.currentTextChanged.connect(self.update_models)  # Zaktualizuj modele przy zmianie marki
        layout.addWidget(self.car_brand)

        self.model = QComboBox()
        self.model.addItem("Select a model...")
        layout.addWidget(self.model)

        year = QComboBox()
        years = ["2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017",
                 "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]
        year.setPlaceholderText("Select a year")
        year.addItems(years)
        layout.addWidget(year)

        # Dodajemy pole na cenę za dobę
        self.price_per_day = QLineEdit()
        self.price_per_day.setPlaceholderText("Price per day")
        layout.addWidget(self.price_per_day)

        # Dodajemy pole na dostępność
        self.available = QComboBox()
        self.available.addItem("Select availability...")
        self.available.addItem("Available")
        self.available.addItem("Not Available")
        layout.addWidget(self.available)

        button = QPushButton("Submit")
        button.clicked.connect(self.add_car)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_models(self):
        """Aktualizuje listę modeli w zależności od wybranej marki."""
        selected_brand = self.car_brand.currentText()  # Pobierz wybraną markę
        self.model.clear()  # Wyczyść obecne modele
        if selected_brand in brands_models:
            self.model.addItems(brands_models[selected_brand])  # Dodaj modele dla wybranej marki
        else:
            self.model.addItem("No models available")

    def add_car(self):
        """Dodaj nowy samochód do bazy danych."""
        marka = self.car_brand.currentText()  # Pobierz wybraną markę
        model = self.model.currentText()  # Pobierz wybrany model
        rocznik = self.findChild(QComboBox).currentText()  # Pobierz wybrany rok (z comboboxa 'year')
        cena_za_dobe = self.price_per_day.text()  # Pobierz cenę za dobę
        dostepny = self.available.currentText()  # Pobierz dostępność

        # Sprawdzenie, czy wszystkie pola są wypełnione
        if marka != "Select a brand..." and model != "Select a model..." and rocznik != "Select a year" \
                and cena_za_dobe != "" and dostepny != "Select availability...":
            # Wstawienie danych do bazy
            connection = sqlite3.connect("wypozyczalnia.sqlite")
            cursor = connection.cursor()

            # Zapisz dane do tabeli Samochody
            cursor.execute("INSERT INTO Samochody (marka, model, rocznik, cena_za_dobe, dostepny) VALUES (?, ?, ?, ?, ?)",
                           (marka, model, rocznik, cena_za_dobe, dostepny))

            connection.commit()
            connection.close()
            
            self.accept()  # Zamknij okno dialogowe po dodaniu samochodu
            main_window.load_data()

class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Car")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()
        self.car_brand = QLineEdit()
        self.car_brand.setPlaceholderText("Brand")
        layout.addWidget(self.car_brand)

        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
            name = self.car_brand.text()
            connection = sqlite3.connect("wypozyczalnia.sqlite")
            cursor = connection.cursor()
            result = cursor.execute("SELECT * FROM Samochody WHERE marka = ?", (name,))
            rows = list(result)
            print(rows)
            items = main_window.table.findItems(name,
            Qt.MatchFlag.MatchFixedString)
            for item in items:
                print(item)
                main_window.table.item(item.row(),1).setSelected(True)
            cursor.close()
            connection.close()
app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())
