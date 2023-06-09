import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import re

# получаем относительный путь к папке с помощью метода os.path.dirname()
# и добавляем к нему нужную папку с помощью метода os.path.join()
folder_path = os.path.join(os.path.dirname(os.getcwd()), 'CBR')

# создаем Firefox профиль и настраиваем его для автоматического скачивания pdf-файлов
fp = webdriver.FirefoxProfile()
fp.set_preference("browser.download.folderList", 2)
fp.set_preference("browser.download.manager.showWhenStarting", False)
fp.set_preference("browser.download.dir", folder_path)
fp.set_preference("pdfjs.disabled", True)
fp.set_preference("plugin.scan.Acrobat", "99.0")
fp.set_preference("plugin.scan.plid.all", False)
fp.set_preference("browser.helperApps.alwaysAsk.force", False)
fp.set_preference("plugin.disable_full_page_plugin_for_types", "application/pdf")
fp.set_preference("pdfjs.disabled", True)
fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")

# создаем браузер
browser = webdriver.Firefox(firefox_profile=fp)

def run_1(form_fill):
    browser.get('https://egrul.nalog.ru/index.html')
    inn_form = browser.find_element_by_id('query')
    inn_form.send_keys(form_fill)
    inn_form.send_keys(Keys.ENTER)
    time.sleep(3)
    content = browser.find_elements_by_class_name('res-text')
    for info in content:
        new_list.append(info.text)
    find = browser.find_elements_by_tag_name('button')
    find[2].click()
    time.sleep(3)

# загружаем список ИНН из файла и преобразуем его в список
inn_list = pd.read_csv('1.csv', encoding='cp1251', header=0)['ИНН'].tolist()

new_list = []

# проходимся по списку ИНН с помощью цикла for и функции enumerate
for i, inn in enumerate(inn_list):
    run_1(inn)
    if (i+1) % 5 == 0:
        browser.quit()  # явно закрываем браузер
        time.sleep(10)
        browser = webdriver.Firefox(firefox_profile=fp)

# создаем DataFrame из списка new_list и сохраняем его в csv-файл
df = pd.DataFrame(new_list, columns=['all'])
df.to_csv(os.path.join(folder_path, 'inn_list.csv'), encoding='cp1251')