from security.password import PasswordHashing
from repositories.user_repository import UserRepository
from sqlalchemy.exc import IntegrityError

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
            raise ValueError("Email ID already exists")
        
        if await self.user_repo.get_by_username(kwargs['user_name']):
            raise ValueError("user name already exists")

        hash_password = self.password_hashed(kwargs['password_hash'])

        payload = {
            "username" : kwargs['username'],
            "email" : kwargs['email'],
            "password_hash" : hash_password, # synchronous so no need to import await here
            "first_name" : kwargs['first_name'],
            "preferred_language_id": kwargs['preferred_language_id'],
            "last_name" : kwargs.get("last_name") # if you want to send the last_name is optional then you have to send like this
        }

        try:
            create_user = await self.user_repo.create(**payload)

        except IntegrityError as exc:
            raise ValueError("Unable to create Users into the DB") from exc
        
        return create_user