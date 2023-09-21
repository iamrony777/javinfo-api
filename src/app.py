from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root(request):
    return {"hello": request}