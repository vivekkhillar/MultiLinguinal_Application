from security.password import PasswordHashing
from repositories.user_repository import UserRepository
from sqlalchemy.exc import IntegrityError
from core.logging_config import _get_logger
from core.exception import EmailAlreadyExistsError, UsernameAlreadyExistsError, InvalidPreferredLanguageError


logger = _get_logger()

class AuthenticationService:

    """
        The registration flow should be:
        1. Receive registration details: username, email, password, first_name, optional last_name and preferred_language_id.
        2. Check whether the email already exists using UserRepository.get_by_email().
        3. Check whether the username already exists using UserRepository.get_by_username().
        4. Hash the raw password using PasswordHashing.hash_password().
        5. Call UserRepository.create() with the hashed password.
        6. Return the safe user details received from the repository.
    """


    def __init__(self, user_repository: UserRepository, password_hasher: PasswordHashing):

        self.password_hashed = password_hasher
        self.user_repo = user_repository

    async def register(self,**kwargs):
        
        if await self.user_repo.get_by_email(kwargs['email']):
            raise EmailAlreadyExistsError("Email ID already exists")
        
        if await self.user_repo.get_by_username(kwargs['username']):
            raise UsernameAlreadyExistsError("user name already exists")

        hash_password = self.password_hashed.hash_password(kwargs['password'])

        payload = {
            "username" : kwargs['username'],
            "email" : kwargs['email'],
            "password_hash" : hash_password, # synchronous so no need to import await here
            "first_name" : kwargs['first_name'],
            "preferred_language_id": kwargs.get("preferred_language_id"),
            "last_name" : kwargs.get("last_name") # if you want to send the last_name is optional then you have to send like this
        }

        try:
            create_user = await self.user_repo.create(**payload)
            
        except IntegrityError as exc:
            
            orig = exc.orig
            cause = getattr(orig, "__cause__", None)
            constraint_name = (
                getattr(cause, "constraint_name", None)
                or getattr(orig, "constraint_name", None)
                or getattr(getattr(orig, "diag", None), "constraint_name", None)
            )
            # logger.exception(f"Database integrity error during registration")
            if constraint_name == "users_email_key":
                raise EmailAlreadyExistsError("Email ID already exists") from exc

            elif constraint_name == "users_username_key":
                raise UsernameAlreadyExistsError("Username already exists") from exc

            elif constraint_name == "fk_users_preferred_language":
                raise InvalidPreferredLanguageError("Invalid preferred language ID") from exc
                
            else:
                logger.exception("Unexpected database integrity error")
                raise 

        logger.info("User registered successfully")
        return create_user