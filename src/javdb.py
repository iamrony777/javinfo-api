import os
import re

import httpx
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator


client = httpx.AsyncClient(http2=True)


async def fetch(id, headers, cookies):
    """Search by ID (filtered)\n
    returns  `id` = str, `url_id` = str | None as tuple"""

    response = await client.get(f'https://javdb.com/search?q={id}&f=1&locale=en&over18=1',
                                headers=headers, cookies=cookies, follow_redirects=True)    # Search result page
    soup = BeautifulSoup(response.text, 'lxml')
    try:
        url_id = soup.find('a', class_="box").get(
            'href')   # Exact video data url
        return id, url_id
    except AttributeError:
        return id, None


async def main(id):
    cookies = {
        "theme": "auto",
        "locale": "en",
        "over18": "1",
        "remember_me_token": os.environ['REMEMBER_ME_TOKEN'],
        "_jdb_session": os.environ['_JDB_SESSION'],
        "redirect_to": "%2F"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
        "Accept": "*/*"
    }


    data = await fetch(id, headers, cookies)

    id = data[0]
    if data[1] is None:
        return None
    else:
        # Main data fetch ,Cookies for login access
        response = await client.get(
            f'https://javdb.com{data[1]}', headers=headers, cookies=cookies, follow_redirects=True)
        soup = BeautifulSoup(response.text, 'lxml')
        jav_id = soup.title.text.split()[0]  # Get the jav_id

        if jav_id == id:
            title_list = soup.title.text.split()  # Get the title as list
            newtitle = []
            for a, b in enumerate(title_list):
                if a == 0:
                    pass
                else:
                    if b == '|':
                        break
                    else:
                        newtitle.append(b)
            title = ' '.join(newtitle)

            translated_title = GoogleTranslator(
                source='auto', target='en').translate_batch(newtitle)
            title = ' '.join(translated_title)

            # Get the image
            image = soup.find('img', class_="video-cover").get('src')
            tags = soup.find_all(
                'a', {'href': re.compile(r'/tags\?c')})  # Get tags list
            tags = [tag.text for tag in tags]
            tags.remove('Tags')

            return {'id': jav_id, 'title': title, 'poster': image, 'tags': tags}
        else:
            # incase search  result contains some results but not that one you are looking for
            return None

# Testing
# if __name__ == "__main__":
#      print(asyncio.run(main('FOW-001')))
