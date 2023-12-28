from enum import Enum
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from lxml import etree
from src.providers.rss import RSS


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


router = APIRouter(
    prefix="/rss",
    tags=["rss","jav"],
    # responses={
    #     200: {
    #         "model": SuccessfulResponse,
    #     },
    #     404: {"model": UnSucessfulResponse},
    # },
)


@router.get("/javdatabase")
async def javdatabase_feed():
    rss = RSS()
    rss.generate_entries(Providers.jvdtbs)

    return Response(
        content=etree.tostring(
            rss.rss,
            pretty_print=True,
            xml_declaration=True,
            encoding="utf-8",
            standalone=True,
        ).decode("utf-8"),
        media_type="application/xml; charset=utf-8",
    )
