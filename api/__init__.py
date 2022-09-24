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

from api.resources.javdatabase import Javdatabase
from api.resources.javdb import Javdb
from api.resources.javlibrary import Javlibrary
from api.resources.r18 import R18

gc.enable()


# using Uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# APscheduler Config
async_scheduler = AsyncIOScheduler(
    job_defaults={"misfire_grace_time": 5 * 60}, timezone=os.getenv("TZ", "UTC")
)


class Tags(Enum):
    """Set tags for each endpoint."""

    DEMO = "demo"
    API = "secured endpoints"
    STATS = "info / statictics"


r18 = R18()
javdatabase = Javdatabase()
javlibrary = Javlibrary()
javdb = Javdb()

# Search function
async def get_results(name: str, provider: str, only_r18: bool) -> dict[str] | None:
    """Search function."""
    if provider == "all":
        tasks = []
        tasks.append(asyncio.create_task(r18.search(name, only_r18)))
        tasks.append(asyncio.create_task(javdatabase.search(name, only_r18)))
        tasks.append(asyncio.create_task(javlibrary.search(name, only_r18)))
        tasks.append(asyncio.create_task(javdb.search(name)))
        for result in await asyncio.gather(*tasks):
            if result is not None:
                return result

    elif provider == "javlibrary":
        return await javlibrary.search(name, only_r18)
    elif provider == "javdb":
        return await javdb.search(name)
    elif provider == "javdatabase":
        return await javdatabase.search(name, only_r18)
    elif provider == "r18":
        return await r18.search(name, only_r18)


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
            format="<level>{level:<6}</level>:  <cyan>{file}</cyan>.<blue>{function}</blue>:<cyan>{line}</cyan> - <level>{message}</level>",
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
