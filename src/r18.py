import asyncio
import json
import re

from httpx import AsyncClient
from bs4 import BeautifulSoup

try:
    from helper.actress import main as actress_search
    from helper.actress import r18 as r18_search
except ImportError:
    from src.helper.actress import main as actress_search
    from src.helper.actress import r18 as r18_search


async def fetch(id: str, url: str, client: AsyncClient):
    response = await client.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    if soup.find('div', class_='mb10 pl10 fzL fwB') is None:
        for item in soup.find_all('li', class_='item-list'):
            if id == item.find('img')['alt'].strip():
                return item.get('data-content_id').strip()
            else:
                return None
    else:
        return None


async def actress_data(actress_list: list):
    boobpedia_tasks = []
    r18_tasks = []
    for actress in actress_list:
        boobpedia_tasks.append(asyncio.create_task(actress_search(actress)))
        r18_tasks.append(asyncio.create_task(r18_search(actress)))

    boobpedia_results = await asyncio.gather(*boobpedia_tasks)
    r18_results = await asyncio.gather(*r18_tasks)
    for index_ in range(len(boobpedia_results)):
        if boobpedia_results[index_] is not None:
            actress_list[index_] = boobpedia_results[index_]
            actress_list[index_]['image2'] = r18_results[index_]
        elif r18_results[index_] is not None:
            actress_list[index_] = {'name': actress_list[index_], 
                                    'image': r18_results[index_] }
        else:
            actress_list[index_] = {'name': actress_list[index_]}
    return actress_list


async def movie_data(content_id: str, client: AsyncClient):
    response = await client.get(url=f'/api/v4f/contents/{content_id}', params={'lang': 'en'})
    if response.status_code == 200:
        response = response.json()
        base_details = {}
        extra_details = {}
        actress_list = []
        defective_list = []
        screenshots = []

        base_details['id'] = response['data']['dvd_id']
        base_details['title'] = response['data']['title']
        base_details['poster'] = response['data']['images']['jacket_image']['large']

        extra_details['Director'] = response['data']['director']
        extra_details['Release Date'] = response['data']['release_date'].split(' ')[0]
        extra_details['Runtime'] = response['data']['runtime_minutes']
        extra_details['Studio'] = response['data']['maker']['name']

        base_details['extra_details'] = extra_details
        try:
            for actress_count in range(len(response['data']['actresses'])):
                actress_name = list(response['data']['actresses'][actress_count]['name'])
                not_string = []
                try:
                    for i in range(len(actress_name)):
                        if actress_name[i] == ' ':
                            continue
                        elif actress_name[i] == '(' or actress_name[i] == ')': # alias = [Name (2nd name)]
                            actress_alias = re.split(r'[()]', ''.join(actress_name))[0:2]
                            if re.search(',', actress_alias[1]) == None:
                                if len(actress_alias[0].split(' ')[-1]) > 0:
                                    actress_name = list(actress_alias[0]) 
                                else:
                                    raise ValueError()  # Includes ony name, no surname                
                            else:
                                actress_name = list(actress_alias[0]) if len(actress_alias[0]) >= len(actress_alias[1].split(',')[0]) else list(actress_alias[1].split(',')[0])
                                break
                        elif not str.isalpha(actress_name[i]):
                            not_string.append(actress_name[i])

                    if len(not_string) != 0:
                        for y in not_string:
                            actress_name = list(filter((y).__ne__, actress_name))
                    actress_list.append(''.join(actress_name).strip())
                except:
                    actress_alias = re.split(r'[()]', ''.join(actress_name))[1] # alias = 2nd name
                    image_url = response['data']['actresses'][actress_count]['image_url']
                    defective_list.append({'name': actress_alias.strip(),
                                            'image': image_url})
            actress_list = await actress_data(actress_list)
            actress_list.extend(defective_list)

            base_details['actress'] = actress_list
        except Exception as exception:
            # If actresses are not available
            # print(exception)
            pass

        try:
            for item in range(len(response['data']['gallery'])):
                for size in ['large', 'medium', 'small']:
                    try:
                        if response['data']['gallery'][item][size] != None:
                            screenshots.append(
                                response['data']['gallery'][item][size])
                            break
                    except:
                        pass
            base_details['screenshots'] = screenshots

        except:
            # If screenshots are not available
            pass

        return base_details
    else:
        return None


async def main(id: str):
    client = AsyncClient(base_url='https://www.r18.com',
                         follow_redirects=True, timeout=120, http2=True)
    content_id = await fetch(id=id, url=f'/common/search/searchword={id}', client=client)
    if content_id is not None:
        return await movie_data(content_id, client)

if __name__ == '__main__':
    print(json.dumps(asyncio.run(main('DOA-017')), indent=4, ensure_ascii=False))
