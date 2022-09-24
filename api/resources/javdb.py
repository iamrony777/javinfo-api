"""Main srcaper - Javdb"""
import os
import re
from typing import Optional

from api.resources import AsyncClient, html, logger
from deep_translator import GoogleTranslator
from redis import Redis


class Javdb:
    def __init__(self, base_url: Optional[str] = "https://javdb.com") -> None:
        self.base_url = base_url
        self.cookies = {
            "theme": "auto",
            "locale": "en",
            "over18": "1",
            "remember_me_token": os.getenv(
                "REMEMBER_ME_TOKEN",
                default=(self._get_tokens("cookie/remember_me_token")),
            ),
            "_jdb_session": os.getenv(
                "JDB_SESSION", default=(self._get_tokens("cookie/_jdb_session"))
            ),
            "redirect_to": "/",
        }
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
            "Accept": "*/*",
        }
        self.client = AsyncClient(
            base_url=self.base_url,
            http2=True,
            follow_redirects=True,
            timeout=20,
            headers=self.headers,
            cookies=self.cookies,
        )
        self.parser = html.HTMLParser(encoding="UTF-8")

    @logger.catch
    async def _get_page_url(self, name: str, **kwargs) -> (str | None):
        """Get the page url."""
        response = await self.client.get(
            "/search",
            params={"q": name, "f": "all", "locale": "en", "over18": 1},
            **kwargs,
        )
        try:
            return (
                html.fromstring(response.content).find('.//a[@class="box"]').get("href")
            )
        except AttributeError:
            return None

    @logger.catch
    def _get_tokens(self, key: str) -> (str | None):
        """Returns a token from redis."""
        with Redis.from_url(os.getenv("REDIS_URL"), decode_responses=True) as redis:
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
    async def _parse_panel_data(self, tree: html.HtmlElement) -> dict[str, str | None]:
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

            page_url = await self._get_page_url(name)
            if page_url is not None:
                movie_dictionary = {}
                # Fetch movie page, and start scraping
                response = await self.client.get(page_url)
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
                        movie_dictionary["page"] = self.base_url + page_url
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


if __name__ == "__main__":
    import asyncio

    from rich import print
    print(asyncio.run(Javdb().search("FOW-001")))
