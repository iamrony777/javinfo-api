#!/usr/bin/env python3
"""Scraps all Actress's name and profile photo from r18's actress section and saves them into database"""
import asyncio
import json
import os
import sys
import time
from datetime import datetime

import httpx
import uvloop
from lxml import html
from redis.asyncio import Redis

from api import logger

ACTRESS_DICTIONARY = {}

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
start_time = time.perf_counter()


async def get_total_pages(client: httpx.AsyncClient) -> int:
    """Get the number of total pages."""
    tree = html.fromstring((await client.get("/")).content)
    return tree.xpath('//div[@class="cmn-list-pageNation02"]/ol/li/a/text()')[-1]


async def get_page_content(page: int, client: httpx.AsyncClient) -> bytes:
    """Send Request to get page."""
    return html.fromstring((await client.get("/", params={"page": page})).content)


async def parse_page_content(tree: html.HtmlElement) -> None:
    """Parse HTML content to JSON dict."""
    for result in tree.findall(".//li/a/p/img"):
        name = "".join(
            filter(
                lambda char: char.isspace() or char.isalpha(), str(result.get("alt"))
            )
        )
        ACTRESS_DICTIONARY["actress/" + name.strip()] = result.get("src")


async def parse_snippet(client: httpx.AsyncClient, start: int, end: int) -> None:
    """just an extra function to remove repetition"""
    get_page_tasks = [
        asyncio.create_task(get_page_content(page, client))
        for page in range(start, end + 1)
    ]

    parse_tasks = [
        asyncio.create_task(parse_page_content(tree))
        for tree in await asyncio.gather(*get_page_tasks)
    ]
    await asyncio.gather(*parse_tasks)
    del get_page_tasks, parse_tasks


@logger.catch
async def main() -> None:
    """Get total page number -> send request to get page -> parse page -> create dictionary -> save to redis."""
    header = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
    }
    url = "https://www.r18.com/videos/vod/movies/actress"
    async with httpx.AsyncClient(
        base_url=url, http2=True, timeout=None, headers=header, follow_redirects=True
    ) as client:
        total_pages = int(await get_total_pages(client))
        start, end = 1, 100  # 100 pages per batch

        for _ in range(total_pages // end):
            await parse_snippet(client, start, end)
            start += 100
            end = total_pages if end + 100 > total_pages else end + 100

        if start != end:
            await parse_snippet(client, start, end)

    async with Redis.from_url(
        os.getenv("REDIS_URL"),
        decode_responses=True,
    ) as redis:
        await redis.mset(ACTRESS_DICTIONARY)

    async with Redis.from_url(os.getenv("REDIS_URL"), decode_responses=True) as redis:
        end_time = time.perf_counter()
        log = json.dumps(
            {
                "pages": str(total_pages),
                "actresses": len(ACTRESS_DICTIONARY),
                "finished in": f"{end_time - start_time:.2f}s",
                "time": datetime.now().strftime("%d/%m/%Y - %H:%M:%S%z"),
            }
        )

        await redis.rpush("log/r18_db", log)
        logger.success(
            f"[R18_DB] Database Updated, Actress Count: {len(ACTRESS_DICTIONARY)}"
        )
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
