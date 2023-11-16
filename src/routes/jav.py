from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from src import search_all_providers


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


class UnSucessfulResponse(BaseModel):
    statuCode: int


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
async def search(req: Request, code: str, includeActressUrl: bool = True):
    response = search_all_providers(code, includeActressUrl)
    # print(response)
    if response:
        return JSONResponse(content=response)
    else:
        return Response(status_code=404)
