from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Schema générique pour les réponses paginées"""

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class MessageResponse(BaseModel):
    """Schema pour les réponses avec message simple"""

    message: str
    detail: Optional[str] = None


class StatsResponse(BaseModel):
    """Schema pour les statistiques globales"""

    total_books: int
    total_copies: int
    active_loans: int
    late_loans: int
    occupancy_rate: float


class BookStatsResponse(BaseModel):
    """Schema pour les statistiques d'un livre"""

    book_id: int
    book_title: str
    total_loans: int
    average_loan_duration: float
    times_late: int
    popularity_rank: Optional[int] = None


class AuthorStatsResponse(BaseModel):
    """Schema pour les statistiques d'un auteur"""

    author_id: int
    author_name: str
    total_books: int
    total_loans: int
