import os
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
import uvicorn

from src.routes import jav, non_jav

app = FastAPI()
app.include_router(jav.router)
app.include_router(non_jav.router)

@app.get("/")
async def root(request: Request):
    return RedirectResponse("/docs")



if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0",port=int(os.getenv("PORT", "3000")), use_colors=False)
