import os
import pandas as pd
import csv
import time
import logging
import pyautogui
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
import urllib3
from selenium.webdriver.common.keys import Keys
import zipfile
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from Work.EGRUL import new_list, run_1, folder_path

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
urllib3.PoolManager(num_pools=20, maxsize=20)
logging.basicConfig(level=logging.INFO)

chrome_options = Options()
chrome_options.add_argument("start-maximized")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

with webdriver.Chrome(executable_path='C:\\chromedriver.exe', options=chrome_options) as browser:
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
        time.sleep(5)
    except Exception as e:
        logging.error('Error:', e)

# Читаем CSV файл и ищем ИНН
    try:
        with open('inn_list2.csv', encoding='cp1251') as csv_file:
            reader = csv.reader(csv_file, delimiter=';')
            inn_list = [(row[0], row[1]) for row in reader]

    except Exception as e:
        logging.error('Error reading CSV file:', e)
        inn_list = []

    for inn, name in inn_list:
        # вставляем ИНН в форму поиска и нажимаем Enter
        inn_form = browser.find_element_by_xpath('//input[@formcontrolname="searchString"]')
        inn_form.clear()
        inn_form.send_keys(inn)
        inn_form.send_keys(Keys.ENTER)

        # ждем загрузки страницы и делаем скриншот
        time.sleep(5)
        now = datetime.now().strftime("%Y-%m-%d")
        directory = f"{os.path.expanduser('~')}/Desktop/{now} ЕФРСБ"
        os.makedirs(directory, exist_ok=True)

        # Создаем имя файла скриншота, соответствующее ИНН и ФИО
        filename = f"{directory}/{inn}_{name}.png"

        # Сделать скриншот всего экрана и сохранить его в файл
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)

# закрываем браузер
browser.quit()

with webdriver.Chrome(executable_path='C:\\chromedriver.exe', options=chrome_options) as browser:
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
        time.sleep(5)
    except Exception as e:
        logging.error('Error:', e)

        # Читаем CSV файл и ищем ИНН
    try:
        with open('inn_list2.csv', encoding='cp1251') as csv_file:
            reader = csv.reader(csv_file, delimiter=';')
            inn_list = [(row[0], row[1]) for row in reader]

    except Exception as e:
        logging.error('Error reading CSV file:', e)
        inn_list = []

    for inn, name in inn_list:
        # вставляем ИНН в форму поиска и нажимаем Enter
        inn_form = browser.find_element_by_xpath('//textarea[@placeholder="название, ИНН или ОГРН"]')
        inn_form.clear()
        inn_form.send_keys(inn)
        inn_form.send_keys(Keys.ENTER)

        # ждем загрузки страницы и делаем скриншот
        time.sleep(5)
        now = datetime.now().strftime("%Y-%m-%d")
        directory = f"{os.path.expanduser('~')}/Desktop/{now} Арбитражный суд"
        os.makedirs(directory, exist_ok=True)

        # Создаем имя файла скриншота, соответствующее ИНН и ФИО
        filename = f"{directory}/{inn}_{name}.png"

        # Сделать скриншот всего экрана и сохранить его в файл
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)

# закрываем браузер
browser.quit()

with webdriver.Chrome(executable_path='C:\\chromedriver.exe', options=chrome_options) as browser:
    stealth(browser,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

    try:
        browser.get('https://egrul.nalog.ru/index.html')
        time.sleep(5)
    except Exception as e:
        logging.error('Error:', e)

# Читаем CSV файл и ищем ИНН
    try:
        with open('inn_list2.csv', encoding='cp1251') as csv_file:
            reader = csv.reader(csv_file, delimiter=';')
            inn_list = [(row[0], row[1]) for row in reader]

    except Exception as e:
        logging.error('Error reading CSV file:', e)
        inn_list = []

    for inn, name in inn_list:
        # вставляем ИНН в форму поиска и нажимаем Enter
        inn_form = browser.find_element_by_xpath('query')
        inn_form.clear()
        inn_form.send_keys(inn)
        inn_form.send_keys(Keys.ENTER)
        time.sleep(3)
        content = browser.find_elements_by_class_name('res-text')
        for info in content:
            new_list.append(info.text)
        find = browser.find_elements_by_tag_name('button')
        find[2].click()
        time.sleep(3)



# проходимся по списку ИНН с помощью цикла for и функции enumerate
for i, inn in enumerate(inn_list):
    run_1(inn)
    if (i + 1) % 5 == 0:
        browser.quit()  # явно закрываем браузер
        time.sleep(10)
        browser = webdriver.Chrome(executable_path='C:\\chromedriver.exe', options=chrome_options)

        # создаем DataFrame из списка new_list и сохраняем его в csv-файл
        df = pd.DataFrame(new_list, columns=['all'])
        df.to_csv(os.path.join(folder_path, 'inn_list.csv'), encoding='cp1251')

# закрываем браузер
browser.quit()