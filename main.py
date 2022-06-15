import asyncio
import gc
import os
import secrets
from enum import Enum

import uvicorn
import uvloop
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import (BackgroundTasks, Depends, FastAPI, HTTPException, Request,
                     status)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from redis import asyncio as aioredis

import src.javdatabase as jdtb
import src.javdb as jdb
import src.javlibrary as jlb
import src.r18 as r18
from src.helper.javdb_login import main as login
from src.helper.r18_db import main as r18_db
from src.helper.redis_log import logger as request_logger
from src.helper.redis_log import manage
from src.helper.string_modify import filter_string
from src.helper.timeout import FILE_TO_CHECK
from src.helper.timeout import set_timeout as timeout

gc.enable()

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

app = FastAPI(docs_url='/demo', redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/docs", StaticFiles(directory="site", html=True),
              name="docs")

app.mount("/readme", StaticFiles(directory="src/root", html=True), name="root")


security = HTTPBasic()
async_scheduler = AsyncIOScheduler()
 

class Tags(Enum):
    """Set tags for each endpoint."""
    DEMO = 'demo'
    DOCS = 'secured endpoints'
    BADGE = 'shields.io badge'


def check_access(credentials: HTTPBasicCredentials = Depends(security)):
    """Check credentials."""
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


async def get_results(name: str, provider:str, only_r18: bool):
    """Search function."""

    if provider == 'all':
        tasks = []
        tasks.append(asyncio.create_task(r18.main(name, only_r18)))
        tasks.append(asyncio.create_task(jdtb.main(name, only_r18)))
        tasks.append(asyncio.create_task(jlb.main(name, only_r18)))
        tasks.append(asyncio.create_task(jdb.main(name)))
        for result in await asyncio.gather(*tasks):
            if result is not None:
                return result

    elif provider == 'javlibrary':
        return await jlb.main(name, only_r18)
    elif provider == 'javdb':
        return await jdb.main(name)
    elif provider == 'javdatabase':
        return await jdtb.main(name, only_r18)
    elif provider == 'r18':
        return await r18.main(name, only_r18)


@app.on_event('startup')
async def startup():
    """Startup events"""
    async_scheduler.add_job(r18_db, trigger='interval', days=1)
    if os.environ.get('CAPTCHA_SOLVER_URL') is not None and len(os.environ.get('CAPTCHA_SOLVER_URL')) > 5:
        if not os.path.exists(
            FILE_TO_CHECK):
            async_scheduler.add_job(login, args=[os.getcwd()])
        async_scheduler.add_job(
            login, args=[os.getcwd()], trigger='interval', days=6)
    if os.environ.get('REDIS_URL') is not None and len(os.environ.get('REDIS_URL')) > 5:
        redis = await aioredis.Redis.from_url(os.environ.get('REDIS_URL'), encoding='utf-8', decode_responses=True, db=2)
        await FastAPILimiter.init(redis)
        print([('INFO:\t    [REDIS] Connection established') if await redis.ping() else ('ERROR:\t    [REDIS] Authentication failed')][0])
        if not os.path.exists(
            FILE_TO_CHECK):
            async_scheduler.add_job(r18_db)
        async_scheduler.add_job(r18_db, trigger='interval', minutes=5)
    else:
        print('ERROR:\t    [REDIS] Connection failed')

    async_scheduler.start()

@app.get('/', include_in_schema=False)
async def root():
    """Redirect to readme."""
    return RedirectResponse('/readme')

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    """Favicon endpoint."""
    return FileResponse(f'{os.getcwd()}/favicon.ico')


@app.head('/check', include_in_schema=False)
async def check():
    """(Uptime) Monitor endpoint."""
    return {'status': 'OK'}

@app.post('/demo/search', dependencies=[Depends(RateLimiter(times=1, seconds=10))], summary='Search for a video by DVD ID / Content ID', tags=[Tags.DEMO])
async def demo_search(request: Request, background_tasks: BackgroundTasks, name: str, provider: str | None = 'all', only_r18: bool | None = False):
    """
### [Demo] Limited to (1 requests/10 seconds)

Search for a Movie by its ID.


|       Provider      | Query | Actress Data | Movie Data | Screenshots |
|:-------------------:|:-----:|:------------:|:----------:|:-----------:|
|       `javdb`       |   Y   |       N      |      Y     |      N      |
|     `javlibrary`    |   Y   |       Y      |      Y     |      N      |
|    `javdatabase`    |   Y   |       Y      |      Y     |      N      |
|        `r18`        |   Y   |       Y      |      Y     |      Y      |
|      Boobpedia      |   N   |       Y      |      N     |      N      |
    """
    background_tasks.add_task(request_logger, request)
    background_tasks.add_task(timeout, async_scheduler)

    name = filter_string(name).upper()
    result = await get_results(name=name, provider=provider, only_r18=only_r18)
    if result is not None:
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'error': f'{name} Not Found'})


@app.get('/database', tags=[Tags.DOCS])
async def logs(request: Request, background_tasks: BackgroundTasks, hasaccess: bool = Depends(check_access)):
    """Get a copy of current database (.rdb file) if using non-plugin redis server"""
    background_tasks.add_task(request_logger, request)
    if hasaccess:
        if os.environ.get('CREATE_REDIS') == 'true':
            try:
                await manage(save=True)
                return FileResponse('/app/src/database.rdb', media_type='application/octet-stream', filename='database.rdb')
            except Exception as exception:
                return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={'error': str(exception)})
        else:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'error': 'Can\'t download database file'})
    else:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={'error': 'Access Denied'})


@app.get('/version', tags=[Tags.BADGE])
async def version():
    """Get the current version of the API."""
    json_msg = {'schemaVersion': 1,
                'label': 'Version',
                'message': '1.2',
                'color': 'informational',
                'style': 'for-the-badge'}
    return json_msg


@app.post('/search', tags=[Tags.DOCS])
async def search(request: Request, background_tasks: BackgroundTasks, name: str, hasaccess: bool = Depends(check_access), provider: str | None = 'all', only_r18: bool | None = False):
    """Protected search endpoint."""
    background_tasks.add_task(request_logger, request)
    background_tasks.add_task(timeout, async_scheduler)
    if hasaccess:
        name = filter_string(name).upper()
        result = await get_results(name=name, provider=provider, only_r18=only_r18)
        if result is not None:
            return JSONResponse(status_code=status.HTTP_200_OK, content=result)
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'error': f'{name} Not Found'})
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={'error': 'Access Denied'})


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=int(os.environ.get('PORT', 8000)), http='httptools', loop='uvloop',
                    proxy_headers=True, reload=True, reload_dirs=['.'], reload_includes=[FILE_TO_CHECK])
