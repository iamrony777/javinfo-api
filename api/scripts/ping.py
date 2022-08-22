"""Simple Healthcheck script, supports Healthchecks.io and Uptime-Kuma (push type)"""
import asyncio
import json
import os
import sys

from httpx import AsyncClient
from redis.asyncio import Redis
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
        # logger.success("[PING] Successful")
        sys.exit(0)


@logger.catch
async def self_ping():
    """
    Self-Ping , Perfect for PaaS like Heroku
    """
    if os.getenv("BASE_URL") is None and not os.path.exists("/tmp/hostname"):
        if os.getenv("REDIS_URL") is not None:
            async with Redis.from_url(os.getenv("REDIS_URL"), decode_responses=True) as redis:
                for key in redis.scan_iter(match="user/*", count=10, _type="list"):
                    data = json.loads(redis.lrange(key, 0, redis.llen(key))[0])
                    url: str = data["headers"]["x-forwarded-proto"] + "://" + (data["headers"]["host"])
                    with open("/tmp/hostname", "w", encoding="utf-8") as output:
                        output.write(url)  # "URL/check"
                    break
            async with AsyncClient(base_url=url, timeout=60) as conn:
                status_code = (await conn.head("/check")).status_code
                if status_code != 200:
                    logger.error(f"ERROR {status_code}")
                    sys.exit(status_code)
        if (
            os.getenv("REDIS_REST_URL") is not None
            and os.getenv("REDIS_REST_TOKEN") is not None
        ):
            header = {"Authorization": f"Bearer {os.getenv('REDIS_REST_TOKEN')}"}
            async with AsyncClient(
                base_url=os.getenv("REDIS_REST_URL"), headers=header, timeout=60
            ) as conn:
                try:
                    user = (
                        await conn.post(
                            "/", json=["SCAN", "0", "MATCH", "user/*", "COUNT", "10"]
                        )
                    ).json()["result"][1][0]
                except IndexError:
                    logger.warning("`BASE_URL` is not set and no request made to this server")
                    sys.exit(1)
                result: dict[str, str | dict[str, str]] = (
                    await conn.post("/", json=["LRANGE", user, "0", "0"])
                ).json()
            result = json.loads(result["result"][0].split("},{")[0]+"}")
            resp_host, resp_proto =  result["headers"]["host"], result["headers"]["x-forwarded-proto"]
            url = resp_proto + "://" + resp_host
            with open("/tmp/hostname", "w", encoding="utf-8") as output:
                output.write(url)  # "URL/check"
            async with AsyncClient(base_url=url, timeout=60) as conn:
                status_code = (await conn.head("/check")).status_code
                if status_code != 200:
                    logger.error(f"ERROR {status_code}")
                    sys.exit(status_code)
    elif os.getenv("BASE_URL") is not None:
        async with AsyncClient(base_url=os.getenv("BASE_URL")) as conn:
            status_code = (await conn.head("/check")).status_code
            if status_code != 200:
                logger.error(f"ERROR {status_code}")
                sys.exit(status_code)
    elif os.path.exists("/tmp/hostname"):
        with open("/tmp/hostname", encoding="utf-8") as data:
            url = data.read()
        async with AsyncClient(base_url=url) as conn:
            status_code = (await conn.head("/check")).status_code
            if status_code != 200:
                logger.error(f"ERROR {status_code}")
                sys.exit(status_code)

    #And if extra monitor needed
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


if __name__ == "__main__":
    asyncio.run(start())
