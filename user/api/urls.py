from django.urls import path
from rest_framework.routers import DefaultRouter
from user.api.user_login.views import LoginView

router = DefaultRouter()

urlpatterns = [
    path("user_login/", LoginView.as_view()),
]

urlpatterns += router.urls
