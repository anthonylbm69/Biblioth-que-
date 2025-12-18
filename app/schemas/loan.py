from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

from app.models.loan import LoanStatus


class LoanBase(BaseModel):
    """Schema de base pour un emprunt"""

    book_id: int
    borrower_name: str
    borrower_email: EmailStr
    library_card_number: str

    @field_validator("library_card_number")
    @classmethod
    def validate_card_number(cls, v: str) -> str:
        """Valide le numéro de carte de bibliothèque"""
        if not v or len(v) < 5:
            raise ValueError(
                "Le numéro de carte de bibliothèque doit contenir au moins 5 caractères"
            )
        return v


class LoanCreate(LoanBase):
    """Schema pour créer un emprunt"""

    comments: Optional[str] = None


class LoanRead(LoanBase):
    """Schema pour lire un emprunt"""

    id: int
    loan_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: LoanStatus
    comments: Optional[str] = None
    renewed: bool = False

    class Config:
        from_attributes = True


class LoanReturn(BaseModel):
    """Schema pour retourner un livre"""

    return_date: Optional[datetime] = None
    comments: Optional[str] = None


class LoanRenew(BaseModel):
    """Schema pour renouveler un emprunt"""

    pass


class LoanReadWithDetails(LoanRead):
    """Schema pour lire un emprunt avec les détails du livre"""

    book_title: str = ""
    penalty: float = 0.0
    days_late: int = 0
