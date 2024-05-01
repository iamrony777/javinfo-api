"""
javdatabase.com scrapper
Author @github.com/iamrony777
"""

import json
import logging
import re
from urllib.parse import urljoin
from cloudscraper import create_scraper
from lxml import html
from os.path import basename, splitext


class Javdatabase:
    """
    Scrapes from javdatabase.com (default url)

    constuctor:
        base_url: str = "https://javdatabase.com/"

    methods:
        search(code: str) -> providerResponse

    """

    def __init__(self, base_url: str = "https://javdatabase.com/") -> None:
        # __handler = logging.StreamHandler()
        # __handler.setLevel(logging.DEBUG)
        # __handler.setFormatter(
        #     logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        # )
        self.base_url = base_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
            "Accept": "*/*",
        }
        self.client = create_scraper(
            browser={"browser": "chrome", "platform": "linux", "desktop": True},
        )
        self.parser = html.HTMLParser(encoding="UTF-8")
        self.logger = logging.getLogger(splitext(basename(__file__))[0])
        # self.logger.addHandler(__handler)
        self.logger.setLevel(logging.DEBUG)

    def __getJsonResult(self, code: str, page: html.HtmlElement):
        result = {"id": code}
        result["title"] = page.cssselect(".entry-header > h1")[0].text.replace(
            f"{code} - ", ""
        )
        result["title_ja"] = None
        result["page"] = urljoin(base=self.base_url, url=f"movies/{code.lower()}/")

        ## result.poster
        try:
            result["poster"] = page.xpath('//meta[@property="og:image"]')[0].get(
                "content"
            )
        except IndexError:
            try:
                result["poster"] = page.xpath('//meta[@name="twitter:image"]')[0].get(
                    "content"
                )
            except IndexError:
                result["poster"] = None

        ## result.preview
        try:
            result["preview"] = page.xpath("//iframe")[0].get("src")
        except IndexError:
            result["preview"] = None

        ## result.details
        result["details"] = {
            "director": None,
            "release_date": None,
            "runtime": None,
            "studio": None,
        }
        ### result.details.director
        try:
            result["details"]["director"] = page.cssselect(
                "div.movietable > table > tr:nth-child(11) > td:nth-child(2) > span > a"
            )[0].text
        except IndexError:
            pass

        ## result.details.release_date
        try:
            result["details"]["release_date"] = page.cssselect(
                "div.movietable > table > tr:nth-child(14) > td:nth-child(2)"
            )[0].text
        except IndexError:
            pass

        ## result.details.runtime
        try:
            result["details"]["runtime"] = re.match(
                r"\d+",
                page.cssselect(
                    "div.movietable > table > tr:nth-child(15) > td:nth-child(2)"
                )[0].text,
            )[0]
        except IndexError:
            pass
        ## result.details.studio
        try:
            result["details"]["studio"] = page.cssselect(
                "div.movietable > table > tr:nth-child(10) > td:nth-child(2) > span > a"
            )[0].text
        except IndexError:
            pass

        ## result.actress
        result["actress"] = []
        try:
            for actr in page.cssselect("div.idol-thumb > a > img"):
                result["actress"].append(
                    {"name": actr.attrib["alt"], "image": actr.attrib["data-src"]}
                )
        except KeyError:
            pass

        ## result.screenshots
        result["screenshots"] = []

        el = (
            2 if not result["actress"] else 3
        )  ## if actress section is not available then screenshot section changes it position
        try:
            for ss in page.cssselect(f".entry-content > div:nth-child({el}) > a"):
                result["screenshots"].append(ss.attrib["href"])
        except KeyError:
            pass

        ## result.tags
        result["tags"] = []
        try:
            _ = 7
            while True:
                for tags in page.cssselect(
                    f"div.movietable > table > tr:nth-child({_}) > td:nth-child(2) > span > a"  # change value of tr:nth-child() if tags arent available
                ):
                    result["tags"].append(tags.text.strip())

                if result["tags"]:
                    break
                _ += 1
        except KeyError:
            self.logger.debug("keyerror:tags")
        return result

    def search(self, code: str) -> dict:
        """public method: search"""
        resp = self.client.get(
            urljoin(base=self.base_url, url=f"movies/{code.lower()}"),
            allow_redirects=True,
            timeout=5,
        )
        self.logger.debug("search:status_code: %s", resp.status_code)

        if not resp.ok:
            return {"statusCode": resp.status_code}
        else:
            return self.__getJsonResult(
                code=code,
                page=html.fromstring(
                    html=resp.content, base_url=self.base_url, parser=self.parser
                ),
            )


if __name__ == "__main__":
    print(json.dumps(Javdatabase().search("MFOD-023"), ensure_ascii=False, indent=2))
