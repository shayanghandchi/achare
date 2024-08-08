from django.urls import path
from rest_framework.routers import DefaultRouter
from user.api.user_login.views import RegisterView

router = DefaultRouter()

urlpatterns = [
    path("user_register/", RegisterView.as_view()),
]

urlpatterns += router.urls
