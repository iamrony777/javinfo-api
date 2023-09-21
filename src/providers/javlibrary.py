from urllib.parse import urljoin
from cloudscraper import create_scraper

class Javlibrary:
    def __init__(self, base_url: str = "https://www.javlibrary.com/en/") -> None:
        self.base_url = base_url
        self.client = create_scraper(
            browser={"browser": "chrome", "platform": "linux", "desktop": True}
        )