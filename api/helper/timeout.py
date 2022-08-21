"""Quick hack to reload worker after X seconds"""
import json
import os
import time

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis import asyncio as aioredis
from api import logger


TIMEOUT = int(os.getenv("INACTIVITY_TIMEOUT", "300"))
FILE_TO_CHECK = "timeout"

# After 5min , worker will restart
@logger.catch
async def set_timeout(timeout_scheduler: AsyncIOScheduler) -> None:
    """Set inactivity timeout for (master) worker."""
    async with aioredis.Redis.from_url(
        os.getenv("REDIS_URL"), decode_responses=True
    ) as redis:
        await redis.set("active", "true", ex=TIMEOUT)
    await manager(timeout_scheduler)


async def manager(timeout_scheduler: AsyncIOScheduler) -> None:
    """Manages timeout process."""
    try:
        timeout_scheduler.add_job(
            check_timeout,
            "interval",
            seconds=60,
            id="check_timeout",
            args=[timeout_scheduler],
        )
        timeout_scheduler.start()
    except Exception:  # if job already exists / api call before timeout
        timeout_scheduler.remove_job("check_timeout")
        timeout_scheduler.add_job(
            check_timeout,
            "interval",
            seconds=60,
            id="check_timeout",
            args=[timeout_scheduler],
        )


async def check_timeout(timeout_scheduler: AsyncIOScheduler) -> None:
    """Check if worker is still active."""
    async with aioredis.Redis.from_url(
        os.getenv("REDIS_URL"), decode_responses=True
    ) as redis:
        if await redis.get("active") != "true":
            timeout_scheduler.remove_job("check_timeout")
            with open(FILE_TO_CHECK, "w", encoding="UTF-8") as output:
                # quick hack just to reload worker
                output.write(json.dumps({"time": round(time.time())}))
