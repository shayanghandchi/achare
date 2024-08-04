import re

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
