from pydantic import BaseModel
from datetime import date


class Item(BaseModel):
    id: int
    name: str
    isbn: str
    year_of_publication: date
    reference: str
    
    description: str | None = None