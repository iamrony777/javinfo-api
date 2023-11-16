"""
An api wrapper of Boobpedia (https://www.boobpedia.com/boobs/Main_Page)
"""

from datetime import datetime
from urllib.parse import urljoin
from cloudscraper import create_scraper
from lxml import html


class Boobpedia:
    def __init__(self, base_url: str = "https://www.boobpedia.com") -> None:
        self.base_url = base_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
            "Accept": "*/*",
        }
        self.client = create_scraper(
            browser={"browser": "chrome", "platform": "linux", "desktop": True}
        )
        self.parser = html.HTMLParser(encoding="UTF-8")

    # def __main_page(self):

    ## interesting links
    # 1. Today's birthday (/Category:October_9_birthdays)

    def todaysBirthdays(self):
        result = []
        curr = datetime.now()
        url = urljoin(
            base=self.base_url,
            url=f'/boobs/Category:{curr.strftime("%B")}_{curr.day}_birthdays',
        )

        response = self.client.get(url, timeout=5)
        response: html.HtmlElement = html.fromstring(
            html=response.content, base_url=self.base_url, parser=self.parser
        )

        for el in response.xpath("//div[@class='mw-category']/*/ul/li/a"):
            result.append(
                {
                    "name": el.text,
                    "link": urljoin(base=self.base_url, url=el.get("href")),
                }
            )

        return result


if __name__ == "__main__":
    import asyncio
    from rich import print

    boobpedia = Boobpedia()
    print(boobpedia.todaysBirthdays())
