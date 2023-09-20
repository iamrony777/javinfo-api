import requests


class R18:
    def __init__(self, base_url: str = "https://r18.dev") -> None:
        self.base_url = base_url
        self.client = requests.Session()

    def __getJsonResult(self):
        pass

    def search(self, code:str):
