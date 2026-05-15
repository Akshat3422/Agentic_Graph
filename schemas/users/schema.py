from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional


class Token(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    id: str

class UserCreate(BaseModel):
    email:EmailStr
    username:str
    password:str
    is_active:bool=True
        # This is used to tell pydantic to convert the data types from ORM to pydantic
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    username: str

class UserLogin(BaseModel):
    email:EmailStr
    password:str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None

class DeleteAccountRequest(BaseModel):
    username: str
    password: str
