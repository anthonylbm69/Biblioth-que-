from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

class LoanHistory(SQLModel, table=True):

    __tablename__ = "loansHistory"

    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="books.id", index=True)
    total_loans: int = Field(foreign_key="loan.id", index= True)
    book_popularity: int = Field(default=0, ge=0)

    book: "Book" = Relationship(back_populates="loans")
    loans: list["Loan"] = Relationship(back_populates="book")
