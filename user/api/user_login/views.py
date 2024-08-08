from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from common.common_utils import (
    mobile_format,
    cache_get_otp,
    set_and_send_login_otp_link,
    check_otp,
)
from common.common_user import get_user_id
from user.authentication import get_user_login_info, JWTAuthentication
from user.models import User
from user.api.user_login.serializers import UserUpdateSerializer


def validate_phone_number(phone_number):
    if mobile_format.match(phone_number):
        if len(phone_number) == 10:
            phone_number = "0" + phone_number
        if phone_number.startswith("+98"):
            phone_number = "0" + phone_number[3:]
        return phone_number
    raise ValidationError({"error": "شماره موبایل وارد شده معتبر نیست"})


class RegisterView(APIView):
    def get_authenticators(self):
        if self.request.method == "PATCH":
            return [JWTAuthentication()]
        return super().get_authenticators()

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get("phone_number")

        if not phone_number:
            raise ValidationError({"error": "ارسال شماره موبایل، اجباری است."})

        phone_number = validate_phone_number(phone_number)
        code = request.data.get("code")

        if code:
            if check_otp(phone_number, code):

                user_id = get_user_id(phone_number)
                return Response(
                    data=get_user_login_info(user_id), status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    data={"error": "کد وارد شده درست نمی باشد یا منقضی شده است."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        else:
            user = User.objects.filter(phone_number=phone_number).first()
            if not user:
                if cache_get_otp(phone_number):
                    return Response(
                        data={
                            "error": "کد ورود قبلا ارسال شده است، پس از چند دقیقه مجددا تلاش کنید"
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

                otp_code = set_and_send_login_otp_link(phone_number)
                # TODO: send OTP code to user at this step and handle potential errors
                return Response(
                    data={
                        "message": "کد یکبار مصرف به شماره همراه شما ارسال شد.",
                        "data": {
                            "is_user": False,
                            "otp_code": otp_code,
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                data={
                    "message": "رمز عبور خود را وارد کنید",
                    "data": {
                        "is_user": True,
                        "phone_number": phone_number,
                    },
                },
                status=status.HTTP_202_ACCEPTED,
            )

    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class LoginView(APIView):
# def post(self, request):
#     phone_number = request.data.get("phone_number")
#     phone_number = request.data.get("password")
#     return Response(data={})
