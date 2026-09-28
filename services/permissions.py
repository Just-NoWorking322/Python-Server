from rest_framework import permissions


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """
    Кастомный класс проверки прав доступа (Permissions) согласно ТЗ:
    
    1. Смотреть услуги на сайте могут вообще все (даже неавторизованные гости) -> SAFE_METHODS (GET).
    2. Добавлять новую услугу могут только зарегистрированные специалисты, вошедшие в свой аккаунт -> IsAuthenticated (POST).
    3. Редактировать (PUT/PATCH) или удалять (DELETE) услугу может только тот мастер,
       который её создал. Ни один мастер не может изменить или удалить чужую услугу!
    4. Администратор сервиса (is_staff / is_superuser) имеет право отредактировать
       или удалить любую услугу при нарушении правил.
    """

    def has_permission(self, request, view):
        # Чтение каталога разрешено абсолютно всем
        if request.method in permissions.SAFE_METHODS:
            return True
        # Создание разрешено только авторизованным мастерам
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Чтение отдельной услуги разрешено всем
        if request.method in permissions.SAFE_METHODS:
            return True
        # Редактировать и удалять может ТОЛЬКО автор либо администратор
        return bool(obj.author == request.user or (request.user and request.user.is_staff))
