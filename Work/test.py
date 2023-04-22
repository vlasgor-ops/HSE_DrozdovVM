import os
import time
import logging
import pandas as pd
import pyautogui
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
import urllib3
from selenium.webdriver.common.keys import Keys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
urllib3.PoolManager(num_pools=10, maxsize=10)
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

        # Читаем CSV файл и ищем ИНН
    try:
        inn_list = pd.read_csv("inn_list2.csv", encoding="cp1251", header=0)
        inn_list = inn_list["ИНН"].to_list()
    except Exception as e:
        logging.error('Error reading CSV file:', e)
        inn_list = []

    for inn in inn_list:
            # вставляем ИНН в форму поиска и нажимаем Enter
        inn_form = browser.find_element_by_xpath('//textarea[@placeholder="название, ИНН или ОГРН"]')
        inn_form.clear()
        inn_form.send_keys(inn)
        inn_form.send_keys(Keys.ENTER)

            # ждем загрузки страницы и делаем скриншот
        time.sleep(2)  # увеличьте время ожидания, если страница долго загружается
        now = datetime.now().strftime("%Y-%m-%d")
        directory = f"{os.path.expanduser('~')}/Desktop/{now} Арбитражный суд"
        os.makedirs(directory, exist_ok=True)

        # Создаем имя файла скриншота, соответствующее ИНН
        filename = f"{directory}/{inn}.png"

        # Сделать скриншот всего экрана и сохранить его в файл
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)


