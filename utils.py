from dotenv import load_dotenv
from passlib.context import CryptContext  # type: ignore
import hashlib
import random
from datetime import datetime, timedelta, timezone
import smtplib
import os
from typing import Dict,Any,cast,List
from schemas.chatbot.schema import OperationParams,OperationType
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

    clean_params = params.model_dump()

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


import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
 
logger = logging.getLogger(__name__)
 
 
# ---------------------------------------------------------------------------
# Assumed enum – include your real import here.
# ---------------------------------------------------------------------------
from enum import Enum
 
 
class TimeRange(str, Enum):
    TODAY = "today"
    YESTERDAY = "yesterday"
    LAST_WEEK = "last_week"   
    LAST_7_DAYS="last_7_days"       # kept as calendar-week; rolling 7-days is LAST_30_DAYS-style
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    LAST_30_DAYS = "last_30_days"
    CUSTOM = "custom"
 
 
# ---------------------------------------------------------------------------
# 1. _coerce_range_value  – no logic changes needed, already correct.
# ---------------------------------------------------------------------------
def _coerce_range_value(range_value: Any) -> Optional[str]:
    """
    Convert enum-like values into the underlying string.
    The chatbot pipeline typically normalises enums to `.value`, but we keep
    this robust for any direct calls.
    """
    if range_value is None:
        return None
    if hasattr(range_value, "value"):
        return str(range_value.value)
    return str(range_value)
 
 
# ---------------------------------------------------------------------------
# 2. parse_utc_datetime
#    FIX 1 – log instead of silently swallowing exceptions.
#    FIX 2 – normalise "+0000" (no colon) so fromisoformat works on all
#             Python versions (< 3.11 rejects some ISO 8601 variants).
# ---------------------------------------------------------------------------
def parse_utc_datetime(value: Optional[str]) -> Optional[datetime]:
    """
    Parse an ISO-8601 datetime string and return it in UTC.
    Returns None when the value is empty or cannot be parsed.
    """
    if not value:
        return None
 
    v = value.strip()
 
    # Normalise trailing "Z" → "+00:00"  (common LLM / JS output).
    if v.endswith("Z"):
        v = v[:-1] + "+00:00"
 
    # FIX 2 – normalise "+0000" / "-0530" (no colon) so Python < 3.11
    # fromisoformat() can handle them.  The offset is always the last 5 chars
    # when it matches ±HHMM.
    import re
    v = re.sub(r"([+-])(\d{2})(\d{2})$", r"\1\2:\3", v)
 
    try:
        dt = datetime.fromisoformat(v)
    except ValueError as exc:
        # FIX 1 – log so callers can diagnose bad input instead of silent None.
        logger.warning("parse_utc_datetime: could not parse %r – %s", value, exc)
        return None
 
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
 
    return dt.astimezone(timezone.utc)
 
 
# ---------------------------------------------------------------------------
# 3. get_this_month_range
#    FIX 1 – end was missing hour/minute/second/microsecond=0 reset, so it
#             would carry the current time-of-day instead of midnight.
#    FIX 2 – December branch had the same missing reset.
#    FIX 3 – function is now used by get_utc_time_range_bounds to remove the
#             duplicated inline logic.
# ---------------------------------------------------------------------------
def get_this_month_range() -> tuple[datetime, datetime]:
    """
    Returns (start_of_month, start_of_next_month) in UTC.
 
    Both bounds are at midnight UTC so callers get a clean half-open interval
    [start, end) that covers exactly one calendar month.
    """
    now = datetime.now(timezone.utc)
 
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
 
    if now.month == 12:
        # FIX 1 & 2 – reset time components on *both* branches.
        end = now.replace(
            year=now.year + 1, month=1, day=1,
            hour=0, minute=0, second=0, microsecond=0,   # ← was missing
        )
    else:
        end = now.replace(
            month=now.month + 1, day=1,
            hour=0, minute=0, second=0, microsecond=0,   # ← was missing
        )
 
    return start, end
 
 
