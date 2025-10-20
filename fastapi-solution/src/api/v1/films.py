from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from core.messages import FILM_NOT_FOUND
from queries.film import FilmFilter, SearchFilmFilter
from services.film import FilmService, get_film_service
from models.film import Film

router = APIRouter()

@router.get("/", response_model=list[Film])
async def all_films(
        film_service: FilmService = Depends(get_film_service),
        film_filter: FilmFilter = Depends(),
) -> list[Film]:
    """Returns all films with pagination."""
    films = await film_service.get_all(film_filter)

    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=FILM_NOT_FOUND)

    return [Film(**film.model_dump()) for film in films]


@router.get("/search", response_model=list[Film])
async def search_films(
        film_service: FilmService = Depends(get_film_service),
        film_filter: SearchFilmFilter = Depends(),
) -> list[Film]:
    """Returns all films found by fuzzy search with pagination."""
    films = await film_service.get_all(film_filter)

    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=FILM_NOT_FOUND)

    return [Film(**film.model_dump()) for film in films]


@router.get("/{film_id}", response_model=Film)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    """Returns the film by identifier."""
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=FILM_NOT_FOUND)

    return Film(**film.model_dump())
