from pydantic import BaseModel


class Film(BaseModel):
    """
    Pydantic model representing a film API schema.

    Attributes:
    - title (str): Заголовок.
    - description (str | None): Содержание.
    - created (datetime): Дата создания.
    - imdb_rating (float | None): Рейтинг.
    - genres (List): Жанры.
    - directors (List): Режиссёры.
    - actors (List): Актёры.
    - writers (List): Сценаристы.
    - file_link (str | None): Ссылка на файл.
    """

    uuid: str
    title: str
    description: str | None
    created: str
    imdb_rating: float | None
    genres: list
    directors: list
    actors: list
    writers: list
    file_link: str | None
