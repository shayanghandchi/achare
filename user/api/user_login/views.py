from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from common.common_utils import (
    mobile_format,
    cache_get_otp,
    set_and_send_login_otp_link,
)


def validate_phone_number(phone_number):
    if mobile_format.match(phone_number):
        if len(phone_number) == 10:
            phone_number = "0" + phone_number
        if phone_number.startswith("+98"):
            phone_number = "0" + phone_number[3:]
        return phone_number
    raise ValidationError("شماره موبایل وارد شده معتبر نیست")


class LoginView(APIView):

    def post(self, request):
        phone_number = request.data.get("phone_number")
        phone_number = validate_phone_number(phone_number)
        code = request.data.get("code")
        if code:
            return Response(data={"data": None}, status=status.HTTP_200_OK)

        else:
            if cache_get_otp(phone_number):
                return Response(
                    data={
                        "error": "کد ورود قبلا ارسال شده است، پس از چند دقیقه مجددا تلاش کنید"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            otp_code = set_and_send_login_otp_link(phone_number)
            return Response(
                data={
                    "message": "کد یکبار مصرف به شماره همراه شما ارسال شد.",
                    "otp_code": otp_code,
                },
                status=status.HTTP_200_OK,
            )
