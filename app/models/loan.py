from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel

class LoanStatus(str, Enum):

    ACTIVE = "actif"
    RETURNED = "retourné"
    LATE = "en retard"


class Loan(SQLModel, table=True):

    __tablename__ = "loans"

    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="books.id", index=True)
    borrower_name: str = Field(index=True)
    borrower_email: str = Field(index=True)
    library_card_number: str = Field(index=True)
    loan_date: datetime = Field(default_factory=datetime.now)
    due_date: datetime
    return_date: Optional[datetime] = Field(default=None)
    status: LoanStatus = Field(default=LoanStatus.ACTIVE)
    comments: Optional[str] = Field(default=None)
    renewed: bool = Field(default=False)

    book: "Book" = Relationship(back_populates="loans")
