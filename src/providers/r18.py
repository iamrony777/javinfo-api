import requests
from providers import CustomSession

class R18:
    def __init__(self, base_url: str = "https://r18.dev") -> None:
        self.base_url = base_url
        self.client = CustomSession(base_url=base_url)

    def __getJsonResult(self):
        pass

    def search(self, code:str):
        self.client.get(url=f"/videos/vod/movies/detail/-/dvd_id=${code}/json")
