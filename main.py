import asyncio

import nest_asyncio

nest_asyncio.apply()

import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_results(id):
    tasks = []
    tasks.append(asyncio.create_task(jlb.main(id)))
    tasks.append(asyncio.create_task(jdtb.main(id)))
    tasks.append(asyncio.create_task(jdb.main(id)))
    results = await asyncio.gather(*tasks)
    for result in results:
        if result is not None:
            return result

@app.get('/env')
async def update_env():
    from src.helper.mongo import main as db
    await db()

    return JSONResponse(status_code=status.HTTP_200_OK)


@app.get('/search')
async def search(id):
    from src.helper.string_modify import filter
    _id = filter(id)
    result = await get_results(_id)
    if result != None:
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    else:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND)

try:
    import src.javdatabase as jdtb
    import src.javdb as jdb
    import src.javlibrary as jlb
except KeyError:
    asyncio.run(update_env())    
    
    import src.javdatabase as jdtb
    import src.javdb as jdb
    import src.javlibrary as jlb


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
