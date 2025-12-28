from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AuthorNotFoundException,
    BookNotAvailableException,
    BookNotFoundException,
    InvalidISBNException,
    LibraryException,
    LoanLimitExceededException,
    LoanNotFoundException,
)


async def library_exception_handler(request: Request, exc: LibraryException):
    """Handler pour les exceptions métier de la bibliothèque"""
    status_code = status.HTTP_400_BAD_REQUEST

    # Déterminer le code de statut approprié
    if isinstance(
        exc, (BookNotFoundException, AuthorNotFoundException, LoanNotFoundException)
    ):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, (BookNotAvailableException, LoanLimitExceededException)):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, InvalidISBNException):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    return JSONResponse(
        status_code=status_code,
        content={"detail": str(exc), "error_type": exc.__class__.__name__},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler pour les erreurs de validation Pydantic"""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({"field": field, "message": error["msg"], "type": error["type"]})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Erreur de validation des données", "errors": errors},
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handler générique pour les erreurs non gérées"""
    # En production, logger l'erreur
    import traceback

    traceback.print_exc()

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Une erreur interne s'est produite",
            "error": str(exc) if request.app.debug else None,
        },
    )
