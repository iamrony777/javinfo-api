import asyncio
import time
import os
from io import BytesIO
from shutil import rmtree

import httpx
from redis import asyncio as aioredis
from bs4 import BeautifulSoup
from PIL import Image, UnidentifiedImageError

EMAIL = os.getenv('JAVDB_EMAIL')
PASSWORD = os.getenv('JAVDB_PASSWORD')
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'


async def token(client: httpx.AsyncClient):
    """Get session token"""
    params = {'f': 1,
              'locale': 'en',
              'over18': 1, }
    login_page = await client.get('/login', params=params)
    soup = BeautifulSoup(login_page.text, 'lxml')
    try:
        return str(soup.find('meta', {'name': 'csrf-token'}).get('content'))
    except AttributeError:
        if login_page.status_code == 403:
            print('INFO:\t     [JAVDB] Login Failed, IP Adress was banned')
            return 403
        return None


async def get_captcha(root_path, client: httpx.AsyncClient) -> str:
    """Get captcha image"""
    image_path = f'{root_path}/uploads/captcha_{int(time.time())}'
    captcha = await client.get('/rucaptcha/')
    try:
        img = Image.open(BytesIO(captcha.content))
        img.save(f'{image_path}.png', 'png', optimize=True)
        return f'{image_path}.png'
    except UnidentifiedImageError:
        return None


def captcha_solver(captcha: str) -> str:
    """Solve captcha"""
    url = os.environ['CAPTCHA_SOLVER_URL']
    try:
        file = {'file': open(captcha, 'rb')}
        resp = httpx.post(url=url, files=file, timeout=120)
        return resp.json()['solved']
    except TypeError:
        return None


async def login(root_path, client: httpx.AsyncClient):
    """Login to JAVDB"""
    token_value = await token(client)
    if token_value != 403:
        url = '/user_sessions'
        payload = {'authenticity_token': await token(client),
                   'email': EMAIL,
                   'password': PASSWORD,
                   '_rucaptcha': captcha_solver(await get_captcha(root_path, client)),
                   'remember': '1',
                   'commit': 'Sign in'}
        user_session = await client.post(url, data=payload)

        soup = BeautifulSoup(user_session.text, 'lxml')
        try:
            signin_msg = (
                soup.find('div', {'class': 'message-header'})).text.strip()
            print('INFO:\t     [JAVDB]', signin_msg)

            profile_id = (soup.find(
                'a', {'class': 'navbar-link', 'href': '/users/profile'})).text.strip()
            print('INFO:\t     [JAVDB] Username:', profile_id)
            cookies = dict(client.cookies)
            async with aioredis.Redis.from_url(os.environ['REDIS_URL'], decode_responses=True, db=2) as redis:
                for key, value in cookies.items():
                    if key in ['remember_me_token', '_jdb_session']:
                        await redis.set(key, value)
                    else:
                        continue
                return True
        except Exception:
            return False
    else:
        return 403


async def main(root_path: str):
    """Main function"""

    try:
        os.mkdir(f'{root_path}/uploads')
    except FileExistsError:
        pass
    try_count = 0
    while True:
        if try_count < 10:
            client = httpx.AsyncClient(
                http2=True,
                follow_redirects=True,
                base_url='https://javdb.com',
                headers={'User-Agent': USER_AGENT})
            async with client:
                response = await login(root_path, client)
                if response == 403:
                    break
                if response is True:
                    print('INFO:\t     [JAVDB] Successfully logged in')
                    rmtree(f'{root_path}/uploads')
                    break
                print(
                    'INFO:\t     [JAVDB] Login Failed, retrying in 10 seconds')
                try_count += 1
                await asyncio.sleep(10)
        else:
            print('INFO:\t     [JAVDB] Login Failed, retrying in 10 minutes')
            try_count = 0
            await asyncio.sleep(600)


if __name__ == '__main__':
    asyncio.run(main(os.getcwd()))
