"""
javdatabase.com scrapper
Author @github.com/iamrony777
"""

import json
import re
from urllib.parse import urljoin
from cloudscraper import create_scraper
from lxml import html

# from lxml.cssselect import CSSSelector


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
        self.parser = html.HTMLParser(encoding="UTF-8")

    def getJsonResult(self, code: str, page: html.HtmlElement):
        result = {"id": code}
        result["title"] = page.cssselect(".entry-header > h1")[0].text
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
                "div.movietable > table > tbody > tr:nth-child(10) > td:nth-child(2) > span > a"
            )[0].text
        except IndexError:
            pass
        return json.dumps(result, ensure_ascii=False, indent=2)

    async def search(self, code: str):
        """public method: search"""
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
                page=html.fromstring(
                    html=resp.content, base_url=self.base_url, parser=self.parser
                ),
            )


if __name__ == "__main__":
    import asyncio

    print(asyncio.run(Javdatabase().search("EBOD-391")))
