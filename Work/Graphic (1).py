# coding: utf-8
import os
import csv
import re
import configparser
from PyQt5.QtCore import QRect, QEasingCurve, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, \
    QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtGui import QIcon

class CSVEditorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Мониторинг должников Банка России")
        self.layout = QVBoxLayout()
        # Set the window icon
        icon = QIcon("../CBR_monitoring_develop/lessthan10.png")
        self.setWindowIcon(icon)

        # Создание таблицы
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ИНН юридического лица", "Наименование юридического лица",
                                              "ИНН должностного лица", "ФИО должностного лица"])

        # Создание полей ввода
        self.inn_legal_input = QLineEdit()
        self.name_legal_input = QLineEdit()
        self.fio_person_input = QLineEdit()
        self.inn_person_input = QLineEdit()
        self.email_input = QLineEdit()

        # Создание кнопок
        self.add_button = QPushButton("Добавить")
        self.delete_button = QPushButton("Удалить")
        self.email_label = QLabel("E-mail:")
        self.email_button = QPushButton("Добавить E-mail")
        self.monitoring_egryul_button = QPushButton("Мониторинг ЕГРЮЛ")
        self.monitoring_efrsb_button = QPushButton("Мониторинг ЕФРСБ")
        self.monitoring_arbitr_button = QPushButton("Мониторинг kad.arbitr")
        self.contact_label = QLabel("v.1.0, Отделение Красноярск, Дроздов Виталий, drozdovvm@cbr.ru")
        self.contact_label.setAlignment(Qt.AlignRight)


        # Компоновка элементов интерфейса
        self.layout.addWidget(self.table)

        input_layout = QVBoxLayout()
        input_layout.addWidget(self.delete_button)
        input_layout.addWidget(QLabel("ИНН юридического лица"))
        input_layout.addWidget(self.inn_legal_input)
        input_layout.addWidget(QLabel("Наименование юридического лица"))
        input_layout.addWidget(self.name_legal_input)
        input_layout.addWidget(QLabel("ИНН должностного лица"))
        input_layout.addWidget(self.inn_person_input)
        input_layout.addWidget(QLabel("ФИО должностного лица"))
        input_layout.addWidget(self.fio_person_input)
        input_layout.addWidget(self.add_button)
        input_layout.addWidget(self.email_label)
        input_layout.addWidget(self.email_input)
        input_layout.addWidget(self.email_button)
        self.layout.addLayout(input_layout)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.monitoring_egryul_button)
        button_layout.addWidget(self.monitoring_efrsb_button)
        button_layout.addWidget(self.monitoring_arbitr_button)
        self.layout.addLayout(button_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.contact_label)
        button_layout.addStretch(1)
        self.layout.addLayout(button_layout)

        self.setLayout(self.layout)

        # Соединение сигналов и слотов
        self.add_button.clicked.connect(self.add_data)
        self.delete_button.clicked.connect(self.delete_data)
        self.email_button.clicked.connect(self.add_email)
        self.monitoring_egryul_button.clicked.connect(self.run_egryul_monitoring)
        self.monitoring_efrsb_button.clicked.connect(self.run_efrsb_monitoring)
        self.monitoring_arbitr_button.clicked.connect(self.run_arbitr_monitoring)

        # Создание папки и файла CSV при первом запуске
        self.csv_folder = "C:/CBR_monitoring"
        self.csv_path = os.path.join(self.csv_folder, "data.csv")

        if not os.path.exists(self.csv_folder):
            os.makedirs(self.csv_folder)

        if not os.path.exists(self.csv_path):
            with open(self.csv_path, "w", newline="") as file:
                writer = csv.writer(file)

        # Загрузка данных из CSV в таблицу
        self.load_data()

        # Загрузка сохраненного e-mail из конфигурационного файла
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        if self.config.has_option("Settings", "email"):
            saved_email = self.config.get("Settings", "email")
            self.email_input.setText(saved_email)

    def load_data(self):
        self.table.clearContents()

        if not os.path.exists("C:/CBR_monitoring"):
            os.makedirs("C:/CBR_monitoring")

        self.csv_path = "C:/CBR_monitoring/data.csv"

        with open(self.csv_path, "r") as file:
            reader = csv.reader(file)
            data = list(reader)

        self.table.setRowCount(len(data) - 0)
        for row, row_data in enumerate(data[0:], start=0):
            for col, col_data in enumerate(row_data):
                item = QTableWidgetItem(col_data)
                self.table.setItem(row, col, item)

        self.table.resizeColumnsToContents()

    def add_data(self):
        inn_legal = self.inn_legal_input.text().strip()
        name_legal = self.name_legal_input.text().strip()
        inn_person = self.inn_person_input.text().strip()
        fio_person = self.fio_person_input.text().strip()

        # Проверяем заполненность хотя бы одного поля
        if not any([inn_legal, name_legal, fio_person, inn_person]):
            QMessageBox.warning(self, "Ошибка", "Необходимо заполнить хотя бы одно поле.")
            return

        if inn_legal and len(inn_legal) != 10:
            QMessageBox.warning(self, "Ошибка", "Цифр в ИНН юридического лица должно быть 10.")
            return

        if inn_person and len(inn_person) != 12:
            QMessageBox.warning(self, "Ошибка", "Цифр в ИНН должностного лица должно быть 12.")
            return

        with open(self.csv_path, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([inn_legal, name_legal, inn_person, fio_person])

        # Очищаем поля ввода после добавления данных
        self.inn_legal_input.clear()
        self.name_legal_input.clear()
        self.fio_person_input.clear()
        self.inn_person_input.clear()

        # Обновляем таблицу
        self.load_data()

    def delete_data(self):
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            return

        with open(self.csv_path, "r") as file:
            reader = csv.reader(file)
            data = list(reader)

        with open(self.csv_path, "w", newline="") as file:
            writer = csv.writer(file)
            for row, item in enumerate(data):
                if row not in selected_rows:
                    writer.writerow(item)

        # Обновляем таблицу
        self.load_data()

    def add_email(self):
        email = self.email_input.text().strip()

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            QMessageBox.warning(self, "Ошибка", "Некорректный адрес электронной почты.")
            return
        code = f"{email}"

        print(code)

        if not self.config.has_section("Settings"):
            self.config.add_section("Settings")

        self.config.set("Settings", "email", email)
        with open("../CBR_monitoring/config.ini", "w") as config_file:
            self.config.write(config_file)

    def run_egryul_monitoring(self):
        # Ваш код для запуска скрипта мониторинга ЕГРЮЛ
        pass

# Код для запуска скрипта мониторинга ЕФРСБ
    def run_efrsb_monitoring(self):

        pass

    def run_arbitr_monitoring(self):
        # Ваш код для запуска скрипта мониторинга kad.arbitr
        pass

if __name__ == '__main__':
    app = QApplication([])
    window = CSVEditorWindow()
    window.showMaximized()
    app.exec_()

