import re
from lxml import html
from urllib.parse import urljoin
from cloudscraper import create_scraper


class Javlibrary:
    def __init__(self, base_url: str = "https://www.javlibrary.com/en/") -> None:
        self.base_url = base_url
        self.parser = html.HTMLParser(encoding="UTF-8")
        self.client = create_scraper(
            browser={"browser": "chrome", "platform": "linux", "desktop": True},
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
        result["poster"] = page.cssselect("#video_jacket_img")[0].get('src')
        return result

    def search(self, code: str):
        # first search for checking availability
        code = code.upper()
        resp = self.client.get(
            url=urljoin(base=self.base_url, url="vl_searchbyid.php"),
            params={"keyword": code},
            cookies={"over18": "18"},
            allow_redirects=True,
        )
        if resp.ok and bool(
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
                                cookies={"over18": "18"},
                                allow_redirects=True,
                            ),
                            allow_redirects=True,
                        )
                        return self.__getJsonResult(
                            page=html.fromstring(
                                html=resp.content,
                                base_url=self.base_url,
                                parser=self.parser,
                            )
                        )

        elif resp.ok and bool(
            re.search(pattern=r"\?v=[a-zA-Z0-9]+", string=resp.url)
        ):  # redirected to actual page
            return self.__getJsonResult(
                page=html.fromstring(
                    html=resp.content,
                    base_url=self.base_url,
                    parser=self.parser,
                )
            )
        elif not resp.ok:
            return {"statusCode": resp.status_code, "url": resp.url}


if __name__ == "__main__":
    print(Javlibrary().search("EBOD-875"))
