"""Saving request logs in redis instead of saving in a .log file as plaintext format """
import json
import os
from datetime import datetime

import httpx
from api import logger
from api.helper import aioredis
from fastapi import Request
from slowapi.util import get_remote_address


@logger.catch()
async def redis_logger(request: Request):
    """Save request data as logs in redis."""
    if os.environ.get("LOG_REQUEST") == "true":
        request_dict = {}
        user_ip = get_remote_address(request)

        # adding request parameters / query
        request_dict["query"] = dict(request.query_params)

        # adding request method type
        request_dict["method"] = request.method

        # adding request path
        request_dict["path"] = request.url.path

        # adding request headers
        request_dict["headers"] = dict(request.headers)

        # adding IP address details from ipinfo.io
        async with httpx.AsyncClient(
            base_url="https://ipinfo.io",
            params={"token": os.getenv("IPINFO_TOKEN")},
            headers={"Accept": "application/json"},
        ) as client:
            resp = await client.get(f"/{user_ip}")
            if resp.status_code == 200:
                request_dict["user"] = resp.json()
            else:
                request_dict["user"] = user_ip
        # current datetime
        request_dict["time"] = f"{datetime.now():%Y-%m-%d %H:%M:%S%z}"
        async with aioredis.Redis.from_url(
            os.environ["REDIS_URL"], decode_responses=True
        ) as redis:
            await redis.rpush(f"user/{user_ip}", json.dumps(request_dict))
    else:
        return
