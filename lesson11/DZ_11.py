import requests


class SirotinskyAPI:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.token = self._get_token()

    def _get_token(self):
        url = "https://api.sirotinsky.com/Root/token"
        payload = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
            "scope": "",
            "client_id": "",
            "client_secret": ""
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()["access_token"]

    def get_hello_name(self, name):
        url = f"https://api.sirotinsky.com/Root/hello/{name}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_efrsb_manager(self, inn):
        url = f"https://api.sirotinsky.com/Root/hello/{self.token}/efrsb/manager/{inn}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_efrsb_trader(self, inn):
        url = f"https://api.sirotinsky.com/Root/hello/{self.token}/efrsb/trader/{inn}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_efrsb_person(self, inn):
        url = f"https://api.sirotinsky.com/Root/hello/{self.token}/efrsb/person/{inn}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_efrsb_organisation(self, inn):
        url = f"https://api.sirotinsky.com/Root/hello/{self.token}/efrsb/organisation/{inn}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_dadata_party(self, inn):
        url = f"https://api.sirotinsky.com/Root/hello/{self.token}/dadata/party/{inn}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

api = SirotinskyAPI("HSE_student", "123123123")

hello_name = api.get_hello_name("Kirill")
print(hello_name)

efrsb_manager = api.get_efrsb_manager("1234567890")
print(efrsb_manager)

dadata_party = api.get_dadata_party("9876543210")
print(dadata_party)

