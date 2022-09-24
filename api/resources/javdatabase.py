"""Main srcaper - Javdatabase"""
import re
from typing import Optional
from api.resources import AsyncClient, actress_search, html, logger


class Javdatabase:
    def __init__(self, base_url: Optional[str] = "https://www.javdatabase.com") -> None:
        self.base_url = base_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
            "Accept": "*/*",
        }
        self.client = AsyncClient(
            base_url=self.base_url,
            http2=True,
            headers=self.headers,
            follow_redirects=True,
            timeout=30,
        )

    @logger.catch
    async def _parse_details(
        self, tree: html.HtmlElement, only_r18: bool
    ) -> (dict[str, str] | None):
        """Parse movie details."""
        movie_dictionary = {}
        if not bool(re.search("Page Not Found", tree.find("head/title").text)):
            movie_dictionary["id"] = tree.find('.//h1[@class="display-1"]').text.strip()
            movie_dictionary["title"] = tree.find(
                './/td[@class="tablevalue"]'
            ).text.strip()
            movie_dictionary["poster"] = (
                tree.find('.//meta[@name="twitter:image"]').get("content").strip()
            )
            movie_dictionary["page"] = (
                tree.find('.//link[@rel="canonical"]').get("href").strip()
            )
            movie_dictionary["details"] = await self._parse_additional_details(tree)
            movie_dictionary["actress"] = await self._parse_actress_details(
                tree, only_r18
            )
            movie_dictionary["screenshots"] = [
                element.get("href")
                for element in tree.findall(".//div/a[@rel]")
                if bool(re.search(r"pics.dmm.co.jp", element.get("href")))
            ]
            movie_dictionary["tags"] = [
                tags.text.strip()
                for tags in tree.findall('.//td[@class="tablevalue"]/span/a')
                if bool(re.match(rf"{self.base_url}/genres", tags.get("href")))
            ]
            return movie_dictionary

    @logger.catch
    async def _parse_additional_details(
        self,
        tree: html.HtmlElement,
    ) -> (dict[str, str] | None):
        """Parse additional details(director, studio etc)."""
        details, sorted_details = {}, {}
        for parent in tree.xpath("//tr"):
            try:
                key = str(parent.find('td[@class="tablelabel"]/h3/b').text.strip())
                value = str(parent.find('td[@class="tablevalue"]').text.strip())
                details["director"] = (
                    value
                    if bool(re.search("Director", key)) and len(value) > 0
                    else None
                )
                details["release_date"] = (
                    value
                    if bool(re.search("Release Date", key)) and len(value) > 0
                    else None
                )
                if bool(re.search("Studio", key)):
                    value = parent.find('td[@class="tablevalue"]/span/a').text.strip()
                    details["studio"] = value if len(value) > 0 else None
                if bool(re.search("Runtime", key)):
                    value = value.split(" ")[0]
                    details["runtime"] = value if len(value) > 0 else None
            except AttributeError:
                pass
        for key, value in sorted(details.items()):
            sorted_details[key] = value

        return sorted_details

    @logger.catch
    async def _parse_actress_details(
        self, tree: html.HtmlElement, only_r18: bool
    ) -> (dict[str, str] | None):
        """Parse actress details."""
        actress_list = []
        for actress_elements in tree.findall(
            './/div[@class="flex-container-idols images"]/div/figure'
        ):
            actress_list.append(actress_elements.find("a/img").get("alt"))
        actress_details = await actress_search(actress_list, only_r18)
        return actress_details

    @logger.catch
    async def search(self, name: str, only_r18: bool = False) -> dict[str] | None:
        """search function."""
        resp = await self.client.get(f"/movies/{name.lower()}")
        if resp.status_code == 200:
            tree = html.fromstring(resp.content)
            details = await self._parse_details(tree, only_r18)
            if details is not None:
                return details
            return
        return
