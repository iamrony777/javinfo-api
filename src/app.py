from fastapi import FastAPI
from fastapi.requests import Request

app = FastAPI()


@app.get("/")
async def root(request: Request):
    return {"hello": request.headers.get("X-Forwarded-From")}
