from fastapi import FastAPI
from fastapi.requests import Request
from src import search_all_providers
app = FastAPI()


@app.get("/")
async def root(request: Request):
    # print(request.headers)
    return {
        "hello": request.headers.get(
            "x-real-ip", request.headers.get("x-forwarded-for", None)
        )
    }

@app.get("/search")
async def search(code: str, reqest: Request):
    return search_all_providers(code)
