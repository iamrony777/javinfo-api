"""Redirects"""
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

temp = APIRouter(include_in_schema=False)


@temp.get("/docs")
async def redirect_to_docs():
    """/docs -> /api/docs"""
    return RedirectResponse("/api/docs")


@temp.get("/demo")
async def redirect_to_demo():
    """/demo -> /api/demo"""
    return RedirectResponse("/api/demo")


@temp.post("/public")
async def redirect_to_public(request: Request):
    """/public -> /api/public"""
    return RedirectResponse(
        "/api/public" + "?" + str(request.query_params),
        headers=request.headers
    )

@temp.post("/search")
async def redirect_to_search(request: Request):
    """/search -> /api/search"""
    return RedirectResponse(
        "/api/search" + "?" + str(request.query_params),
        headers=request.headers
    )
