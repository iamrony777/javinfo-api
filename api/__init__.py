"""api/__init__.py"""

import asyncio
import gc
import json
import os
import sys
from enum import Enum

import uvloop
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from redis import asyncio as aioredis

import api.resources.javdatabase as jdtb
import api.resources.javdb as jdb
import api.resources.javlibrary as jlb
from api.helper.redis_log import redis_logger
from api.helper.string_filter import filter_string
from api.helper.timeout import FILE_TO_CHECK
from api.helper.timeout import set_timeout as timeout
from api.resources import r18
from api.scripts.javdb_login import main as login
from api.scripts.r18_db import main as r18_db

gc.enable()


# using Uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# APscheduler Config
async_scheduler = AsyncIOScheduler(job_defaults={"misfire_grace_time": 5 * 60})


class Tags(Enum):
    """Set tags for each endpoint."""

    DEMO = "demo"
    API = "secured endpoints"
    STATS = "info / statictics"


# Search function
async def get_results(name: str, provider: str, only_r18: bool):
    """Search function."""
    if provider == "all":
        tasks = []
        tasks.append(asyncio.create_task(r18.main(name, only_r18)))
        tasks.append(asyncio.create_task(jdtb.main(name, only_r18)))
        tasks.append(asyncio.create_task(jlb.main(name, only_r18)))
        tasks.append(asyncio.create_task(jdb.main(name)))
        for result in await asyncio.gather(*tasks):
            if result is not None:
                return result

    elif provider == "javlibrary":
        return await jlb.main(name, only_r18)
    elif provider == "javdb":
        return await jdb.main(name)
    elif provider == "javdatabase":
        return await jdtb.main(name, only_r18)
    elif provider == "r18":
        return await r18.main(name, only_r18)


# Loguru - Logger config
LOGGER_CONFIG = {
    "handlers": [
        dict(
            format="{time:%Y-%m-%d at %H:%M:%S} [{level}] {file.name}:{function}#{line} | {message} ",
            sink="javinfo.log",
            enqueue=True,
            level=5,
        ),
        dict(
            sink=sys.stdout,
            format="<green>{time:%Y-%m-%d %H:%M:%S}</green> | <level>{level: <8}</level> | <cyan>{file}</cyan>.<blue>{function}</blue>:<cyan>{line}</cyan> - <level>{message}</level>",
            enqueue=True,
            colorize=True,
            level=20,
        ),
    ],
}
logger.configure(**LOGGER_CONFIG)

try:
    with open("docs/version", "r", encoding="UTF-8") as ver:
        version: str = json.loads(ver.read())["message"]

except FileNotFoundError:
    with open("/app/docs/version", "r", encoding="UTF-8") as ver:
        version: str = json.loads(ver.read())["message"]


if os.getenv("PLATFORM") == 'heroku' and os.getenv("APP_NAME") is not None:
    os.environ["BASE_URL"] = f"https://{os.getenv('APP_NAME')}.herokuapp.com"

