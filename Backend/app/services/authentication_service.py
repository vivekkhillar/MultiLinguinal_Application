from security.password import PasswordHashing
from repositories.user_repository import UserRepository
from repositories.session_repository import SessionRepository
from security.session_token import SessionToken,SessionTokenError
from sqlalchemy.exc import IntegrityError
from core.logging_config import _get_logger
from core.config import config
from security.jwt import JWT
from core.exception import (
    EmailAlreadyExistsError, 
    UsernameAlreadyExistsError,
    InvalidPreferredLanguageError,
    InvalidCredentialsError,
    AccountInactiveError,
    InvalidSessionTokenError, 
    SessionCreationError
)
from datetime import datetime,timezone,timedelta

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


    def __init__(self, user_repository: UserRepository, 
                password_hasher: PasswordHashing,
                session_repository: SessionRepository,
                session_token: SessionToken,
                jwt: JWT,
                config_details: config):

        self.password_hashed = password_hasher
        self.user_repo = user_repository
        self.session_repo = session_repository
        self.session_token = session_token
        self.jwt = jwt
        self.cfg = config_details
        

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


    async def login(self, **kwargs):

        account_details =  await self.user_repo.get_by_username(kwargs["username"])
        if not account_details:
            raise InvalidCredentialsError()
                
        if not self.password_hashed.verify_password(password= kwargs['password'],password_hash=account_details['password_hash']):
            raise InvalidCredentialsError()

        if account_details['account_status'] != 'ACTIVE':
            raise AccountInactiveError()
        
        # Generated and send in the response
        access_token = self.jwt.create_access_token(sub=str(account_details["user_id"]))
        expires_in = self.cfg.ACCESS_TOKEN_EXPIRE_MINUTES * 60 

        # generated and send in the refresh_token field during the logout option called then from cookies it will find raw_refresh_token
        # and raw_refresh_token will hashed and store into the db user_session
        raw_refresh_token = self.session_token.generate_token()
        token_hash = self.session_token.hash_token(raw_refresh_token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=self.cfg.SESSION_TOKEN_EXPIRE_DAYS)

        payload = {
            "user_id": account_details["user_id"],
            "token_hash": token_hash,
            "ip_address": kwargs.get("ip_address"),
            "user_agent": kwargs.get("user_agent"),
            "expires_at": expires_at,
            "device_info": kwargs.get("device_info"),
        }

        
        
        created_session = await self.session_repo.create(**payload)

        if not created_session:
            raise SessionCreationError()

        logger.info("User logged in successfully")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": expires_in,
            "user_id": account_details["user_id"],
            "username": account_details["username"],
            "refresh_token": raw_refresh_token,
        }
    
    async def refresh(self, **kwargs) -> dict[str, Any]:
        
        refresh_token = kwargs.get("refresh_token")
        if not refresh_token:
            raise InvalidSessionTokenError()
        
        try:

            _token_hash = self.session_token.hash_token(refresh_token)
            
        except SessionTokenError as exc:
            raise InvalidSessionTokenError() from exc

        _token_details = await self.session_repo.get_by_token_hash(_token_hash)
        
        if not _token_details:
            raise InvalidSessionTokenError()
        
        if _token_details['session_status'] != 'ACTIVE':
            raise InvalidSessionTokenError()
        
        expires_at = _token_details["expires_at"]
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        # in the datetime.now(timezone.utc) which will return the current time with the UTC format
        if expires_at <= datetime.now(timezone.utc) : 
            raise InvalidSessionTokenError()
        
        access_token = self.jwt.create_access_token(sub = str(_token_details['user_id']))
        expires_in = self.cfg.ACCESS_TOKEN_EXPIRE_MINUTES*60


        new_raw_refresh_token = self.session_token.generate_token()
        _new_hash_token = self.session_token.hash_token(new_raw_refresh_token)

        # Rotate token hash in database
        updated_session = await self.session_repo.update_token(session_id = _token_details['session_id'],
                                                                old_token_hash = _token_hash ,
                                                                new_token_hash = _new_hash_token)

        if not updated_session:
            raise InvalidSessionTokenError()
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": expires_in,
            "refresh_token": new_raw_refresh_token,
        }



    async def logout(self, **kwargs) -> dict[str,str]:

        if not kwargs['refresh_token']:
            logger.warning("No active refresh token cookie found during logout")
            return {"message": "Logged out successfully"}

        try:
            
            # hashed the token here and passed into the below get_by_token_hash
            token_hash = self.session_token.hash_token(kwargs['refresh_token'])

        except SessionTokenError:
            
            logger.warning("Malformed refresh token received during logout")
            return {"message": "Logged out successfully."}

        session_detail = await self.session_repo.get_by_token_hash(token_hash)
            
        if session_detail:
            revoked = await self.session_repo.revoke(session_detail["session_id"])
            if not revoked:
                logger.warning("Session was already revoked or not found during revoke")
                
        return {"message": "Logged out successfully."}