import re
from django.core.cache import cache
import secrets
import string
from datetime import datetime
from django.conf import settings

from achare.settings import OTP_CODE_LENGTH, OTP_TIMEOUT_SECOND, OTP_CHECK_MAX_ATTEMPT

mobile_format = re.compile(r"^(\+98|0)?9\d{9}$")


def persian_digit_to_english(num: str):
    if num is None:
        return None
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    for i in range(10):
        num = num.replace(persian_digits[i], str(i))
    return num


def arabic_to_persian(s: str):
    if s is None:
        return None
    chars = {
        "ك": "ک",
        "دِ": "د",
        "بِ": "ب",
        "زِ": "ز",
        "ذِ": "ذ",
        "شِ": "ش",
        "سِ": "س",
        "ى": "ی",
        "ي": "ی",
        "١": "۱",
        "٢": "۲",
        "٣": "۳",
        "٤": "۴",
        "٥": "۵",
        "٦": "۶",
        "٧": "۷",
        "٨": "۸",
        "٩": "۹",
        "٠": "۰",
    }
    for ar, pr in chars.items():
        s = s.replace(ar, pr)
    return s


def otp_cache_key(user_phone_number):
    return f"otp_{user_phone_number}"


def cache_get_otp(user_phone_number):
    return cache.get(otp_cache_key(user_phone_number))


def cache_set_otp(user_phone_number, otp_code):
    cache.set(otp_cache_key(user_phone_number), otp_code, OTP_TIMEOUT_SECOND)


def cache_delete_otp(user_phone_number):
    cache.delete(otp_cache_key(user_phone_number))


def generate_otp_code() -> str:
    return "".join(secrets.choice(string.digits) for _ in range(OTP_CODE_LENGTH))


def set_and_send_login_otp_link(user_phone_number: str) -> None:
    otp_code = generate_otp_code()
    cache_set_otp(user_phone_number, {"code": otp_code, "attempt": 0})
    return otp_code


def check_otp(user_phone_number, received_otp_code) -> bool:
    otp = cache_get_otp(user_phone_number)
    if otp is None:
        return False
    otp_code = otp.get("code")
    attempt = otp.get("attempt") + 1
    if attempt >= int(OTP_CHECK_MAX_ATTEMPT):
        cache_delete_otp(user_phone_number)
        return False

    cache_set_otp(user_phone_number, {"code": otp_code, "attempt": attempt})
    return otp_code == received_otp_code
