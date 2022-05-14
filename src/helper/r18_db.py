import asyncio

from bs4 import BeautifulSoup
from httpx import AsyncClient

try:
    from mongo import *
except ImportError:
    from src.helper.mongo import *

actress_dictionary = {}

# Get All pages (popular)
async def get(page: int, client: AsyncClient):

    with open(f'/tmp/{page}.html', 'w') as output:
        response = await client.get('/', params={'page': page})

        soup = BeautifulSoup(response.text, 'lxml')
        output.write(soup.prettify())

async def scrap(page: int) -> None:
    soup = BeautifulSoup(open(f'/tmp/{page}.html'), 'lxml')
    for x in soup.find_all('img', {'height': '135', 'width': '135'}):
        actress_name = list(x.get('alt'))
        for i in range(len(actress_name)):
            if actress_name[i] == ' ':
                pass
            elif not str.isalpha(actress_name[i]):
                actress_name[i] = ''
        actress_dictionary[''.join(actress_name)] = x.get('src')

async def main():
    URL = 'https://www.r18.com/videos/vod/movies/actress'

    # Get the number of total pages
    async with AsyncClient(base_url=URL, follow_redirects=True, timeout=None) as client:
        print(f'INFO:\t [R18_DB] Getting the number of total pages')
        response = await client.get('/')
        soup = BeautifulSoup(response.text, 'lxml')
        total= soup.find('div', class_='cmn-list-pageNation02')
        total = int(' '.join(total.text.split()).split(' ')[-1])

        # Save all pages as .html file
        tasks = []
        for i in range(1, total + 1):
            tasks.append(asyncio.create_task(get(i, client)))
        await asyncio.gather(*tasks)
        print(f"INFO:\t [R18_DB] Fetched {total} Pages")

        # Scrap all pages
        tasks = []
        for i in range(1, total + 1):
            tasks.append(asyncio.create_task(scrap(i)))
        await asyncio.gather(*tasks)
        print(f"INFO:\t [R18_DB] Scraped {total} Pages")

        # Try to drop previous collection
        await drop('R18', 'actress')
        print(f"INFO:\t [R18_DB] Dropped previous collection")


        # Upload updated data to Database
        print(f"INFO:\t [R18_DB] Uploading total {len(actress_dictionary)} Actresses Data")
        actress_list = []
        for x, y in actress_dictionary.items():
            actress_list.append({'name': x, 'image': y})

        await insert_bulk(actress_list, 'R18', 'actress')
    print('INFO:\t [R18_DB] Actress DB updated')



if __name__ == '__main__':
    asyncio.run(main())