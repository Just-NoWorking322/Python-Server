from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import UserRegisterView, UserProfileView

urlpatterns = [
    # Регистрация
    path('register/', UserRegisterView.as_view(), name='auth-register'),
    
    # Вход и получение JWT-токенов (access + refresh)
    path('token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    
    # Обновление access-токена с помощью refresh-токена
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Профиль текущего авторизованного пользователя
    path('me/', UserProfileView.as_view(), name='auth-me'),
]
