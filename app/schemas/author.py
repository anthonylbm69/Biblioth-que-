from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, HttpUrl, field_validator

from app.schemas.validators import validate_birth_date


class AuthorBase(BaseModel):
    """Schema de base pour un auteur"""

    first_name: str
    last_name: str
    birth_date: date
    nationality: str
    biography: Optional[str] = None
    death_date: Optional[date] = None
    website: Optional[str] = None

    @field_validator("nationality")
    @classmethod
    def validate_nationality(cls, v: str) -> str:
        """Valide que la nationalité est un code pays ISO de 2 lettres"""
        if len(v) != 2 or not v.isalpha():
            raise ValueError("La nationalité doit être un code pays ISO de 2 lettres")
        return v.upper()

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date_field(cls, v: date, info) -> date:
        """Valide la date de naissance"""
        death_date = info.data.get("death_date")
        return validate_birth_date(v, death_date)


class AuthorCreate(AuthorBase):
    """Schema pour créer un auteur"""

    pass


class AuthorUpdate(BaseModel):
    """Schema pour mettre à jour un auteur (tous les champs optionnels)"""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[date] = None
    nationality: Optional[str] = None
    biography: Optional[str] = None
    death_date: Optional[date] = None
    website: Optional[str] = None

    @field_validator("nationality")
    @classmethod
    def validate_nationality(cls, v: Optional[str]) -> Optional[str]:
        """Valide que la nationalité est un code pays ISO de 2 lettres"""
        if v is not None:
            if len(v) != 2 or not v.isalpha():
                raise ValueError("La nationalité doit être un code pays ISO de 2 lettres")
            return v.upper()
        return v


class AuthorRead(AuthorBase):
    """Schema pour lire un auteur"""

    id: int

    class Config:
        from_attributes = True


class AuthorWithBooks(AuthorRead):
    """Schema pour lire un auteur avec ses livres"""

    books_count: int = 0
