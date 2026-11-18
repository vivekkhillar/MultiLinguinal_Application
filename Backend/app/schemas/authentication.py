from typing import Optional
from pydantic import BaseModel, EmailStr,Field
from uuid import UUID

# Cookie are manage by Response.set_cookie() and response.delete_cookie()


class RegisterRequest(BaseModel):

    username : str = Field(..., min_length=3, max_length=50)
    email : EmailStr
    password :  str = Field(..., min_length=8, max_length=128)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)  
    preferred_language_id: UUID

class RegisterResponse(BaseModel):
    
    user_id : UUID
    username : str
    email : EmailStr
    first_name : str
    last_name: Optional[str] = None
    account_status : str

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)

class LoginResponse(BaseModel):
    access_token : str
    token_type : str = "bearer"
    expires_in : int
    user_id : UUID
    username : str


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in : int

class LogoutResponse(BaseModel):
    message: str

