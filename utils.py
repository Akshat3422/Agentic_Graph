from dotenv import load_dotenv
from passlib.context import CryptContext # type: ignore
import hashlib
import random
from datetime import datetime, timedelta
import smtplib
import os
from typing import Dict,Any,cast,List
from schemas.chatbot.schema import *
from email.message import EmailMessage
import json

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
load_dotenv()

GMAIL_ID=os.getenv("GMAIL_ID")
PASSWORD=os.getenv("PASSWORD")


def hash(password: str):
    # pre-hash to reduce any length
    pre_hashed = hashlib.sha256(password.encode()).digest()
    return pwd_context.hash(pre_hashed)

def verify(password: str, hashed):
    pre_hashed = hashlib.sha256(password.encode()).digest()
    return pwd_context.verify(pre_hashed, hashed)


def generate_otp():
    return str(random.randint(100000, 999999))

def otp_expiry_time(minutes=10):
    return datetime.utcnow() + timedelta(minutes=minutes)


def send_otp_email(to_email: str, otp: str):
    msg = EmailMessage()
    msg["Subject"] = "Verify your email"
    msg["From"] = GMAIL_ID
    msg["To"] = to_email
    msg.set_content(f"Your OTP is: {otp}")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(str(GMAIL_ID), str(PASSWORD))
        server.send_message(msg)


def output_format(response) -> Dict[str, Dict[str, Any]]:
    params: OperationParams = response.params
    operation: OperationType = response.operation

    clean_params = params.model_dump(exclude_none=True)

    # Normalize enums inside params
    for k, v in clean_params.items():
        if hasattr(v, "value"):
            clean_params[k] = v.value

    return {
        "operation": operation,   # type: ignore
        "params": clean_params
    }



def is_future_query(query: str) -> bool:
    q = query.lower()
    return any(word in q for word in {"predict", "forecast", "next year", "future"})



def extract_sub_query(response)->List[str]:
    data=json.loads(response)
    return data['sub_queries']





