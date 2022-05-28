import json
import os
from datetime import datetime
from typing import Optional

import httpx
from fastapi import Request
from redis import asyncio as aioredis

# async def read_from_list(key: str, redis: aioredis.Redis):
#     result = []
#     for data in await redis.lrange(key, 0, -1):
#         result.append(json.loads(data))

#     print(json.dumps(result, indent=4))


async def push_dict_to_list(key: str, value: dict, redis: aioredis.Redis):
    await redis.rpush(key, json.dumps(value))


async def logger(request: Request):
    if os.environ.get('LOG_REQUEST') == 'true':
        TOKEN = os.environ.get('IPINFO_TOKEN')

        request_dict = {}
        method = request.method
        user_ip = request.headers.get('X-Forwarded-For')
        path = request.url.path

        # adding request parameters / query
        request_dict['query'] = {}
        for key, value in request.query_params.items():
            request_dict['query'][key] = value

        # adding request method type
        request_dict['method'] = method

        # adding request path
        request_dict['path'] = path

        # adding request headers
        request_dict['headers'] = {}
        for key, value in request.headers.items():
            request_dict['headers'][key] = value

        # adding IP address details from ipinfo.io
        if TOKEN != None and len(TOKEN) > 4:
            async with httpx.AsyncClient(base_url='https://ipinfo.io', params={'token': TOKEN}, headers={'Accept': 'application/json'}) as client:
                request_dict['user'] = (await client.get(f'/{user_ip}')).json()
        else:
            async with httpx.AsyncClient(base_url='https://ipinfo.io', headers={'Accept': 'application/json'}) as client:
                ip_data = (await client.get(f'/{user_ip}')).json()
                ip_data.pop('readme')
            request_dict['user'] = ip_data

        # current datetime
        request_dict['time'] = f'{datetime.now():%Y-%m-%d %H:%M:%S%z}'

        await manage(f'user:{user_ip}', request_dict, push=True)
    else:
        return


async def manage(key: Optional[any] = None, values: Optional[any] = None, **kwargs):
    # DB=1 is for logging purposes
    async with aioredis.Redis.from_url(os.environ['REDIS_URL'], decode_responses=True, db=1) as redis:

        # if kwargs.get('read'):
        #         await read_from_list(key, redis)
        if kwargs.get('push'):
            await push_dict_to_list(key, values, redis)
        elif kwargs.get('save'):
            await redis.save()
