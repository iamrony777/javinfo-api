"""Server"""
import os
import sys
import time

import uvicorn

from api import (FILE_TO_CHECK, BackgroundTasks, Depends, FastAPILimiter,
                 FileResponse, JSONResponse, RateLimiter, RedirectResponse,
                 Request, Tags, aioredis, app, async_scheduler, check_access,
                 filter_string, get_results, logger, login, manage, r18_db,
                 request_logger, status, timeout)


@app.on_event("startup")
@logger.catch
async def startup():
    """Startup events."""
    # async_scheduler.add_job(r18_db, trigger="interval", days=1)
    # if (
    #     os.environ.get("CAPTCHA_SOLVER_URL") is not None
    #     and len(os.environ.get("CAPTCHA_SOLVER_URL")) > 5
    # ):
    #     if not os.path.exists(FILE_TO_CHECK):
    #         async_scheduler.add_job(login, args=[os.getcwd()])
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

        # if not os.path.exists(FILE_TO_CHECK):
        #     async_scheduler.add_job(r18_db)
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


@app.post(
    "/public",
    dependencies=[Depends(RateLimiter(times=1, seconds=10))],
    summary="Search for a video by DVD ID / Content ID",
    tags=[Tags.DEMO],
)
@logger.catch
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


@app.get("/database", tags=[Tags.DOCS])
async def logs(
    request: Request,
    background_tasks: BackgroundTasks,
    hasaccess: bool = Depends(check_access),
):
    """Get a copy of current database (.rdb file) if using non-plugin redis server."""
    background_tasks.add_task(request_logger, request)
    if hasaccess:
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
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Can't download database file"},
        )


@app.get("/logs", tags=[Tags.DOCS])
@logger.catch
async def get_logs(
    request: Request,
    background_tasks: BackgroundTasks,
    hasaccess: bool = Depends(check_access),
):
    """An endpoint to download saved logs"""
    background_tasks.add_task(request_logger, request)
    if hasaccess:
        return FileResponse(
            "/app/javinfo.log",
            media_type="text/plain",
            filename=f"javinfo_{round(time.time())}.log",
        )
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={'error': 'Access Denied'})


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
    if hasaccess:
        name = filter_string(name).upper()
        result = await get_results(name=name, provider=provider, only_r18=only_r18)
        if result is not None:
            return JSONResponse(status_code=status.HTTP_200_OK, content=result)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{name} Not Found"},
        )
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED, content={"error": "Access Denied"}
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
        reload_includes=[FILE_TO_CHECK],
    )
