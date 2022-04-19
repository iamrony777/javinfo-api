import asyncio

import httpx
import nest_asyncio
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from src.helper.javdb_login import main as login

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

nest_asyncio.apply()


@app.on_event("startup")
async def startup_event():
    await login('/app')
    scheduler = AsyncIOScheduler()
    scheduler.add_job(login, args=['/app'], trigger='interval', days=6)
    scheduler.start()


async def get_results(id, provider):
    import src.javdatabase as jdtb
    import src.javdb as jdb
    import src.javlibrary as jlb

    if provider == None:
        tasks = []
        tasks.append(asyncio.create_task(jlb.main(id)))
        tasks.append(asyncio.create_task(jdtb.main(id)))
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


@app.get('/')
async def root():
    async with httpx.AsyncClient() as client:
        response = await client.get('https://http.cat/200')
    return Response(status_code=status.HTTP_200_OK, content=response.content, media_type='image/png')


@app.get('/search')
async def search(id: str, provider=None):
    """
    Search for a Movie by its ID. 

    Required : `id` (str)\n
    Optional : `provider` (str)\n\n

    Returns : JSONResponse\n

    Providers :

        javlibrary : https://javlibrary.com/en \n
        javdatabase : https://javdatabase.com \n
        javdb : https://javdb.com \n

    """
    from src.helper.string_modify import filter
    _id = filter(id.upper())
    result = await get_results(id=_id, provider=provider)
    if result != None:
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    else:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
