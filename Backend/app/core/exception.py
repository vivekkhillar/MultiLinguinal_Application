class AuthenticationError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)
    
class EmailAlreadyExistsError(AuthenticationError):

    def __init__(self, message: str = "Email address is already registered.") -> None:
        super().__init__(message)

class UsernameAlreadyExistsError(AuthenticationError):

    def __init__(self, message: str = "Username is already taken.") -> None:
        super().__init__(message)

class InvalidPreferredLanguageError(AuthenticationError):

    def __init__(self, message: str = "Invalid preferred language ID.") -> None:
        super().__init__(message)
