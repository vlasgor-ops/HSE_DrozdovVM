import requests
from bs4 import BeautifulSoup
import json
import datetime
from decimal import Decimal

class ParserCBRF:
    def __init__(self, url, filename):
        self.url = url
        self.filename = filename
        self.data = {}

    def start(self):
        self.data = self.parse_cbrf_page()
        self.save_data()

    def parse_cbrf_page(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'class': 'data'})
            data = {}
            if table:
                rows = table.find_all('tr')
                for row in rows[1:]:
                    cells = row.find_all('td')
                    date_str = cells[0].text.strip()
                    rate_str = cells[1].text.strip()
                    try:
                        date = datetime.datetime.strptime(date_str, '%d.%m.%Y').date()
                        rate = Decimal(rate_str.replace(',', '.'))
                        data[date] = rate
                    except ValueError:
                        pass
            return data
        else:
            raise requests.HTTPError(f'Request failed with status code {response.status_code}')

    def save_data(self):
        formatted_data = self.format_data(self.data)
        with open(self.filename, 'w') as file:
            json.dump(formatted_data, file, indent=4)

    def load_data(self):
        with open(self.filename, 'r') as file:
            formatted_data = file.read()
        self.data = self.deserialize_data(formatted_data)

    @staticmethod
    def deserialize_data(json_data):
        serialized_data = json.loads(json_data)
        data = {datetime.datetime.strptime(date_str, '%Y-%m-%d').date(): Decimal(rate_str)
                for date_str, rate_str in serialized_data.items()}
        return data

    @staticmethod
    def format_data(data):
        formatted_data = {}
        previous_date = None
        previous_rate = None
        for date, rate in sorted(data.items()):
            formatted_date = date.isoformat()
            if previous_date and previous_date + datetime.timedelta(days=1) != date:
                # Заполнение пробелов в данных
                missing_dates = previous_date + datetime.timedelta(days=1)
                while missing_dates != date:
                    formatted_missing_date = missing_dates.isoformat()
                    formatted_data[formatted_missing_date] = str(previous_rate)
                    missing_dates += datetime.timedelta(days=1)
            formatted_data[formatted_date] = str(rate)
            previous_date = date
            previous_rate = rate
        return formatted_data

class KeyRateOvernightCBRF:
    def __init__(self, filename):
        self.filename = filename
        self.data = {}

    def load_data(self):
        with open(self.filename, 'r') as file:
            formatted_data = file.read()
        self.data = self.deserialize_data(formatted_data)

    @staticmethod
    def deserialize_data(json_data):
        serialized_data = json.loads(json_data)
        data = {datetime.datetime.strptime(date_str, '%Y-%m-%d').date(): Decimal(rate_str)
                for date_str, rate_str in serialized_data.items()}
        return data

    def keyrateovernight_by_date(self, date):
        formatted_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        rate = self.data.get(formatted_date)
        return str(rate) if rate else None

    def keyrateovernight_last(self):
        last_date = max(self.data.keys())
        rate = self.data.get(last_date)
        return str(rate) if rate else None

    def keyrateovernight_range_dates(self, from_date, to_date):
        formatted_from_date = datetime.datetime.strptime(from_date, '%Y-%m-%d').date()
        formatted_to_date = datetime.datetime.strptime(to_date, '%Y-%m-%d').date()
        rates = []
        for date, rate in sorted(self.data.items()):
            if formatted_from_date <= date <= formatted_to_date:
                rates.append((date.isoformat(), str(rate)))
        return rates

# Использование класса ParserCBRF для сбора данных
parser = ParserCBRF('https://www.cbr.ru/hd_base/overnight/?UniDbQuery.Posted=True&UniDbQuery.From=18.06.1998&UniDbQuery.To=19.09.2022',
                    'parsed_data/data.json')
parser.start()

# Использование класса KeyRateOvernightCBRF для работы с данными
key_rate = KeyRateOvernightCBRF('parsed_data/data.json')
key_rate.load_data()

rate = key_rate.keyrateovernight_by_date('2022-04-07')
print(rate)

last_rate = key_rate.keyrateovernight_last()
print(last_rate)

range_rates = key_rate.keyrateovernight_range_dates('2022-04-07', '2022-04-13')
print(range_rates)





