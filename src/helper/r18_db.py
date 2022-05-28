import asyncio
import os
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from redis import asyncio as aioredis
from bs4 import BeautifulSoup
from httpx import AsyncClient

actress_dictionary = {}

# Get All pages (popular)
async def get(page: int, client: AsyncClient) -> None:

    with open(f'/tmp/{page}.html', 'w') as output:
        response = await client.get('/', params={'page': page})

        soup = BeautifulSoup(response.text, 'lxml')
        output.write(soup.prettify())


async def scrap(page: int) -> None:
    soup = BeautifulSoup(open(f'/tmp/{page}.html'), 'lxml')
    for x in soup.find_all('img', {'height': '135', 'width': '135'}):
        actress_name = list(x.get('alt'))
        name_len = len(actress_name)
        not_string = []
        for i in range(name_len):
            if actress_name[i] == ' ':
                continue
            elif not str.isalpha(actress_name[i]):
                not_string.append(actress_name[i])

        if len(not_string) != 0:
            for y in not_string:
                actress_name = list(filter((y).__ne__, actress_name))

        actress_dictionary[''.join(actress_name).strip(' ')] = x.get('src')


async def main() -> None:
    URL = 'https://www.r18.com/videos/vod/movies/actress'

    # Get the number of total pages
    async with AsyncClient(base_url=URL, follow_redirects=True, timeout=None) as client:
        print(f'INFO:\t    [R18_DB] Getting the number of total pages')
        response = await client.get('/')
        soup = BeautifulSoup(response.text, 'lxml')
        total = soup.find('div', class_='cmn-list-pageNation02')
        total = int(' '.join(total.text.split()).split(' ')[-1])

        # Save all pages as .html file
        tasks = []
        for i in range(1, total + 1):
            tasks.append(asyncio.create_task(get(i, client)))
        await asyncio.gather(*tasks)
        print(f"INFO:\t    [R18_DB] Fetched {total} Pages")

        # Scrap all pages
        tasks = []
        for i in range(1, total + 1):
            tasks.append(asyncio.create_task(scrap(i)))
        await asyncio.gather(*tasks)
        print(f"INFO:\t    [R18_DB] Scraped {total} Pages")

        # Upload updated data to Database 0
        print(
            f"INFO:\t    [R18_DB] saving total {len(actress_dictionary)} Actresses Data")
        async with aioredis.Redis.from_url(os.environ.get('REDIS_URL'), decode_responses=True, db=0) as redis_client:
            await redis_client.mset(actress_dictionary)

    print('INFO:\t    [R18_DB] Actress DB updated')

if __name__ == '__main__':
    asyncio.run(main())
