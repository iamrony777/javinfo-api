import os
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from src.routes import jav, nsfw
import uvicorn

app = FastAPI()

app.include_router(jav.router)
app.include_router(nsfw.router)

@app.get("/")
async def root(request: Request):
    # print(request.headers)

    # return {
    #     "hello": request.headers.get(
    #         "x-real-ip", request.headers.get("x-forwarded-for", None)
    #     )
    # }
    return RedirectResponse("/docs")


if __name__ == "__main__":
    uvicorn.run(app=app, port=int(os.environ.get("PORT", "3000")), use_colors=False)
