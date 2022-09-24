"""Server"""
import os
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from redis.asyncio import Redis
from api import logger
from api.helper.timeout import FILE_TO_CHECK
from api.routers import endpoints, redirects

app = FastAPI(
    title="JAVINFO-API | Swagger UI",
    docs_url=None,
    openapi_url="/openapi.json",
    redoc_url=None,
)

app.mount("/api", endpoints.endpoint, name="API Endpoints")
app.include_router(redirects.temp)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "HEAD"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Startup events."""
    if os.environ.get("REDIS_URL") is not None and len(os.environ.get("REDIS_URL")) > 5:
        redis = await Redis.from_url(
            os.environ.get("REDIS_URL"), encoding="utf-8", decode_responses=True
        )
        if await redis.ping():
            logger.success("[REDIS] Connection established")
        else:
            logger.critical("[REDIS] Authentication failed")
            sys.exit(1)
    else:
        logger.critical("[REDIS] Connection failed, no REDIS_URL found in env")
        sys.exit(1)


app.mount("/", StaticFiles(directory="api/html", html=True), name="root")

if __name__ == "__main__":
    uvicorn.run(
        "api.__main__:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        http="httptools",
        loop="uvloop",
        proxy_headers=True,
        reload=True,
        reload_dirs=["."],
        reload_excludes=["*.log", "*.py"],
        reload_includes=[FILE_TO_CHECK],
    )
