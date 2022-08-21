"""Main srcaper - Javdb"""
import os
import re

from deep_translator import GoogleTranslator
from redis import asyncio as aioredis

from api.resources import AsyncClient, html, logger

BASE_URL = "https://javdb.com"


async def get_page_url(client: AsyncClient, name: str, **kwargs) -> (str | None):
    """Get the page url from javdb.com."""
    response = await client.get(
        "/search", params={"q": name, "f": "all", "locale": "en", "over18": 1}, **kwargs
    )
    try:
        return html.fromstring(response.content).find('.//a[@class="box"]').get("href")
    except AttributeError:
        return None


async def get_tokens(key: str) -> (str | None):
    """Returns a token from redis."""
    async with aioredis.Redis.from_url(
        os.getenv("REDIS_URL"), decode_responses=True
    ) as redis:
        return await redis.get(key)


async def parse_tags(tree: html.HtmlElement) -> list[str] | None:
    """Get list of tags"""
    for element in tree.findall('.//div[@class="panel-block"]'):
        try:
            if element.find("strong").text.strip() == "Tags:":
                return element.xpath("span/a/text()")
        except AttributeError:
            pass


async def parse_panel_data(tree: html.HtmlElement) -> dict[str, str | None]:
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


async def main(name: str) -> dict[str] | None:
    """Main function to get video data from javdb.com."""
    cookies = {
        "theme": "auto",
        "locale": "en",
        "over18": "1",
        "remember_me_token": os.getenv(
            "REMEMBER_ME_TOKEN", default=(await get_tokens("cookie/remember_me_token"))
        ),
        "_jdb_session": os.getenv(
            "JDB_SESSION", default=(await get_tokens("cookie/_jdb_session"))
        ),
        "redirect_to": "%2F",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
        "Accept": "*/*",
    }
    async with AsyncClient(
        base_url=BASE_URL,
        http2=True,
        follow_redirects=True,
        timeout=20,
        headers=headers,
        cookies=cookies,
    ) as client:
        try:
            parser = html.HTMLParser(encoding="UTF-8")
            page_url = await get_page_url(client, name)
            if page_url is not None:
                movie_dictionary = {}
                # Fetch movie page, and start scraping
                response = await client.get(page_url)
                tree = html.fromstring(response.content, parser=parser)
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
                        movie_dictionary["page"] = BASE_URL + page_url
                        movie_dictionary["details"] = await parse_panel_data(tree)
                        movie_dictionary["screenshots"] = [
                            el.get("href")
                            for el in tree.findall('.//a[@data-fancybox="gallery"]')
                            if bool(re.match(r"https", el.get("href")))
                        ]
                        movie_dictionary["tags"] = await parse_tags(tree)

                        return movie_dictionary
                except AttributeError:
                    return None
        except Exception as exception:
            logger.error(exception)
            return None


if __name__ == "__main__":
    from pprint import pprint
    from asyncio import run

    pprint(run(main("EBOD-391")))
