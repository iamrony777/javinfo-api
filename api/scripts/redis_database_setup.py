#!/usr/bin/env python3
"""Move all key-values into one database"""
import asyncio
import os
import re
import sys
from time import sleep

import uvloop
from redis import asyncio as aioredis
from api import logger

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# Check DB number
async def need_to_setup():
    """
    If redis-database have more than 1 database then it needs to be configured first
    """
    async with aioredis.Redis.from_url(
        os.getenv("REDIS_URL"), decode_responses=True, db=0
    ) as redis:
        if len(await redis.info("Keyspace")) == 1:
            logger.success("No need to configure Redis, starting API")
            sys.exit(0)
        return True


# Restructure Actress DB
@logger.catch()
async def actress_db():
    """
    Rename `name`: `url`
    to actress/`name`: `url` under DB:0
    """
    async with aioredis.from_url(
        os.getenv("REDIS_URL"),
        db=0,
        decode_responses=True,
    ) as redis:
        randomkey = await redis.randomkey()
        if randomkey is not None and not bool(re.search(r"actress", randomkey)):
            # Get all keys, and values
            names: list[str] = (await redis.scan(0, "*", 99999))[1]
            urls: list[str] = await redis.mget(names)
            logger.info(f"[Actress DB]: Total {len(names)} actress data found")
            # Dump them all
            await redis.delete(*names)
            while True:
                try:
                    # Rename & Reinsert
                    names = [name.replace(name, f"actress/{name}") for name in names]
                    await redis.mset(dict(zip(names, urls)))
                    break
                except Exception as exception:
                    logger.critical(f'{exception}, Trying again')
                    sleep(10)


# Restructure Logs DB
@logger.catch()
async def logs_db():
    """
    Rename `log:` & `user:` to `log/` & `user/`\n
    Also Move keys from DB:1 to DB:0
    """
    async with aioredis.from_url(
        os.getenv("REDIS_URL"), db=1, decode_responses=True
    ) as redis:
        randomkey = await redis.randomkey()
        if (
            randomkey is not None
            and bool(re.search(r"user:", randomkey))
            or bool(re.search(r"log:", randomkey))
        ):
            old_keys: list[str] = (await redis.scan(0, "*", 10000))[1]
            logger.info(
                f"[Logs DB]: Total {len(old_keys)} request data was saved so far"
            )

            # # Change "user:" -> "user/" or "log:" -> "log/"
            new_keys = [
                key.replace(key.split(":")[0] + ":", key.split(":")[0] + "/")
                for key in old_keys
            ]

            for src, dst in list(zip(old_keys, new_keys)):
                (await redis.rename(src, dst))
                (await redis.move(dst, 0))


# Restructure JavDB Login creds
@logger.catch()
async def javdb_login_db():
    """
    Rename `<cookie>` to `cookie/<cookie>` , Move keys from DB:2 to DB:0
    """
    async with aioredis.from_url(
        os.getenv("REDIS_URL"),
        db=2,
        decode_responses=True,
    ) as redis:
        if (await redis.dbsize()) == 2 and (
            await redis.get("remember_me_token")
        ) is not None:
            # Get all keys, and values
            cookies: list[str] = (await redis.scan(0, "*", 10))[1]
            values: list[str] = await redis.mget(cookies)

            # Dump them all
            await redis.delete(*cookies)

            # Rename & Reinsert
            cookies = [cookie.replace(cookie, f"cookie/{cookie}") for cookie in cookies]
            await redis.mset(dict(zip(cookies, values)))
            for cookie in cookies:
                await redis.move(cookie, 0)


if __name__ == "__main__":
    with logger.catch():
        if (
            os.getenv("CREATE_REDIS")
            == re.search(r"false", os.getenv("CREATE_REDIS"), re.IGNORECASE)
            or os.getenv("REDIS_URL") is None
        ):
            logger.info("Couldn't connect to Redis Instance")
            sys.exit(1)
        else:
            logger.info("Checking redis instance")
            if asyncio.run(need_to_setup()):
                logger.info("Restructuring Redis instance")

                # ActressDB
                asyncio.run(actress_db())
                logger.success("[Actress DB]: Done")

                # LogsDB
                asyncio.run(logs_db())
                logger.success("[Logs DB]: Done")

                # JavDB Login cookies
                asyncio.run(javdb_login_db())
                logger.success("[JAVDB Login DB]: Done")
                sys.exit(0)
