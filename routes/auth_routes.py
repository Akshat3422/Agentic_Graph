from fastapi import APIRouter, HTTPException,status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from schemas import Token
from database import get_db
from oauth2 import create_access_token
from utils import verify
from models import User                              
from app_logger import setup_logging

logger = setup_logging(__name__)






router=APIRouter(
    tags=["Authentication"]
) 
@router.post("/login",response_model=Token)
def login(user_credentials:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    {
        "username":user_credentials.username,
        "password":user_credentials.password
    } #type: ignore
    user=db.query(User).filter(User.username==user_credentials.username).first()
    if not user:
        logger.warning(f"Invalid login attempt - user not found: {user_credentials.username}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid Credentials")
    if not verify(user_credentials.password,user.password):
        logger.warning(f"Invalid login attempt - bad password for user: {user_credentials.username}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid Credentials") 
    access_token=create_access_token(data={"user_id":user.id})
    logger.info(f"User logged in: {user.username}")
    return {"access_token":access_token,"token_type":"bearer"}
     