from user.models import User


def get_user_id(phone_number: str) -> str:
    user_obj, _ = User.objects.get_or_create(phone_number=phone_number)
    return str(user_obj.id)
