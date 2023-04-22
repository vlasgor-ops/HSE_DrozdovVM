import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pyautogui
import pandas as pd
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium_stealth import stealth

# Устанавливаем настройки загрузки PDF файлов
fp = webdriver.FirefoxProfile()
fp.set_preference("browser.download.folderList", 2)
fp.set_preference("browser.download.manager.showWhenStarting", False)
fp.set_preference("browser.download.dir", os.getcwd())
fp.set_preference("pdfjs.disabled", True)
fp.set_preference("plugin.scan.Acrobat", "99.0")
fp.set_preference("plugin.scan.plid.all", False)
fp.set_preference("browser.helperApps.alwaysAsk.force", False)
fp.set_preference("plugin.disable_full_page_plugin_for_types", "application/pdf")
fp.set_preference("pdfjs.disabled", True)
fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")

# Создаем экземпляр браузера Firefox
browser = webdriver.Firefox(firefox_profile=fp)

# Идем на сайт https://kad.arbitr.ru/
browser.get("https://kad.arbitr.ru/")

# Ищем элементы на странице
search_box = browser.find_element_by_class_name("g-ph")
bankruptcy_option = browser.find_element_by_xpath("//li[@class='bankruptcy']")
search_button = browser.find_element_by_css_selector("div.b-button-container")

# Читаем CSV файл и ищем ИНН
inn_list = pd.read_csv("inn_list.csv", encoding="cp1251", header=0)
inn_list = inn_list["ИНН"].to_list()

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




