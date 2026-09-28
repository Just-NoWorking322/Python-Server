from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from .models import Order
from .serializers import OrderSerializer
from .permissions import OrderPermission
from services.signals import invalidate_top_5_cache


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet для заявок клиентов (Заказы):
    - Создание заявки (POST): доступно любому клиенту/гостю без авторизации.
    - Просмотр списка заявок (GET):
      * Мастер видит ТОЛЬКО заявки на свои собственные услуги.
      * Администратор видит ВСЕ заявки в системе.
    - Удаление заявки (DELETE):
      * Разрешено ТОЛЬКО администратору сервиса. Мастерам удалять запрещено!
    """
    serializer_class = OrderSerializer
    permission_classes = [OrderPermission]
    search_fields = ['client_name', 'client_phone', 'comment', 'service__title']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Order.objects.none()

        # Администратор видит все заявки сервиса
        if user.is_staff or user.is_superuser:
            return Order.objects.all().select_related('service', 'service__author')

        # Мастер видит только заявки, оформленные на его услуги (чужие заявки скрыты)
        return Order.objects.filter(service__author=user).select_related('service', 'service__author')

    def perform_create(self, serializer):
        serializer.save()
        # Обновляем кэш топа популярных услуг
        invalidate_top_5_cache()

    @swagger_auto_schema(
        operation_summary="Оставить заявку («Заказать услугу»)",
        operation_description="Клиент указывает ID услуги, свое имя, номер телефона и комментарий (адрес или время)."
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Список заявок",
        operation_description=(
            "Мастер видит только заявки на свои услуги. "
            "Администратор сервиса видит все поступившие заявки."
        )
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удалить заявку (Только для Администратора)",
        operation_description="Мастерам удаление заявок запрещено. Только админ может удалить заявку из базы."
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
