"""[SCRIPT] Auto Login for JAVDB ,solves captcha using custom ML api, not public usable for now as it is unstable"""
import asyncio
import json
import os
import sys
import time
from datetime import datetime
from io import BytesIO
from shutil import rmtree

import httpx
import uvloop
from loguru import logger
from lxml import html
from PIL import Image, UnidentifiedImageError
from redis import asyncio as aioredis

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
start_time = time.perf_counter()


EMAIL = os.getenv("JAVDB_EMAIL")
PASSWORD = os.getenv("JAVDB_PASSWORD")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
LOGGER_CONFIG = {
    "handlers": [
        dict(
            sink=sys.stdout,
            format="<b>tasks  |</b> <lvl>{level}</lvl>: <y>{module}</y>.<c>{function}#{line}</c> | <lvl>{message}</lvl>",
            enqueue=True,
            colorize=True,
            level=20,
        )
    ],
}

LOGGER_CONFIG_2 = {
    "handlers": [
        dict(
            sink=sys.stdout,
            format="<lvl>{level}</lvl>: <y>{module}</y>.<c>{function}#{line}</c> | <lvl>{message}</lvl>",
            enqueue=True,
            colorize=True,
            level=20,
        )
    ],
}


def up_days() -> int:
    """return current uptime (day only)"""
    startup_file='/tmp/startup'
    with open(startup_file, encoding='UTF-8') as _input:
        start = json.loads(_input.read())['startup']
        current = round(time.time())
        return ((current - start) // 86400)

async def token(client: httpx.AsyncClient):
    """Get session token (csrf-token)."""
    params = {
        "f": 1,
        "locale": "en",
        "over18": 1,
    }
    login_page = await client.get("/login", params=params)
    tree = html.HtmlElement(html.fromstring(login_page.content))
    try:
        return str(tree.find('.//meta[@name="csrf-token"]').get("content"))
    except AttributeError:
        if login_page.status_code == 403:
            logger.critical("[JAVDB_LOGIN] Login Failed, IP Adress was banned")
            return 403
        return None


async def solved_captcha(root_path, client: httpx.AsyncClient) -> str | None:
    """Get captcha image -> Solve captcha."""
    image_path = f"{root_path}/uploads/captcha_{int(time.time())}"
    captcha = await client.get("/rucaptcha/")
    try:
        img = Image.open(BytesIO(captcha.content))
        img.save(f"{image_path}.png", "png", optimize=True)
        with open(f"{image_path}.png", "rb") as content:
            return (
                await client.post(
                    os.getenv("CAPTCHA_SOLVER_URL"),
                    files={"file": content},
                    timeout=120,
                )
            ).json()["solved"]

    except [UnidentifiedImageError, TypeError]:
        return None


async def login(root_path, client: httpx.AsyncClient):
    """Login to JAVDB."""
    token_value = await token(client)
    if token_value != 403:
        url = "/user_sessions"
        payload = {
            "authenticity_token": await token(client),
            "email": EMAIL,
            "password": PASSWORD,
            "_rucaptcha": await solved_captcha(root_path, client),
            "remember": "1",
            "commit": "Sign in",
        }
        user_session = await client.post(url, data=payload)

        tree = html.fromstring(user_session.content)
        try:
            signin_msg = tree.find('.//div[@class="message-header"]').text.strip()
            logger.info(f'[JAVDB_LOGIN] {signin_msg}')

            profile_id = [
                element.text
                for element in tree.findall('.//div/a[@class="navbar-link"]')
                if element.get("href") == "/users/profile"
            ][0].strip()
            logger.info(f"[JAVDB_LOGIN] Username: {profile_id}")
            cookies = dict(client.cookies)
            async with aioredis.Redis.from_url(
                os.getenv("REDIS_URL"), decode_responses=True, db=2
            ) as redis:
                for key, value in cookies.items():
                    if key in ["remember_me_token", "_jdb_session"]:
                        await redis.set(key, value)
                return True
        except Exception as exception:
            print(exception)
            return False
    else:
        return 403

@logger.catch
async def main(root_path: str):
    """Main function."""
    if os.getenv("CAPTCHA_SOLVER_URL") not in [None, 'None', 'none', '']:
        try:
            os.mkdir(f"{root_path}/uploads")
        except FileExistsError:
            pass
        try_count = 0
        while True:
            if try_count < 10:
                async with httpx.AsyncClient(
                    http2=True,
                    follow_redirects=True,
                    base_url="https://javdb.com",
                    headers={"User-Agent": USER_AGENT},
                ) as client:
                    response = await login(root_path, client)
                    if response == 403:
                        break
                    if response:
                        async with aioredis.from_url(
                            os.getenv("REDIS_URL"), db=1, decode_responses=True
                        ) as redis:
                            end_time = time.perf_counter()
                            log = json.dumps(
                                {
                                    "finished in": f"{end_time - start_time:.2f}s",
                                    "time": datetime.now().strftime(
                                        "%d/%m/%Y - %H:%M:%S%z"
                                    ),
                                }
                            )
                            await redis.rpush("log:javdb_login", log)
                        rmtree(f"{root_path}/uploads")
                        sys.exit(0)
                    logger.warning("[JAVDB_LOGIN] Login Failed, retrying in 10 seconds")
                    try_count += 1
                    time.sleep(10)
            else:
                logger.error("[JAVDB_LOGIN] Login Failed, retrying in 10 minutes")
                try_count = 0
                time.sleep(600)


if __name__ == "__main__":

    if not up_days():
        time.sleep(30) # 30s to wait for redis-server
        logger.configure(**LOGGER_CONFIG)
        asyncio.run(main(os.getcwd()))
    else:
        logger.configure(**LOGGER_CONFIG_2)
        asyncio.run(main(os.getcwd()))
