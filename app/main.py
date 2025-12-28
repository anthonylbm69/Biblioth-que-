from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import create_db_and_tables
from app.core.error_handlers import (
    generic_exception_handler,
    library_exception_handler,
    validation_exception_handler,
)
from app.core.exceptions import LibraryException
from app.routers import author, book, loan, loanHistory


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gérer le cycle de vie de l'application"""
    # Startup
    create_db_and_tables()
    yield
    # Shutdown
    pass


# Créer l'application FastAPI
app = FastAPI(
    title="API Gestion de Bibliothèque",
    description="API REST complète pour gérer une bibliothèque moderne",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routers
app.include_router(author.router)
app.include_router(book.router)
app.include_router(loan.router)
"""app.include_router(loanHistory.router)"""


@app.get("/", tags=["Root"])
def read_root():
    """Endpoint racine de l'API"""
    return {
        "message": "Bienvenue sur l'API de gestion de bibliothèque",
        "version": "1.0.0",
        "documentation": "/docs",
    }


@app.get("/health", tags=["Root"])
def health_check():
    """Endpoint de vérification de santé de l'API"""
    return {"status": "healthy"}
