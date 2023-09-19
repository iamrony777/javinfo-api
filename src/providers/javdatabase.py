"""
javdatabase.com scrapper
Author @github.com/iamrony777
"""

from httpx import AsyncClient

class Javdatabase:
    def __init__(self, base_url: str = "https://www.javdatabase.com" ) -> None:
        self.base_url = base_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
            "Accept": "*/*",
        }

        self.client = AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            http2=True,
            follow_redirects=True,
            timeout=5,
        )

javdatabase = Javdatabase()
print(javdatabase.base_url)