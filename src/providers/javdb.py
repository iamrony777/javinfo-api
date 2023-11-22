"""
Javdb.com scrapper
Author @github.com/iamrony777
"""
import re
from os import getenv
from urllib.parse import urljoin
from googletrans import Translator
from lxml import html
from cloudscraper import create_scraper

class Javdb:
    """
    Simple Javdb API client.

    It provides methods to interact with the Javdb API and retrieve data.

    """

    def __init__(self, base_url: str = "https://www.javdb.com/") -> None:
        """
        Initializes the class with the given base URL.

        Parameters:
            base_url (str): The base URL to be used for the API requests. Defaults to "https://www.javdb.com/".

        Returns:
            None
        """
        self.base_url = base_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
            "Accept": "*/*",
        }
        self.cookies = {
            "theme": "auto",
            "locale": "en",
            "over18": "1",
            "remember_me_token": getenv("REMEMBER_ME_TOKEN"),
            "_jdb_session": getenv("JDB_SESSION"),
            "redirect_to": "/",
        }
        self.client = create_scraper(
            browser={"browser": "chrome", "platform": "linux", "desktop": True},
        )
        self.parser = html.HTMLParser(encoding="UTF-8")
        self.translator = Translator()

    def __fixPreivewUrl(self, url:str|None):
        if url:
            if url.startswith("//"):
                url = f"https:{url}"
            return url


    def __getJsonResult(self, page: html.HtmlElement):
        _id = page.xpath('//a[@title="Copy ID"]')[0].get('data-clipboard-text')

        result = { "id": _id}
        _title_ja = page.cssselect('div.video-detail > h2 > strong.current-title')[0].text

        result["title"] = self.translator.translate(_title_ja, dest='en').text
        result["title_ja"] = _title_ja
        result["page"] = page.xpath('//link[@rel="canonical"]')[0].get('href')
        result["poster"] = page.cssselect('div.column.column-video-cover > a > img')[0].get('src')
        result["preview"] = self.__fixPreivewUrl(page.cssselect("#preview-video > source")[0].get('src'))

        ## result.details
        result["details"] = {
            "director": None,
            "release_date": None,
            "runtime": None,
            "studio": None,
        }

        result["actress"] = []
        result["screenshots"] = []
        result["tags"] = []

        for item in page.xpath('//div/nav[@class="panel movie-panel-info"]/div'):
            try:
                if item.find('strong').text == 'Director:':
                    result["details"]["director"] = item.find('span/a').text

                if item.find('strong').text == 'Duration:':
                    result["details"]["runtime"] = re.match(pattern=r'\d+', string=item.find('span').text).group()

                if item.find('strong').text == 'Released Date:':
                    result["details"]["release_date"] = item.find('span').text

                if item.find('strong').text == 'Publisher:':
                    result["details"]["studio"] = item.find('span/a').text

                if item.find('strong').text == 'Actor(s):':
                    for actress in item.findall('span/a'):
                        # result["actress"].append(actress.find('a').text)
                        result["actress"].append(actress.text)

                if item.find('strong').text == 'Tags:':
                    for tag in item.findall('span/a'):
                        result["tags"].append(tag.text)

            except AttributeError:
                pass


        for item in page.xpath('//a[@class="tile-item"][@data-fancybox="gallery"]'):
            result["screenshots"].append(item.get('href'))



        return result
    def search(self, code: str) -> dict:
        """
        public method: search
        """
        resp = self.client.get(
            urljoin(self.base_url, "/search"),
            params={"q": code, "f": "all", "locale": "en", "over18": 1},
            allow_redirects=True,
            headers=self.headers,
            cookies=self.cookies,
            timeout=5,
        )

        if resp.ok:
            page: html.HtmlElement = html.fromstring(
                html=resp.content, base_url=self.base_url, parser=self.parser
            )

            for eachItem in page.cssselect("div > div.movie-list > div.item"):
                if code == eachItem.find('a/div[@class="video-title"]/strong').text: # when the code is found
                    resp = self.client.get(
                        url=urljoin(base=self.base_url, url=eachItem.find('a').get("href")),
                        allow_redirects=True,
                        headers=self.headers,
                        cookies=self.cookies,
                        timeout=5,
                    )
                    return self.__getJsonResult(
                        page=html.fromstring(
                            html=resp.content, base_url=self.base_url, parser=self.parser
                        ),
                    )
                return {"statusCode": 404, "message": "Not Found"}


        if not resp.ok:
            return {"statusCode": resp.status_code}




# if __name__ == "__main__":
    # import json

    # print(json.dumps(Javdb().search("EBOD-132"), indent=4, ensure_ascii=False))
