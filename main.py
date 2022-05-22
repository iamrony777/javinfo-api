# v4 or 5 ..
# Today is 10th May, 2020
# Sky is clear and the sun is shining
# But my code isn't
# To my future self, I'm sorry now fix all extra if..else, for loops

import asyncio
import os
import secrets
from typing import Optional

import aioredis
import nest_asyncio
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

import src.javdatabase as jdtb
import src.javdb as jdb
import src.javlibrary as jlb
import src.r18 as r18
from src.helper.javdb_login import main as login
from src.helper.r18_db import main as r18_db
from src.helper.string_modify import filter

nest_asyncio.apply()

app = FastAPI(docs_url='/demo', redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
security = HTTPBasic()


def check_access(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(
        credentials.username, os.environ['API_USER'])
    correct_password = secrets.compare_digest(
        credentials.password, os.environ['API_PASS'])
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access Denied",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True


async def get_results(id: str, provider: Optional[str] = None):

    if provider == None:
        tasks = []
        tasks.append(asyncio.create_task(r18.main(id)))
        tasks.append(asyncio.create_task(jdtb.main(id)))
        tasks.append(asyncio.create_task(jlb.main(id)))
        tasks.append(asyncio.create_task(jdb.main(id)))
        results = await asyncio.gather(*tasks)
        for result in results:
            if result is not None:
                return result
    elif provider == 'javlibrary':
        return await jlb.main(id)
    elif provider == 'javdb':
        return await jdb.main(id)
    elif provider == 'javdatabase':
        return await jdtb.main(id)
    elif provider == 'r18':
        return await r18.main(id)


@app.on_event('startup')
async def startup_event():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(r18_db, trigger='interval', days=1)
    if os.environ.get('CAPTCHA_SOLVER_URL') is not None:
        await login(os.getcwd())
        scheduler.add_job(login, args=[os.getcwd()],
                          trigger='interval', days=6)
    if os.environ.get('REDIS_URL') is not None:
        await r18_db()
        scheduler.add_job(r18_db, trigger='interval', days=1)
    scheduler.start()
    redis = await aioredis.from_url(os.environ.get('REDIS_URL'), encoding='utf-8', decode_responses=True, db=1)
    await FastAPILimiter.init(redis)
    if await redis.ping():
        print('INFO:\t  [REDIS] Connection established')
    else:
        print('ERROR:\t  [REDIS] Connection failed')


@app.get('/', include_in_schema=False)
async def root():
    with open('./src/img/logo.png', 'rb') as image:
        return Response(status_code=status.HTTP_200_OK, content=image.read(), media_type='image/png')

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(f'{os.getcwd()}/favicon.ico')


@app.post('/demo/search', dependencies=[Depends(RateLimiter(times=1, seconds=10))], summary='Search for a video by DVD ID / Content ID')
async def search(id: str, provider=None):
    """
### [Demo] Limited to (1 requests/10 seconds)

Search for a Movie by its ID. 


|     Provider    | Query | Actress Data | Movie Data | Image Data | Screenshots |
|:---------------:|:-----:|:------------:|:----------:|:----------:|-------------|
|     `javdb`     |   Y   |       N      |      Y     |      Y     | N           |
|   `javlibrary`  |   Y   |       Y      |      Y     |      N     | N           |
|  `javdatabase`  |   Y   |       Y      |      Y     |      Y     | N           |
| `r18` <br>(default) |   Y   |       Y      |      Y     |      Y     | Y           |
|    Boobpedia    |   N   |       Y      |      N     |      Y     | N           |


    """
    _id = filter(id).upper()
    result = await get_results(id=_id, provider=provider)
    if result != None:
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    else:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'error': f'{_id} Not Found'})


@app.post('/search', include_in_schema=False)
async def search(id: str, hasaccess: bool = Depends(check_access), provider=None):
    if hasaccess:
        _id = filter(id).upper()
        result = await get_results(id=_id, provider=provider)
        if result != None:
            return JSONResponse(status_code=status.HTTP_200_OK, content=result)
        else:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'error': f'{_id} Not Found'})
    else:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={'error': 'Access Denied'})

@app.head('/check', include_in_schema=False)
async def check():
    return JSONResponse(status_code=status.HTTP_200_OK, content={'status': 'OK'})

@app.get('/version', include_in_schema=False)
async def version():
    json_msg = {'schemaVersion': 1,
                'label': 'Version',
                'message': '2.3',
                'color': 'FF4489',
                'style': 'for-the-badge'}
    return json_msg

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get('PORT', 8000)))
