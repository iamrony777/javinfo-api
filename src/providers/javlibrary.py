"""
Javlibrary.com/en/ scrapper
Author @github.com/iamrony777
"""

import re
import os
from lxml import html
from urllib.parse import urljoin

# from cloudscraper import create_scraper
from httpx import Client
from src.common.trailer import getPreview

class Javlibrary:
    """
    Simple Javlibrary API client.

    It provides methods to interact with the Javlibrary API and retrieve data.

    """

    def __init__(self, base_url: str = "https://www.javlibrary.com/en/") -> None:
        """
        Initializes the class with the given base URL.

        Parameters:
            base_url (str): The base URL to be used for the API requests. Defaults to "https://www.javlibrary.com/en/".

        Returns:
            None
        """
        self.base_url = base_url
        self.parser = html.HTMLParser(encoding="UTF-8")
        # self.client = create_scraper(
        #     browser={"browser": "chrome", "platform": "linux", "desktop": True},
        # )
        self.client = Client(
            verify=False,
            timeout=60,
            http2=True,
            headers={
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            },
        )

        if os.getenv("HTTP_PROXY"):
            self.client.proxies.update(
                {
                    "http://": os.getenv("HTTP_PROXY"),
                }
            )

        if os.getenv("HTTPS_PROXY"):
            self.client.proxies.update(
                {
                    "https://": os.getenv("HTTPS_PROXY"),
                }
            )

    def __getJapanesePage(self, url: str) -> html.HtmlElement:
        return html.fromstring(
            html=self.client.get(
                url=urljoin(base="https://www.javlibrary.com/ja/", url=url),
                cookies={"over18": "18"},
                allow_redirects=True,
            ).content,
            base_url=urljoin(base="https://www.javlibrary.com/ja/", url=url),
            parser=self.parser,
        )

    def __getJsonResult(self, page: html.HtmlElement):
        _id = page.cssselect("#video_id > table > tr > td.text")[0].text

        result = {"id": _id}
        result["title"] = page.cssselect("#video_title > h3 > a")[0].text.replace(
            f"{_id} ", ""
        )
        result["title_ja"] = (
            self.__getJapanesePage(
                page.cssselect("#video_title > h3 > a")[0]
                .get("href")
                .replace("/en/", "./")
            )
            .cssselect("#video_title > h3 > a")[0]
            .text.replace(f"{_id} ", "")
        )
        result["page"] = urljoin(
            base=self.base_url,
            url=page.cssselect("#video_title > h3 > a")[0].get("href"),
        )
        result["poster"] = page.cssselect("#video_jacket_img")[0].get("src")
        result["preview"] = (
            getPreview(
                page.cssselect("div.previewthumbs > a.btn_videoplayer")[0].get(
                    "attr-data"
                )
            )
            if page.cssselect("div.previewthumbs > a.btn_videoplayer")
            else None
        )

        ## result.details
        result["details"] = {
            "director": None,
            "release_date": None,
            "runtime": None,
            "studio": None,
        }

        try:
            result["details"]["director"] = page.xpath(
                '//td/span[@class="director"]/a/text()'
            )[0].strip()
        except IndexError:
            pass

        try:
            result["details"]["runtime"] = int(
                page.cssselect("#video_length > table > tr > td:nth-child(2) > span")[
                    0
                ].text
            )
        except IndexError:
            pass

        try:
            result["details"]["release_date"] = page.cssselect(
                "#video_date > table > tr > td.text"
            )[0].text.strip()
        except IndexError:
            pass

        try:
            result["details"]["studio"] = page.xpath(
                '//td/span[@class="maker"]/a/text()'
            )[0]
        except IndexError:
            pass

        result["actress"] = []
        try:
            for act in page.xpath('//*/span[@class="star"]'):
                result["actress"].append({"name": act.find("a").text, "image": None})
        except TypeError:
            pass

        result["screenshots"] = []
        try:
            for ss in page.cssselect("div.previewthumbs > a"):
                if ss.get("href") != "#":
                    result["screenshots"].append(ss.get("href"))
        except [IndexError, TypeError, KeyError]:
            pass

        result["tags"] = []
        try:
            for t in page.cssselect("#video_genres > table > tr > td.text > span > a"):
                result["tags"].append(t.text)
        except [IndexError, TypeError, KeyError]:
            pass
        return result

    def search(self, code: str) -> dict:
        """
        Searches by Movie Code

        Args:
            code (str): The code to search for. (Format: XXX-000)

        Returns:
            dict: A dictionary containing the search result. If the code is not found,
            the dictionary contains the following keys:
                - "statusCode": The status code of the search request (404).
                - "error": The error message indicating that no result was found.
            If the code is found, the dictionary contains the search result in JSON format.

        Raises:
            None
        """
        # first search for checking availability
        code = code.upper()
        resp = self.client.get(
            url=urljoin(base=self.base_url, url="vl_searchbyid.php"),
            params={"keyword": code},
            cookies={"over18": "18"},
            allow_redirects=True,
        )
        if resp.status_code == 200 and bool(
            re.search(pattern=r"\?keyword=[a-zA-Z0-9]+", string=resp.url)
        ):  # duplicate or no results found
            page: html.HtmlElement = html.fromstring(
                html=resp.content, base_url=self.base_url
            )
            try:  ## No result found
                return {
                    "statusCode": 404,
                    "error": page.cssselect("#rightcolumn > p > em")[0].text,
                }
            except IndexError:  ## Duplicate/Many results
                for each in page.cssselect("div.videothumblist > div.videos > div"):
                    if code == each.find("a/div").text:
                        resp = self.client.get(
                            url=urljoin(
                                base=self.base_url,
                                url=each.find("a").get("href"),
                            ),
                            cookies={"over18": "18"},
                            allow_redirects=True,
                            timeout=5,
                        )
                        return self.__getJsonResult(
                            page=html.fromstring(
                                html=resp.content,
                                base_url=self.base_url,
                                parser=self.parser,
                            )
                        )
                    continue
        elif resp.status_code == 200 and bool(
            re.search(pattern=r"\?v=[a-zA-Z0-9]+", string=resp.url)
        ):  # redirected to actual page
            return self.__getJsonResult(
                page=html.fromstring(
                    html=resp.content,
                    base_url=self.base_url,
                    parser=self.parser,
                )
            )
        elif not resp.status_code == 200:
            return {"statusCode": resp.status_code, "url": str(resp.url)}


if __name__ == "__main__":
    print(Javlibrary().search("SSIS-001"))
