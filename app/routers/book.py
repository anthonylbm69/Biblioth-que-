from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import func, or_, select

from app.core.database import SessionDep
from app.models.author import Author
from app.models.book import Book, BookCategory
from app.models.loan import Loan, LoanStatus
from app.schemas.book import BookCreate, BookRead, BookReadWithAuthor, BookUpdate
from app.schemas.common import MessageResponse, PaginatedResponse

router = APIRouter(prefix="/books", tags=["Books"])


@router.post(
    "/", response_model=BookRead, status_code=201
)  # décorateur, fastapi ne renverra que ceux qu'il y a dans le BookRead
def create_book(
    book: BookCreate, session: SessionDep
):  # fonction, injection de dependence avec le sessionDep

    # vérification de l'unicité du book
    statement = select(Book).where(Book.isbn == book.isbn)
    existing = session.exec(statement).first()
    if existing:
        raise HTTPException(
            status_code=400, detail=f"Un livre avec l'ISBN {book.isbn} existe déjà"
        )

    # vérification si l'auteur existe ou pas
    author = session.get(Author, book.author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Auteur non trouvé")

    # si tout est bon je créer mon livre
    db_book = Book.model_validate(book)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@router.get("/search", response_model=PaginatedResponse[BookReadWithAuthor])
def search_books(
    session: SessionDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    title: Optional[str] = None,
    author_name: Optional[str] = None,
    category: Optional[BookCategory] = None,
    available_only: bool = False,
):
    statement = select(Book, Author).join(Author, Book.author_id == Author.id)

    if title:
        statement = statement.where(Book.title.ilike(f"%{title}%"))
    if author_name:
        statement = statement.where(
            or_(
                Author.first_name.ilike(f"%{author_name}%"),
                Author.last_name.ilike(f"%{author_name}%"),
            )
        )
    if category:
        statement = statement.where(Book.category == category)
    if available_only:
        statement = statement.where(Book.available_copies > 0)

    total = session.exec(select(func.count()).select_from(statement.subquery())).one()
    results = session.exec(
        statement.offset((page - 1) * page_size).limit(page_size)
    ).all()

    books_with_authors = []
    for book, author in results:
        loans_count = session.exec(
            select(func.count()).where(Loan.book_id == book.id)
        ).one()
        book_dict = book.model_dump()
        book_dict["author_name"] = f"{author.first_name} {author.last_name}"
        book_dict["loans_count"] = loans_count
        books_with_authors.append(BookReadWithAuthor(**book_dict))

    return PaginatedResponse(
        items=books_with_authors,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.patch("/{book_id}", response_model=BookRead)
def update_book(book_id: int, book_update: BookUpdate, session: SessionDep):
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")

    update_data = book_update.model_dump(exclude_unset=True)

    available = update_data.get("available_copies", db_book.available_copies)
    total = update_data.get("total_copies", db_book.total_copies)
    if available > total:
        raise HTTPException(status_code=400, detail="Disponibles > Total impossible")

    for key, value in update_data.items():
        setattr(db_book, key, value)

    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@router.delete("/{book_id}", response_model=MessageResponse)
def delete_book(book_id: int, session: SessionDep):
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")

    active_loans = session.exec(
        select(func.count()).where(
            Loan.book_id == book_id,
            or_(Loan.status == LoanStatus.ACTIVE, Loan.status == LoanStatus.LATE),
        )
    ).one()
    if active_loans > 0:
        raise HTTPException(
            status_code=400, detail="Emprunts en cours, suppression impossible"
        )

    session.delete(db_book)
    session.commit()
    return MessageResponse(message="Livre supprimé")


@router.get("/search-by-isbn", response_model=BookReadWithAuthor)
def get_book_by_isbn(
    isbn: str = Query(..., description="L'ISBN exact du livre"),
    session: SessionDep = None,
):
    statement = (
        select(Book, Author)
        .join(Author, Book.author_id == Author.id)
        .where(Book.isbn == isbn.strip())
    )
    result = session.exec(statement).first()

    if not result:
        raise HTTPException(
            status_code=404, detail=f"Livre avec l'ISBN {isbn} non trouvé"
        )

    book, author = result

    book_dict = book.model_dump()
    book_dict["author_name"] = f"{author.first_name} {author.last_name}"

    return BookReadWithAuthor(**book_dict)


@router.get("/search-by-year", response_model=PaginatedResponse[BookReadWithAuthor])
def search_books_by_year(
    session: SessionDep,
    year_min: Optional[int] = Query(None, description="Année de début"),
    year_max: Optional[int] = Query(None, description="Année de fin"),
    year_exact: Optional[int] = Query(
        None, description="Année précise (ignore min/max si rempli)"
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    statement = select(Book, Author).join(Author, Book.author_id == Author.id)

    if year_exact:
        statement = statement.where(Book.publication_year == year_exact)
    else:
        if year_min:
            statement = statement.where(Book.publication_year >= year_min)
        if year_max:
            statement = statement.where(Book.publication_year <= year_max)

    total = session.exec(select(func.count()).select_from(statement.subquery())).one()
    results = session.exec(
        statement.offset((page - 1) * page_size).limit(page_size)
    ).all()

    books_with_authors = []
    for book, author in results:
        loans_count = session.exec(
            select(func.count()).where(Loan.book_id == book.id)
        ).one()
        book_dict = book.model_dump()
        book_dict["author_name"] = f"{author.first_name} {author.last_name}"
        book_dict["loans_count"] = loans_count
        books_with_authors.append(BookReadWithAuthor(**book_dict))

    return PaginatedResponse(
        items=books_with_authors,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/search-books-by-iso/{iso}", response_model=list[BookReadWithAuthor])
def get_books_by_language(iso: str, session: SessionDep):
    statement = (
        select(Book, Author)
        .join(Author, Book.author_id == Author.id)
        .where(Book.language.ilike(iso.strip()))
    )

    results = session.exec(statement).all()

    if not results:
        raise HTTPException(
            status_code=404, detail=f"Aucun livre trouvé pour la langue : {iso}"
        )

    books_with_authors = []
    for book, author in results:
        loans_count = session.exec(
            select(func.count()).where(Loan.book_id == book.id)
        ).one()

        book_dict = book.model_dump()
        book_dict["author_name"] = f"{author.first_name} {author.last_name}"
        book_dict["loans_count"] = loans_count
        books_with_authors.append(BookReadWithAuthor(**book_dict))

    return books_with_authors
