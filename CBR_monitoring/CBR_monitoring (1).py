import os
import csv
import pickle
import re
import configparser
import time
import logging
import pyautogui
import chromedriver_autoinstaller
from IPython.external.qt_for_kernel import QtCore
from PIL import Image
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, \
    QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAbstractItemView
from datetime import datetime
from PyQt5.QtCore import Qt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
import urllib3
from selenium.webdriver.common.keys import Keys
import zipfile
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

class CSVEditorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Мониторинг должников Банка России")
        self.layout = QVBoxLayout()
        # Set the window icon
        icon = QIcon("lessthan10.png")
        self.setWindowIcon(icon)

        # Создание таблицы
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ИНН юридического лица", "Наименование юридического лица",
                                              "ИНН должностного лица", "ФИО должностного лица"])

        self.table.setDragEnabled(True)
        self.table.setAcceptDrops(True)
        self.table.setDragDropMode(QAbstractItemView.InternalMove)

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
        self.contact_label = QLabel("v.1.1, Отделение Красноярск, Дроздов Виталий, drozdovvm@cbr.ru")
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
    def edit_data(self, item):
        row = item.row()
        col = item.column()
        new_value = item.text()

        with open(self.csv_path, "r") as file:
            reader = csv.reader(file)
            data = list(reader)

        # Обновляем данные в списке
        data[row][col] = new_value

        with open(self.csv_path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(data)
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

        for row, row_data in enumerate(data[0:], start=0):
            for col, col_data in enumerate(row_data):
                item = QTableWidgetItem(col_data)
                item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)  # Разрешаем редактирование
                self.table.setItem(row, col, item)

        self.table.itemChanged.connect(self.edit_data)

    def mimeData(self, indexes):
        mime_data = super().mimeData(indexes)
        encoded_data = pickle.dumps([(index.row(), index.column()) for index in indexes])
        mime_data.setData("application/x-qabstractitemmodeldatalist", encoded_data)
        return mime_data

    def dragEnterEvent(self, event):
        mime_data = event.mimeData()
        if mime_data.hasFormat("application/x-qabstractitemmodeldatalist"):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        mime_data = event.mimeData()
        if mime_data.hasFormat("application/x-qabstractitemmodeldatalist"):
            event.acceptProposedAction()

    def dropEvent(self, event):
        mime_data = event.mimeData()
        if mime_data.hasFormat("application/x-qabstractitemmodeldatalist"):
            encoded_data = mime_data.data("application/x-qabstractitemmodeldatalist")
            data = pickle.loads(encoded_data)

            # Получаем координаты курсора
            drop_position = event.pos()

            # Определяем строку, над которой был отпущен элемент
            target_row = self.table.rowAt(drop_position.y())

            # Если над пустой областью, вставляем в конец
            if target_row == -1:
                target_row = self.table.rowCount()

            # Получаем выделенные строки
            selected_rows = set(row for row, _ in data)

            # Получаем текущие данные
            with open(self.csv_path, "r") as file:
                reader = csv.reader(file)
                current_data = list(reader)

            # Если перемещение в ту же область, удаляем выделенные строки
            if target_row in selected_rows:
                selected_rows.remove(target_row)

            # Вставляем строки перед целевой строкой
            for row in sorted(selected_rows, reverse=True):
                new_row_data = current_data[row]
                current_data.insert(target_row, new_row_data)

            # Удаляем строки, если перемещение в ту же область
            if target_row in selected_rows:
                for row in selected_rows:
                    current_data.pop(row)

            # Обновляем CSV-файл
            with open(self.csv_path, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerows(current_data)

            # Обновляем таблицу
            self.load_data()

    def add_data(self):
        inn_legal = self.inn_legal_input.text().strip()
        name_legal = self.name_legal_input.text().strip()
        inn_person = self.inn_person_input.text().strip()
        fio_person = self.fio_person_input.text().strip()

        # Проверяем заполненность хотя бы одного поля
        if not any([inn_legal, inn_person]):
            QMessageBox.warning(self, "Ошибка", "Необходимо заполнить хотя бы одно поле с ИНН.")
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
        with open("../lesson1/config.ini", "w") as config_file:
            self.config.write(config_file)

    # Код для запуска скрипта мониторинга ЕГРЮЛ
    def run_egryul_monitoring(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        urllib3.PoolManager(num_pools=20, maxsize=20)
        logging.basicConfig(level=logging.INFO)

        now = datetime.now().strftime("%Y-%m-%d")
        directory = f"C:/CBR_monitoring/ЕГРЮЛ/{now}_ЕГРЮЛ"
        os.makedirs(directory, exist_ok=True)

        chromedriver_autoinstaller.install()
        # Получаем версию браузера Chrome
        chrome_version = chromedriver_autoinstaller.get_chrome_version()

        # Получаем версию ChromeDriver для указанной версии Chrome
        chrome_driver_path = chromedriver_autoinstaller.install(cwd=True, verbose=True, chrome_version=chrome_version)

        chrome_options = Options()
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("--disable-popup-blocking=false")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Подсчет количества обработанных ИНН
        processed_count = 0
        # Читаем CSV файл и ищем ИНН
        try:
            with open(r'C:\CBR_monitoring\data.csv', encoding='cp1251') as csv_file:
                reader = csv.reader(csv_file, delimiter=',')
                inn_list = [(row[0], row[1], row[2], row[3]) for row in reader if len(row) >= 4]

        except Exception as e:
            logging.error('Error reading CSV file:', e)
            inn_list = []

        # Цикл по списку ИНН
        while inn_list:
            # Запуск браузера
            with webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options) as browser:
                stealth(browser, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32",
                        webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True)

                try:
                    browser.get('https://egrul.nalog.ru/index.html')
                    time.sleep(2)
                except Exception as e:
                    logging.error('Error:', e)

                # Цикл по 5 ИНН
                for inn, name, _, _ in inn_list[:5]:
                    if inn:
                        inn_form = browser.find_element_by_xpath('//input[@id="query"]')
                        inn_form.clear()
                        inn_form.send_keys(inn)
                        inn_form.send_keys(Keys.ENTER)
                        # ждем загрузки страницы и скачиваем выписку
                        time.sleep(2)
                        find = browser.find_element_by_xpath('//button[contains(@class, "btn-excerpt")]')
                        find.click()
                        time.sleep(3)

                        # Получение данных из элемента <div class="res-text"></div>
                        res_text = browser.find_element_by_class_name('res-text').text

                        # Сохранение данных в файл inn_list.csv
                        with open(os.path.join(directory, 'inn_list_egrul.csv'), 'a', newline='',
                                  encoding='utf-8-sig') as csv_file:
                            csv_writer = csv.writer(csv_file)
                            csv_writer.writerow([inn, name, res_text])

                        # Увеличение счетчика обработанных ИНН
                        processed_count += 1

                # Удаление обработанных ИНН из списка
                inn_list = inn_list[5:]

            # Закрытие браузера
            browser.quit()

            # Проверка условия для продолжения цикла
            if inn_list:
                time.sleep(1)

            # создаем архив с выписками
        now = datetime.now().strftime("%Y-%m-%d")
        directory = f"C:/CBR_monitoring/ЕГРЮЛ/{now}_ЕГРЮЛ"
        zip_filename = os.path.join(directory, 'Выписки ЕГРЮЛ.zip')

        with zipfile.ZipFile(zip_filename, 'w') as zip_file:
            # Добавляем файл inn_list_egrul.csv в архив
            inn_list_file = os.path.join(directory, 'inn_list_egrul.csv')
            zip_file.write(inn_list_file, os.path.basename(inn_list_file))

            # Получаем текущую дату
            current_date = datetime.now().strftime("%Y-%m-%d")
            download_dir = os.path.expanduser("~\Downloads")

            # Добавляем в архив только PDF-файлы, скачанные в текущую дату
            for filename in os.listdir(download_dir):
                file_path = os.path.join(download_dir, filename)
                if (
                        os.path.isfile(file_path) and
                        filename.endswith('.pdf') and
                        datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d") == current_date
                ):
                    zip_file.write(file_path, filename)

        # отправляем архив по электронной почте
        smtp_host = 'smtp.yandex.ru'
        smtp_port = 587
        smtp_user = 'servis.monitoringa@yandex.ru'
        smtp_password = 'vfqtjwgkzlrcveix'
        recipient_email = self.email_input.text().strip()
        subject = 'Выписки ЕГРЮЛ'
        body = ''
        filename = os.path.basename(zip_filename)

        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body))

        with open(zip_filename, 'rb') as f:
            attachment = MIMEApplication(f.read(), _subtype='zip')
            attachment.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(attachment)

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, recipient_email, msg.as_string())

        QMessageBox.information(None, 'Мониторинг ЕГРЮЛ выполнен',
                                    'Выписки отправлены на указанный адрес электронной почты')

        pass

