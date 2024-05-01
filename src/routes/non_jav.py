from fastapi import APIRouter
from src.providers import boobpedia

router = APIRouter(tags=["non-jav", "boobpedia"])
boobpedia = boobpedia.Boobpedia()


@router.get("/boobpedia/todaysBirthdays", tags=["boobpedia"])
async def todaysBirthday():
    """
    Get today's birthdays from the Boobpedia API.

    Returns:
        The list of today's birthdays.

    Raises:
        None.
    """
    return boobpedia.todaysBirthdays()
