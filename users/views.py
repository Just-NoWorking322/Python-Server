from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from .serializers import UserSerializer, UserRegisterSerializer

User = get_user_model()


class UserRegisterView(generics.CreateAPIView):
    """
    Эндпоинт регистрации нового специалиста (мастера) или пользователя.
    Доступен всем без авторизации.
    """
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Регистрация нового мастера/пользователя",
        operation_description="Позволяет зарегистрировать нового мастера, указав логин, email, имя и пароль."
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "Пользователь успешно зарегистрирован!",
                "user": UserSerializer(user).data
            },
            status=status.HTTP_201_CREATED
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Эндпоинт просмотра и редактирования собственного профиля.
    Доступен только авторизованным пользователям.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Профиль текущего пользователя",
        operation_description="Возвращает данные вошедшего пользователя (мастера)."
    )
    def get_object(self):
        return self.request.user
