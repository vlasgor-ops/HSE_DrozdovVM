import json
import csv
import re

# Получаем список ИНН из файла "traders.txt"
inn_list = []
with open("traders.txt", "r") as f:
    for line in f:
        inn_list.append(line.strip())

# Находим информацию об организациях с этими ИНН в файле "traders.json"
traders_data = {}
with open("traders.json", "r") as f:
    data = json.load(f)
    for trader in data:
        if trader["inn"] in inn_list:
            traders_data[trader["inn"]] = {"ogrn": trader["ogrn"], "address": trader["address"]}

# Сохраняем информацию об ИНН, ОГРН и адресе организаций из файла "traders.txt" в файл "traders.csv"
with open("traders.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["INN", "OGRN", "Address"])
    for inn in inn_list:
        if inn in traders_data:
            writer.writerow([inn, traders_data[inn]["ogrn"], traders_data[inn]["address"]])


# Находим все email-адреса в дата-сете и собираем их в словарь
with open('1000_efrsb_messages.json', 'r') as f:
    data = json.load(f)

emails_dict = {}
for message in data:
    inn = message['publisher_inn']
    msg_text = message['msg_text']
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', msg_text)
    if emails:
        if inn not in emails_dict:
            emails_dict[inn] = set()
        emails_dict[inn].update(emails)

with open('emails.json', 'w') as f:
    json.dump({k: list(v) for k, v in emails_dict.items()}, f, ensure_ascii=False, indent=4)