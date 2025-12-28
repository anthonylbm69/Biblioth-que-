import re
from datetime import date, datetime

from app.core.exceptions import InvalidISBNException


def validate_isbn13(isbn: str) -> str:
    """
    Valide un ISBN-13 selon l'algorithme de checksum.

    Args:
        isbn: L'ISBN à valider

    Returns:
        L'ISBN nettoyé (sans tirets)

    Raises:
        InvalidISBNException: Si l'ISBN est invalide
    """
    # Nettoyer l'ISBN (enlever les tirets et espaces)
    clean_isbn = isbn.replace("-", "").replace(" ", "")

    # Vérifier le format
    if not re.match(r"^\d{13}$", clean_isbn):
        raise InvalidISBNException("L'ISBN doit être au format ISBN-13 (13 chiffres)")

    # Calculer le checksum
    total = 0
    for i, digit in enumerate(clean_isbn[:-1]):
        weight = 1 if i % 2 == 0 else 3
        total += int(digit) * weight

    checksum = (10 - (total % 10)) % 10

    # Vérifier le checksum
    if checksum != int(clean_isbn[-1]):
        raise InvalidISBNException("Le checksum de l'ISBN est invalide")

    return clean_isbn


def validate_publication_year(year: int) -> int:
    """
    Valide l'année de publication.

    Args:
        year: L'année à valider

    Returns:
        L'année validée

    Raises:
        ValueError: Si l'année est hors limites
    """
    current_year = datetime.now().year
    if year < 1450 or year > current_year:
        raise ValueError(
            f"L'année de publication doit être entre 1450 et {current_year}"
        )
    return year


def validate_birth_date(birth_date: date, death_date: date | None = None) -> date:
    """
    Valide la date de naissance d'un auteur.

    Args:
        birth_date: La date de naissance
        death_date: La date de décès (optionnelle)

    Returns:
        La date de naissance validée

    Raises:
        ValueError: Si la date est invalide
    """
    if birth_date > date.today():
        raise ValueError("La date de naissance ne peut pas être dans le futur")

    if death_date and birth_date >= death_date:
        raise ValueError("La date de naissance doit être antérieure à la date de décès")

    return birth_date


def validate_available_copies(available: int, total: int) -> int:
    """
    Valide que les exemplaires disponibles ne dépassent pas le total.

    Args:
        available: Nombre d'exemplaires disponibles
        total: Nombre total d'exemplaires

    Returns:
        Le nombre d'exemplaires disponibles validé

    Raises:
        ValueError: Si la validation échoue
    """
    if available < 0:
        raise ValueError("Le nombre d'exemplaires disponibles ne peut pas être négatif")

    if available > total:
        raise ValueError(
            "Le nombre d'exemplaires disponibles ne peut pas dépasser le total"
        )

    return available
