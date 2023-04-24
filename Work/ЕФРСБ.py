import os
import pandas as pd
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pyautogui
import zipfile
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

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
inn_list = pd.read_csv('inn_list2.csv', encoding='cp1251', delimiter=';', header=0)
inn_list = inn_list.rename(columns={'ИНН': 'inn', 'ФИО': 'fio'})
inn_list['fio'] = inn_list['fio'].str.replace('.', '', regex=False)  # убираем точки из ФИО

inn_list = inn_list.to_dict('records')
inn = [row['inn'] for row in inn_list]
fio_list = [row['fio'] for row in inn_list]

# запускаем цикл поиска
for i, inn in enumerate(inn_list):
    fio = fio_list[i]
    # вставляем ИНН в форму поиска и нажимаем Enter
    inn_form = browser.find_element_by_xpath('//input[@formcontrolname="searchString"]')
    inn_form.clear()
    inn_form.send_keys(inn['inn'])
    inn_form.send_keys(Keys.ENTER)

    # ждем загрузки страницы и делаем скриншот
    time.sleep(2)  # увеличьте время ожидания, если страница долго загружается
    screenshot_filename = os.path.join(working_directory, f'{inn["inn"]} {fio}.png')

    pyautogui.screenshot(screenshot_filename)

# закрываем браузер
browser.quit()

# создаем архив со скриншотами
zip_filename = os.path.join(os.path.dirname(working_directory), f'Скриншоты ЕФРСБ.zip')
with zipfile.ZipFile(zip_filename, 'w') as zip_file:
    for filename in os.listdir(working_directory):
        file_path = os.path.join(working_directory, filename)
        if os.path.isfile(file_path):
            zip_file.write(file_path, os.path.basename(file_path))

# отправляем архив по электронной почте
smtp_host = 'smtp.yandex.ru'
smtp_port = 587
smtp_user = 'servis.monitoringa@yandex.ru'
smtp_password = 'vfqtjwgkzlrcveix'
recipient_email = 'vlasgor@gmail.com'
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



