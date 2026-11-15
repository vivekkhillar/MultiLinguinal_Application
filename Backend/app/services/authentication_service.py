from security.password import PasswordHashing
from repositories.user_repository import UserRepository
from sqlalchemy.exc import IntegrityError

class AuthenticService:

    """
        The registration flow should be:
        1. Receive registration details: username, email, password, first_name, optional last_name and preferred_language_id.
        2. Check whether the email already exists using UserRepository.get_by_email().
        3. Check whether the username already exists using UserRepository.get_by_username().
        4. Hash the raw password using PasswordHashing.hash_password().
        5. Call UserRepository.create() with the hashed password.
        6. Return the safe user details received from the repository.
    """


    def __init__(self,session : AsyncSession):
        
        self.password_hashed = PasswordHashing()
        self.user_repo = UserRepository()
        self.session = session

    async def register(self,**kwargs):

        payload = {
            "user_name" : kwargs['user_name'],
            "email" : kwargs['email'],
            "password" : await self.password_hashed(kwargs['password']),
            "first_name" : kwargs['first_name'],
            "preferred_language_id": kwargs['preferred_language_id'],
            "last_name" : kwargs.get("last_name") # if you want to send the last_name is optional then you have to send like this
        }

        if await UserRepository.get_by_email(kwargs['email']):
            raise ValueError("Email ID already exists")
        
        if await UserRepository.get_by_username(kwargs['user_name']):
            raise ValueError("user name already exists")

        try:
            create_user = await self.user_repo.create(payload)

        except IntegrityError as exc:
            raise ValueError("Username or email already exists") from exc
        
        return create_user