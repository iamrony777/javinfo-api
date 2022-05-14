import json

from bs4 import BeautifulSoup
from httpx import AsyncClient

try:
    from helper.mongo import search as query 
except ImportError:
    from src.helper.mongo import search as query   
  
async def special_search(name: str, client: AsyncClient):
    params = {  'title': 'Special:Search',
                'search': name,
                'profile': 'default',
                'fulltext': '1' }
    response = await client.get('/wiki/index.php', params=params)
    soup = BeautifulSoup(response.text, 'lxml')
    result_name = []

    try:
        result = soup.find('li', class_='mw-search-result')
        for i in result.find('div', class_='searchresult').text.split():
            if i.isalpha() and i == 'alias':
                for i in result.find_all('span', class_='searchmatch'):
                    result_name.append(i.text.strip())

                if name in ' '.join(result_name):
                    return ('https://boobpedia.com' + result.find('a').get('href'))
                else:
                    return None
            else:
                pass
        return None
    except AttributeError:
        return None
    

async def search(name: str, client: AsyncClient):   # search for the actress
    params = { 'action': 'opensearch',
                'format': 'json',
                'formatversion': '2',
                'search': name,
                'namespace': '0',
                'limit': '10',
                'suggest': 'true' }
    response = await client.get('/wiki/api.php', params=params)
    try:
        return response.json()[-1][0]
    except IndexError:
        return await special_search(name, client)

async def fetch(url: str, client: AsyncClient): # fetch page, get soup
    response = await client.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup

async def image(soup: BeautifulSoup, client: AsyncClient):
    try:
        image = soup.find('td', {'colspan': '2', 'style': 'text-align:center;' }).find('a').get('href')
        response = await client.get(image)
        image_soup = BeautifulSoup(response.text, 'lxml')
        image_link = image_soup.find('div', {'class': 'fullMedia'}).find('a').get('href')
        image_link = 'https://www.boobpedia.com' + image_link
        return image_link
    except:
        return None

async def details(soup: BeautifulSoup, client: AsyncClient):
    details = {}
    tr_list = soup.find_all('tr', valign='top')
    for td in tr_list:
        result = ' '.join(td.text.split()).split(': ')
        details[result[0]] = result[1]
        
    return details

async def main(name: str):
    client = AsyncClient(base_url='https://www.boobpedia.com',http2=True, follow_redirects=True, timeout=None)
    result = await search(name, client)
    data = {}
    if result is not None:
        soup = await fetch(result, client)
        image_link =  await image(soup, client)
    else:
        name_ = name.split(' ')
        name_.reverse()
        name_ = ' '.join(name_)
        result = await search(name_, client)
        if result is not None:
            soup = await fetch(result, client)
            image_link =  await image(soup, client)
        else:
            return None

    data['name'] = name
    data['image'] = image_link
    data['image2'] = ''
    data['details'] = await details(soup, client)

    return data

async def r18(name: str):
    result = await query({'name': {"$regex": name}}, 'actress')
    if result != []:
        for i in result:
            return ({ 'name': i['name'], 'image': i['image']})
    else:
        name = name.split(' ')
        name.reverse()
        name = ' '.join(name)
        result = await query({'name': {"$regex": name}}, 'actress')
        for i in result:
            return ({ 'name': i['name'], 'image': i['image']})

if __name__ == '__main__':
    import asyncio
    data = asyncio.run(main('Julia'))
    print(json.dumps(data, indent=4))
    