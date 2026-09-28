from django.core.cache import cache
from django.db.models import Count
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Service
from .serializers import ServiceSerializer
from .permissions import IsAuthorOrAdminOrReadOnly
from .filters import ServiceFilter
from .signals import TOP_5_SERVICES_CACHE_KEY, invalidate_top_5_cache


class ServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления каталогом услуг:
    - Просмотр каталога и карточки услуги: доступен всем (включая неавторизованных).
    - Добавление новой услуги: только для авторизованных мастеров (автор проставляется автоматически).
    - Редактирование / удаление: только автор услуги либо администратор.
    - Фильтрация: по категории, по статусу «Принимаю заказы сейчас», по диапазону цен.
    - Поиск: по названию и тексту описания.
    - Сортировка: по цене (возрастание/убывание), по новизне, по скидке.
    - Пагинация: порциями по 5 штук.
    """
    queryset = Service.objects.all().select_related('author')
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    filterset_class = ServiceFilter
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'discount']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        """
        Система сама автоматически запоминает автора услуги (текущего мастера)
        и мгновенно инвалидирует кэш главной страницы.
        """
        serializer.save(author=self.request.user)
        invalidate_top_5_cache()

    def perform_update(self, serializer):
        serializer.save()
        invalidate_top_5_cache()

    def perform_destroy(self, instance):
        instance.delete()
        invalidate_top_5_cache()

    @swagger_auto_schema(
        operation_summary="Блок «Топ-5 популярных услуг» (кэш в быстрой памяти)",
        operation_description=(
            "Возвращает Топ-5 актуальных услуг для главного экрана мобильного приложения. "
            "Отдается мгновенно из кэша. При добавлении или изменении услуги кэш сразу обновляется."
        ),
        responses={200: ServiceSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='top', permission_classes=[permissions.AllowAny])
    def top_services(self, request):
        """
        ТЗ пункт 5: Скорость работы (Главная страница)
        Блок «Топ-5 популярных услуг» отдается мгновенно из быстрой памяти (кэша).
        """
        cached_data = cache.get(TOP_5_SERVICES_CACHE_KEY)
        if cached_data is not None:
            response = Response(cached_data)
            response['X-Cache'] = 'HIT'
            return response

        # Если в кэше нет — выбираем топ-5 активных услуг (по количеству заявок и новизне)
        top_qs = (
            Service.objects.filter(is_active=True)
            .annotate(orders_count=Count('orders'))
            .select_related('author')
            .order_by('-orders_count', '-created_at')[:5]
        )
        serializer = self.get_serializer(top_qs, many=True)
        data = serializer.data

        # Сохраняем в кэш на 1 час (3600 секунд)
        cache.set(TOP_5_SERVICES_CACHE_KEY, data, timeout=3600)

        response = Response(data)
        response['X-Cache'] = 'MISS'
        return response

    @swagger_auto_schema(
        operation_summary="Мои услуги (для личного кабинета мастера)",
        operation_description="Возвращает список услуг, созданных текущим авторизованным мастером.",
        responses={200: ServiceSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='my-services', permission_classes=[permissions.IsAuthenticated])
    def my_services(self, request):
        """
        Список услуг текущего мастера.
        """
        services = self.queryset.filter(author=request.user)
        page = self.paginate_queryset(services)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(services, many=True)
        return Response(serializer.data)
