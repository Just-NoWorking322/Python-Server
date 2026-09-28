from rest_framework import permissions


class OrderPermission(permissions.BasePermission):
    """
    Права доступа для заявок клиентов согласно ТЗ:
    
    1. Создать заявку («Заказать») может любой клиент (даже не зарегистрированный) -> AllowAny на POST.
    2. Просматривать список и детали заявок могут только авторизованные пользователи:
       - Мастер видит ТОЛЬКО заявки на свои услуги.
       - Администратор видит ВСЕ заявки.
    3. Удалять заявки из базы может ТОЛЬКО администратор сервиса (is_staff).
       Мастерам удаление строго запрещено!
    """

    def has_permission(self, request, view):
        # Оставить заявку может любой посетитель сайта
        if view.action == 'create':
            return True
        # Просмотр и остальные действия требуют авторизации
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Администратор имеет полные права на любые действия (включая удаление)
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Удаление заявок мастерами строго запрещено по ТЗ!
        if view.action in ['destroy']:
            return False

        # Мастер может видеть только заявку на СВОЮ услугу
        return obj.service.author == request.user
