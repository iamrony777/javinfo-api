"""
javdatabase.com scrapper
Author @github.com/iamrony777
"""

from urllib.parse import urljoin
from cloudscraper import create_scraper
from lxml import html
from lxml.cssselect import CSSSelector


class Javdatabase:
    def __init__(self, base_url: str = "https://javdatabase.com/") -> None:
        self.base_url = base_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
            "Accept": "*/*",
        }
        self.client = create_scraper(
            browser={"browser": "chrome", "platform": "linux", "desktop": True}
        )

    def getJsonResult(self, code: str, page: bytes):
        resultObject = {
            id: code
        }
        resultObject['title'] = CSSSelector()
        pass

    async def search(self, code: str):
        """public method: search"""
        # code = code.lower()
        # resp = await self.client.get(f"movies/{code.lower()}")
        resp = self.client.get(
            urljoin(base=self.base_url, url=f"movies/{code.lower()}"),
            allow_redirects=True,
            timeout=5,
        )
        if not resp.ok:
            return {"statusCode": resp.status_code}
        else:
            return self.getJsonResult(
                code=code,
                page=html.fromstring(html=resp.content, base_url=self.base_url)
            )


if __name__ == "__main__":
    import asyncio

    print(asyncio.run(Javdatabase().search("MKCK-324")))
