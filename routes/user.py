from fastapi import status,HTTPException,Depends,APIRouter
from sqlalchemy.orm import Session
from database import engine,get_db
from datetime import datetime
from oauth2 import get_current_user
from schemas.users.schema import UserOut, UserCreate, DeleteAccountRequest, UserUpdate
from schemas.email.schema import VerifyEmailOTP
from utils import send_otp_email,generate_otp,otp_expiry_time,hash,verify
from models import User
from app_logger import setup_logging


logger = setup_logging(__name__)



user_router=APIRouter(
    prefix="/users",
    tags=["Users"]
)



@user_router.post("/",status_code=status.HTTP_201_CREATED)
def create_user(user:UserCreate, db:Session=Depends(get_db)):
    # hash the password
    try:
        hashed_password=hash(user.password)
        otp = generate_otp()
        expiry = otp_expiry_time()
        # cursor.execute("""INSERT INTO users(email,password) VALUES(%s,%s) RETURNING *""",(user.email,hashed_password))
        user.password=hashed_password
        new_user=User(
            username=user.username,
            email=user.email,
            password=hashed_password,
            email_otp=otp,
            otp_expiry=expiry,
            is_email_verified=False
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        send_otp_email(new_user.email, otp) # type: ignore
        logger.info(f"New user created: {new_user.username}, OTP sent to email.")
    except Exception as e:
        db.rollback()  # type: ignore
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))




@user_router.post("/verify-email",status_code=status.HTTP_200_OK)
def verify_email_otp(
    request: VerifyEmailOTP,
    db: Session = Depends(get_db)
):
    try:
        user = db.query(User).filter(
            User.email == request.email
        ).first()


        if not user:
            raise HTTPException(status_code=400, detail="User not found")

        if not user.email_otp or not user.otp_expiry: # type: ignore
            raise HTTPException(status_code=400, detail="No active OTP")

        if datetime.utcnow() > user.otp_expiry: # type: ignore
            raise HTTPException(status_code=400, detail="OTP expired")

        if user.email_otp != request.otp: # type: ignore
            raise HTTPException(status_code=400, detail="Invalid OTP")
        
        user.is_email_verified = True # type: ignore
        user.email_otp = None # type: ignore
        user.otp_expiry = None # type: ignore

        db.commit()
        logger.info(f"Email verified for user: {user.username}")
        return {"detail": "Email verified successfully"}        
    except Exception as e:
        db.rollback()  # type: ignore
        logger.error(f"Error verifying email: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@user_router.get("/me",response_model=UserOut,status_code=status.HTTP_200_OK)
def get_user(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_email_verified: # type: ignore
        logger.warning(f"Unverified email access attempt by user: {current_user.username}")
        raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Email not verified"
    )
    try:
        logger.info(f"User data retrieved for: {current_user.username}")
        return current_user
    except Exception as e:
        db.rollback()  # type: ignore
        logger.error(f"Error retrieving user data: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))




@user_router.post("/delete/request-otp")
def request_delete_otp(
    request: DeleteAccountRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not verify(request.password, current_user.password):
        raise HTTPException(status_code=403, detail="Incorrect password")

    otp = generate_otp()
    current_user.email_otp = otp #type:ignore
    db.commit()

    send_otp_email(current_user.email, otp) #type:ignore

    return {"detail": "OTP sent to your email"}

@user_router.post("/delete/confirm")
def confirm_delete(
    otp: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.email_otp != otp: #type: ignore
        raise HTTPException(status_code=400, detail="Invalid OTP")

    db.delete(current_user)
    db.commit()

    return {"detail": "Account deleted successfully"}


@user_router.delete("/",status_code=status.HTTP_200_OK)
def delete_user(request: DeleteAccountRequest,
                otp_:str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    try:
        user = db.query(User).filter(User.username == current_user.username).first()
        otp=generate_otp()

        # otp mail sent
        send_otp_email(current_user.email,otp=otp) #type:ignore
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User not found")
        if not verify(request.password, user.password):
            logger.warning(f"Incorrect password attempt for account deletion by user: {current_user.username}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Incorrect password")
        if not current_user.is_email_verified: # type: ignore
            logger.warning(f"User is not verified please verify your name first")
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )
        if current_user.email_otp == otp_: #type: ignore

            db.delete(user)
            db.commit() 
            logger.info("The user has been succesfully deleted")
            return {"detail": f"The user with username {current_user.username} has been deleted successfully."}
        
    except Exception as e:
        db.rollback()  # type: ignore
        logger.exception("Unexpected Error Occured")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@user_router.put("/",response_model=UserOut,status_code=status.HTTP_202_ACCEPTED)
def update_user(
    updated_user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        user = db.query(User).filter(
            User.id == current_user.id
        ).first()

        if not user:
            logger.warning("New User Found please register yourself")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # EMAIL UPDATE (requires verification)
        if updated_user.email and updated_user.email != user.email:
            if not user.is_email_verified: # type: ignore
                logger.warning("Verify your current email before changing it")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                )

            existing_email = db.query(User).filter(
                User.email == updated_user.email
            ).first()
            if existing_email:
                logger.warning("Email already in use")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST)
            
            logger.info("OTP has been generated ")
            otp = generate_otp()

            logger.info("Expiry time is 10 minutes only ")
            expiry = otp_expiry_time()

            user.email = updated_user.email  # type: ignore
            user.email_otp = otp # type: ignore
            user.otp_expiry = expiry # type: ignore
            user.is_email_verified = False  # type: ignore

            logger.info(f"OTP has been generated  and send to email {user.email}")
            send_otp_email(user.email, otp)  # type: ignore

        # USERNAME UPDATE
        if updated_user.username and updated_user.username != user.username:
            existing_username = db.query(User).filter(
                User.username == updated_user.username
            ).first()

            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )

            user.username = updated_user.username  # type: ignore

        # PASSWORD UPDATE
        if updated_user.password:
            logger.info("password has been changed successfully")
            user.password = hash(updated_user.password)  # type: ignore
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()  # type: ignore
        logger.error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@user_router.post("/resend-otp",status_code=status.HTTP_200_OK)
def resend_email_otp(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        if not current_user:
            logger.warning("Unauthorized User")
            raise HTTPException(status_code=401, detail="Unauthorized")

        if current_user.is_email_verified: # type: ignore
            logger.warning("Email already verified")
            raise HTTPException(status_code=400, detail="Email already verified")

        # Optional: prevent OTP spam
        if current_user.otp_expiry and datetime.utcnow() < current_user.otp_expiry: # type: ignore

            raise HTTPException(
                status_code=429,
                detail="Please wait before requesting another OTP"
            )

        otp = generate_otp()
        expiry = otp_expiry_time()

        current_user.email_otp = otp # type: ignore
        current_user.otp_expiry = expiry # type: ignore

        logger.info("OTP resent Successful")
        send_otp_email(current_user.email, otp)  # type: ignore

        db.commit()
        return {"detail": "OTP resent successfully"}
    except Exception as e:
        db.rollback()  # type: ignore
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
