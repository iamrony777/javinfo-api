"""Saving request logs in redis instead of saving in a .log file as plaintext format """
import json
import os
from datetime import datetime

import httpx
from fastapi import Request
from redis import asyncio as aioredis
from api import logger

TOKEN = os.environ.get("IPINFO_TOKEN")


@logger.catch()
async def redis_logger(request: Request):
    """Save request data as logs in redis."""
    if os.environ.get("LOG_REQUEST") == "true":
        request_dict = {}
        user_ip = request.headers.get("X-Forwarded-For")

        # adding request parameters / query
        request_dict["query"] = dict(request.query_params)

        # adding request method type
        request_dict["method"] = request.method

        # adding request path
        request_dict["path"] = request.url.path

        # adding request headers
        request_dict["headers"] = dict(request.headers)

        # adding IP address details from ipinfo.io
        if TOKEN is not None and len(TOKEN) > 4:
            async with httpx.AsyncClient(
                base_url="https://ipinfo.io",
                params={"token": TOKEN},
                headers={"Accept": "application/json"},
            ) as client:
                request_dict["user"] = (await client.get(f"/{user_ip}")).json()
        else:
            async with httpx.AsyncClient(
                base_url="https://ipinfo.io", headers={"Accept": "application/json"}
            ) as client:
                ip_data = (await client.get(f"/{user_ip}")).json()
                ip_data.pop("readme")
            request_dict["user"] = ip_data

        # current datetime
        request_dict["time"] = f"{datetime.now():%Y-%m-%d %H:%M:%S%z}"
        async with aioredis.Redis.from_url(
            os.environ["REDIS_URL"], decode_responses=True
        ) as redis:
            await redis.rpush(f"user/{user_ip}", json.dumps(request_dict))
    else:
        return
