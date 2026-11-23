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


class InvalidCredentialsError(AuthenticationError):

    def __init__(self, message: str = "Invalid username or Password") -> None:
        super().__init__(message)

class AccountInactiveError(AuthenticationError):

    def __init__(self, message: str = "User account is not active") -> None:
        super().__init__(message)

class SessionTokenError(AuthenticationError):

    def __init__(self, message : str = "Malformed refresh token received during logout") -> None:
        super().__init__(message)