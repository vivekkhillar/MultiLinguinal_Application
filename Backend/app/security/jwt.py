import jwt
from datetime import datetime,timezone,timedelta
from core.config import config
from core.logging_config import _get_logger

logger = _get_logger()

class JWT:

    def __init__(self):

        cfg = config()
        self.algorithm : str = cfg.JWT_ALGORITHM
        self.secretKey : str = cfg.JWT_SECRET_KEY
        self.expireTime = int(cfg.ACCESS_TOKEN_EXPIRE_MINUTES)
        self.sessionExpireTime = cfg.SESSION_TOKEN_EXPIRE_DAYS

    def _create_access_token(self, expires_delta : int, sub: str) -> str: 

        now = datetime.now(timezone.utc)

        if expires_delta:
            exp = now + expires_delta
        else: 
            exp = now + timedelta(minutes=self.expire_minutes)

        payload: Dict[str, Any] = {
            "sub" : str(sub),
            "iat" : now,
            "exp" : exp,
            "type" : "access"
        }
        
        try: 

            token = jwt.encode(payload, self.secretKey, algorithm=self.algorithm, )
            logger.info("Token generated successfully")
            return token

        except Exception as e:
            logger.error("Failed to generate access token: %s",str(e))
    
    def _decode_access_token(self,encoded_string: str) -> dict:
        
        try:

            payload = jwt.decode(
                token, self.secretKey, algorithms=[self.algorithm], options= {"require" : ["exp", "iat", "sub"]},
            )

            # Ensure this is an access token, not another token type
            if payload.get('type') != "acess":
                logger.warning("Token verification failed: Invalid token type")
                raise InvalidTokenError("Invalid token type")

            return payload

        except ExpiredSignatureError:
            logger.warning("Token verification failed: Token has expired")
            raise

        except InvalidTokenError as e:
            logger.warning("Token verification failed: %s", str(e))
            raise