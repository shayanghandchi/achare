from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import UserRateThrottle

from common.common_utils import (
    mobile_format,
    cache_get_otp,
    set_and_send_login_otp_link,
    check_otp,
    is_blocked,
    is_ip_blocked,
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
    throttle_classes = [UserRateThrottle]

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
        ip_address = request.META.get("REMOTE_ADDR")

        if code:
            if is_ip_blocked(ip_address):
                return Response(
                    data={
                        "error": "آیپی شما به علت خطای زیاد، به مدت 1 ساعت مسدود شده اید"
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
            if is_blocked(phone_number):
                return Response(
                    data={"error": "شما به علت خطای زیاد، به مدت 1 ساعت مسدود شده اید"},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
            if check_otp(phone_number, code, ip_address):

                user_id = get_user_id(phone_number)
                return Response(
                    data=get_user_login_info(user_id), status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    data={
                        "error": "کد وارد شده درست نمی باشد یا منقضی شده است . لطفا مجددا درخواست ارسال کد نمایید."
                    },
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

                otp_code = set_and_send_login_otp_link(phone_number, ip_address)
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


class LoginView(APIView):
    def post(self, request):
        phone_number = request.data.get("phone_number")
        password = request.data.get("password")
        if not phone_number or not password:
            return Response(
                data={"error": "شماره تماس و رمز عبور اجباری هستند."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        try:
            user = User.objects.get(phone_number=phone_number)
            if user.check_password(password):
                return Response(data=get_user_login_info(user.id))
            return Response(
                data={"error": "رمز عبور وارد شده معتبر نیست"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except User.DoesNotExist:
            # prevent users to find out user is exist or not by returning general error message
            return Response(
                {"error": "رمز عبور وارد شده معتبر نیست"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(data={})
