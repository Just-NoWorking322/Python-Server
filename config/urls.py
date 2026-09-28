"""
URL Configuration for TOP STR Enterprise project (ТОП СТР энтерпрайс).
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Настройка интерактивной документации Swagger / OpenAPI для фронтендеров и тестирования
schema_view = get_schema_view(
    openapi.Info(
        title="ТОП СТР Enterprise API",
        default_version='v1',
        description=(
            "Серверная часть для онлайн-сервиса специалистов «ТОП СТР».\n\n"
            "Здесь мастера (сантехники, электрики, репетиторы, клинеры) выкладывают услуги, "
            "а клиенты находят специалистов и оставляют заявки.\n\n"
            "**Возможности API:**\n"
            "- 🔐 Аутентификация через JWT токены (Bearer <token>)\n"
            "- 🛠 Каталог услуг: добавление, редактирование (только автор/админ), фильтры, поиск, сортировка\n"
            "- ⚡ Топ-5 популярных услуг для главного экрана мобильного приложения (мгновенно из кэша)\n"
            "- 📋 Заявки от клиентов (заказы): создание гостями, просмотр мастером только своих заявок, удаление только админом\n"
            "- ⚙ Стандартная админка Django для руководства"
        ),
        contact=openapi.Contact(email="support@topstr.enterprise"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Главная страница веб-сайта онлайн-сервиса «ТОП СТР»
    path('', TemplateView.as_view(template_name='index.html'), name='home'),

    # Стандартная панель администратора для руководства
    path('admin/', admin.site.urls),

    # Интерактивная документация Swagger и ReDoc для фронтенд-разработчиков
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # API: Аутентификация и пользователи
    path('api/auth/', include('users.urls')),

    # API: Каталог услуг
    path('api/', include('services.urls')),

    # API: Заявки клиентов
    path('api/', include('orders.urls')),
]
