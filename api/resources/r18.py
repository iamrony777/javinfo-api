"""Main srcaper - R18"""
import re

from api.resources import AsyncClient, actress_search, html, logger


async def fetch(name: str, url: str, client: AsyncClient) -> str | None:
    """Get contentname from search result."""
    response = await client.get(url)
    tree = html.fromstring(response.content)
    try:
        for item in tree.findall('.//li[@class="item-list"]'):
            if name == item.find("a/p/img").get("alt"):
                return item.get("data-content_id")
    except AttributeError:
        return None


async def movie_data(
    client: AsyncClient, content_id: str, only_r18: bool
) -> dict[str] | None:
    """Fetch data from r18.com's api."""
    response = await client.get(
        url=f"/api/v4f/contents/{content_id}", params={"lang": "en"}
    )
    if response.status_code == 200:
        response = response.json()["data"]
        base_details, extra_details = {}, {}
        actress_list = []

        base_details["id"] = response.get("dvd_id")
        base_details["title"] = response.get("title")
        base_details["poster"] = response.get("images").get("jacket_image").get("large")
        base_details["page"] = response.get("detail_url")

        extra_details["director"] = response.get("director")
        extra_details["release_data"] = response.get("release_date").split(" ")[0]
        extra_details["runtime"] = response.get("runtime_minutes")
        extra_details["studio"] = response.get("maker").get("name")

        base_details["details"] = extra_details

        temp_actresses = response.get("actresses")
        if temp_actresses is not None:
            for actresses in temp_actresses:
                if bool(re.search(r"\(", actresses["name"])):
                    for name in str(actresses["name"].replace(" (", ", ")).replace(")", "").split(", "):
                        actress_list.append(name)
                actress_list.append(actresses["name"].strip())

            base_details["actress"] = await actress_search(actress_list, only_r18)
        else:
            base_details["actress"] = [] # Add empty list for avoiding keyError

        temp_screenshots = response.get("gallery")
        if temp_screenshots is not None:
            screenshots = [
                screenshot[list(screenshot.keys())[0]]
                for screenshot in temp_screenshots
                if screenshot.get(list(screenshot.keys())[0]) is not None
            ]
            base_details["screenshots"] = screenshots
        else:
            base_details["screenshots"] = [] # Add empty list for avoiding keyError

        base_details["tags"] = [
            category["name"] for category in response["categories"]
        ]

        return base_details


@logger.catch
async def main(name: str, only_r18: bool = False) -> dict[str]:
    """Main Function to manage rest of the fucntion."""
    async with AsyncClient(
        base_url="https://www.r18.com", follow_redirects=True, timeout=20, http2=True
    ) as client:
        contentname = await fetch(
            name=name, url=f"/common/search/searchword={name}", client=client
        )
        if contentname is not None:
            return await movie_data(client, contentname, only_r18)


if __name__ == "__main__":
    import asyncio
    from json import dumps

    print(dumps(asyncio.run(main("EBOD-391")), indent=4))
