import re
from lxml import html
from urllib.parse import urljoin
from cloudscraper import create_scraper


class Javlibrary:
    def __init__(self, base_url: str = "https://www.javlibrary.com/en/") -> None:
        self.base_url = base_url
        self.client = create_scraper(
            browser={"browser": "chrome", "platform": "linux", "desktop": True}
        )

    def search(self, code: str):
        # first search for checking availability
        code = code.upper()
        resp = self.client.get(
            url=urljoin(base=self.base_url, url="vl_searchbyid.php"),
            params={"keyword": code},
            allow_redirects=True,
        )
        if resp.ok and bool(
            re.search(pattern=r"\?keyword=[a-zA-Z0-9]+", string=resp.url)
        ):  # duplicate or no results found
            page: html.HtmlElement = html.fromstring(html=resp.content, base_url=self.base_url)
            try: ## No result found
                return { "statusCode": 404, "error": page.cssselect("#rightcolumn > p > em")[0].text}
            except IndexError: ## Duplicate/Many results
                for each in page.cssselect("div.videothumblist > div.videos > div"):
                    if code == each.find('a/div').text:
                        url = urljoin(base=self.base_url, url=each.find("a").get("href"))
                return { "url": resp.url }

        elif resp.ok and bool(
            re.search(pattern=r"\?v=[a-zA-Z0-9]+", string=resp.url)
        ):  # redirected to actual page
            pass
        elif not resp.ok:
            return {"statusCode": resp.status_code, "url": resp.url}


if __name__ == "__main__":
    print(Javlibrary().search("SSIS-001"))
