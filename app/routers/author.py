from fastapi import APIRouter, HTTPException, Query
from sqlmodel import func, select
from app.core.database import SessionDep
from app.core.exceptions import AuthorHasBooksException, AuthorNotFoundException
from app.models.author import Author
from app.models.book import Book
from app.schemas.author import AuthorCreate, AuthorRead, AuthorUpdate, AuthorWithBooks
from app.schemas.common import MessageResponse, PaginatedResponse

router = APIRouter(prefix="/authors", tags=["Authors"])


@router.post("/", response_model=AuthorRead, status_code=201)
def create_author(author: AuthorCreate, session: SessionDep):
    try:
        statement = select(Author).where(
            Author.first_name == author.first_name,
            Author.last_name == author.last_name,
        )
        existing = session.exec(statement).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Un auteur avec le nom {author.first_name} {author.last_name} existe déjà",
            )

        db_author = Author.model_validate(author)
        session.add(db_author)
        session.commit()
        session.refresh(db_author)
        return db_author
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error : {str(e)}")


@router.get("/", response_model=PaginatedResponse[AuthorRead])
def list_authors(
    session: SessionDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    nationality: str | None = None,
    sort_by: str = Query("last_name", regex="^(last_name|first_name|birth_date)$"),
    order: str = Query("asc", regex="^(asc|desc)$"),
):
    statement = select(Author)

    if search:
        statement = statement.where(
            (Author.first_name.ilike(f"%{search}%")) | (Author.last_name.ilike(f"%{search}%"))
        )

    if nationality:
        statement = statement.where(Author.nationality == nationality.upper())

    sort_column = getattr(Author, sort_by)
    if order == "desc":
        statement = statement.order_by(sort_column.desc())
    else:
        statement = statement.order_by(sort_column)

    count_statement = select(func.count()).select_from(statement.subquery())
    total = session.exec(count_statement).one()

    # Pagination
    offset = (page - 1) * page_size
    statement = statement.offset(offset).limit(page_size)

    authors = session.exec(statement).all()

    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=authors,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{author_id}", response_model=AuthorWithBooks)
def get_author(author_id: int, session: SessionDep):
    author = session.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Auteur non trouvé")

    books_count = session.exec(select(func.count()).where(Book.author_id == author_id)).one()

    author_dict = author.model_dump()
    author_dict["books_count"] = books_count

    return AuthorWithBooks(**author_dict)


@router.patch("/{author_id}", response_model=AuthorRead)
def update_author(author_id: int, author_update: AuthorUpdate, session: SessionDep):
    db_author = session.get(Author, author_id)
    if not db_author:
        raise HTTPException(status_code=404, detail="Auteur non trouvé")

    update_data = author_update.model_dump(exclude_unset=True)

    if "first_name" in update_data or "last_name" in update_data:
        first_name = update_data.get("first_name", db_author.first_name)
        last_name = update_data.get("last_name", db_author.last_name)

        statement = select(Author).where(
            Author.first_name == first_name,
            Author.last_name == last_name,
            Author.id != author_id,
        )
        existing = session.exec(statement).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Un auteur avec le nom {first_name} {last_name} existe déjà",
            )

    for key, value in update_data.items():
        setattr(db_author, key, value)

    session.add(db_author)
    session.commit()
    session.refresh(db_author)
    return db_author


@router.delete("/{author_id}", response_model=MessageResponse)
def delete_author(author_id: int, session: SessionDep):
    db_author = session.get(Author, author_id)
    if not db_author:
        raise HTTPException(status_code=404, detail="Auteur non trouvé")

    books_count = session.exec(select(func.count()).where(Book.author_id == author_id)).one()

    if books_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Impossible de supprimer l'auteur car il a {books_count} livre(s) associé(s)",
        )

    session.delete(db_author)
    session.commit()
    return MessageResponse(
        message="Auteur supprimé avec succès",
        detail=f"L'auteur {db_author.first_name} {db_author.last_name} a été supprimé",
    )
