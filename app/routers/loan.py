from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import func, or_, select

from app.core.config import settings
from app.core.database import SessionDep
from app.models.book import Book
from app.models.loan import Loan, LoanStatus
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.loan import LoanCreate, LoanRead, LoanReadWithDetails, LoanRenew, LoanReturn

router = APIRouter(prefix="/loans", tags=["Loan"])


def calculate_penalty(due_date: datetime, return_date: datetime) -> tuple[float, int]:
    """
    Calcule la pénalité pour un retour en retard.

    Args:
        due_date: Date limite de retour
        return_date: Date de retour effectif

    Returns:
        Tuple (pénalité, jours de retard)
    """
    if return_date <= due_date:
        return 0.0, 0

    days_late = (return_date - due_date).days
    penalty = min(days_late * settings.PENALTY_RATE_PER_DAY, settings.MAX_PENALTY)
    return round(penalty, 2), days_late


def update_loan_status(loan: Loan) -> None:
    """Met à jour le statut d'un emprunt en fonction de la date"""
    if loan.return_date:
        loan.status = LoanStatus.RETURNED
    elif datetime.now() > loan.due_date:
        loan.status = LoanStatus.LATE
    else:
        loan.status = LoanStatus.ACTIVE


@router.post("/", response_model=LoanRead, status_code=201)
def create_loan(loan: LoanCreate, session: SessionDep):
    """Créer un nouvel emprunt"""
    book = session.get(Book, loan.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")

    if book.available_copies <= 0:
        raise HTTPException(
            status_code=400,
            detail=f"Le livre '{book.title}' n'est pas disponible actuellement",
        )

    active_loans = session.exec(
        select(func.count()).where(
            Loan.borrower_email == loan.borrower_email,
            or_(Loan.status == LoanStatus.ACTIVE, Loan.status == LoanStatus.LATE),
        )
    ).one()

    if active_loans >= settings.MAX_LOANS_PER_USER:
        raise HTTPException(
            status_code=400,
            detail=f"Limite d'emprunts atteinte ({settings.MAX_LOANS_PER_USER} maximum)",
        )

    now = datetime.now()
    due_date = now + timedelta(days=settings.LOAN_DURATION_DAYS)

    db_loan = Loan(
        book_id=loan.book_id,
        borrower_name=loan.borrower_name,
        borrower_email=loan.borrower_email,
        library_card_number=loan.library_card_number,
        loan_date=now,
        due_date=due_date,
        status=LoanStatus.ACTIVE,
        comments=loan.comments,
    )

    book.available_copies -= 1

    session.add(db_loan)
    session.add(book)
    session.commit()
    session.refresh(db_loan)

    return db_loan


@router.get("/", response_model=PaginatedResponse[LoanReadWithDetails])
def list_loans(
    session: SessionDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[LoanStatus] = None,
    borrower_email: Optional[str] = None,
    book_id: Optional[int] = None,
    active_only: bool = False,
    late_only: bool = False,
):
    """Lister les emprunts avec filtres"""
    statement = select(Loan, Book).join(Book, Loan.book_id == Book.id)

    if status:
        statement = statement.where(Loan.status == status)

    if borrower_email:
        statement = statement.where(Loan.borrower_email.ilike(f"%{borrower_email}%"))

    if book_id:
        statement = statement.where(Loan.book_id == book_id)

    if active_only:
        statement = statement.where(
            or_(Loan.status == LoanStatus.ACTIVE, Loan.status == LoanStatus.LATE)
        )

    if late_only:
        statement = statement.where(Loan.status == LoanStatus.LATE)

    statement = statement.order_by(Loan.loan_date.desc())

    count_statement = select(func.count()).select_from(statement.subquery())
    total = session.exec(count_statement).one()

    offset = (page - 1) * page_size
    statement = statement.offset(offset).limit(page_size)

    results = session.exec(statement).all()

    loans_with_details = []
    for loan, book in results:
        update_loan_status(loan)

        penalty = 0.0
        days_late = 0
        if loan.return_date:
            penalty, days_late = calculate_penalty(loan.due_date, loan.return_date)
        elif loan.status == LoanStatus.LATE:
            penalty, days_late = calculate_penalty(loan.due_date, datetime.now())

        loan_dict = loan.model_dump()
        loan_dict["book_title"] = book.title
        loan_dict["penalty"] = penalty
        loan_dict["days_late"] = days_late
        loans_with_details.append(LoanReadWithDetails(**loan_dict))

    session.commit()

    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=loans_with_details,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
