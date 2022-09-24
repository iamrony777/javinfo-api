"""Redirects"""
from typing import Optional
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

temp = APIRouter(include_in_schema=False)


@temp.api_route("/{path}", methods=["GET", "POST", "HEAD"])
async def redirect_to(path: Optional[str], request: Request, ):
    """
    If request is made to `/{path}`
    redirect all of them to `/api/{path}`
    """
    if bool(request.query_params):
        return RedirectResponse(
            "/api/" + path + "?" + str(request.query_params), headers=request.headers
        )
    return RedirectResponse("/api/" + path, headers=request.headers)
