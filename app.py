import os
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse, RedirectResponse, Response
from src import search_all_providers
import uvicorn

app = FastAPI()


@app.get("/")
async def root(request: Request):
    # print(request.headers)

    # return {
    #     "hello": request.headers.get(
    #         "x-real-ip", request.headers.get("x-forwarded-for", None)
    #     )
    # }
    return RedirectResponse('/docs')

@app.get("/search")
async def search(req: Request, code: str, includeActressUrl: bool = True):
    response = search_all_providers(code, includeActressUrl)
    # print(response)
    if response:
        return JSONResponse( content=response )
    else:
       return Response(
            status_code=404
        )




if __name__ == "__main__":
    uvicorn.run(app=app, port=int(os.environ.get("PORT", "3000")), use_colors=False)
