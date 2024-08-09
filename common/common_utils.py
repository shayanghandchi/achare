import re
from django.core.cache import cache
import secrets
import string
from datetime import datetime
from django.conf import settings

from achare.settings import (
    OTP_CODE_LENGTH,
    OTP_TIMEOUT_SECOND,
    OTP_CHECK_MAX_ATTEMPT,
    BLOCK_TIMEOUT_SECOND,
    USER_TIMEOUT_SECOND,
    IP_TIMEOUT_SECOND,
)

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


def block_cache_key(key):
    return f"blocked_{key}"


def ip_cache_key(key):
    return f"ip_{key}"


def user_cache_key(key):
    return f"user_{key}"


def cache_get_otp(user_phone_number):
    return cache.get(otp_cache_key(user_phone_number))


def cache_get_block(key):
    return cache.get(block_cache_key(key))


def cache_get_ip(ip):
    return cache.get(ip_cache_key(ip))


def cache_get_user(user):
    return cache.get(user_cache_key(user))


def cache_set_otp(user_phone_number, otp_code):
    cache.set(otp_cache_key(user_phone_number), otp_code, OTP_TIMEOUT_SECOND)


def cache_set_ip(ip, data):
    cache.set(ip_cache_key(ip), data, IP_TIMEOUT_SECOND)


def cache_set_block(key, value=True):
    cache.set(block_cache_key(key), value, BLOCK_TIMEOUT_SECOND)


def cache_set_user(key, value=True):
    cache.set(user_cache_key(key), value, USER_TIMEOUT_SECOND)


def cache_delete_otp(user_phone_number):
    cache.delete(otp_cache_key(user_phone_number))


def cache_delete_ip(ip):
    cache.delete(ip_cache_key(ip))


def cache_delete_user(user):
    cache.delete(user_cache_key(user))


def generate_otp_code() -> str:
    return "".join(secrets.choice(string.digits) for _ in range(OTP_CODE_LENGTH))


def set_and_send_login_otp_link(user_phone_number: str, ip_address: str) -> None:
    otp_code = generate_otp_code()
    cache_set_otp(user_phone_number, {"code": otp_code, "attempt": 0})
    cache_set_ip(ip_address, {"attempt": 0})
    return otp_code


def check_otp(user_phone_number, received_otp_code, ip_address) -> bool:
    otp = cache_get_otp(user_phone_number)
    if otp is None:
        return False
    otp_code = otp.get("code")

    if otp_code == received_otp_code:
        return True

    # otp was inccorect, increase phone_number failed attemps in the cache
    attempt = otp.get("attempt") + 1
    if attempt >= int(OTP_CHECK_MAX_ATTEMPT):
        cache_delete_otp(user_phone_number)
        cache_set_block(user_phone_number, True)
    cache_set_otp(user_phone_number, {"code": otp_code, "attempt": attempt})

    # otp was inccorect, store ip address in the cache
    ip = cache_get_ip(ip_address)
    if ip is not None:
        ip_attempt = ip.get("attempt") + 1
        cache_set_ip(ip_address, {"attempt": ip_attempt})

    return False


def is_ip_blocked(ip_address) -> bool:
    if is_blocked(ip_address):
        return True
    ip = cache_get_ip(ip_address)
    if ip is None:
        return False
    ip_attempt = ip.get("attempt")
    if ip_attempt >= int(OTP_CHECK_MAX_ATTEMPT):
        cache_delete_ip(ip_address)
        cache_set_block(ip_address, True)
        return True
    return False


def is_blocked(key) -> bool:
    is_blocked = cache_get_block(key)
    if is_blocked is None:
        return False
    return is_blocked


def set_ip_login_attempt(ip_address) -> None:
    ip = cache_get_ip(ip_address)
    if ip is None:
        ip_attempt = 1
        cache_set_ip(ip_address, {"attempt": ip_attempt})
    else:
        ip_attempt = ip.get("attempt") + 1
        cache_set_ip(ip_address, {"attempt": ip_attempt})

    if ip_attempt >= int(OTP_CHECK_MAX_ATTEMPT):
        cache_delete_ip(ip_address)
        cache_set_block(ip_address, True)


def set_user_login_attempt(user) -> None:
    user_cache = cache_get_user(user.id)
    if user_cache is None:
        attempt = 1
        cache_set_user(user.id, {"attempt": attempt})
    else:
        attempt = user_cache.get("attempt") + 1
        cache_set_user(user.id, {"attempt": attempt})

    if attempt >= int(OTP_CHECK_MAX_ATTEMPT):
        cache_delete_user(user.id)
        cache_set_block(f"user_{user.id}", True)
