"""api/routers/endpoints"""
import base64
import os
import re
import secrets
import time

from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi_limiter.depends import RateLimiter
from httpx import AsyncClient

from api import (
    Tags,
    aioredis,
    async_scheduler,
    filter_string,
    get_results,
    logger,
    redis_logger,
    timeout,
    version,
)

# SwaggerUI Demo @ /api/demo
endpoint = FastAPI(root_path="/api", docs_url="/demo")

# Fastapi Config
security = HTTPBasic()

# MKDocs Documentation @ /api/docs
endpoint.mount(
    "/docs",
    StaticFiles(directory="site", html=True),
    name="Documentation",
)


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


@logger.catch
@endpoint.post(
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
    |       `javdb`       |   Y   |       N      |      Y     |      Y      |
    |     `javlibrary`    |   Y   |       Y      |      Y     |      Y      |
    |    `javdatabase`    |   Y   |       Y      |      Y     |      Y      |
    |        `r18`        |   Y   |       Y      |      Y     |      Y      |
    |      Boobpedia      |   N   |       Y      |      N     |      N      |
    """
    background_tasks.add_task(redis_logger, request)
    background_tasks.add_task(timeout, async_scheduler)

    filtered_name = filter_string(name)
    if filtered_name is not None:
        result = await get_results(
            name=filtered_name.upper(), provider=provider, only_r18=only_r18
        )
        if result is not None:
            return JSONResponse(status_code=status.HTTP_200_OK, content=result)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": f"{name} Not Found",
                "message": f"Possible Movie ID: {filtered_name}",
            },
            background=background_tasks
        )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": f"{name} Not Found",
            "message": "No Movie is found from input string",
        },
        background=background_tasks
    )


@logger.catch
@endpoint.get("/database", tags=[Tags.API])
async def logs(
    request: Request,
    background_tasks: BackgroundTasks,
    hasaccess: bool = Depends(check_access),
):
    """Get a copy of current database (.rdb file) if using non-plugin redis server."""
    async with aioredis.Redis.from_url(
        os.environ["REDIS_URL"], decode_responses=True
    ) as redis:
        if os.environ.get("CREATE_REDIS") == re.search(
            r"true", os.getenv("CREATE_REDIS"), re.IGNORECASE
        ) and (await redis.save()):
            return FileResponse(
                "/app/database.rdb",
                media_type="application/octet-stream",
                filename="database.rdb",
                background=background_tasks.add_task(redis_logger, request),
            )


@logger.catch
@endpoint.get("/logs", tags=[Tags.API])
async def get_logs(
    request: Request,
    background_tasks: BackgroundTasks,
    hasaccess: bool = Depends(check_access),
):
    """An endpoint to download saved logs"""
    return FileResponse(
        "/app/javinfo.log",
        media_type="text/plain",
        filename=f"javinfo_{round(time.time())}.log",
        background=background_tasks.add_task(redis_logger, request),
    )


@endpoint.post("/search", tags=[Tags.API])
@logger.catch
async def search(
    request: Request,
    background_tasks: BackgroundTasks,
    name: str,
    provider: str | None = "all",
    only_r18: bool | None = False,
    hasaccess: bool = Depends(check_access),
):
    """Protected search endpoint."""
    filtered_name = filter_string(name)
    background_tasks.add_task(timeout, async_scheduler)
    background_tasks.add_task(redis_logger, request)
    if filtered_name is not None:
        result = await get_results(
            name=filtered_name.upper(), provider=provider, only_r18=only_r18
        )
        if result is not None:
            return JSONResponse(status_code=status.HTTP_200_OK, content=result)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": f"{name} Not Found",
                "message": f"Possible Movie ID: {filtered_name}",
            },
            background=background_tasks,
        )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": f"{name} Not Found",
            "message": "No Movie is found from input string",
        },
        background=background_tasks,
    )

@endpoint.get("/total_users", tags=[Tags.STATS])
@logger.catch
async def get_total_users() -> str:
    """Get number of total users from redis database log"""

    data = {
        "label": "Total Users",
        "labelColor": "232a2d",
        "message": "0",
        "color": "67b0e8",
        "style": "for-the-badge",
    }

    try:
        async with aioredis.Redis.from_url(
            os.getenv("REDIS_URL"), decode_responses=True
        ) as redis:
            users = len((await redis.scan(0, "user/*", 10000))[1])
            if users > 10000:
                data["message"] = "10K+"
            else:
                data["message"] = str(users)
    except Exception as exception:
        logger.error(exception)

    with open("api/html/images/users.png", "rb") as users_png:
        users_base64 = base64.b64encode(users_png.read()).decode("utf-8")
        data["logo"] = f"data:image/png;base64,{users_base64}"
        async with AsyncClient(timeout=10) as client:
            return Response(
                content=(
                    await client.get(
                        "https://img.shields.io/static/v1",
                        params=data,
                    )
                ).text,
                media_type="image/svg+xml;charset=utf-8"
                # background=background_tasks.add_task(redis_logger, request),
            )


@endpoint.get("/version", tags=[Tags.STATS])
@logger.catch
async def get_current_version():
    """Version Badge"""
    async with AsyncClient(timeout=10) as client:
        return Response(
            content=(
                await client.get(
                    "https://img.shields.io/static/v1",
                    params={
                        "label": "JAVINFO API",
                        "labelColor": "232a2d",
                        "message": version,
                        "color": "c47fd5",
                        "style": "for-the-badge",
                    },
                )
            ).text,
            media_type="image/svg+xml;charset=utf-8",
        )
