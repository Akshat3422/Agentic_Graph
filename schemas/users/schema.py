from pydantic import BaseModel, EmailStr
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
    id:int
    email:EmailStr
    username:str
    class Config:
        orm_mode=True

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
