# Its messy but it works, and takes less time so i wont change it
import asyncio
import os
import re

from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from httpx import AsyncClient
from redis import asyncio as aioredis

BASE_URL = "https://javdb.com"


async def get_page_url(client: AsyncClient, name: str, **kwargs) -> (str | None):
    """Get the page url from javdb.com"""

    response = await client.get(
        "/search", params={"q": name, "f": "all", "locale": "en", "over18": 1}, **kwargs
    )
    try:
        return BeautifulSoup(response.text, "lxml").find("a", class_="box").get("href")
    except AttributeError:
        return None


async def get_tokens(key: str) -> (str | None):
    """Returns a token from redis"""
    async with aioredis.Redis.from_url(
        os.getenv("REDIS_URL"), decode_responses=True, db=2
    ) as redis:
        return await redis.get(key)


async def parse_panel_data(soup: BeautifulSoup) -> dict[str, str | None]:
    """Extract additional data from the panel"""
    details, sorted_details = {}, {}
    data = soup.find_all("div", class_="panel-block")
    for element in data:
        try:
            element_text = element.strong.text.strip()
            if element_text == "Director:":
                details["director"] = GoogleTranslator(
                    source="auto", target="en"
                ).translate(element.span.text.strip())
            elif element_text == "Released Date:":
                details["release_date"] = element.span.text.strip()
            elif element_text == "Duration:":
                details["runtime"] = element.span.text.strip().split(" ")[0]
            elif element_text == "Maker:":
                details["studio"] = element.span.text.strip()
            elif element_text == "Rating:":
                details["user_rating"] = element.span.text.strip().split(",")[
                    0]
        except AttributeError:
            pass

    for key, value in sorted(details.items()):
        sorted_details[key] = value

    return sorted_details


async def main(name: str) -> dict[str]:
    """Main function to get video data from javdb.com"""
    cookies = {
        "theme": "auto",
        "locale": "en",
        "over18": "1",
        "remember_me_token": await get_tokens("remember_me_token"),
        "_jdb_session": await get_tokens("_jdb_session"),
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
        page_url = await get_page_url(client, name)
        if page_url is not None:
            movie_dictionary = {}
            # Fetch movie page, and start scraping
            response = await client.get(page_url)
            soup = BeautifulSoup(response.text, "lxml")
            movie_code = soup.find("a", {"title": "Copy ID"}).get(
                "data-clipboard-text"
            )  # Get the movie_code
            if movie_code == name:
                movie_dictionary["id"] = movie_code
                movie_title = re.sub(
                    rf"{movie_dictionary['id']} | JavDB, Online information source for adult movies",
                    "",
                    soup.title.text.strip(),
                )
                movie_dictionary["title"] = GoogleTranslator(
                    source="auto", target="en"
                ).translate(movie_title.replace(" |", " ").strip())
                movie_dictionary["poster"] = soup.find("img", class_="video-cover").get(
                    "src"
                )
                movie_dictionary["page"] = BASE_URL + page_url
                movie_dictionary["details"] = await parse_panel_data(soup)
                tags = soup.find_all(
                    "a", {"href": re.compile(r"/tags\?c")}
                )  # Get tags list
                tags = [tag.text for tag in tags]
                tags.remove("Tags")
                movie_dictionary["tags"] = tags

                return movie_dictionary


# Testing
if __name__ == "__main__":
    import json
    print(json.dumps(asyncio.run(main("FOW-001")), indent=4, ensure_ascii=False))
