from fastapi import FastAPI
from fastapi.requests import Request

app = FastAPI()


@app.get("/")
async def root(request: Request):
    print(request.headers)
    return {
        "hello": request.headers.get(
            "x-real-ip", request.headers.get("x-forwarded-for", None)
        )
    }
