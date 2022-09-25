"""[SCRIPT] Auto Login for JAVDB ,solves captcha using custom ML api, not public usable for now as it is unstable"""
import asyncio
import json
import os
import sys
import time
from datetime import datetime
from io import BytesIO
from shutil import rmtree
from builtins import bool, int
from typing import Optional
from urllib.parse import urljoin

import uvloop
from lxml import html
from PIL import Image, UnidentifiedImageError
from redis import Redis
from cloudscraper import create_scraper

from api import logger

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class JavdbLogin:
    def __init__(self, base_url: Optional[str] = None) -> None:
        self.email: str = os.getenv("JAVDB_EMAIL")
        self.password: str = os.getenv("JAVDB_PASSWORD")
        self.base_url = self.base_url = [
            os.getenv("JAVDB_URL", "https://javdb.com/")
            if base_url is None
            else base_url
        ][0]
        self.client = create_scraper(
            browser={"browser": "chrome", "platform": "linux", "desktop": True}
        )
        self.start_time = time.perf_counter()
        self.root_path = os.getcwd()
        os.makedirs(f"{self.root_path}/uploads", exist_ok=True)

        [
            sys.exit(0)
            if os.getenv("CAPTCHA_SOLVER_URL") in [None, "None"]
            else logger.debug("[JAVDB_LOGIN] - starting")
        ]

    @logger.catch
    def token(self):
        """Get session token (csrf-token)."""
        params = {
            "f": 1,
            "locale": "en",
            "over18": 1,
        }
        login_page = self.client.get(
            urljoin(self.base_url, "/login"), params=params, allow_redirects=True
        )
        tree = html.HtmlElement(html.fromstring(login_page.content))
        try:
            return str(tree.find('.//meta[@name="csrf-token"]').get("content"))
        except AttributeError:
            if login_page.status_code == 403:
                logger.error("[JAVDB_LOGIN] - login failed - IP address was banned")
                return login_page.status_code
            return login_page.status_code

    @logger.catch
    def solved_captcha(self, root_path) -> str | None:
        """Get captcha image -> Solve captcha."""
        image_path = f"{root_path}/uploads/captcha_{int(time.time())}"
        captcha = self.client.get(urljoin(self.base_url, "/rucaptcha/"))
        try:
            img = Image.open(BytesIO(captcha.content))
            img.save(f"{image_path}.png", "png", optimize=True)
            with open(f"{image_path}.png", "rb") as content:
                return (
                    self.client.post(
                        os.getenv("CAPTCHA_SOLVER_URL"),
                        files={"file": content},
                        timeout=120,
                    )
                ).json()["solved"]

        except (UnidentifiedImageError, TypeError):
            return None

    @logger.catch
    def execute(self, root_path) -> bool | int:
        """Login to JAVDB."""
        token_value = self.token()
        if isinstance(token_value, str):
            url = "/user_sessions"
            payload = {
                "authenticity_token": token_value,
                "email": self.email,
                "password": self.password,
                "_rucaptcha": self.solved_captcha(root_path),
                "remember": "1",
                "commit": "Sign in",
            }
            tree: html.HtmlElement = html.fromstring(
                self.client.post(urljoin(self.base_url, url), data=payload).content
            )
            try:
                signin_msg: str = tree.find(
                    './/div[@class="message-header"]'
                ).text.strip()
                logger.info(f"[JAVDB_LOGIN] - sign in message - {signin_msg}")

                profile_id = [
                    element.text
                    for element in tree.findall('.//div/a[@class="navbar-link"]')
                    if element.get("href") == "/users/profile"
                ][0].strip()
                logger.info(f"[JAVDB_LOGIN] - username - {profile_id}")
                with Redis.from_url(
                    os.getenv("REDIS_URL"), decode_responses=True
                ) as redis:
                    for key, value in dict(self.client.cookies).items():
                        if key in ["remember_me_token", "_jdb_session"]:
                            redis.set("cookie/" + key, value)
                return True
            except Exception as exception:
                logger.error(f"[JAVDB_LOGIN] - exception - {exception}")
                return False
        else:
            return token_value

    @logger.catch
    def login(self):
        """Main function."""
        try_count = 1
        while try_count < 10:
            response = self.execute(self.root_path)
            if response:
                with Redis.from_url(
                    os.getenv("REDIS_URL"), decode_responses=True
                ) as redis:
                    log = json.dumps(
                        {
                            "finished in": f"{time.perf_counter() - self.start_time:.2f}s",
                            "time": datetime.now().strftime("%d/%m/%Y - %H:%M:%S%z"),
                        }
                    )
                    redis.rpush("log/javdb_login", log)
                rmtree(f"{self.root_path}/uploads")
                sys.exit(0)
            if not isinstance(response, bool):
                logger.error(f"[JAVDB_LOGIN] - http status - {response}")
                sys.exit(1)
            else:
                try_count += 1
                logger.error(f"[JAVDB_LOGIN] - login failed - ({try_count}/10)")
                time.sleep(10)


if __name__ == "__main__":
    JavdbLogin().login()
