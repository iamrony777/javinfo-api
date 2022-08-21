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
from api.helper.string_modify import filter_string
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
    DOCS = "secured endpoints"
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

API_BASE_URL = os.getenv('BASE_URL', default=os.getenv('RAILWAY_STATIC_URL'))

# Shields.io | /total_users
user_resp = {
        "schemaVersion": 1,
        "label": "Total Users",
        "labelColor": "white",
        "message": "",
        "logoSvg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512"><!--! Font Awesome Pro 6.1.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. --><path d="M319.9 320c57.41 0 103.1-46.56 103.1-104c0-57.44-46.54-104-103.1-104c-57.41 0-103.1 46.56-103.1 104C215.9 273.4 262.5 320 319.9 320zM369.9 352H270.1C191.6 352 128 411.7 128 485.3C128 500.1 140.7 512 156.4 512h327.2C499.3 512 512 500.1 512 485.3C512 411.7 448.4 352 369.9 352zM512 160c44.18 0 80-35.82 80-80S556.2 0 512 0c-44.18 0-80 35.82-80 80S467.8 160 512 160zM183.9 216c0-5.449 .9824-10.63 1.609-15.91C174.6 194.1 162.6 192 149.9 192H88.08C39.44 192 0 233.8 0 285.3C0 295.6 7.887 304 17.62 304h199.5C196.7 280.2 183.9 249.7 183.9 216zM128 160c44.18 0 80-35.82 80-80S172.2 0 128 0C83.82 0 48 35.82 48 80S83.82 160 128 160zM551.9 192h-61.84c-12.8 0-24.88 3.037-35.86 8.24C454.8 205.5 455.8 210.6 455.8 216c0 33.71-12.78 64.21-33.16 88h199.7C632.1 304 640 295.6 640 285.3C640 233.8 600.6 192 551.9 192z"/></svg>',
        "color": "success",

    }