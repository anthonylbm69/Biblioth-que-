from fastapi import APIRouter, FastAPI
from app.models import Item
from typing import Union

app = FastAPI()
router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Binevenue dans la bibliothèque"}

@router.get("/books/{book.id}")
def read_item(book: Item, q: Union[str, None] = None):
    return {"book_id": book.id, "q": q }

@router.post("/books/")
def create_item(book: Item):
    return {"book": book, "message": "Livre a bien était ajouté"}

@router.put("/books/{book.id}")
def update_item(book: Item):
    return {"book_name": book.name, "book_id": book.id}

app.include_router(router)