
from bs4 import BeautifulSoup
from httpx import AsyncClient
import re
import json
import asyncio

try:
    from helper.actress import main as actress_search
    from helper.actress import r18 as r18_search
except ImportError:
    from src.helper.actress import main as actress_search
    from src.helper.actress import r18 as r18_search


async def fetch(url: str, client: AsyncClient):
    response = await client.get(url)
    return BeautifulSoup(response.text, 'lxml')


async def actress_data(raw_list: list):
    boobpedia_tasks = []
    r18_tasks = []
    defective_list = []
    defective_r18_task = []
    actress_list = []

    try:
        for actress_ in raw_list:
            try:
                name = actress_.split(' ')[0:2]
                for x in range(2):
                    part = list(name[x])
                    for i in part:
                        if not i.isalpha():
                            part.remove(i)
                    name[x] = ''.join(part)
                actress_list.append(' '.join(name))
            except Exception:
                defective_list.append(actress_)
    except:
        # If actresses are not available
        pass

    for actress_ in actress_list:
        boobpedia_tasks.append(asyncio.create_task(actress_search(actress_)))
        r18_tasks.append(asyncio.create_task(r18_search(actress_)))
    for actress_ in defective_list:
        defective_r18_task.append(asyncio.create_task(r18_search(actress_)))

    boobpedia_results = await asyncio.gather(*boobpedia_tasks)
    r18_results = await asyncio.gather(*r18_tasks)
    defective_r18_results = await asyncio.gather(*defective_r18_task)

    for i in range(len(boobpedia_results)):
        if boobpedia_results[i] is not None:
            actress_list[i] = boobpedia_results[i]
            try:
                actress_list[i]['image2'] = r18_results[i]
            except:
                actress_list[i]['image2'] = None
        elif r18_results[i] is not None:
            actress_list[i] = {'name': actress_list[i], 
                                    'image': r18_results[i] }
        else:
            actress_list[i] = {'name': actress_list[i]}

    for i in range(len(defective_r18_results)):
        if defective_r18_results[i] is not None:
            defective_list[i] = defective_r18_results[i]

    actress_list.extend(defective_list)

    return actress_list


async def search(id: str, client: AsyncClient):
    soup = await fetch(url=f'/movies/{id}/', client=client)    # Fetch the soup

    if re.match(pattern='Page Not Found', string=soup.title.text):
        return None
    else:
        # JAV Title
        title = ' '.join((soup.find('td', class_="tablevalue").text).split())

        # JAV Poster
        poster = soup.find('meta', {"name": "twitter:image"}).get('content')

        # JAV Tags
        tags = soup.find_all('a', {'rel': re.compile('tag'), 'href': re.compile(
            r'https://www\.javdatabase\.com/genres/')})
        list_tags = []
        for tag in tags:
            list_tags.append(' '.join((tag.text).split()))

        # Movie Details
        details = await extra_details(soup)

        # JAV Actresses
        idols = soup.find_all('div', {'class': 'idol-name'})
        actress_data_ = []
        actress_list = []
        # tasks = []
        for i, idol in enumerate(idols):
            web_id = idol.find('a').get('href').split('/')[-2]
            image = 'https://www.javdatabase.com/idolimages/full/' + \
                web_id + '.webp'  # Image link
            idol = ' '.join(idol.text.split())  # remove extra spaces
            actress_list.append(''.join(idol))
        actress_data_ = await actress_data(actress_list)

        return {'id': id, 'title': title, 'poster': poster, 'extra_details': details, 'actress': actress_data_, 'tags': list_tags}


async def actress_details(web_id: str, client: AsyncClient):
    # Fetch the soup
    soup = await fetch(url=f'/idols/{web_id}/', client=client)
    details = soup.find_all('table', {'width': '100%'})
    key = []
    value = {}

    for data in details:
        for row in data.find_all('b'):
            key.append(' '.join(row.text.split()))
        switch = 0
        previous_key = str
        for row in data.find_all('td'):
            current_key = (' '.join(row.text.split()))
            if current_key in key and switch == 0:
                previous_key = current_key
                switch += 1
            elif current_key not in key and switch == 1:
                value[previous_key] = current_key
                switch -= 1
            else:
                pass

    return value


async def extra_details(soup: BeautifulSoup):
    key = []
    value = []
    detail = {}

    results = soup.find_all('td', {'class': 'tablelabel'})
    for result in results:
        i = ' '.join(result.find('b').text.split())
        key.append(i.split(':')[0])

    data = soup.find_all('td', {'class': 'tablevalue'})
    for d in data:
        value.append(' '.join(d.text.split()))

    for i in range(len(key)):
        if key[i] == 'Translated Title' \
                or key[i] == 'Genre(s)' \
                or key[i] == 'DVD ID' \
                or key[i] == 'Label' \
                or key[i] == 'Series' \
                or key[i] == 'Content ID':
            pass
        elif key[i] == 'Runtime':
            detail[key[i]] = value[i].split(' ')[0]
        else:
            detail[key[i]] = value[i]

    extra_details = {}
    for i in sorted(detail.keys()):
        extra_details[i] = detail[i]
    return extra_details


async def main(id: str):
    client = AsyncClient(
        http2=True, base_url='https://www.javdatabase.com', timeout=120, follow_redirects=True)
    return await search(id=id, client=client)

if __name__ == '__main__':
    print(json.dumps(asyncio.run(main('ebod-391')), ensure_ascii=False, indent=4))
