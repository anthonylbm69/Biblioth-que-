from datetime import date
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.book import Book


class Author(SQLModel, table=True):

    __tablename__ = "authors"

    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str = Field(index=True)
    last_name: str = Field(index=True)
    birth_date: date
    nationality: str = Field(max_length=2)
    biography: Optional[str] = Field(default=None)
    death_date: Optional[date] = Field(default=None)
    website: Optional[str] = Field(default=None)

    books: list["Book"] = Relationship(back_populates="author")
