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
        resp = self.client.get(
            url=urljoin(base=self.base_url, url="vl_searchbyid.php"),
            params={"keyword": code.upper()},
            allow_redirects=True,
        )
        print({"statusCode": resp.status_code, "url": resp.url})
        return resp.ok


if __name__ == "__main__":
    print(Javlibrary().search("SSIS-001"))
