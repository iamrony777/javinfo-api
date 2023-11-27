"""
Javdb.com scrapper
Author @github.com/iamrony777
"""
import difflib
import re
from os import getenv
from urllib.parse import quote, urljoin
from googletrans import Translator
from lxml import html
from cloudscraper import create_scraper
from os.path import basename, splitext
import logging


class Javdb:
    """
    Simple Javdb API client.

    It provides methods to interact with the Javdb API and retrieve data.

    """

    def __init__(self, base_url: str = "https://javdb.com/") -> None:
        """
        Initializes the class with the given base URL.

        Parameters:
            base_url (str): The base URL to be used for the API requests. Defaults to "https://javdb.com/".

        Returns:
            None
        """
        __handler = logging.StreamHandler()
        __handler.setLevel(logging.DEBUG)
        __handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))

        self.base_url = base_url
        self.cookies = {
            "redirect_to": "/",
            "theme": "auto",
            "locale": "en",
            "over18": "1",
            "remember_me_token": quote(getenv("REMEMBER_ME_TOKEN")),
            "_jdb_session": quote(getenv("JDB_SESSION")),
        }
        self.client = create_scraper(
            browser={"browser": "chrome", "platform": "linux", "desktop": True},
        )
        self.parser = html.HTMLParser(encoding="UTF-8")
        self.translator = Translator()

        self.logger = logging.getLogger(splitext(basename(__file__))[0])
        self.logger.addHandler(__handler)
        self.logger.setLevel(logging.DEBUG)

    def __fixPreivewUrl(self, url: str | None):
        if url:
            if url.startswith("//"):
                url = f"https:{url}"
            return url

    def __getJsonResult(self, page: html.HtmlElement):
        _id = page.xpath('//a[@title="Copy ID"]')[0].get("data-clipboard-text")

        result = {"id": _id}
        _title_ja = page.cssselect("div.video-detail > h2 > strong.current-title")[
            0
        ].text

        result["title"] = self.translator.translate(_title_ja, dest="en").text
        result["title_ja"] = _title_ja
        result["page"] = page.xpath('//link[@rel="canonical"]')[0].get("href")
        result["poster"] = page.cssselect("div.column.column-video-cover > a > img")[
            0
        ].get("src")
        result["preview"] = self.__fixPreivewUrl(
            page.cssselect("#preview-video > source")[0].get("src")
        )

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
                if item.find("strong").text == "Director:":
                    result["details"]["director"] = item.find("span/a").text

                if item.find("strong").text == "Duration:":
                    result["details"]["runtime"] = re.match(
                        pattern=r"\d+", string=item.find("span").text
                    ).group()

                if item.find("strong").text == "Released Date:":
                    result["details"]["release_date"] = item.find("span").text

                if item.find("strong").text == "Publisher:":
                    result["details"]["studio"] = item.find("span/a").text

                if item.find("strong").text == "Actor(s):":
                    for actress in item.findall("span/a"):
                        # result["actress"].append(actress.find('a').text)
                        result["actress"].append({ "name": actress.text, "image": None})

                if item.find("strong").text == "Tags:":
                    for tag in item.findall("span/a"):
                        result["tags"].append(tag.text)

            except AttributeError:
                pass

        for item in page.xpath('//a[@class="tile-item"][@data-fancybox="gallery"]'):
            result["screenshots"].append(item.get("href"))

        return result

    def search(self, code: str) -> dict:
        """
        public method: search
        """
        resp = self.client.get(
            urljoin(self.base_url, "/search"),
            params={"q": code, "f": "all", "locale": "en", "over18": 1},
            cookies=self.cookies,
            allow_redirects=True,
            timeout=5,
        )


        resultObj = []

        if resp.status_code == 200:
            self.logger.debug('search:status_code: 200')
            page: html.HtmlElement = html.fromstring(
                html=resp.content, base_url=self.base_url, parser=self.parser
            )

            for eachItem in page.cssselect("div > div.movie-list > div.item"):
                # save results for getting the closest match
                resultObj.append(
                    {
                        "id": eachItem.find('a/div[@class="video-title"]/strong').text,
                        "url": eachItem.find("a").get("href"),
                    }
                )
                if (
                    code == eachItem.find('a/div[@class="video-title"]/strong').text
                ):  # when the code is found
                    self.logger.debug('search:code: found')
                    resp = self.client.get(
                        urljoin(base=self.base_url, url=eachItem.find("a").get("href")),
                        cookies=self.cookies,
                        allow_redirects=True,
                        timeout=5,
                    )
                    self.logger.debug('search:code: scraped')
                    return self.__getJsonResult(
                        page=html.fromstring(
                            html=resp.content,
                            base_url=self.base_url,
                            parser=self.parser,
                        ),
                    )

            # get the most similar
            most_similar = difflib.get_close_matches(
                code, [i["id"] for i in resultObj], n=1, cutoff=0.6
            )
            if most_similar:

                self.logger.debug('search:most_similar: found %s', most_similar[0])
                resp = self.client.get(
                    urljoin(
                        base=self.base_url,
                        url=next(obj['url'] for obj in resultObj if obj['id'] == most_similar[0]),
                    ),
                    cookies=self.cookies,
                    allow_redirects=True,
                    timeout=5,
                )

                if bool(
                    re.search(pattern=r"plans", string=resp.url)
                ):

                    self.logger.error('search:most_similar: vip required')
                    return {
                        "statusCode": 402,
                        "message": "VIP permission is required to watch the movie",
                    }

                self.logger.debug('search:most_similar: scraped')
                return self.__getJsonResult(
                    page=html.fromstring(
                        html=resp.content,
                        base_url=self.base_url,
                        parser=self.parser,
                    ),
                )

            self.logger.debug('search:code: not found')
            return {"statusCode": 404, "message": "Not Found"}

        if not resp or resp.status_code != 200:
            self.logger.debug('search:code:status: %s', resp.status_code)
            return {"statusCode": resp.status_code}


if __name__ == "__main__":
    import json
    from dotenv import load_dotenv

    load_dotenv(".env")
    print(json.dumps(Javdb().search("FC2 3185212"), indent=4, ensure_ascii=False))
