"""Main srcaper - Javdb"""
import re
from os import getenv
from typing import Optional
from urllib.parse import urljoin

from api.resources import html, logger
from cloudscraper import create_scraper
from deep_translator import GoogleTranslator
from redis import Redis


class Javdb:
    def __init__(self, base_url: Optional[str] = None) -> None:
        self.base_url = self.base_url = [
            getenv("JAVDB_URL", "https://javdb.com/") if base_url is None else base_url
        ][0]
        self.cookies = {
            "theme": "auto",
            "locale": "en",
            "over18": "1",
            "remember_me_token": getenv(
                "REMEMBER_ME_TOKEN",
                default=(self._get_tokens("cookie/remember_me_token")),
            ),
            "_jdb_session": getenv(
                "JDB_SESSION", default=(self._get_tokens("cookie/_jdb_session"))
            ),
            "redirect_to": "/",
        }
        self.client = create_scraper(
            browser={"browser": "chrome", "platform": "linux", "desktop": True}
        )
        self.parser = html.HTMLParser(encoding="UTF-8")

    @logger.catch
    def _get_page_url(self, name: str, **kwargs) -> (str | None):
        """Get the page url."""
        response = self.client.get(
            urljoin(self.base_url, "/search"),
            params={"q": name, "f": "all", "locale": "en", "over18": 1},
            cookies=self.cookies,
            allow_redirects=True,
            timeout=30,
            **kwargs,
        )
        try:
            return (
                html.fromstring(response.content).find('.//a[@class="box"]').get("href")
            )
        except AttributeError:
            return None

    @logger.catch
    def _get_tokens(self, key: str) -> str | None:
        """Returns a token from redis."""
        with Redis.from_url(getenv("REDIS_URL"), decode_responses=True) as redis:
            return redis.get(key)

    @logger.catch
    async def _parse_tags(self, tree: html.HtmlElement) -> list[str] | None:
        """Get list of tags"""
        for element in tree.findall('.//div[@class="panel-block"]'):
            try:
                if element.find("strong").text.strip() == "Tags:":
                    return element.xpath("span/a/text()")
            except AttributeError:
                pass

    @logger.catch
    async def _parse_panel_data(self, tree: html.HtmlElement) -> dict[str] | None:
        """Extract additional data from the panel."""
        details, sorted_details = {}, {}
        data = tree.findall('.//div[@class="panel-block"]')
        for element in data:
            try:
                element_text = element.find("strong").text.strip()
                if element_text == "Director:":
                    details["director"] = GoogleTranslator(
                        source="auto", target="en"
                    ).translate(element.find("span/a").text.strip())
                elif element_text == "Released Date:":
                    details["release_date"] = element.find("span").text.strip()
                elif element_text == "Duration:":
                    details["runtime"] = element.find("span").text.strip().split(" ")[0]
                elif element_text == "Maker:":
                    details["studio"] = element.find("span/a").text.strip()
                elif element_text == "Rating:":
                    details["user_rating"] = (
                        element.xpath("span/text()")[-1].strip().split(",")[0]
                    )
            except AttributeError:
                pass
        for key, value in sorted(details.items()):
            sorted_details[key] = value

        return sorted_details

    @logger.catch
    async def search(self, name: str) -> dict[str] | None:
        """Main function to get video data from javdb.com."""
        try:

            page_url = self._get_page_url(name)
            if page_url is not None:
                movie_dictionary = {}
                # Fetch movie page, and start scraping
                response = self.client.get(
                    urljoin(self.base_url, page_url), cookies=self.cookies
                )
                tree = html.fromstring(response.content, parser=self.parser)
                try:
                    movie_code = tree.find('.//a[@title="Copy ID"]').get(
                        "data-clipboard-text"
                    )
                    # Get the movie_code
                    if movie_code == name:
                        movie_dictionary["id"] = movie_code
                        movie_title = re.sub(
                            rf"{movie_dictionary['id']} | JavDB, Online information source for adult movies",
                            "",
                            tree.find("head/title").text.strip(),
                        )
                        movie_dictionary["title"] = GoogleTranslator(
                            source="auto", target="en"
                        ).translate(movie_title.replace(" |", " ").strip())
                        movie_dictionary["poster"] = tree.find(
                            './/img[@class="video-cover"]'
                        ).get("src")
                        movie_dictionary["page"] = urljoin(self.base_url, page_url)
                        movie_dictionary["details"] = await self._parse_panel_data(tree)
                        movie_dictionary["screenshots"] = [
                            el.get("href")
                            for el in tree.findall('.//a[@data-fancybox="gallery"]')
                            if bool(re.match(r"https", el.get("href")))
                        ]
                        movie_dictionary["tags"] = await self._parse_tags(tree)

                        return movie_dictionary
                except AttributeError:
                    return None
        except Exception as exception:
            logger.error(exception)
            return None

