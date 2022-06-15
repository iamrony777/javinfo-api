import asyncio
import logging
import os

import httpx
from lxml import html
from redis import asyncio as aioredis

ACTRESS_DICTIONARY = {}

async def get_total_pages(client: httpx.AsyncClient) -> int:
    """Get the number of total pages"""
    tree = html.fromstring((await client.get('/')).content)
    return tree.xpath('//div[@class="cmn-list-pageNation02"]/ol/li/a/text()')[-1]


async def get_page_content(page: int, client: httpx.AsyncClient) -> bytes:
    """Send Request to get page"""
    return html.fromstring((await client.get('/', params={'page': page})).content)


async def parse_page_content(tree: html.HtmlElement) -> None:
    """Parse HTML content to JSON dict"""
    for result in tree.xpath('//img[@width="135"]'):
        name = str(result.get('alt'))
        non_string = []
        for char in name:
            if char != ' ' and not str.isalpha(char):
                non_string.append(char)
        if len(non_string) != 0:
            for char in non_string:
                name = name.replace(char, '')

        ACTRESS_DICTIONARY[name.strip()] = result.get('src')


async def main() -> None:
    """Get total page number -> send request to get page -> parse page -> create dictionary -> save to redis"""
    header = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'}
    url = 'https://www.r18.com/videos/vod/movies/actress'
    parse_tasks, get_page_tasks = [], []
    try:
        async with httpx.AsyncClient(base_url=url, http2=True, timeout=None, headers=header, follow_redirects=True) as client:
            total_pages = await get_total_pages(client)

            for page in range(1, int(total_pages) + 1):
                get_page_tasks.append(asyncio.create_task(
                    get_page_content(page, client)))
            for tree in await asyncio.gather(*get_page_tasks):
                parse_tasks.append(asyncio.create_task(
                    parse_page_content(tree)))

            await asyncio.gather(*parse_tasks)
    except Exception as exception_1:
        logging.error(exception_1)

    try:
        async with aioredis.from_url(os.getenv('REDIS_URL'), db=0, decode_responses=True) as redis:
            await redis.mset(ACTRESS_DICTIONARY)
            print('Saved to Redis')

    except Exception as exception_2:
        logging.error(exception_2)
if __name__ == '__main__':
    asyncio.run(main())
