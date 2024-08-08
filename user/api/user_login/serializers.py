from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from user.models import User


class UserUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "password")

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("طول رمز عبور باید حداقل 6 حرف باشد")
        return make_password(value)

    def validate(self, data):
        if self.partial:
            required_fields = [
                "first_name",
                "last_name",
                "email",
                "password",
            ]
            for field in required_fields:
                if field not in data:
                    raise serializers.ValidationError(
                        {field: "This field is required."}
                    )
        return data