# Код для запуска скрипта мониторинга ЕФРСБ
    def run_efrsb_monitoring(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        urllib3.PoolManager(num_pools=20, maxsize=20)
        logging.basicConfig(level=logging.INFO)
        # Указываем путь к исполняемому файлу Google Chrome
        chrome_path = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
        # Установка ChromeDriver
        chromedriver_autoinstaller.install()
        chrome_options = Options()
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("--disable-popup-blocking=false")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.binary_location = chrome_path

        with webdriver.Chrome(options=chrome_options) as browser:
            stealth(browser,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True,
                    )

            try:
                browser.get('https://bankrot.fedresurs.ru/')
                time.sleep(2)
            except Exception as e:
                logging.error('Error:', e)

            # Читаем CSV файл и ищем ИНН
            try:
                with open(r'C:\CBR_monitoring\data.csv', encoding='cp1251') as csv_file:
                    reader = csv.reader(csv_file, delimiter=',')
                    inn_list = [(row[0], row[1], row[2], row[3]) for row in reader if len(row) >= 4]

            except Exception as e:
                logging.error('Error reading CSV file:', e)
                inn_list = []

            for inn, name, innDL, FIO in inn_list:
                if inn:
                    inn_form = browser.find_element_by_xpath('//input[@formcontrolname="searchString"]')
                    inn_form.clear()
                    inn_form.send_keys(inn)
                    inn_form.send_keys(Keys.ENTER)

                # ждем загрузки страницы и делаем скриншот
                    time.sleep(3)
                    now = datetime.now().strftime("%Y-%m-%d")
                    directory = f"C:/CBR_monitoring/ЕФРСБ/{now} ЕФРСБ"
                    os.makedirs(directory, exist_ok=True)

                # Создаем имя файла скриншота, соответствующее ИНН и ФИО
                    sanitized_name = re.sub(r'[<>:"/\\|?*]', "", name)  # Удаляем недопустимые символы из имени файла
                    filename = f"{directory}/{inn}_{sanitized_name}.png"

                # Сделать скриншот всего экрана и сохранить его в файл
                    screenshot = pyautogui.screenshot()
                    resized_screenshot = screenshot.resize((1920, 1080), Image.ANTIALIAS)
                    resized_screenshot.save(filename)
                    time.sleep(1)  # Ждем некоторое время, чтобы страница полностью загрузилась
                if innDL:
                    inn_form = browser.find_element_by_xpath('//input[@formcontrolname="searchString"]')  # Находим элемент заново
                    inn_form.clear()
                    inn_form.send_keys(innDL)
                    inn_form.send_keys(Keys.ENTER)

                # ждем загрузки страницы и делаем скриншот
                    time.sleep(3)
                    now = datetime.now().strftime("%Y-%m-%d")
                    directory = f"C:/CBR_monitoring/ЕФРСБ/{now} ЕФРСБ"
                    os.makedirs(directory, exist_ok=True)

                # Создаем имя файла скриншота, соответствующее ИНН и ФИО
                    sanitized_nameDL = re.sub(r'[<>:"/\\|?*]', "", FIO)  # Удаляем недопустимые символы из имени файла
                    filenameDL = f"{directory}/{innDL}_{sanitized_nameDL}.png"

                # Сделать скриншот всего экрана и сохранить его в файл
                    screenshot = pyautogui.screenshot()
                    resized_screenshot = screenshot.resize((1920, 1080), Image.ANTIALIAS)
                    resized_screenshot.save(filenameDL)
                    time.sleep(1)
                if FIO:
                    inn_form = browser.find_element_by_xpath('//input[@formcontrolname="searchString"]')  # Находим элемент заново
                    inn_form.clear()
                    inn_form.send_keys(FIO)
                    inn_form.send_keys(Keys.ENTER)

                # ждем загрузки страницы и делаем скриншот
                    time.sleep(3)
                    now = datetime.now().strftime("%Y-%m-%d")
                    directory = f"C:/CBR_monitoring/ЕФРСБ/{now} ЕФРСБ"
                    os.makedirs(directory, exist_ok=True)

                # Создаем имя файла скриншота, соответствующее ИНН и ФИО
                    sanitized_nameDL = re.sub(r'[<>:"/\\|?*]', "", FIO)  # Удаляем недопустимые символы из имени файла
                    filenameDLFIO = f"{directory}/{sanitized_nameDL}.png"

                # Сделать скриншот всего экрана и сохранить его в файл
                    screenshot = pyautogui.screenshot()
                    resized_screenshot = screenshot.resize((1920, 1080), Image.ANTIALIAS)
                    resized_screenshot.save(filenameDLFIO)
                    time.sleep(1)
            # закрываем браузер
        browser.quit()

        # создаем архив со скриншотами
        zip_filename = os.path.join(os.path.dirname(directory), f'Скриншоты ЕФРСБ.zip')
        with zipfile.ZipFile(zip_filename, 'w') as zip_file:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    zip_file.write(file_path, os.path.basename(file_path))

        # отправляем архив по электронной почте
        smtp_host = 'smtp.yandex.ru'
        smtp_port = 587
        smtp_user = 'servis.monitoringa@yandex.ru'
        smtp_password = 'vfqtjwgkzlrcveix'
        recipient_email = self.email_input.text().strip()
        subject = 'Скриншоты ЕФРСБ'
        body = ''
        filename = os.path.basename(zip_filename)

        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body))

        with open(zip_filename, 'rb') as f:
            attachment = MIMEApplication(f.read(), _subtype='zip')
            attachment.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(attachment)

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, recipient_email, msg.as_string())

        QMessageBox.information(None, 'Мониторинг ЕФРСБ выполнен', 'Скриншоты отправлены на указанный адрес электронной почты')

        pass

    def run_arbitr_monitoring(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        urllib3.PoolManager(num_pools=20, maxsize=20)
        logging.basicConfig(level=logging.INFO)
        # Указываем путь к исполняемому файлу Google Chrome
        chrome_path = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
        # Установка ChromeDriver
        chromedriver_autoinstaller.install()
        chrome_options = Options()
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("--disable-popup-blocking=false")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.binary_location = chrome_path

        with webdriver.Chrome(options=chrome_options) as browser:
            stealth(browser,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True,
                    )

            try:
                browser.get('https://kad.arbitr.ru')
                time.sleep(2)
                # Закрыть всплывающее окно, если оно присутствует
                close_button = browser.find_element(By.CSS_SELECTOR, 'a.b-promo_notification-popup-close')
                close_button.click()

            except Exception as e:
                logging.error('Error:', e)

                # Читаем CSV файл и ищем ИНН
            try:
                with open(r'C:\CBR_monitoring\data.csv', encoding='cp1251') as csv_file:
                    reader = csv.reader(csv_file, delimiter=',')
                    inn_list = [(row[0], row[1], row[2], row[3]) for row in reader if len(row) >= 4]

            except Exception as e:
                logging.error('Error reading CSV file:', e)
                inn_list = []

            for inn, name, innDL, FIO in inn_list:
                if inn:
                    # вставляем ИНН в форму поиска и нажимаем Enter
                    inn_form = browser.find_element_by_xpath('//textarea[@placeholder="название, ИНН или ОГРН"]')
                    inn_form.clear()
                    inn_form.send_keys(inn)
                    inn_form.send_keys(Keys.ENTER)

                    # ждем загрузки страницы и делаем скриншот
                    time.sleep(3)
                    now = datetime.now().strftime("%Y-%m-%d")
                    directory = f"C:/CBR_monitoring/kad.arbitr/{now} kad.arbitr"
                    os.makedirs(directory, exist_ok=True)

                    # Создаем имя файла скриншота, соответствующее ИНН и ФИО
                    sanitized_name = re.sub(r'[<>:"/\\|?*]', "", name)  # Удаляем недопустимые символы из имени файла
                    filename = f"{directory}/{inn}_{sanitized_name}.png"

                    # Сделать скриншот всего экрана и сохранить его в файл
                    screenshot = pyautogui.screenshot()
                    resized_screenshot = screenshot.resize((1920, 1080), Image.ANTIALIAS)
                    resized_screenshot.save(filename)
                    time.sleep(1)
                if innDL:
                    inn_form = browser.find_element_by_xpath('//textarea[@placeholder="название, ИНН или ОГРН"]')  # Находим элемент заново
                    inn_form.clear()
                    inn_form.send_keys(innDL)
                    inn_form.send_keys(Keys.ENTER)

                # ждем загрузки страницы и делаем скриншот
                    time.sleep(3)
                    now = datetime.now().strftime("%Y-%m-%d")
                    directory = f"C:/CBR_monitoring/kad.arbitr/{now} kad.arbitr"
                    os.makedirs(directory, exist_ok=True)

                # Создаем имя файла скриншота, соответствующее ИНН и ФИО
                    sanitized_nameDL = re.sub(r'[<>:"/\\|?*]', "", FIO)  # Удаляем недопустимые символы из имени файла
                    filenamedl = f"{directory}/{innDL}_{sanitized_nameDL}.png"

                # Сделать скриншот всего экрана и сохранить его в файл
                    screenshot = pyautogui.screenshot()
                    resized_screenshot = screenshot.resize((1920, 1080), Image.ANTIALIAS)
                    resized_screenshot.save(filenamedl)
                    time.sleep(1)
                if FIO:
                    inn_form = browser.find_element_by_xpath('//textarea[@placeholder="название, ИНН или ОГРН"]')  # Находим элемент заново
                    inn_form.clear()
                    inn_form.send_keys(FIO)
                    inn_form.send_keys(Keys.ENTER)

                # ждем загрузки страницы и делаем скриншот
                    time.sleep(3)
                    now = datetime.now().strftime("%Y-%m-%d")
                    directory = f"C:/CBR_monitoring/kad.arbitr/{now} kad.arbitr"
                    os.makedirs(directory, exist_ok=True)

                # Создаем имя файла скриншота, соответствующее ИНН и ФИО
                    sanitized_nameDL = re.sub(r'[<>:"/\\|?*]', "", FIO)  # Удаляем недопустимые символы из имени файла
                    filenamedlfio = f"{directory}/{sanitized_nameDL}.png"

                # Сделать скриншот всего экрана и сохранить его в файл
                    screenshot = pyautogui.screenshot()
                    resized_screenshot = screenshot.resize((1920, 1080), Image.ANTIALIAS)
                    resized_screenshot.save(filenamedlfio)
                    time.sleep(1)
        # закрываем браузер
        browser.quit()

        # создаем архив со скриншотами
        zip_filename = os.path.join(os.path.dirname(directory), f'Скриншоты kad.arbitr.zip')
        with zipfile.ZipFile(zip_filename, 'w') as zip_file:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    zip_file.write(file_path, os.path.basename(file_path))

        # отправляем архив по электронной почте
        smtp_host = 'smtp.yandex.ru'
        smtp_port = 587
        smtp_user = 'servis.monitoringa@yandex.ru'
        smtp_password = 'vfqtjwgkzlrcveix'
        recipient_email = self.email_input.text().strip()
        subject = 'Скриншоты kad.arbitr'
        body = ''
        filename = os.path.basename(zip_filename)

        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body))

        with open(zip_filename, 'rb') as f:
            attachment = MIMEApplication(f.read(), _subtype='zip')
            attachment.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(attachment)

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, recipient_email, msg.as_string())

        QMessageBox.information(None, 'Мониторинг kad.arbitr выполнен', 'Скриншоты отправлены на указанный адрес электронной почты')

        pass

if __name__ == '__main__':
    app = QApplication([])
    window = CSVEditorWindow()
    window.showMaximized()
    app.exec_()

