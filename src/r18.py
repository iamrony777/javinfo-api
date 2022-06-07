import asyncio
import json
import re

from bs4 import BeautifulSoup
from httpx import AsyncClient
try:
    from helper.actress import actress_search
except ImportError:
    from .helper.actress import actress_search


async def fetch(name: str, url: str, client: AsyncClient):
    """Get contentname from search result."""
    response = await client.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    if soup.find('div', class_='mb10 pl10 fzL fwB') is None:
        for item in soup.find_all('li', class_='item-list'):
            if name == item.find('img')['alt'].strip():
                return item.get('data-content_id').strip()


async def movie_data(client: AsyncClient, content_id: str, only_r18: bool) -> dict[str] | None:
    """Fetch data from r18.com's api."""
    response = await client.get(url=f'/api/v4f/contents/{content_id}', params={'lang': 'en'})
    if response.status_code == 200:
        response = response.json()['data']
        base_details, extra_details = {}, {}
        actress_list, screenshots = [], []

        base_details['id'] = response.get('dvd_id')
        base_details['title'] = response.get('title')
        base_details['poster'] = response.get(
            'images').get('jacket_image').get('large')
        base_details['page'] = response.get('detail_url')

        extra_details['director'] = response.get('director')
        extra_details['release_data'] = response.get(
            'release_date').split(' ')[0]
        extra_details['runtime'] = response.get('runtime_minutes')
        extra_details['studio'] = response.get('maker').get('name')

        base_details['details'] = extra_details

        temp_actresses = response.get('actresses')
        if temp_actresses is not None:
            for actresses in temp_actresses:
                if bool(re.search(r'\(', actresses['name'])):
                    name = actresses['name'].replace(' (', ', ')
                    name = name.replace(')', '')
                    [actress_list.append(name) for name in name.split(', ')]
                else:
                    actress_list.append(actresses['name'].strip())

            base_details['actress'] = await actress_search(actress_list, only_r18)

        temp_screenshots = response.get('gallery')
        if temp_screenshots is not None:
            for screenshot in temp_screenshots:
                for size in ['large', 'medium', 'small']:
                    if screenshot.get(size) is not None:
                        screenshots.append(screenshot[size])
                        break
            base_details['screenshots'] = screenshots

        return base_details


async def main(name: str, only_r18: bool = False) -> dict[str]:
    """Main Function to manage rest of the fucntion."""
    async with AsyncClient(base_url='https://www.r18.com', follow_redirects=True, timeout=20, http2=True) as client:
        contentname = await fetch(name=name, url=f'/common/search/searchword={name}', client=client)
        if contentname is not None:
            return await movie_data(client, contentname, only_r18)

if __name__ == '__main__':
    # import time
    # start = time.perf_counter()
    # print(json.dumps(asyncio.run(main('DOA-017')), indent=4, ensure_ascii=False))
    print(json.dumps(asyncio.run(main('SSIS-391', False)), indent=4, ensure_ascii=False))
    # print(json.dumps(asyncio.run(main('MKCK-274')), indent=4, ensure_ascii=False))
    # print(time.perf_counter() - start)
