import asyncio
import os
import sys

import httpx
from loguru import logger

LOGGER_CONFIG = {
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

HEALTHCHECK_PROVIDER = str(os.getenv("HEALTHCHECK_PROVIDER"))
UPTIMEKUMA_PUSH_URL = str(os.getenv("UPTIMEKUMA_PUSH_URL"))
HEALTHCHECKSIO_PING_URL = str(os.getenv("HEALTHCHECKSIO_PING_URL"))

logger.configure(**LOGGER_CONFIG)


@logger.catch
async def healthchecks_io(url: str) -> None:
    """
    Healthchecks.io integration \n
    set `HEALTHCHECK_PROVIDER` to `healthchecksio` \n
    set `HEALTHCHECKSIO_PING_URL` as following `https://<healthchecks-io-instance-url>/<monitor-uuid>`
    or `https://<healthchecks-io-instance-url>/<ping-key>/<monitor-name>`
    """
    async with httpx.AsyncClient(timeout=10) as client:
        await client.get(url)
        logger.success("[PING] Successful")


@logger.catch
async def uptime_kuma(url: str) -> None:
    """
    Uptimekuma integration \n
    set `HEALTHCHECK_PROVIDER` to `uptimekuma` \n
    set `UPTIMEKUMA_PUSH_URL` as following `https://<uptime-kuma-instance-url>/api/push/<monitor-slug>` with or without optional parameters
    """
    async with httpx.AsyncClient(timeout=10, http2=True) as client:
        await client.get(url)
        logger.success("[PING] Successful")


if __name__ == "__main__":
    if HEALTHCHECK_PROVIDER == "uptimekuma" or UPTIMEKUMA_PUSH_URL not in [
        None,
        "None",
        "",
    ]:
        asyncio.run(uptime_kuma(UPTIMEKUMA_PUSH_URL))
    if HEALTHCHECK_PROVIDER == "healthchecksio" or HEALTHCHECKSIO_PING_URL not in [
        None,
        "None",
        "",
    ]:
        asyncio.run(healthchecks_io(HEALTHCHECKSIO_PING_URL))
