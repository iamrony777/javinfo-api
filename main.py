"""Server"""
import os
import secrets
import sys
import time

import uvicorn
from fastapi import (BackgroundTasks, Depends, FastAPI, HTTPException, Request,
                     status)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from api import (FILE_TO_CHECK, Tags, aioredis, async_scheduler, filter_string,
                 get_results, logger, manage, request_logger, timeout, version)

# Fastapi Config
security = HTTPBasic()

app = FastAPI(
    title="JAVINFO-API | Swagger UI",
    version=version,
    docs_url="/demo",
    openapi_url="/openapi.json",
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# site folder is created only during docker build
app.mount("/docs", StaticFiles(directory="site", html=True), name="docs")

app.mount("/readme", StaticFiles(directory="api/html", html=True), name="root")

def check_access(credentials: HTTPBasicCredentials = Depends(security)):
    """Check credentials."""
    correct_username = secrets.compare_digest(
        credentials.username, os.environ["API_USER"]
    )
    correct_password = secrets.compare_digest(
        credentials.password, os.environ["API_PASS"]
    )
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access Denied",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True


@app.on_event("startup")
async def startup():
    """Startup events."""
    if os.environ.get("REDIS_URL") is not None and len(os.environ.get("REDIS_URL")) > 5:
        redis = await aioredis.Redis.from_url(
            os.environ.get("REDIS_URL"), encoding="utf-8", decode_responses=True, db=2
        )
        await FastAPILimiter.init(redis)
        if await redis.ping():
            logger.success("[REDIS] Connection established")
        else:
            logger.critical("[REDIS] Authentication failed")
            sys.exit(1)
    else:
        logger.critical("[REDIS] Connection failed, no REDIS_URL found in env")
        sys.exit(1)


# TODO: Dashboard or Something on '/' route
@app.get("/", include_in_schema=False)
async def root():
    """Redirect to readme."""
    return RedirectResponse("/readme")


@app.head("/check", include_in_schema=False)
async def check():
    """(Uptime) Monitor endpoint."""
    return {"status": "OK"}


@logger.catch
@app.post(
    "/public",
    dependencies=[Depends(RateLimiter(times=1, seconds=10))],
    summary="Search for a video by DVD ID / Content ID",
    tags=[Tags.DEMO],
)
async def demo_search(
    request: Request,
    background_tasks: BackgroundTasks,
    name: str,
    provider: str | None = "all",
    only_r18: bool | None = False,
):
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
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"error": f"{name} Not Found"}
    )


@logger.catch
@app.get("/database", tags=[Tags.DOCS])
async def logs(
    request: Request,
    background_tasks: BackgroundTasks,
    hasaccess: bool = Depends(check_access),
):
    """Get a copy of current database (.rdb file) if using non-plugin redis server."""
    background_tasks.add_task(request_logger, request)
    if os.environ.get("CREATE_REDIS") == "true":
        try:
            await manage(save=True)
            return FileResponse(
                "/app/database.rdb",
                media_type="application/octet-stream",
                filename="database.rdb",
            )
        except Exception as exception:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": str(exception)},
            )

@logger.catch
@app.get("/logs", tags=[Tags.DOCS])
async def get_logs(
    request: Request,
    background_tasks: BackgroundTasks,
    hasaccess: bool = Depends(check_access),
):
    """An endpoint to download saved logs"""
    background_tasks.add_task(request_logger, request)
    return FileResponse(
        "/app/javinfo.log",
        media_type="text/plain",
        filename=f"javinfo_{round(time.time())}.log",
    )

@app.post("/search", tags=[Tags.DOCS])
@logger.catch
async def search(
    request: Request,
    background_tasks: BackgroundTasks,
    name: str,
    hasaccess: bool = Depends(check_access),
    provider: str | None = "all",
    only_r18: bool | None = False,
):
    """Protected search endpoint."""
    background_tasks.add_task(request_logger, request)
    background_tasks.add_task(timeout, async_scheduler)
    name = filter_string(name).upper()
    result = await get_results(name=name, provider=provider, only_r18=only_r18)
    if result is not None:
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": f"{name} Not Found"},
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        http="httptools",
        loop="uvloop",
        proxy_headers=True,
        reload=True,
        reload_dirs=["."],
        reload_excludes=["*.log", "*.py"],
        reload_includes=[FILE_TO_CHECK],
    )
