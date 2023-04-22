import os
import time
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
import pyautogui
import pandas as pd

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
        browser.get('https://kad.arbitr.ru')
        time.sleep(5)
    except Exception as e:
        logging.error('Error:', e)

    # Ищем элементы на странице
    search_box = browser.find_element(By.ID, "search")
    bankruptcy_option = browser.find_element(By.XPATH, "//li[@class='bankruptcy']")
    search_button = browser.find_element(By.CSS_SELECTOR, "button[data-test-id='search-button']")

    # Читаем CSV файл и ищем ИНН
    try:
        inn_list = pd.read_csv("inn_list.csv", encoding="cp1251", header=0)
        inn_list = inn_list["ИНН"].to_list()
    except Exception as e:
        logging.error('Error reading CSV file:', e)
        inn_list = []

# Перебираем все ИНН из CSV файла
for inn in inn_list:
    # Вставляем ИНН в элемент <textarea> и отправляем форму
    search_box.clear()
    time.sleep(2)
    search_box.send_keys(inn)
    time.sleep(2)
    search_button.click()
    time.sleep(2)
    bankruptcy_option.click()

    # Ждем, пока страница загрузится полностью
    time.sleep(3)

    # Создаем папку для сохранения скриншота
    now = datetime.now().strftime("%Y-%m-%d")
    directory = f"{os.path.expanduser('~')}/Desktop/{now} Арбитражный суд"
    os.makedirs(directory, exist_ok=True)

    # Создаем имя файла скриншота, соответствующее ИНН
    filename = f"{directory}/{inn}.png"

    # Сделать скриншот всего экрана и сохранить его в файл
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)

# Закрываем браузер
browser.quit()