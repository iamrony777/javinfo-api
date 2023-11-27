from enum import Enum
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from src import search_all_providers


class Providers(str, Enum):
    """
    Enumeration of providers for the API.

    This class represents the available providers for the API. Each provider has a unique value
    that can be used to identify it.
    """
    r18 = "r18"
    jvdtbs = "jvdtbs"
    jvlib = "jvlib"
    javdb = "javdb"
    all = "all"


class Details(BaseModel):
    director: str
    release_date: str
    runtime: int
    studio: str


class Actress(BaseModel):
    name: str
    image: str


class SuccessfulResponse(BaseModel):

    id: str
    title: str
    title_ja: str | None
    page: str
    poster: str
    preview: str | None
    details: Details
    actress: list[Actress]
    screenshots: list[str]
    tags: list[str]
    screenshots: list[str]
    tags: list[str]


class UnSucessfulResponse(BaseModel):
    statuCode: int
    message: str | None

router = APIRouter(
    prefix="/jav",
    tags=["jav"],
    responses={
        200: {
            "model": SuccessfulResponse,
        },
        404: {"model": UnSucessfulResponse},
    },
)


@router.get("/search")
async def search(
    req: Request, code: str, provider: Providers = Providers.all, includeActressUrl: bool = True
):
    response = search_all_providers(code, provider, includeActressUrl)
    if response:
        return JSONResponse(content=response)
    return Response(status_code=404)
