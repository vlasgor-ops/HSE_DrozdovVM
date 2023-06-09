import requests
import json
from bs4 import BeautifulSoup

class ParserCBRF:
    def __init__(self, url):
        self.url = url
        self.data = {}

    def start(self):
        page = self._get_page()
        if page is not None:
            self._parse_page(page)
            self._save_data()

    def _get_page(self):
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                return response.content
        except requests.exceptions.RequestException as e:
            print("error:", str(e))
        return None

    def _parse_page(self, page):
        soup = BeautifulSoup(page, 'html.parser')
        table = soup.find('table', {'class': 'data'})
        if table is not None:
            rows = table.find_all('tr')

            for row in rows[1:]:
                columns = row.find_all('td')
                if len(columns) == 2:
                    date = columns[0].text.strip()
                    rate = columns[1].text.strip().replace(',', '.')
                    self.data[date] = rate
        else:
            print("Информация не найдена на странице")

    def _save_data(self):
        with open('cb_rates.json', 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)

    @staticmethod
    def load_data(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return str(self.data)


url = 'http://www.cbr.ru/hd_base/KeyRate/?UniDbQuery.Posted=True&UniDbQuery.From=01.01.2020&UniDbQuery.To=09.06.2023'
parser = ParserCBRF(url)
parser.start()

loaded_data = ParserCBRF.load_data('cb_rates.json')
print(loaded_data)



