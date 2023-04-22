import os
import pandas as pd
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pyautogui

# устанавливаем путь к рабочей папке
working_directory = os.path.join(os.environ['USERPROFILE'], 'Desktop', datetime.date.today().strftime('%Y-%m-%d'))
if not os.path.exists(working_directory):
    os.makedirs(working_directory)

# создаем профиль Firefox
fp = webdriver.FirefoxProfile()
fp.set_preference("browser.download.folderList", 2);
fp.set_preference("browser.download.manager.showWhenStarting", False);
fp.set_preference("browser.download.dir", working_directory);
fp.set_preference("pdfjs.disabled", True);
fp.set_preference("plugin.scan.Acrobat", "99.0");
fp.set_preference("plugin.scan.plid.all", False);
fp.set_preference("browser.helperApps.alwaysAsk.force", False);
fp.set_preference("plugin.disable_full_page_plugin_for_types", "application/pdf")
fp.set_preference("pdfjs.disabled", True)
fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")

# создаем экземпляр браузера
browser = webdriver.Firefox(firefox_profile=fp)

# открываем главную страницу
browser.get('https://bankrot.fedresurs.ru/')

# читаем ИНН из файла CSV
inn_list = pd.read_csv('inn_list.csv', encoding='cp1251', header=0)
inn_list = inn_list['ИНН'].to_list()

# запускаем цикл поиска
for inn in inn_list:
    # вставляем ИНН в форму поиска и нажимаем Enter
    inn_form = browser.find_element_by_xpath('//input[@formcontrolname="searchString"]')
    inn_form.clear()
    inn_form.send_keys(inn)
    inn_form.send_keys(Keys.ENTER)

    # ждем загрузки страницы и делаем скриншот
    time.sleep(5)  # увеличьте время ожидания, если страница долго загружается
    screenshot_filename = os.path.join(working_directory, f'{inn}.png')
    pyautogui.screenshot(screenshot_filename)

# закрываем браузер
browser.quit()
