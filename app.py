import os
from fastapi import FastAPI
from fastapi.requests import Request
from src import search_all_providers
import uvicorn
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

if __name__ == "__main__":
    uvicorn.run(
        app=app,
        port=int(os.environ.get("PORT", "3000")),
        use_colors=True
    )