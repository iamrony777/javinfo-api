import re

import httpx
from bs4 import BeautifulSoup

client = httpx.AsyncClient(http2=True, follow_redirects=True)


async def result_filter(name, soup):
    """takes result page as `soup` soup and checks if search result if available / matches with input\n
    if True , then searches for the exact page and return `soup`"""

    try:
        result = soup.p.em.text
        return None
    except AttributeError:
        pass

    # Check all video page results
    pages = soup.find_all('div', {'id': re.compile(r'vid_jav')})
    if len(pages) == 0:
        return soup_info(soup)

    for page in pages:
        try:
            video_link = page.a['href']
            video_id = page.div.text

            if name == video_id:
                video_link = video_link.split('./')
                video_link = f'https://javlibrary.com/en/{video_link[1]}'
                return await page_info(video_link)
                
        except KeyError:
            pass


async def page_info(link):
    cookies = {'over18': '18'}
    response = await client.get(url=link, cookies=cookies)
    response = response.text
    soup = BeautifulSoup(response, 'lxml')
    return soup_info(soup)


def soup_info(soup):
    jav_poster = soup.find(id="video_jacket_img")
    jav_poster = 'https:' + jav_poster.get('src')  # --------> VIDEO POSTER

    title_list = soup.find('title').text
    title_list = title_list.split()
    jav_id = title_list.pop(0)  # ---------> VIDEO ID

    remove = title_list.remove('-')
    remove = title_list.remove('JAVLibrary')
    jav_title = ' '.join(title_list)  # ---------> VIDEO TITLE

    tags = soup.find_all('a', rel='category tag')
    jav_tags = []
    for tag in tags:
        jav_tags.append(tag.text)
    response_json = {'id': jav_id,
                     'title': jav_title,
                     'poster': jav_poster,
                     'tags': jav_tags}

    return response_json


async def soup_gen(id):
    cookies = {'over18': '18'}
    query = {'keyword': id}
    url = f"https://www.javlibrary.com/en/vl_searchbyid.php"
    response = await client.get(url, params=query, cookies=cookies)
    response = response.text
    soup = BeautifulSoup(response, 'lxml')

    return soup


async def main(id):
    return (await result_filter(id, soup=await soup_gen(id)))

#Testing
# if __name__ == '__main__':
#     print(asyncio.run(main('EBOD-391')))
