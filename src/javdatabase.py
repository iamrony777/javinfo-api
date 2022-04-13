import re

import httpx
from bs4 import BeautifulSoup

client = httpx.AsyncClient(http2=True)


async def fetch(id):
    # Search result page
    response = await client.get(
        f'https://www.javdatabase.com/movies/{id}/', follow_redirects=True)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


async def main(id):
    soup = await fetch(id)    # Fetch the soup

    if re.match(pattern='Page Not Found', string=soup.title.text):
        return None
    else:
        title = ' '.join((soup.find('td', class_="tablevalue").text).split())
        poster = soup.find('meta', {"name": "twitter:image"}).get('content')
        tags = soup.find_all('a', {'rel': re.compile('tag'), 'href': re.compile(
            r'https://www\.javdatabase\.com/genres/')})
        list_tags = []
        for tag in tags:
            list_tags.append(' '.join((tag.text).split()))
        return {'id': id, 'title': title, 'poster': poster, 'tags': list_tags}


# Testing
# if __name__ == "__main__":
#     print(asyncio.run(main(('SSIS-366'))))
