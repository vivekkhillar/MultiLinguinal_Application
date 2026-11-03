import jwt
from typing import Optional, Dict, Any
from datetime import datetime,timezone,timedelta
from core.config import config
from core.logging_config import _get_logger
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
logger = _get_logger()

class JWT:

    def __init__(self) -> None:
        cfg = config()
        self.algorithm : str = cfg.JWT_ALGORITHM
        self.secretKey : str = cfg.JWT_SECRET_KEY
        self.expire_minutes = int(cfg.ACCESS_TOKEN_EXPIRE_MINUTES)

    def create_access_token(self,sub: str, expires_delta: Optional[timedelta] = None) -> str: 

        now = datetime.now(timezone.utc)

        if expires_delta is not None:
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

        except Exception:
            logger.exception("Failed to generate access token")
            raise
    
    def decode_access_token(self,encoded_string: str) -> Dict[str, Any]:
        
        try:

            payload = jwt.decode(
                encoded_string, self.secretKey, algorithms=[self.algorithm], options= {"require" : ["exp", "iat", "sub", "type"]},
            )

            # Ensure this is an access token, not another token type
            if payload.get('type') != "access":
                logger.warning("Token verification failed: Invalid token type")
                raise InvalidTokenError("Invalid token type")

            return payload

        except ExpiredSignatureError:
            logger.warning("Token verification failed: Token has expired")
            raise

        except InvalidTokenError as e:
            logger.warning("Token verification failed: %s", str(e))
            raise