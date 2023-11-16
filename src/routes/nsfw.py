from fastapi import APIRouter
from src.providers import boobpedia

router = APIRouter(prefix="/nsfw", tags=["nsfw"])
boobpedia = boobpedia.Boobpedia()


@router.get("/boobpedia/todaysBirthdays", tags=["boobpedia"])
async def todaysBirthday():
    return boobpedia.todaysBirthdays()
