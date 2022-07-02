"""api/__init__.py"""

import asyncio
import gc
import os
import secrets
import sys
from enum import Enum

import uvloop
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from loguru import logger
from redis import asyncio as aioredis

import api.resources.javdatabase as jdtb
import api.resources.javdb as jdb
import api.resources.javlibrary as jlb
import api.resources.r18 as r18
from api.helper.redis_log import logger as request_logger
from api.helper.redis_log import manage
from api.helper.string_modify import filter_string
from api.helper.timeout import FILE_TO_CHECK
from api.helper.timeout import set_timeout as timeout
from api.scripts.javdb_login import main as login
from api.scripts.r18_db import main as r18_db

gc.enable()


# using Uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# APscheduler Config
async_scheduler = AsyncIOScheduler(job_defaults={"misfire_grace_time": 5 * 60})

# Fastapi Config
security = HTTPBasic()

app = FastAPI(docs_url="/demo", redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# site folder is created only during docker build
app.mount("/docs", StaticFiles(directory="site", html=True), name="docs")

app.mount("/readme", StaticFiles(directory="api/html", html=True), name="root")


class Tags(Enum):
    """Set tags for each endpoint."""

    DEMO = "demo"
    DOCS = "secured endpoints"


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


# Security Templacte
def check_access(credentials: HTTPBasicCredentials = Depends(security)):
    """Check credentials."""
    correct_username = secrets.compare_digest(
        credentials.username, os.environ["API_USER"]
    )
    correct_password = secrets.compare_digest(
        credentials.password, os.environ["API_PASS"]
    )
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access Denied",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True


# Loguru - Logger config
LOGGER_CONFIG = {
    "handlers": [
        dict(
            format="{time:%Y-%m-%d at %H:%M:%S} [{level}] {file.name} -> {function}#{line} | {message} ",
            sink="javinfo.log",
            enqueue=True,
            level=20,
        ),
        dict(
            sink=sys.stdout,
            format="<lvl>{level}</lvl>: <y>{module}</y>.<c>{function}#{line}</c> | <lvl>{message}</lvl>",
            enqueue=True,
            colorize=True,
            level=20,
        ),
    ],
}

logger.configure(**LOGGER_CONFIG)
