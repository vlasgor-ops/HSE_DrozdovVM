import os
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
        time.sleep(4)
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

# создаем архив со скриншотами
zip_filename = os.path.join(os.path.dirname(directory), f'Скриншоты Арбитр.zip')
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
recipient_email = 'vlasgor@gmail.com'
subject = 'Скриншоты Арбитр'
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




