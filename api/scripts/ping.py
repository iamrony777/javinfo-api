#!/usr/bin/env python3
"""Simple Healthcheck script, supports Healthchecks.io and Uptime-Kuma (push type)"""
import asyncio
import os
import sys

from httpx import AsyncClient
from api import logger

HEALTHCHECK_PROVIDER = str(os.getenv("HEALTHCHECK_PROVIDER"))
UPTIMEKUMA_PUSH_URL = str(os.getenv("UPTIMEKUMA_PUSH_URL"))
HEALTHCHECKSIO_PING_URL = str(os.getenv("HEALTHCHECKSIO_PING_URL"))


@logger.catch()
async def healthchecks_io(url: str) -> None:
    """
    Healthchecks.io integration \n
    set `HEALTHCHECK_PROVIDER` to `healthchecksio` \n
    set `HEALTHCHECKSIO_PING_URL` as following `https://<healthchecks-io-instance-url>/<monitor-uuid>`
    or `https://<healthchecks-io-instance-url>/<ping-key>/<monitor-name>`
    """
    async with AsyncClient(timeout=10) as client:
        await client.get(url)
        # logger.success("[PING] Successful")
        sys.exit(0)


@logger.catch()
async def uptime_kuma(url: str) -> None:
    """
    Uptimekuma integration \n
    set `HEALTHCHECK_PROVIDER` to `uptimekuma` \n
    set `UPTIMEKUMA_PUSH_URL` as following `https://<uptime-kuma-instance-url>/api/push/<monitor-slug>` with or without optional parameters
    """
    async with AsyncClient(timeout=15, http2=True) as client:
        await client.get(url)
        sys.exit(0)

@logger.catch
async def local_ping() -> None:
    """docker healthcheck"""
    async with AsyncClient(timeout=30) as client:
        if (await client.head("http://127.0.0.1:8000/api/check")).status_code == 200:
            sys.exit(0)
        sys.exit(1)

@logger.catch
async def self_ping():
    """
    Self-Ping , Perfect for PaaS like Heroku
    """
    if os.getenv("BASE_URL") is not None:
        async with AsyncClient(base_url=os.getenv("BASE_URL")) as conn:
            status_code = (await conn.head("/api/check")).status_code
            if status_code != 200:
                logger.error(f"ERROR {status_code}")
                sys.exit(1)
            sys.exit(0)
    else:
        logger.error("BASE_URL is not set")


    #And if extra monitor needed with self-ping
    if HEALTHCHECK_PROVIDER == "uptimekuma":
        await uptime_kuma(UPTIMEKUMA_PUSH_URL)
    if HEALTHCHECK_PROVIDER == "healthchecksio":
        await healthchecks_io(HEALTHCHECKSIO_PING_URL)

@logger.catch
async def start():
    if HEALTHCHECK_PROVIDER == "uptimekuma":
        await uptime_kuma(UPTIMEKUMA_PUSH_URL)
    if HEALTHCHECK_PROVIDER == "healthchecksio":
        await healthchecks_io(HEALTHCHECKSIO_PING_URL)
    if HEALTHCHECK_PROVIDER == "self":
        await self_ping()
    if HEALTHCHECK_PROVIDER == "local":
        await local_ping()


if __name__ == "__main__":
    asyncio.run(start())
