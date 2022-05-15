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


async def fetch(**kwargs):
    # Fetch page
    try:
        response = await kwargs['client'].get(kwargs['url'], params=kwargs['params'])
    except Exception:
        response = await kwargs['client'].get(kwargs['url'])
    return BeautifulSoup(response.text, 'lxml')


def duplicate(soup: BeautifulSoup):

    title = soup.title.text.strip()
    for i in list(title):
        if i == '"':
            title = title.replace(i, '')
    title = title.split(' ')[0]
    for result in soup.find_all('div', class_='videos'):
        for x in (result.find_all('div', class_='video')):
            if title == (''.join(x.find('div', class_='id').text.split())):
                link = x.find('a').get('href')  # --------> VIDEO LINK
                link = link.split('.')[-1]
                return str(link)


async def filter(soup: BeautifulSoup):

    try:
        # No Search Result
        result = soup.find('em').text
        if result == 'Search returned no result.':
            return None
        else:
            return soup
    except AttributeError:
        # Check if there are multiple results
        if re.search('ID Search Result', soup.title.text) is None:
            # if none , then its a single result
            # Return soup for data scrapping
            return soup
        else:
            # if there are multiple results, then get the appropriate result
            # and return the soup
            video_link = duplicate(soup)
            if video_link is not None:
                return video_link


async def extra_details(soup: BeautifulSoup):
    key = []
    for result in soup.find_all('td', class_='header'):
        i = ' '.join(result.text.split())
        if (i.split(':')[0]) == 'Length':
            pass
        else:
            key.append(i.split(':')[0])

    value = []
    for result in soup.find_all('td', class_='text'):
        i = ' '.join(result.text.split())
        value.append(i)

    detail = {}
    for i in range(len(key)):
        if key[i] == 'Genre(s)' \
            or key[i] == 'ID' \
            or key[i] == 'Label' \
            or key[i] == 'Cast':
            pass
        elif key[i] == 'User Rating':
            try:
                x = list(value[i])
                x.pop(0)
                x.pop(-1)
                x = ''.join(x)
                detail[key[i]] = x
            except:
                detail[key[i]] = None
        elif key[i] == 'Director':
            try:
                if value[i].isalpha():
                    detail[key[i]] = value[i]
                else:
                    detail[key[i]] = None
            except:
                detail[key[i]] = None
        elif key[i] == 'Maker':
            detail['Studio'] = value[i]

        else:
            detail[key[i]] = value[i]


    length = soup.find('div', {'id':'video_length'})
    length = length.find('span', {'class':'text'}).text.strip()
    detail['Runtime'] = length


    extra_details = {}
    for i in sorted(detail.keys()):
        extra_details[i] = detail[i]

    return extra_details

async def actress_details(soup: BeautifulSoup):
    # Create Actress List
    actress_list = []
    for star in soup.find_all('span', class_='star'):
        actress_list.append(' '.join(star.text.split()))
    
    # Create Actress Details
    boobpedia_tasks = []
    r18_tasks = []
    for actress in actress_list:
        if actress.isalpha():
            boobpedia_tasks.append(asyncio.create_task(actress_search(actress)))
            r18_tasks.append(asyncio.create_task(r18_search(actress)))
        else:
            r18_tasks.append(asyncio.create_task(r18_search(actress)))
    
    boobpedia_results = await asyncio.gather(*boobpedia_tasks)
    r18_results = await asyncio.gather(*r18_tasks)
    if len(boobpedia_results) != 0:
        for i in range(len(boobpedia_results)):
            try:
                if boobpedia_results[i] is not None:
                    actress_list[i] = boobpedia_results[i]
                    actress_list[i]['image2'] = r18_results[i]
                elif r18_results[i] is not None:
                    actress_list[i] = {'name': actress_list[i], 
                                    'image': r18_results[i] }
                else:
                    actress_list[i] = { 'name': actress_list[i] }
            except KeyError:
                actress_list[i].pop('image2', None)
    else:
        for i in range(len(r18_results)):
            try:
                actress_list[i] = {'name': actress_list[i], 
                                    'image': r18_results[i] }
            except KeyError:
                actress_list[i].pop('image2', None)

    return actress_list

    

async def scrap(soup: BeautifulSoup):
    # Scrap the data
    id = soup.find('div', {'id': 'video_id'}).find('td', class_='text').text.strip()
    title = ' '.join(soup.find('h3', class_='post-title text').text.split()[1:-1])
    poster = 'https://' + soup.find('img', {'id':'video_jacket_img'}).get('src').strip().split('//')[-1]
    extra_details_ = await extra_details(soup)
    actress_details_ = await actress_details(soup)

    tags = soup.find_all('a', rel='category tag')
    jav_tags = []
    for tag in tags:
        jav_tags.append(tag.text)

    base_details = {
        'id': id,
        'title': title,
        'poster': poster,
        'extra_details': extra_details_,
        'actress' : actress_details_,
        'tags': jav_tags
    }

    return base_details


async def main(id: str):
    client = AsyncClient(base_url='https://www.javlibrary.com/en',
                         cookies={'over18': '18'}, http2=True, follow_redirects=True)
    # Fetch the soup
    soup = await fetch(url=f'/vl_searchbyid.php', client=client, params={'keyword': id})

    # Filter the soup
    filtered_result = await filter(soup)

    # Scrap the data
    if type(filtered_result) == BeautifulSoup:
        return await scrap(soup)
    elif type(filtered_result) == str:
        soup = await fetch(url=filtered_result, client=client)
        return await scrap(soup)
    else:
        return None

if __name__ == '__main__':
    print(json.dumps(asyncio.run(main('PPBD-205')), indent=4, ensure_ascii=False))