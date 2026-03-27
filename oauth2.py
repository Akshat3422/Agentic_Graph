from dotenv import load_dotenv
from jose import JWTError, jwt 
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from schemas.token import TokenData
from database import get_db
from models import User
import os


oauth2_scheme=OAuth2PasswordBearer(tokenUrl='login')
#SECRET_KEY
#Algorithm
#Expiration time
load_dotenv()

SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES=os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set")

if not ALGORITHM:
    raise RuntimeError("ALGORITHM is not set")

if not ACCESS_TOKEN_EXPIRE_MINUTES:
    raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES is not set")

SECRET_KEY = str(SECRET_KEY)
ALGORITHM = str(ALGORITHM)
ACCESS_TOKEN_EXPIRE_MINUTES = int(ACCESS_TOKEN_EXPIRE_MINUTES)



def create_access_token(data:dict):
    to_encode=data.copy()
    expire= datetime.utcnow()+timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)) #type:ignore
    to_encode.update({"exp":expire})

    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM) #type: ignore
    return encoded_jwt

def verify_access_token(token:str,credentials_exception):
    try:
        payload= jwt.decode(token=token,key=SECRET_KEY,algorithms=[ALGORITHM]) #type: ignore
        id:str=payload.get("user_id") #type: ignore
        if id is None:
            raise credentials_exception
        token_data=TokenData(id=str(id))
    except JWTError:
        raise credentials_exception
    return token_data
     
def get_current_user(token:str=Depends(oauth2_scheme),db:Session=Depends(get_db)):
    credentials_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                        detail="Could not validate credentials",
                                        headers={"WWW-Authenticate":"Bearer"})
    token=verify_access_token(token,credentials_exception) # type: ignore
    user=db.query(User).filter(User.id==token.id).first() # type: ignore
    if not user:
        raise credentials_exception
    return user