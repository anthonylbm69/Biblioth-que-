from enum import Enum
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel
from app.models.author import Author
from app.models.loan import Loan

class BookCategory(str, Enum):

    FICTION = "Fiction"
    SCIENCE = "Science"
    HISTOIRE = "Histoire"
    PHILOSOPHIE = "Philosophie"
    BIOGRAPHIE = "Biographie"
    POESIE = "Poésie"
    THEATRE = "Théâtre"
    JEUNESSE = "Jeunesse"
    BD = "BD"
    AUTRE = "Autre"


class Book(SQLModel, table=True):

    __tablename__ = "books"

    id: Optional[int] = Field(default=None, primary_key=True) #fonction Field sert a ajouter des metadonnées
    title: str = Field(index=True)
    isbn: str = Field(unique=True, index=True, max_length=17)
    publication_year: int
    author_id: int = Field(foreign_key="authors.id", index=True)
    available_copies: int = Field(default=0, ge=0)
    total_copies: int = Field(gt=0)
    description: Optional[str] = Field(default=None)
    category: BookCategory = Field(default=BookCategory.AUTRE)
    language: str = Field(max_length=2)  # Code langue ISO
    pages: int = Field(gt=0)
    publisher: str

    author: "Author" = Relationship(back_populates="books")
    loans: list["Loan"] = Relationship(back_populates="book")
