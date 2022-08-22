"""Redirects"""
from fastapi import APIRouter
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
async def redirect_to_public():
    """/public -> /api/public"""
    return RedirectResponse("/api/public")


@temp.post("/search")
async def redirect_to_search():
    """/search -> /api/search"""
    return RedirectResponse("/api/search")
