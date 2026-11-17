from typing import Optional
from pydantic import BaseModel, EmailStr,Field
from uuid import UUID

class RegisterRequest(BaseModel):

    user_name : str = Field(..., min_length=3, max_length=50)
    email : EmailStr
    password :  str = Field(..., min_length=8, max_length=128)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    preferred_language_id: UUID

class RegisterResponse(BaseModel):
    
    user_id : str
    username : str
    email : EmailStr
    first_name : str
    last_name : str
    account_status : str



class LoginRequest(BaseModel):
    user_name: str = Field(..., min_length=3, max_length=50)
    pass_word: str = Field(..., min_length=8, max_length=128)
