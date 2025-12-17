class LibraryException(Exception):
    """Exception de base pour l'application bibliothèque"""

    pass


class BookNotFoundException(LibraryException):
    """Levée quand un livre n'est pas trouvé"""

    pass


class AuthorNotFoundException(LibraryException):
    """Levée quand un auteur n'est pas trouvé"""

    pass


class LoanNotFoundException(LibraryException):
    """Levée quand un emprunt n'est pas trouvé"""

    pass


class BookNotAvailableException(LibraryException):
    """Levée quand un livre n'est pas disponible pour l'emprunt"""

    pass


class LoanLimitExceededException(LibraryException):
    """Levée quand un utilisateur atteint sa limite d'emprunts"""

    pass


class InvalidISBNException(LibraryException):
    """Levée quand un ISBN est invalide"""

    pass


class AuthorHasBooksException(LibraryException):
    """Levée quand on tente de supprimer un auteur avec des livres"""

    pass


class BookHasActiveLoansException(LibraryException):
    """Levée quand on tente de supprimer un livre avec des emprunts actifs"""

    pass