# ---------------------------------------------------------------------------
# 4. get_utc_time_range_bounds
#    FIX 1 – THIS_MONTH now delegates to get_this_month_range() instead of
#             duplicating the (buggy) logic inline.
#    FIX 2 – LAST_WEEK now returns a proper Mon-00:00 → Sun-23:59:59 calendar
#             week instead of a rolling 7-day window. Rename to LAST_7_DAYS
#             if rolling behaviour is what you need.
#    FIX 3 – CUSTOM: log a warning when a fallback bound is applied so callers
#             are not silently misled.
#    FIX 4 – CUSTOM: log a warning when start/end are swapped.
#    FIX 5 – timedelta import moved to top of file (was missing from snippet).
# ---------------------------------------------------------------------------
def get_utc_time_range_bounds(
    params: dict,
) -> Optional[tuple[datetime, datetime]]:
    """
    Returns (start_utc, end_utc) for a supported TimeRange key.
    Returns None when `range` is missing or unrecognised.
    """
    range_key = _coerce_range_value(params.get("range"))
    if not range_key:
        return None
    range_key = range_key.lower()

    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # ── TODAY ────────────────────────────────────────────────────────────────
    if range_key == TimeRange.TODAY.value:
        return (today_start, now)

    # ── YESTERDAY ────────────────────────────────────────────────────────────
    if range_key == TimeRange.YESTERDAY.value:
        start = today_start - timedelta(days=1)
        end = today_start
        return (start, end)

    # ── LAST_WEEK ────────────────────────────────────────────────────────────
    if range_key == TimeRange.LAST_WEEK.value:
        days_since_monday = today_start.weekday()
        this_monday = today_start - timedelta(days=days_since_monday)
        last_monday = this_monday - timedelta(weeks=1)
        last_sunday_end = this_monday
        return (last_monday, last_sunday_end)

    # ── LAST_7_DAYS ──────────────────────────────────────────────────────────
    if range_key == TimeRange.LAST_7_DAYS.value:
        start = today_start - timedelta(days=6)   # 6 days ago midnight
        end = today_start + timedelta(days=2)      # tomorrow midnight
        return (start, end)

    # ── THIS_MONTH ───────────────────────────────────────────────────────────
    if range_key == TimeRange.THIS_MONTH.value:
        start, _end = get_this_month_range()
        return (start, _end)

    # ── LAST_MONTH ───────────────────────────────────────────────────────────
    if range_key == TimeRange.LAST_MONTH.value:
        first_this_month = now.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        last_month_end = first_this_month
        last_month_start = (first_this_month - timedelta(days=1)).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        return (last_month_start, last_month_end)

    # ── LAST_30_DAYS ─────────────────────────────────────────────────────────
    if range_key == TimeRange.LAST_30_DAYS.value:
        return (now - timedelta(days=30), now+timedelta(days=1))

    # ── CUSTOM ───────────────────────────────────────────────────────────────
    if range_key == TimeRange.CUSTOM.value:
        start_date = parse_utc_datetime(params.get("start_date"))
        end_date = parse_utc_datetime(params.get("end_date"))

        if not start_date and not end_date:
            logger.warning(
                "get_utc_time_range_bounds: CUSTOM range requested but neither "
                "start_date nor end_date was provided."
            )
            return None

        if not start_date:
            logger.warning(
                "get_utc_time_range_bounds: CUSTOM range missing start_date; "
                "defaulting to now - 30 days."
            )
            start_date = now - timedelta(days=30)

        if not end_date:
            logger.warning(
                "get_utc_time_range_bounds: CUSTOM range missing end_date; "
                "defaulting to now."
            )
            end_date = now

        if start_date > end_date:
            logger.warning(
                "get_utc_time_range_bounds: CUSTOM start_date (%s) is after "
                "end_date (%s); swapping.",
                start_date.isoformat(),
                end_date.isoformat(),
            )
            start_date, end_date = end_date, start_date

        return (start_date, end_date)

    # ── UNRECOGNISED ─────────────────────────────────────────────────────────
    logger.warning(
        "get_utc_time_range_bounds: unrecognised range key %r; returning None.",
        range_key,
    )
    return None

def get_naive_time_range_bounds(
    params: dict,
) -> Optional[tuple[datetime, datetime]]:
    """
    Same as get_utc_time_range_bounds but strips tzinfo so it works
    with naive timestamps stored in the DB.
    """
    bounds = get_utc_time_range_bounds(params)
    if not bounds:
        return None
    start, end = bounds
    return (start.replace(tzinfo=None), end.replace(tzinfo=None))