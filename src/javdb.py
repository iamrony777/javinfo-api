import os
import re

from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from httpx import AsyncClient


async def fetch(id, headers, cookies, client: AsyncClient):
    """Search by ID (filtered)\n
    returns  `id` = str, `url_id` = str | None as tuple"""

    response = await client.get(f'https://javdb.com/search',
                                params={'q': id, 'f': 1,
                                        'locale': 'en', 'over18': 1},
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
        "remember_me_token": os.environ.get('REMEMBER_ME_TOKEN'),
        "_jdb_session": os.environ.get('JDB_SESSION'),
        "redirect_to": "%2F"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
        "Accept": "*/*"
    }

    async with AsyncClient(http2=True) as client:
        data = await fetch(id, headers, cookies, client)

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

                # Extra Movie Details
                details = {}
                data = soup.find_all('div', class_='panel-block')
                for element in data:
                    try:
                        if (element.strong.text.strip()) == 'Director:':
                            details['Director'] = GoogleTranslator(
                                source='auto', target='en').translate(element.span.text.strip())
                        elif (element.strong.text.strip()) == 'Released Date:':
                            details['Released Date'] = element.span.text.strip()
                        elif (element.strong.text.strip()) == 'Duration:':
                            details['Runtime'] = element.span.text.strip().split(' ')[
                                0]
                        elif (element.strong.text.strip()) == 'Maker:':
                            details['Studio'] = element.span.text.strip()
                        elif (element.strong.text.strip()) == 'Rating:':
                            details['User Rating'] = element.span.text.strip().split(',')[
                                0]
                        else:
                            pass
                    except AttributeError:
                        break

                extra_details = {}
                for i in sorted(details.keys()):
                    extra_details[i] = details[i]

                return {'id': jav_id, 'title': title, 'poster': image, 'extra_details': extra_details, 'tags': tags}
            else:
                # incase search  result contains some results but not that one you are looking for
                return None

# Testing
if __name__ == "__main__":
    import asyncio
    print(asyncio.run(main('MKCK-274')))
