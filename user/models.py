from django.db import models
from django.core.validators import RegexValidator
from common.common_utils import arabic_to_persian, persian_digit_to_english
from django.contrib.auth.models import AbstractBaseUser


class User(AbstractBaseUser):
    phone_number = models.CharField(
        max_length=11,
        unique=True,
        verbose_name="شماره همراه",
        db_index=True,
        validators=[
            RegexValidator(regex="^0[0-9]{10}$", message="فرمت شماره همراه صحیح نیست.")
        ],
    )
    first_name = models.CharField(max_length=100, null=True, verbose_name="نام")
    last_name = models.CharField(max_length=100, null=True, verbose_name="نام خانوادگی")
    email = models.EmailField(
        validators=[
            RegexValidator(
                regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
                message="فرمت ایمیل معتبر نیست.",
            )
        ],
        unique=True,
        blank=False,
        null=False,
        verbose_name="ایمیل",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.phone_number = persian_digit_to_english(self.phone_number)
        self.first_name = arabic_to_persian(self.first_name)
        self.last_name = arabic_to_persian(self.last_name)
        super().save(*args, **kwargs)

    def fullname(self):
        return f"{self.first_name} {self.last_name}"
